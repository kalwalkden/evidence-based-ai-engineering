#!/usr/bin/env python3
"""Local preflight and filtered evidence for native Codex workers; never launches models."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

SKILLS = (
    "developer",
    "task-reviewer",
    "trace-domain-flow",
    "discover-architecture",
    "archive-work-artifact",
)
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def command(argv, cwd):
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        return {
            "argv": argv,
            "cwd": str(cwd),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"argv": argv, "cwd": str(cwd), "exit_code": None, "error": str(error)}


def preflight(repo, skills_dir, tools):
    """Read source state, skills, and explicitly supplied tool commands. No installation."""
    repo, skills_dir = Path(repo).resolve(), Path(skills_dir).expanduser().resolve()
    checks, blockers = {}, []
    for name, args in {
        "root": ["rev-parse", "--show-toplevel"],
        "commit": ["rev-parse", "HEAD"],
        "status": ["status", "--porcelain"],
        "files": ["ls-files"],
    }.items():
        checks[name] = command(["git", *args], repo)
        if checks[name]["exit_code"] != 0:
            blockers.append(f"Git {name} unavailable")
    if checks["status"].get("stdout", "").strip():
        blockers.append("Source has uncommitted inputs; freeze a clean commit before trials")
    skill_files = {}
    for name in SKILLS:
        folder = skills_dir / name
        if not (folder / "SKILL.md").is_file():
            blockers.append(f"Missing installed skill: {name}")
            continue
        for file in sorted(folder.rglob("*")):
            if (
                file.is_file()
                and not any(part.startswith(".") for part in file.relative_to(folder).parts)
                and "__pycache__" not in file.parts
                and file.suffix != ".pyc"
            ):
                skill_files[f"{name}/{file.relative_to(folder)}"] = {
                    "path": str(file),
                    "sha256": sha(file.read_bytes()),
                }
    tool_checks = {}
    for name, config in tools.items():
        argv, expected = config["argv"], config["version"]
        if (
            not isinstance(argv, list)
            or not argv
            or not all(isinstance(a, str) and a for a in argv)
        ):
            raise ValueError(f"Invalid argument array for {name}")
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][\w.-]+)?", expected):
            raise ValueError(f"Exact version required for {name}")
        version = command([*argv, "--version"], repo)
        help_result = command([*argv, "--help"], repo)
        observed = re.search(r"\b\d+\.\d+\.\d+(?:[-+][\w.-]+)?", version.get("stdout", ""))
        passed = (
            version["exit_code"] == 0
            and help_result["exit_code"] == 0
            and observed is not None
            and observed.group() == expected
        )
        tool_checks[name] = {
            "version": version,
            "help": help_result,
            "expected_version": expected,
            "launcher_path": shutil.which(argv[0]),
            "passed": passed,
        }
        if not passed:
            blockers.append(f"{name}: command/version/help preflight failed")
    return {
        "format": "codex-agent-tools-preflight-v1",
        "repository": str(repo),
        "git": checks,
        "skills": skill_files,
        "tools": tool_checks,
        "local_checks_passed": not blockers,
        "blockers": blockers,
        "native_worker_smoke_test": "pending",
        "ready_for_measured_trials": False,
        "note": "Repeat on destination machine and on each prepared checkout. Native smoke, "
        "spec, dependencies, browser access, and isolation must also pass.",
    }


def collect(rollout, worker_id):
    """Exact-session, per-response accounting. Export only selected visible evidence fields."""
    raw = Path(rollout).read_bytes()
    records, problems = [], []
    for line, content in enumerate(raw.splitlines(), 1):
        try:
            item = json.loads(content)
            if not isinstance(item, dict) or not isinstance(item.get("payload"), dict):
                raise ValueError("Invalid record")
            records.append((line, item))
        except (ValueError, UnicodeDecodeError):
            problems.append(f"Malformed record at line {line}")
    identities = {
        r["payload"].get("id", r["payload"].get("session_id"))
        for _, r in records
        if r.get("type") == "session_meta"
    }
    if identities != {worker_id}:
        raise ValueError("Rollout session identity does not match exact worker ID")
    responses, evidence, contexts = {}, [], []
    for line, record in records:
        kind, payload = record.get("type"), record["payload"]
        if kind == "token_usage_record":
            # Native children use their own thread_id but the ROOT session_id.
            # Bind attribution to the exact rollout identity and worker thread_id.
            if payload.get("thread_id") != worker_id:
                problems.append(f"Foreign token record at line {line}")
                continue
            response_id, usage = payload.get("response_id"), payload.get("usage", {})
            if (
                not response_id
                or not isinstance(usage, dict)
                or any(type(usage.get(k)) is not int or usage[k] < 0 for k in TOKEN_FIELDS)
            ):
                problems.append(f"Incomplete token record at line {line}")
                continue
            usage = {k: usage[k] for k in TOKEN_FIELDS}
            if (
                usage["cached_input_tokens"] > usage["input_tokens"]
                or usage["reasoning_output_tokens"] > usage["output_tokens"]
                or usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"]
            ):
                problems.append(f"Inconsistent token record at line {line}")
            if response_id in responses and responses[response_id]["usage"] != usage:
                problems.append(f"Conflicting duplicate response: {response_id}")
            responses[response_id] = {
                "response_id": response_id,
                "usage": usage,
                "turn_id": payload.get("turn_id"),
                "line": line,
                "root_session_id": payload.get("session_id"),
            }
        elif kind == "turn_context":
            contexts.append({k: payload.get(k) for k in ("turn_id", "model", "effort", "cwd")})
        elif kind == "response_item":
            subtype = payload.get("type")
            visible = None
            if (
                subtype == "message"
                and payload.get("role") in ("user", "assistant")
                and payload.get("channel") != "analysis"
            ):
                content = [
                    {"type": p["type"], "text": p["text"]}
                    for p in payload.get("content", [])
                    if isinstance(p, dict)
                    and p.get("type") in ("input_text", "output_text", "text")
                    and isinstance(p.get("text"), str)
                ]
                visible = {"type": subtype, "role": payload["role"], "content": content}
            elif subtype in ("function_call", "custom_tool_call"):
                visible = {
                    k: payload[k]
                    for k in ("type", "call_id", "name", "arguments", "input")
                    if k in payload
                }
            elif subtype in ("function_call_output", "custom_tool_call_output"):
                visible = {k: payload[k] for k in ("type", "call_id", "output") if k in payload}
            if visible is not None:
                evidence.append({"line": line, "timestamp": record.get("timestamp"), **visible})
    if not responses:
        problems.append(
            "No per-response usage records; cumulative/account totals are not substituted"
        )
    observed = {k: sum(r["usage"][k] for r in responses.values()) for k in TOKEN_FIELDS}
    return {
        "format": "codex-agent-tools-worker-evidence-v1",
        "worker_id": worker_id,
        "source": {"path": str(Path(rollout).resolve()), "sha256": sha(raw)},
        "usage": observed if not problems else None,
        "observed_usage": observed,
        "usage_issues": problems,
        "responses": list(responses.values()),
        "contexts": contexts,
        "evidence": evidence,
        "reported_cost_usd": None,
        "cost_missing_reason": "Local rollout has no verified per-worker billed USD field",
        "coverage": "Filtered text messages and tool calls/results; excludes internal reasoning, "
        "system/developer messages, session instructions, and image/audio data. "
        "Source may be partial until worker completion and log flush are verified. "
        "Visible tool results may still contain private project data.",
    }


def locate(sessions, parent_id, agent_path):
    """Resolve native task name using explicit parent/task metadata, never filename recency."""
    matches = []
    for path in Path(sessions).expanduser().rglob("*.jsonl"):
        with path.open(encoding="utf-8") as stream:
            try:
                item = json.loads(stream.readline())
            except (ValueError, UnicodeDecodeError):
                continue
        if item.get("type") != "session_meta":
            continue
        payload = item.get("payload", {})
        source = payload.get("source")
        if not isinstance(source, dict):
            continue
        spawn = source.get("subagent", {}).get("thread_spawn", {})
        if spawn.get("parent_thread_id") == parent_id and spawn.get("agent_path") == agent_path:
            matches.append(
                {
                    "worker_id": payload.get("id", payload.get("session_id")),
                    "rollout": str(path.resolve()),
                }
            )
    if len(matches) != 1:
        raise ValueError(f"Expected one exact parent/task match; found {len(matches)}")
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("preflight")
    check.add_argument("--repo", default=".")
    check.add_argument("--skills-dir", default="~/.codex/skills")
    check.add_argument(
        "--tools", required=True, help="JSON file: reveal/ast-grep argv and exact version"
    )
    check.add_argument("--output", required=True)
    evidence = sub.add_parser("collect")
    evidence.add_argument("--rollout", required=True)
    evidence.add_argument("--worker-id", required=True)
    evidence.add_argument("--output", required=True)
    find = sub.add_parser("locate")
    find.add_argument(
        "--sessions",
        default=str(Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser() / "sessions"),
    )
    find.add_argument("--parent-id", required=True)
    find.add_argument("--agent-path", required=True)
    args = parser.parse_args()
    if args.action == "locate":
        print(json.dumps(locate(args.sessions, args.parent_id, args.agent_path), indent=2))
        return
    if args.action == "preflight":
        tools = json.loads(Path(args.tools).read_text())
        if set(tools) != {"reveal", "ast-grep"}:
            parser.error("tools must contain exactly reveal and ast-grep")
        result = preflight(args.repo, args.skills_dir, tools)
    else:
        result = collect(args.rollout, args.worker_id)
    save_new(args.output, result)
    if args.action == "preflight" and not result["local_checks_passed"]:
        raise SystemExit(1)
    if args.action == "collect" and result["usage_issues"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
