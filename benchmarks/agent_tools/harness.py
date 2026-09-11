#!/usr/bin/env python3
"""Headless, serial, reproducible Claude Code experiments. Python 3.10+, stdlib only."""
# cspell:words killpg getpid

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from metrics import number, parse_stream

HERE = Path(__file__).resolve().parent
ARMS = ("baseline", "reveal", "ast-grep")
SKILLS = ("build", "flow", "architecture")
SKILL_NAMES = {
    "build": "developer",
    "flow": "trace-domain-flow",
    "architecture": "discover-architecture",
}
COMMON = """This run tests the installed evidence-based-ai-engineering skills.
Follow the requested skill's full workflow, including its validation, review, archival,
documentation, and handoff requirements. Follow the target repository's normal instructions.
The only experimental override is the inspection-tool assignment below. Apply that assignment
throughout this task and any skill handoffs. Do not rewrite or replace the skill workflow.
Keep task changes in this checkout. Do not read other trial outputs or evaluator answer keys.
If a skill requires missing input or approval, report the blocker instead of guessing or bypassing it.
"""


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def git(path, *args):
    return (
        subprocess.check_output(["git", "-C", str(path), *args], stderr=subprocess.PIPE)
        .decode()
        .strip()
    )


def argv(value, name):
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f"{name} must be a nonempty array of command arguments")
    return value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", value):
        raise ValueError(f"Invalid identifier: {value!r}")
    return value


