"""Local quality-first reports. Incomplete measurements stay missing."""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def quality(path):
    if not path.exists():
        return {}, False, False
    value = read(path)
    scores = [value.get(k) for k in ("correctness", "completeness", "evidence")]
    reviewed = (
        bool(value.get("reviewer"))
        and bool(value.get("answer_key_reference"))
        and all(type(s) is int and 0 <= s <= 4 for s in scores)
        and type(value.get("critical_errors")) is int
        and value["critical_errors"] >= 0
        and type(value.get("tool_policy_followed")) is bool
        and type(value.get("skill_workflow_followed")) is bool
        and type(value.get("assigned_tool_used")) is bool
    )
    acceptable = bool(
        reviewed
        and min(scores) >= 3
        and value["critical_errors"] == 0
        and value["tool_policy_followed"]
        and value["skill_workflow_followed"]
    )
    return value, bool(reviewed), acceptable


def median(rows, key):
    values = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    return statistics.median(values) if values else None


def display(value):
    return "—" if value is None else f"{value:.3f}" if isinstance(value, float) else str(value)


def write_csv(path, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def paired_rows(rows):
    keys = ("repository", "language", "skill", "mode", "repetition")
    baselines = {tuple(r[k] for k in keys): r for r in rows if r["arm"] == "baseline"}
    pairs = []
    for row in rows:
        if row["arm"] == "baseline":
            continue
        baseline = baselines[tuple(row[k] for k in keys)]
        eligible = row["acceptable"] and baseline["acceptable"]
        item = {
            **{k: row[k] for k in keys},
            "arm": row["arm"],
            "run_id": row["run_id"],
            "baseline_run_id": baseline["run_id"],
            "candidate_acceptable": row["acceptable"],
            "baseline_acceptable": baseline["acceptable"],
            "quality_eligible_pair": eligible,
        }
        for field in ("reported_cost_usd", "total_tokens", "wall_seconds"):
            a, b = row[field], baseline[field]
            item[field + "_delta"] = a - b if eligible and a is not None and b is not None else None
        pairs.append(item)
    return pairs


def export_results(campaign, plan, rows, output):
    """One portable file for reviewing a codebase's experiment outside Claude."""
    runs = []
    for row in rows:
        trial = row["run_id"].rsplit("-", 1)[0]
        folder = campaign / "trials" / trial / row["skill"]
        record = {"summary": row, "files": {}}
        for name in (
            "result.json",
            "quality.json",
            "raw_result.json",
            "tool_calls.json",
            "command.json",
            "prompt.md",
            "answer.md",
            "changes.patch",
            "stderr.log",
            "stdout.jsonl",
        ):
            path = folder / name
            if path.exists():
                record["files"][name] = path.read_text(encoding="utf-8", errors="replace")
        for subfolder in ("documents", "checks"):
            for path in sorted((folder / subfolder).rglob("*")):
                if path.is_file():
                    record["files"][str(path.relative_to(folder))] = path.read_text(
                        encoding="utf-8", errors="replace"
                    )
        runs.append(record)
    bundle = {
        "format": "evidence-based-ai-engineering-skill-experiment",
        "schema_version": 1,
        "plan": plan,
        "runs": runs,
        "skill_references": {
            str(path.relative_to(campaign / "skill-reference")): path.read_text(
                encoding="utf-8", errors="replace"
            )
            for path in sorted((campaign / "skill-reference").rglob("*"))
            if path.is_file()
        },
        "review_status": "Quality review belongs in the follow-up evaluation; blank scores are pending.",
    }
    for name in ("versions.json", "environment.json"):
        if (campaign / name).exists():
            bundle[name.removesuffix(".json")] = read(campaign / name)
    output.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")


def make_report(campaign: Path):
    plan = read(campaign / "plan.json")
    rows = []
    for trial in plan["trials"]:
        repo = next(r for r in plan["config"]["repositories"] if r["id"] == trial["repository"])
        for task in repo["tasks"]:
            folder = campaign / "trials" / trial["id"] / task["skill"]
            row = {
                "run_id": f"{trial['id']}-{task['skill']}",
                "repository": repo["id"],
                "language": repo["language"],
                "mode": trial["mode"],
                "arm": trial["arm"],
                "repetition": trial["repetition"],
                "skill": task["skill"],
                "requested_skill": {
                    "build": "developer",
                    "flow": "trace-domain-flow",
                    "architecture": "discover-architecture",
                }[task["skill"]],
                "status": "interrupted" if (folder / "started.json").exists() else "not_run",
                "attempted": (folder / "started.json").exists(),
                "reported_cost_usd": None,
                "input_tokens": None,
                "output_tokens": None,
                "cache_read_input_tokens": None,
                "cache_creation_input_tokens": None,
                "total_tokens": None,
                "accounting_complete": False,
                "wall_seconds": None,
                "tool_call_count": None,
                "checks_passed": None,
                "reported_review_status": None,
            }
            if (folder / "result.json").exists():
                result = read(folder / "result.json")
                row.update({key: result[key] for key in row if key in result})
                if not (folder / "finished.json").exists():
                    row["status"] = "interrupted"
            score, reviewed, acceptable = quality(folder / "quality.json")
            if reviewed and score.get("run_id") != row["run_id"]:
                raise ValueError(f"Quality form belongs to another run: {folder}")
            row.update(
                reviewed=reviewed,
                acceptable=bool(
                    acceptable
                    and row["status"] == "completed"
                    and (
                        row["skill"] != "build"
                        or (
                            row["reported_review_status"] == "passed"
                            and row["checks_passed"] is not False
                        )
                    )
                ),
            )
            for field in (
                "correctness",
                "completeness",
                "evidence",
                "critical_errors",
                "tool_policy_followed",
                "skill_workflow_followed",
                "assigned_tool_used",
            ):
                row[field] = score.get(field) if reviewed else None
            rows.append(row)
    report_dir = campaign / "reports"
    report_dir.mkdir(exist_ok=True)
    write_csv(report_dir / "runs.csv", rows)
    export_results(campaign, plan, rows, report_dir / "results.json")
    write_csv(report_dir / "paired.csv", paired_rows(rows))
    groups = defaultdict(list)
    for row in rows:
        groups[(row["mode"], row["repository"], row["language"], row["skill"], row["arm"])].append(
            row
        )
    summary = []
    for key, group in sorted(groups.items()):
        attempted = [r for r in group if r["attempted"]]
        reviewed = [r for r in group if r["reviewed"]]
        acceptable = [r for r in group if r["acceptable"]]
        summary.append(
            {
                **dict(zip(("mode", "repository", "language", "skill", "arm"), key, strict=True)),
                "planned": len(group),
                "attempted": len(attempted),
                "completed": sum(r["status"] == "completed" for r in group),
                "reviewed": len(reviewed),
                "acceptable": len(acceptable),
                "acceptable_rate_attempted": len(acceptable) / len(attempted)
                if attempted
                else None,
                "median_correctness": median(reviewed, "correctness"),
                "median_completeness": median(reviewed, "completeness"),
                "median_evidence": median(reviewed, "evidence"),
                "known_reported_cost_usd": sum(
                    r["reported_cost_usd"] for r in attempted if r["reported_cost_usd"] is not None
                ),
                "unknown_cost_runs": sum(r["reported_cost_usd"] is None for r in attempted),
                "median_tokens_all_attempts": median(attempted, "total_tokens"),
                "unknown_token_runs": sum(r["total_tokens"] is None for r in attempted),
                "median_seconds_all_attempts": median(attempted, "wall_seconds"),
                "median_tokens_acceptable": median(acceptable, "total_tokens"),
            }
        )
    write_csv(report_dir / "summary.csv", summary)
    # Keep every repository as a block instead of letting large repositories dominate.
    lines = [
        "# Agent tool experiment results",
        "",
        "Quality is reviewed separately from efficiency. Runs awaiting review have no quality verdict.",
        "Reported USD is Claude's estimate, not an invoice. Unknown cost is not zero.",
        "Do not compare chained and independent results as if their inputs were identical.",
        "",
        "| Mode | Repository | Language | Skill | Tool | Attempts | Reviewed | Acceptable | "
        "Known USD | Unknown cost | Median tokens |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary:
        fields = (
            "mode",
            "repository",
            "language",
            "skill",
            "arm",
            "attempted",
            "reviewed",
            "acceptable",
            "known_reported_cost_usd",
            "unknown_cost_runs",
            "median_tokens_all_attempts",
        )
        lines.append("| " + " | ".join(display(row[k]).replace("|", "\\|") for k in fields) + " |")
    lines += [
        "",
        "## Interpretation",
        "",
        "Compare tools within repository, language, skill, mode, and repetition first. "
        "Use runs.csv to form matched comparisons. No overall winner is calculated.",
        "",
        "Check failures, missing measurements, policy adherence, and tool use before "
        "claiming a saving. An acceptable answer requires all three quality scores >= 3, "
        "zero critical errors, tool-policy and skill-workflow adherence, a completed run, "
        "a reported passing task review for builds, and no failed optional external checks. "
        "The reported task review is agent evidence, not an independent quality verdict.",
        "Acceptance rates use attempted runs as the denominator; reviews may still be pending, "
        "so rates are provisional until review is complete.",
        "",
    ]
    (report_dir / "results.md").write_text("\n".join(lines), encoding="utf-8")
    print(report_dir / "results.md")
    return rows
