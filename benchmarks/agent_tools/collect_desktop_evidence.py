"""Recover Desktop evidence without starting agents or changing a running campaign."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

COUNTERS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Evidence path escapes its root: {relative}")
    return path


def analyze_transcript(raw, worker_id):
    """Deduplicate streaming blocks by request/message ID; retain tools and their results."""
    events, issues = [], []
    for index, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("not an object")
        except ValueError:
            issues.append(f"Unreadable transcript line {index}; snapshot may end mid-write.")
            continue
        if event.get("agentId") != worker_id:
            raise ValueError("Transcript contains an unexpected or missing worker ID")
        events.append(event)
    messages, calls, results = {}, {}, {}
    models, efforts = set(), set()
    for event in events:
        message = event.get("message", {})
        content = message.get("content", [])
        if not isinstance(content, list):
            content = []
        if event.get("type") == "assistant":
            if message.get("model"):
                models.add(message["model"])
            if event.get("effort"):
                efforts.add(event["effort"])
            identity = (event.get("requestId"), message.get("id"))
            usage = message.get("usage") or {}
            if not identity[1]:
                issues.append("Assistant response has no message ID; accounting is incomplete.")
            else:
                previous = messages.get(identity)
                if previous:
                    for field in COUNTERS:
                        a, b = previous.get(field), usage.get(field)
                        if type(a) is int and type(b) is int and b < a:
                            issues.append(f"Usage regressed for {identity[1]}: {field}.")
                # Later blocks carry cumulative usage for this response, not new requests.
                messages[identity] = usage
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("id"):
                calls[block["id"]] = {
                    "id": block["id"],
                    "name": block.get("name"),
                    "input": block.get("input"),
                    "timestamp": event.get("timestamp"),
                }
            if block.get("type") == "tool_result" and block.get("tool_use_id"):
                key = event.get("uuid"), block["tool_use_id"]
                results[key] = {**block, "timestamp": event.get("timestamp")}
    totals = {}
    for field in COUNTERS:
        values = [usage.get(field) for usage in messages.values()]
        totals[field] = (
            sum(values)
            if values and not issues and all(type(v) is int and v >= 0 for v in values)
            else None
        )
    delegated = any(c["name"] in ("Agent", "Task", "Workflow") for c in calls.values())
    totals["total_tokens"] = (
        sum(totals.values()) if all(v is not None for v in totals.values()) else None
    )
    missing = [field for field in COUNTERS if totals[field] is None]
    if missing:
        issues.append("Unreliable or missing counters: " + ", ".join(missing))
    return {
        "source": "Saved native Desktop transcript; last usage block per request/message ID",
        "scope": "Observed requests in this worker's saved transcript, including cache reads",
        "counters": totals,
        "request_count": len(messages),
        "observed_models": sorted(models),
        "observed_efforts": sorted(efforts),
        "delegated_work_observed": delegated,
        "delegation_note": "Child-worker usage is not included; do not treat this as a whole-task total."
        if delegated
        else None,
        "first_event_at": events[0].get("timestamp") if events else None,
        "last_event_at": events[-1].get("timestamp") if events else None,
        "issues": issues,
        "tool_calls": list(calls.values()),
        "tool_results": list(results.values()),
    }


def read_evidence(path, root, sources):
    data = path.read_bytes()
    name = str(path.relative_to(root))
    sources[name] = {"sha256": sha256(data), "bytes": len(data)}
    return data.decode("utf-8")


def collect(experiment, transcript_root, output):
    experiment, transcript_root, output = map(
        lambda p: Path(p).resolve(), (experiment, transcript_root, output)
    )
    if output.exists():
        raise ValueError("Choose a new output file; existing evidence is never overwritten")
    if output.is_relative_to(experiment / "checkouts"):
        raise ValueError("Evidence output must stay outside experiment checkouts")
    source = experiment / "reports/results.json"
    raw = source.read_bytes()
    bundle = json.loads(raw)
    if bundle.get("format") != "evidence-based-ai-engineering-desktop-experiment":
        raise ValueError("Expected a Desktop experiment results file")
    manifest = {"reports/results.json": {"sha256": sha256(raw), "bytes": len(raw)}}
    notes, recovered = [], []
    bundle["original_limitations"] = list(bundle.get("limitations", []))
    bundle["original_accounting_capabilities"] = copy.deepcopy(
        bundle.get("accounting_capabilities", {})
    )
    bundle["original_skill_references"] = bundle.get("skill_references", {})
    bundle["skill_references"] = {}
    for name, value in bundle["original_skill_references"].items():
        if isinstance(value, dict) and isinstance(value.get("text"), str):
            expected = value.get("sha256")
            if expected and sha256(value["text"].encode()) != expected:
                notes.append(f"Changed inline skill reference: {name}")
            else:
                bundle["skill_references"][name] = value["text"]
            continue
        if not isinstance(value, str):
            notes.append(f"Unsupported skill reference: {name}")
            continue
        if re.fullmatch(r"[0-9a-f]{64}", value):
            path = inside(experiment, "skill-reference/" + name)
            if not path.is_file() or sha256(path.read_bytes()) != value:
                notes.append(f"Missing or changed skill reference: {name}")
                continue
            try:
                bundle["skill_references"][name] = read_evidence(path, experiment, manifest)
            except UnicodeDecodeError:
                notes.append(f"Non-text skill reference omitted: {name}")
        else:
            bundle["skill_references"][name] = value
    bundle["collection_files"] = {}
    for name in ("plan.json", "verification.md", "workflow.md", "workflow.reference.js"):
        path = experiment / name
        if path.is_file():
            bundle["collection_files"][name] = read_evidence(path, experiment, manifest)
    for run in bundle.get("runs", []):
        run_id = run["run_id"]
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", run_id):
            raise ValueError("Invalid run ID")
        for attempt in run.get("attempts", []):
            worker = attempt.get("native_worker_id", "")
            if not worker:
                notes.append(
                    f"No worker ID for {run_id}; recorded status: {attempt.get('status', 'unknown')}."
                )
                continue
            if not isinstance(worker, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", worker):
                raise ValueError("Invalid native worker ID")
            files = attempt.setdefault("files", {})
            attempt["original_file_references"] = dict(files)
            for key, value in list(files.items()):
                if (
                    isinstance(value, str)
                    and value.startswith(("reports/", "tasks/"))
                    and "\n" not in value
                ):
                    path = inside(experiment, value)
                    if path.is_file():
                        files[key] = read_evidence(path, experiment, manifest)
                    else:
                        files[key] = None
                        notes.append(f"Missing artifact for {run_id}: {value}")
            # Sidecars can have been replaced by a retry; attach only a matching worker's files.
            sidecar = experiment / "reports/attempts" / f"{run_id}.attempt.json"
            if (
                sidecar.exists()
                and json.loads(sidecar.read_text()).get("native_worker_id") == worker
            ):
                files["original-attempt.json"] = read_evidence(sidecar, experiment, manifest)
                preparation = sidecar.with_name(f"{run_id}.prepare.json")
                if preparation.exists():
                    files["preparation.json"] = read_evidence(preparation, experiment, manifest)
            # Read documents from the recorded output tree, never the changing working directory.
            checkout = Path(attempt.get("checkout_dir", "")).resolve()
            tree, base = attempt.get("output_tree"), attempt.get("input_commit")
            if tree and base and checkout.is_relative_to(experiment / "checkouts"):
                if not all(re.fullmatch(r"[0-9a-f]{40,64}", rev) for rev in (tree, base)):
                    raise ValueError("Invalid tree/commit ID")
                command = ["git", "--no-optional-locks", "-C", str(checkout)]
                try:
                    paths = subprocess.check_output(
                        command + ["diff", "--name-only", "-z", base, tree, "--", "*.md"]
                    )
                    for name in paths.decode().split("\0"):
                        if not name:
                            continue
                        result = subprocess.run(
                            command + ["show", f"{tree}:{name}"], capture_output=True
                        )
                        if result.returncode == 0:
                            files["documents/" + name] = result.stdout.decode()
                except (OSError, subprocess.SubprocessError, UnicodeDecodeError) as exc:
                    notes.append(
                        f"Could not recover recorded documents for {run_id}: {type(exc).__name__}"
                    )
            matches = list(transcript_root.rglob(f"agent-{worker}.jsonl"))
            if len(matches) != 1:
                notes.append(f"Transcript match count for {worker}: {len(matches)}; none selected.")
                continue
            path = matches[0].resolve()
            if not path.is_relative_to(transcript_root):
                raise ValueError("Transcript path escapes its root")
            transcript = path.read_bytes()
            analysis = analyze_transcript(transcript.decode(), worker)
            files["native-transcript.jsonl"] = transcript.decode()
            files["native-tool-calls.json"] = json.dumps(analysis.pop("tool_calls"), indent=2)
            files["native-tool-results.json"] = json.dumps(analysis.pop("tool_results"), indent=2)
            attempt["original_validation_output_missing_reason"] = attempt.get(
                "validation_output_missing_reason"
            )
            attempt["validation_evidence_recovery"] = (
                "Raw command outputs are in native-tool-results.json, linked by tool_use_id to "
                "native-tool-calls.json. No tests were rerun; validation still needs review."
            )
            attempt["original_transcript_coverage"] = attempt.get("transcript_coverage")
            attempt["transcript_coverage"] = {
                "status": "partial",
                "reason": "Full available local file captured at collection time. Runtime completeness is not certified.",
                "source": str(path),
                "sha256": sha256(transcript),
                "bytes": len(transcript),
            }
            attempt["recovered_request_usage"] = analysis
            recovered.append(
                {"run_id": run_id, "worker_id": worker, "transcript_bytes": len(transcript)}
            )
    # A coordinator may drop a completed attempt after reconciling a gate. Preserve matching
    # native workers separately; never invent completion or merge their usage into other runs.
    known_workers = {
        a.get("native_worker_id") for r in bundle.get("runs", []) for a in r.get("attempts", [])
    }
    planned = bundle.get("plan", {}).get("runs", [])
    bundle["unlinked_worker_evidence"] = []
    for path in transcript_root.rglob("agent-*.jsonl"):
        worker = path.stem.removeprefix("agent-")
        if worker in known_workers or not path.resolve().is_relative_to(transcript_root):
            continue
        with path.open(encoding="utf-8") as handle:
            first_line = handle.readline()
        try:
            first = json.loads(first_line)
        except ValueError:
            continue
        prompt = json.dumps(first.get("message", {}).get("content", ""))
        matching = [
            r["run_id"] for r in planned if r.get("checkout_dir") and r["checkout_dir"] in prompt
        ]
        if len(matching) != 1:
            continue
        raw_transcript = path.read_bytes()
        analysis = analyze_transcript(raw_transcript.decode(), worker)
        bundle["unlinked_worker_evidence"].append(
            {
                "native_worker_id": worker,
                "candidate_run_id": matching[0],
                "note": "Prompt names this planned checkout, but no result attempt links this worker. It may be active or discarded; reconcile separately.",
                "source": str(path),
                "sha256": sha256(raw_transcript),
                "native_transcript": raw_transcript.decode(),
                "analysis": analysis,
            }
        )
    bundle["evidence_collection"] = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source_results_sha256": sha256(raw),
        "recovered_workers": recovered,
        "source_artifacts": manifest,
        "notes": notes,
        "method": "Read-only recovery; original run status, native totals, and costs were not changed.",
    }
    bundle["limitations"] = [
        "Original limitations are preserved in original_limitations; some evidence has since been recovered.",
        "Saved native transcripts improve coverage but do not certify every runtime event was persisted.",
        "Recovered request counters and original subagent_tokens have different scopes; do not combine them.",
        "Reported USD remains unavailable. No pricing estimate was fabricated.",
        "This is a snapshot of a running experiment. Later results and coordinator overhead may be absent.",
        *notes,
    ]
    bundle.setdefault("accounting_capabilities", {})["local_transcript_recovery"] = {
        "workers_recovered": len(recovered),
        "note": "See recovered_request_usage for per-worker counters, model/effort evidence, and limitations.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(bundle, handle, indent=2)
        handle.write("\n")
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True)
    parser.add_argument(
        "--transcripts", required=True, help="Local transcript directory; matches exact worker IDs"
    )
    parser.add_argument(
        "--output", required=True, help="New file, separate from live reports/results.json"
    )
    args = parser.parse_args()
    bundle = collect(args.experiment, args.transcripts, args.output)
    print(
        f"Recovered {len(bundle['evidence_collection']['recovered_workers'])} worker transcripts into {args.output}"
    )


if __name__ == "__main__":
    main()