def load_config(path):
    path = Path(path).resolve()
    config = read_json(path)
    if config.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if not config.get("model") or "REPLACE" in config["model"]:
        raise ValueError("Choose an explicit Claude model before planning")
    for key in ("budget_per_session_usd", "campaign_budget_usd", "timeout_seconds"):
        if number(config.get(key)) is None or config[key] <= 0:
            raise ValueError(f"{key} must be an explicit positive number")
    for key in ("repetitions", "max_turns"):
        if type(config.get(key)) is not int or config[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if type(config.get("seed")) is not int:
        raise ValueError("seed must be an integer")
    if config.get("effort") not in ("low", "medium", "high", "max"):
        raise ValueError("Choose effort: low, medium, high, or max (model must support it)")
    modes = config.get("modes", [])
    if not modes or len(set(modes)) != len(modes) or set(modes) - {"independent", "chained"}:
        raise ValueError("modes must contain independent and/or chained, without duplicates")
    argv(config.get("claude_command"), "claude_command")
    if set(config.get("arms", {})) != set(ARMS):
        raise ValueError(f"Provide exactly these three arms: {ARMS}")
    for name, arm in config["arms"].items():
        if not arm.get("instructions"):
            raise ValueError(f"Missing instructions for {name}")
        if name != "baseline":
            argv(arm.get("version_command"), f"{name}.version_command")
    repos = config.get("repositories", [])
    if not repos or len({r["id"] for r in repos}) != len(repos):
        raise ValueError("Provide repositories with unique ids")
    for repo in repos:
        identifier(repo["id"])
        if not repo.get("language") or not repo.get("ref"):
            raise ValueError("Each repository needs a language label and Git ref")
        repo["path"] = str((path.parent / Path(repo["path"]).expanduser()).resolve())
        repo["commit"] = git(repo["path"], "rev-parse", "--verify", repo["ref"] + "^{commit}")
        if "160000 " in git(repo["path"], "ls-tree", "-r", repo["commit"]):
            raise ValueError("Submodules are not supported; use a self-contained fixture")
        repo["source_dirty"] = bool(git(repo["path"], "status", "--porcelain"))
        repo["evaluation_hashes"] = {}
        for file in repo.get("evaluation_files", []):
            file = (path.parent / file).resolve()
            repo["evaluation_hashes"][str(file)] = digest(file.read_bytes())
        if [task["skill"] for task in repo["tasks"]] != list(SKILLS):
            raise ValueError("Each repository needs tasks ordered build, flow, architecture")
        for command in repo.get("prepare", []):
            argv(command, "prepare")
        for task in repo["tasks"]:
            source = (path.parent / task.pop("prompt_file")).resolve()
            task["prompt"] = source.read_text(encoding="utf-8")
            if not task["prompt"].strip():
                raise ValueError(f"Empty prompt: {source}")
            task["prompt_sha256"] = digest(task["prompt"].encode())
            for command in task.get("checks", []):
                argv(command, "checks")
    config["common_prompt"] = COMMON
    return config


def save_skill_reference(output):
    """Record the repository skills for evidence, without installing or loading alternate skills."""
    root = HERE.parents[1]
    references = {}
    for name in (root / "installable-skills.txt").read_text().splitlines():
        if not name.strip() or name.startswith("#"):
            continue
        for source in sorted((root / name).rglob("*")):
            if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            relative = source.relative_to(root)
            content = source.read_bytes()
            target = output / "skill-reference" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            references[str(relative)] = digest(content)
    return {"repository_commit": git(root, "rev-parse", "HEAD"), "files": references}


def make_plan(config_path, output):
    config = load_config(config_path)
    output = Path(output).resolve()
    # Never put experimental answers inside a source repository visible to an agent.
    for repo in config["repositories"]:
        if output.is_relative_to(Path(repo["path"])):
            raise ValueError("Campaign output must be outside every source repository")
    output.mkdir(parents=True, exist_ok=False)
    trials = []
    rng = random.Random(config["seed"])
    # Randomize blocks and arm order reproducibly.
    blocks = [
        (repo["id"], mode, repeat)
        for repo in config["repositories"]
        for mode in config["modes"]
        for repeat in range(1, config["repetitions"] + 1)
    ]
    rng.shuffle(blocks)
    for repo_id, mode, repeat in blocks:
        arms = list(ARMS)
        rng.shuffle(arms)
        for arm in arms:
            trials.append(
                {
                    "id": f"trial-{len(trials) + 1:04d}",
                    "repository": repo_id,
                    "mode": mode,
                    "repetition": repeat,
                    "arm": arm,
                }
            )
    plan = {
        "schema_version": 1,
        "created_at": now(),
        "config": config,
        "trials": trials,
        "session_count": len(trials) * len(SKILLS),
        "maximum_requested_usd": len(trials) * len(SKILLS) * config["budget_per_session_usd"],
        "harness_sha256": harness_hash(),
        "skill_reference": save_skill_reference(output),
    }
    write_json(output / "plan.json", plan)
    (output / "plan.sha256").write_text(digest((output / "plan.json").read_bytes()) + "\n")
    print(
        json.dumps(
            {
                "campaign": str(output),
                "sessions": plan["session_count"],
                "maximum_requested_usd": plan["maximum_requested_usd"],
                "campaign_budget_usd": config["campaign_budget_usd"],
            },
            indent=2,
        )
    )
    return plan


def harness_hash():
    return digest(
        b"".join((HERE / name).read_bytes() for name in ("harness.py", "metrics.py", "report.py"))
    )


def checked_plan(campaign):
    path = campaign / "plan.json"
    if digest(path.read_bytes()) != (campaign / "plan.sha256").read_text().strip():
        raise ValueError("Frozen plan changed; create a new campaign")
    plan = read_json(path)
    if plan["harness_sha256"] != harness_hash():
        raise ValueError("Harness changed; create a new campaign")
    return plan


def execute(command, cwd, output, timeout, env=None, prompt=None):
    """Persist streams immediately and kill the process group on timeout/interruption."""
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timed_out = False
    with (
        (output / "stdout.jsonl").open("wb") as stdout,
        (output / "stderr.log").open("wb") as stderr,
    ):
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE if prompt else subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        try:
            process.communicate(input=prompt.encode() if prompt else None, timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            if isinstance(exc, KeyboardInterrupt):
                raise
            timed_out = True
    return {
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "wall_seconds": round(time.monotonic() - started, 3),
    }


def preflight(config):
    commands = {"claude": config["claude_command"] + ["--version"], "git": ["git", "--version"]}
    commands.update(
        {
            arm: value["version_command"]
            for arm, value in config["arms"].items()
            if arm != "baseline"
        }
    )
    versions = {}
    for name, command in commands.items():
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=True)
        versions[name] = {"command": command, "version": result.stdout.strip()}
    return versions


def check_evaluation_files(config):
    for repo in config["repositories"]:
        for file, expected in repo.get("evaluation_hashes", {}).items():
            if digest(Path(file).read_bytes()) != expected:
                raise ValueError(f"Evaluation input changed: {file}; create a new campaign")


def checkout(repo, destination):
    subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "--no-local",
            "--no-checkout",
            "--",
            repo["path"],
            str(destination),
        ],
        check=True,
        capture_output=True,
    )
    git(destination, "config", "core.hooksPath", "/dev/null")
    git(destination, "checkout", "--quiet", "--detach", repo["commit"])
    git(destination, "remote", "remove", "origin")
    git(destination, "config", "user.name", "Experiment Harness")
    git(destination, "config", "user.email", "experiment@localhost")


def snapshot(workspace, output, baseline="HEAD"):
    """Save a patch including new files not excluded by Git, without changing the real index."""
    index = output / "snapshot-index"
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    subprocess.run(["git", "read-tree", "HEAD"], cwd=workspace, env=env, check=True)
    subprocess.run(["git", "add", "-A"], cwd=workspace, env=env, check=True)
    patch = subprocess.check_output(
        ["git", "diff", "--cached", "--binary", baseline], cwd=workspace, env=env
    )
    tree = subprocess.check_output(["git", "write-tree"], cwd=workspace, env=env).decode().strip()
    (output / "changes.patch").write_bytes(patch)
    index.unlink()
    return tree


def run_checks(commands, workspace, output, timeout):
    results = []
    for i, command in enumerate(commands):
        result = execute(command, workspace, output / f"check-{i + 1}", timeout)
        results.append({"argv": command, **result})
    return results


def claude_argv(config, skill):
    return config["claude_command"] + [
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--model",
        config["model"],
        "--effort",
        config["effort"],
        "--max-turns",
        str(config["max_turns"]),
        "--max-budget-usd",
        str(config["budget_per_session_usd"]),
        "--no-session-persistence",
        "--allowedTools",
        "Bash,Read,Glob,Grep,Write,Edit,Skill,Agent,Task",
        "--permission-mode",
        "dontAsk",
    ]


def prompt_for(config, repo, trial, task):
    pieces = [
        config["common_prompt"],
        f"Use the installed {SKILL_NAMES[task['skill']]} skill from this repository's skill set.",
        config["arms"][trial["arm"]]["instructions"],
        "Additional project context:\n" + repo.get("context", "None supplied."),
        "Task:\n" + task["prompt"],
    ]
    if task["skill"] == "build":
        pieces.append(
            "Use the installed task-reviewer skill as the build review gate within the developer "
            "workflow, in this same context; do not create a separate reviewer session or subagent. "
            "Read the complete task/spec and resolve the exact full change target as required by "
            "that skill. Keep the review pass read-only; use developer's normal repair and "
            "validation loop for any fixes. Apply this run's inspection-tool assignment to review "
            "as well. Preserve the verified findings (or No findings.), final assessment, and "
            "material test gaps in your final response. Do not omit normal tests and validation. "
            "After your report, end with exactly one standalone accounting line: "
            "EXPERIMENT_REVIEW: passed if the final task review and required validation are "
            "complete with no unresolved findings or blockers; otherwise EXPERIMENT_REVIEW: blocked. "
            "This is your reported workflow status, not the experiment's later quality score."
        )
    if trial["mode"] == "chained" and task["skill"] != "build":
        pieces.append(
            "This checkout contains the preceding stage's code and documentation. "
            "Continue the workflow from those artifacts in this fresh conversation."
        )
    return "\n\n".join(pieces) + "\n"


def reported_review_status(answer):
    """Record the agent's report, without treating it as independent quality verification."""
    matches = re.findall(r"^EXPERIMENT_REVIEW: (passed|blocked)$", answer.strip(), re.MULTILINE)
    return matches[0] if len(matches) == 1 else "missing"


def build_ready(result):
    return (
        result.get("reported_review_status") == "passed"
        and result.get("checks_passed") is not False
    )


def spent_so_far(campaign):
    total = 0
    for file in campaign.glob("trials/*/*/result.json"):
        result = read_json(file)
        if result.get("attempted"):
            cost = result.get("reported_cost_usd")
            if cost is None:
                raise ValueError(
                    f"Unknown spend in {file}; stop and reconcile before a new campaign"
                )
            total += cost
    return total


def review_form(run_id):
    return {
        "run_id": run_id,
        "reviewer": "",
        "answer_key_reference": "",
        "correctness": None,
        "completeness": None,
        "evidence": None,
        "critical_errors": None,
        "tool_policy_followed": None,
        "skill_workflow_followed": None,
        "assigned_tool_used": None,
        "notes": "",
    }


def run_session(campaign, config, repo, trial, task, workspace, output):
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "started.json", {"started_at": now()})
    run_id = f"{trial['id']}-{task['skill']}"
    metadata = {
        "run_id": run_id,
        "repository": repo["id"],
        "language": repo["language"],
        "skill": task["skill"],
        **trial,
        "base_commit": repo["commit"],
        "input_commit": git(workspace, "rev-parse", "HEAD"),
        "input_tree": git(workspace, "rev-parse", "HEAD^{tree}"),
        "attempted": True,
        "started_at": now(),
        "configured_model": config["model"],
        "requested_skill": SKILL_NAMES[task["skill"]],
    }
    prompt = prompt_for(config, repo, trial, task)
    (output / "prompt.md").write_text(prompt, encoding="utf-8")
    command = claude_argv(config, task["skill"])
    write_json(output / "command.json", command)
    # Preserve the user's existing Claude login, skills, settings, and provider environment.
    env = dict(os.environ)
    execution = execute(command, workspace, output, config["timeout_seconds"], env, prompt)
    usage = parse_stream(output / "stdout.jsonl")
    final = usage.get("result") or {}
    status = "completed"
    if execution["timed_out"]:
        status = "timeout"
    elif (
        execution["exit_code"] != 0
        or not usage["has_result"]
        or final.get("is_error")
        or final.get("subtype") != "success"
    ):
        status = "failed"
    if usage["malformed_lines"]:
        status = "invalid_stream"
    metadata["agent_head_commit"] = git(workspace, "rev-parse", "HEAD")
    metadata["output_tree"] = snapshot(workspace, output, metadata["input_commit"])
    changed = (
        subprocess.check_output(
            ["git", "diff", "--name-only", "-z", metadata["input_tree"], metadata["output_tree"]],
            cwd=workspace,
        )
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    changed = [path for path in changed if path]
    if task["skill"] != "build":
        allowed_roots = {"ARCHITECTURE.md", "AGENTS.md"}
        if task["skill"] == "flow":
            allowed_roots.update({"README.md", "CLAUDE.md"})
        unexpected = [
            path
            for path in changed
            if path not in allowed_roots
            and not (task["skill"] == "flow" and path.startswith("docs/"))
        ]
        if unexpected:
            status = "invalid_source_changes"
        metadata["unexpected_changes"] = unexpected
    metadata["documents"] = []
    for path in changed:
        source = workspace / path
        if source.suffix == ".md" and source.is_file() and not source.is_symlink():
            target = output / "documents" / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            metadata["documents"].append(path)
    metadata["observed_skill_calls"] = [
        call["input"].get("skill") for call in usage["tool_calls"] if call["name"] == "Skill"
    ]
    answer = str(usage.pop("answer"))
    metadata["reported_review_status"] = (
        reported_review_status(answer) if task["skill"] == "build" else None
    )
    (output / "answer.md").write_text(answer, encoding="utf-8")
    write_json(output / "tool_calls.json", usage.pop("tool_calls"))
    write_json(output / "raw_result.json", usage.pop("result"))
    metadata.update(execution)
    metadata.update(usage)
    metadata.update(status=status, ended_at=now())
    # Persist spend before external checks, so a validation crash cannot erase accounting.
    write_json(output / "result.json", metadata)
    checks = run_checks(
        task.get("checks", []), workspace, output / "checks", config["timeout_seconds"]
    )
    metadata["checks"] = checks
    metadata["checks_passed"] = all(c["exit_code"] == 0 for c in checks) if checks else None
    write_json(output / "result.json", metadata)
    write_json(output / "quality.json", review_form(run_id))
    print(f"{run_id}: {status}; reported cost={metadata['reported_cost_usd']}", flush=True)
    return metadata


def run_campaign(campaign):
    campaign = Path(campaign).resolve()
    plan = checked_plan(campaign)
    config = plan["config"]
    if os.name != "posix":
        raise ValueError("The runner currently supports macOS/Linux process groups only")
    lock = campaign / "runner.lock"
    with lock.open("x") as handle:
        handle.write(str(os.getpid()))
    try:
        versions = preflight(config)
        check_evaluation_files(config)
        version_file = campaign / "versions.json"
        if version_file.exists() and read_json(version_file) != versions:
            raise ValueError("Tool versions changed; start a new campaign")
        write_json(version_file, versions)
        write_json(
            campaign / "environment.json",
            {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": platform.python_version(),
                "logical_cpu_count": os.cpu_count(),
            },
        )
        for trial in plan["trials"]:
            repo = next(r for r in config["repositories"] if r["id"] == trial["repository"])
            trial_dir = campaign / "trials" / trial["id"]
            trial_dir.mkdir(parents=True, exist_ok=True)
            for task in repo["tasks"]:
                output = trial_dir / task["skill"]
                if (output / "finished.json").exists():
                    continue
                if output.exists():
                    raise ValueError(f"Interrupted run at {output}; do not silently retry it")
                if task["skill"] != "build" and trial["mode"] == "chained":
                    previous = SKILLS[SKILLS.index(task["skill"]) - 1]
                    upstream = read_json(trial_dir / previous / "result.json")
                    if upstream["status"] != "completed" or (
                        previous == "build" and not build_ready(upstream)
                    ):
                        output.mkdir()
                        write_json(
                            output / "result.json",
                            {
                                **trial,
                                "run_id": f"{trial['id']}-{task['skill']}",
                                "skill": task["skill"],
                                "language": repo["language"],
                                "attempted": False,
                                "status": (
                                    upstream["status"]
                                    if upstream["status"].startswith("blocked_")
                                    else f"blocked_{previous}"
                                ),
                            },
                        )
                        write_json(output / "finished.json", {"finished_at": now()})
                        continue
                spent = spent_so_far(campaign)
                if spent + config["budget_per_session_usd"] > config["campaign_budget_usd"]:
                    print("Campaign budget cannot cover another session reservation; stopping.")
                    return
                check_evaluation_files(config)
                workspace = trial_dir / f"workspace-{task['skill']}"
                source = repo
                if trial["mode"] == "chained" and task["skill"] != "build":
                    previous = SKILLS[SKILLS.index(task["skill"]) - 1]
                    upstream = read_json(trial_dir / previous / "result.json")
                    source = dict(
                        repo,
                        path=str(trial_dir / f"workspace-{previous}"),
                        commit=upstream["output_commit"],
                    )
                if not workspace.exists():
                    checkout(source, workspace)
                prepared = trial_dir / f"prepared-{task['skill']}.json"
                if not prepared.exists():
                    prep = run_checks(
                        repo.get("prepare", []),
                        workspace,
                        trial_dir / f"prepare-{task['skill']}",
                        config["timeout_seconds"],
                    )
                    if any(p["exit_code"] != 0 for p in prep):
                        raise ValueError(f"Preparation failed: {workspace}")
                    if git(workspace, "status", "--porcelain", "--untracked-files=normal"):
                        raise ValueError(
                            "Preparation must not change source files that Git would track"
                        )
                    write_json(prepared, {"checks": prep, "prepared_at": now()})
                result = run_session(campaign, config, repo, trial, task, workspace, output)
                if (
                    trial["mode"] == "chained"
                    and result["status"] == "completed"
                    and (task["skill"] != "build" or build_ready(result))
                ):
                    # Commit exactly the captured agent tree, excluding changes from checks.
                    env = dict(
                        os.environ,
                        GIT_AUTHOR_DATE="2000-01-01T00:00:00+00:00",
                        GIT_COMMITTER_DATE="2000-01-01T00:00:00+00:00",
                    )
                    commit = (
                        subprocess.check_output(
                            [
                                "git",
                                "commit-tree",
                                result["output_tree"],
                                "-p",
                                result["input_commit"],
                                "-m",
                                f"Experiment {task['skill']} output",
                            ],
                            cwd=workspace,
                            env=env,
                        )
                        .decode()
                        .strip()
                    )
                    git(workspace, "update-ref", "refs/heads/experiment-output", commit)
                    # The next stages clone this exact tree into separate checkouts.
                    result["output_commit"] = commit
                    write_json(output / "result.json", result)
                write_json(output / "finished.json", {"finished_at": now()})
                if result["reported_cost_usd"] is None:
                    raise ValueError("Run has unknown cost; stopping to avoid untracked spend")
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Freeze inputs and order; no Claude calls")
    plan.add_argument("config")
    plan.add_argument("--output", required=True)
    run = commands.add_parser("run", help="Execute paid sessions from an existing frozen plan")
    run.add_argument("campaign")
    report = commands.add_parser("report", help="Create CSV and Markdown; no Claude calls")
    report.add_argument("campaign")
    demo = commands.add_parser("demo", help="Create a tiny local fixture and editable config")
    demo.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if args.command == "plan":
            make_plan(args.config, args.output)
        elif args.command == "run":
            run_campaign(args.campaign)
        elif args.command == "report":
            from report import make_report

            make_report(Path(args.campaign).resolve())
        else:
            from demo import make_demo

            make_demo(Path(args.output).resolve())
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
