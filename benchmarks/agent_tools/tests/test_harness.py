"""Offline checks of accounting and experiment orchestration, including real Git clones."""
# cspell:words delenv

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import harness  # noqa: E402
from demo import make_demo  # noqa: E402
from metrics import parse_stream  # noqa: E402
from report import make_report, paired_rows  # noqa: E402


def result(cost=0.1, **extra):
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "total_cost_usd": cost,
        "result": "Evidence-backed answer.",
        "modelUsage": {
            "test-model": {
                "inputTokens": 10,
                "outputTokens": 3,
                "cacheReadInputTokens": 20,
                "cacheCreationInputTokens": 5,
            }
        },
        **extra,
    }


def stream(tmp_path, events):
    file = tmp_path / "events.jsonl"
    file.write_text("\n".join(json.dumps(e) for e in events))
    return parse_stream(file)


def test_cumulative_usage_is_not_double_counted(tmp_path):
    event = {
        "type": "assistant",
        "message": {
            "model": "test-model",
            "content": [
                {"type": "tool_use", "id": "same-call", "name": "Bash", "input": {"command": "pwd"}}
            ],
            "usage": {"input_tokens": 999},
        },
    }
    data = stream(tmp_path, [event, event, result(0.05), result(0.1)])
    assert data["total_tokens"] == 38
    assert data["reported_cost_usd"] == 0.1
    assert data["tool_call_count"] == 1


def test_multiple_models_counted_once(tmp_path):
    event = result()
    event["modelUsage"]["other"] = {
        "inputTokens": 2,
        "outputTokens": 4,
        "cacheReadInputTokens": 6,
        "cacheCreationInputTokens": 8,
    }
    assert stream(tmp_path, [event])["total_tokens"] == 58


def test_missing_accounting_is_unknown(tmp_path):
    data = stream(tmp_path, [{"type": "assistant", "message": {"content": []}}])
    assert data["reported_cost_usd"] is None
    assert data["total_tokens"] is None
    assert not data["accounting_complete"]


def test_error_cost_preserved_but_crash_zeroes_not_trusted(tmp_path):
    data = stream(tmp_path, [result(0.3, subtype="error_max_turns", is_error=True)])
    assert data["reported_cost_usd"] == 0.3
    crash = stream(tmp_path, [result(0, subtype="error_during_execution", is_error=True)])
    assert crash["reported_cost_usd"] is None


def test_budget_error_prefers_model_totals(tmp_path):
    event = result(2.1, subtype="error_max_budget_usd", is_error=True)
    event["usage"] = {"input_tokens": 1, "output_tokens": 1}
    assert stream(tmp_path, [event])["total_tokens"] == 38
    event.pop("modelUsage")
    data = stream(tmp_path, [event])
    assert data["reported_cost_usd"] == 2.1
    assert data["total_tokens"] is None


def test_partial_model_counters_not_silently_zero(tmp_path):
    event = result()
    del event["modelUsage"]["test-model"]["cacheReadInputTokens"]
    assert stream(tmp_path, [event])["total_tokens"] is None


def test_delegated_skill_work_needs_whole_call_usage(tmp_path):
    event = result()
    event.pop("modelUsage")
    event["usage"] = {
        "input_tokens": 1,
        "output_tokens": 2,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0,
    }
    delegated = {
        "type": "assistant",
        "message": {
            "content": [{"type": "tool_use", "id": "review", "name": "Agent", "input": {}}]
        },
    }
    data = stream(tmp_path, [delegated, event])
    assert data["reported_cost_usd"] == 0.1
    assert data["total_tokens"] is None


def test_malformed_line_retained_and_flagged(tmp_path):
    file = tmp_path / "events.jsonl"
    file.write_text("bad line\n" + json.dumps(result()))
    data = parse_stream(file)
    assert data["malformed_lines"] == 1
    assert data["reported_cost_usd"] == 0.1


@pytest.fixture
def experiment(tmp_path, monkeypatch):
    fixture = tmp_path / "fixture"
    make_demo(fixture)
    fake = tmp_path / "fake_claude.py"
    fake.write_text('''import json, pathlib, sys
if "--version" in sys.argv:
    print("fake-claude 1.0")
    raise SystemExit()
prompt = sys.stdin.read()
root = pathlib.Path.cwd()
before = (root / "checkout.py").read_text()
if "Use the installed developer skill" in prompt:
    (root / "checkout.py").write_text("""def total(prices, discount_percent=0):
    if type(discount_percent) is not int:
        raise TypeError('integer required')
    if not 0 <= discount_percent <= 100:
        raise ValueError('range')
    return sum(prices) * (100 - discount_percent) // 100
""")
    (root / "new-file.txt").write_text("new source artifact")
    before += "\\nNo findings.\\nEXPERIMENT_REVIEW: passed"
elif "Use the installed trace-domain-flow skill" in prompt:
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "checkout-flow.md").write_text("# Checkout flow\\n")
    (root / "ARCHITECTURE.md").write_text("See docs/checkout-flow.md\\n")
else:
    before += "flow inherited" if (root / "docs" / "checkout-flow.md").exists() else ""
    (root / "ARCHITECTURE.md").write_text("# Architecture\\n")
    (root / "AGENTS.md").write_text("Canonical command: python3 -m unittest discover\\n")
payload = {
    "type": "result", "subtype": "success", "is_error": False,
    "total_cost_usd": 0.1, "result": before,
    "modelUsage": {"fake-model": {"inputTokens": 10, "outputTokens": 3,
        "cacheReadInputTokens": 20, "cacheCreationInputTokens": 5}}
}
print(json.dumps(payload))
''')
    config_path = fixture / "experiment.json"
    config = json.loads(config_path.read_text())
    config["claude_command"] = [sys.executable, str(fake)]
    config["timeout_seconds"] = 30
    for arm in config["arms"].values():
        if "version_command" in arm:
            arm["version_command"] = [sys.executable, str(fake), "--version"]
    config_path.write_text(json.dumps(config))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "offline-test-placeholder")
    return fixture, config_path, tmp_path / "campaign", fake


def test_plan_is_frozen_reproducible_and_offline(experiment, tmp_path):
    _, config, campaign, _ = experiment
    first = harness.make_plan(config, campaign)
    second = harness.make_plan(config, tmp_path / "second")
    assert first["trials"] == second["trials"]
    assert first["session_count"] == 18
    assert {trial["arm"] for trial in first["trials"]} == {"baseline", "reveal", "ast-grep"}
    assert not (campaign / "trials").exists()
    (campaign / "plan.json").write_text("{}")
    with pytest.raises(ValueError, match="Frozen plan changed"):
        harness.checked_plan(campaign)


def test_complete_campaign_isolated_chained_and_reported(experiment):
    fixture, config, campaign, _ = experiment
    original = (fixture / "repository" / "checkout.py").read_text()
    harness.make_plan(config, campaign)
    harness.run_campaign(campaign)
    rows = make_report(campaign)
    assert len(rows) == 18
    assert all(row["status"] == "completed" for row in rows)
    assert sum(row["reported_cost_usd"] for row in rows) == pytest.approx(1.8)
    assert not any(row["reviewed"] for row in rows)
    bundle = json.loads((campaign / "reports/results.json").read_text())
    assert len(bundle["runs"]) == 18
    assert "developer/SKILL.md" in bundle["skill_references"]
    exported_build = next(r for r in bundle["runs"] if r["summary"]["skill"] == "build")
    assert "changes.patch" in exported_build["files"]
    assert "stdout.jsonl" in exported_build["files"]
    assert "EXPERIMENT_REVIEW: passed" in exported_build["files"]["answer.md"]
    assert "task-reviewer/SKILL.md" in bundle["skill_references"]
    for row in rows:
        if row["skill"] == "build":
            assert row["checks_passed"] is None
            assert row["reported_review_status"] == "passed"
            continue
        trial = row["run_id"].rsplit("-", 1)[0]
        folder = campaign / "trials" / trial / row["skill"]
        answer = (folder / "answer.md").read_text()
        assert ("discount_percent" in answer) == (row["mode"] == "chained")
        if row["skill"] == "architecture":
            assert ("flow inherited" in answer) == (row["mode"] == "chained")
        assert list((folder / "documents").rglob("*.md"))
    assert (fixture / "repository" / "checkout.py").read_text() == original
    assert not harness.git(fixture / "repository", "status", "--porcelain")
    assert any(
        "new-file.txt" in p.read_text() for p in campaign.glob("trials/*/build/changes.patch")
    )
    before = [(p, p.read_bytes()) for p in campaign.glob("trials/*/*/result.json")]
    harness.run_campaign(campaign)
    assert all(p.read_bytes() == data for p, data in before)


def test_failed_optional_check_blocks_chained_followups(experiment):
    _, config, campaign, _ = experiment
    data = json.loads(config.read_text())
    data["modes"] = ["chained"]
    data["repositories"][0]["tasks"][0]["checks"] = [[sys.executable, "-c", "raise SystemExit(1)"]]
    config.write_text(json.dumps(data))
    harness.make_plan(config, campaign)
    harness.run_campaign(campaign)
    rows = make_report(campaign)
    assert sum(row["status"] == "blocked_build" for row in rows) == 6
    assert sum(row["attempted"] for row in rows) == 3


def test_campaign_budget_reserves_next_session(experiment):
    _, config, campaign, _ = experiment
    data = json.loads(config.read_text())
    data["budget_per_session_usd"] = 0.2
    data["campaign_budget_usd"] = 0.25
    config.write_text(json.dumps(data))
    harness.make_plan(config, campaign)
    harness.run_campaign(campaign)
    rows = make_report(campaign)
    assert sum(row["attempted"] for row in rows) == 1
    assert sum(row["status"] == "not_run" for row in rows) == 17


def test_unknown_cost_stops_more_sessions(experiment):
    _, config, campaign, fake = experiment
    fake.write_text(fake.read_text().replace('"total_cost_usd": 0.1', '"unknown_cost": 0.1'))
    harness.make_plan(config, campaign)
    with pytest.raises(ValueError, match="unknown cost"):
        harness.run_campaign(campaign)
    rows = make_report(campaign)
    assert sum(row["attempted"] for row in rows) == 1
    assert next(row for row in rows if row["attempted"])["reported_cost_usd"] is None


def test_interrupted_run_is_not_retried(experiment):
    _, config, campaign, _ = experiment
    plan = harness.make_plan(config, campaign)
    folder = campaign / "trials" / plan["trials"][0]["id"] / "build"
    folder.mkdir(parents=True)
    harness.write_json(folder / "started.json", {})
    with pytest.raises(ValueError, match="Interrupted run"):
        harness.run_campaign(campaign)
    assert not (folder / "result.json").exists()


def test_evaluator_changes_rejected_before_spend(experiment):
    fixture, config, campaign, _ = experiment
    evaluator = fixture / "optional-check.py"
    evaluator.write_text("pass")
    data = json.loads(config.read_text())
    data["repositories"][0]["evaluation_files"] = [str(evaluator)]
    config.write_text(json.dumps(data))
    harness.make_plan(config, campaign)
    evaluator.write_text("raise RuntimeError('changed')")
    with pytest.raises(ValueError, match="Evaluation input changed"):
        harness.run_campaign(campaign)
    assert not (campaign / "trials").exists()


def test_timeout_preserves_partial_stream(tmp_path):
    command = [
        sys.executable,
        "-u",
        "-c",
        "import time; print('partial', flush=True); time.sleep(30)",
    ]
    output = tmp_path / "timeout"
    value = harness.execute(command, tmp_path, output, 0.2)
    assert value["timed_out"]
    assert "partial" in (output / "stdout.jsonl").read_text()


def test_analysis_source_edit_invalidates_session(experiment):
    _, config, campaign, fake = experiment
    fake.write_text(
        fake.read_text().replace('if "Use the installed developer skill" in prompt:', "if True:")
    )
    data = json.loads(config.read_text())
    data["modes"] = ["independent"]
    config.write_text(json.dumps(data))
    harness.make_plan(config, campaign)
    harness.run_campaign(campaign)
    rows = make_report(campaign)
    assert sum(row["status"] == "invalid_source_changes" for row in rows) == 6


def test_cli_limits_and_tools_are_explicit():
    config = {
        "claude_command": ["claude"],
        "model": "test",
        "effort": "high",
        "max_turns": 10,
        "budget_per_session_usd": 1,
    }
    args = harness.claude_argv(config, "flow")
    assert "--bare" not in args
    assert "--dangerously-skip-permissions" not in args
    assert "--tools" not in args
    assert "--setting-sources" not in args
    assert "--strict-mcp-config" not in args
    allowed = args[args.index("--allowedTools") + 1]
    assert all(name in allowed for name in ("Skill", "Write", "Edit", "Agent"))
    assert "--no-session-persistence" in args


@pytest.mark.parametrize("skill", ["build", "flow"])
def test_quality_does_not_turn_missing_scores_into_success(experiment, skill):
    _, config, campaign, _ = experiment
    plan = harness.make_plan(config, campaign)
    folder = campaign / "trials" / plan["trials"][0]["id"] / skill
    folder.mkdir(parents=True)
    run_id = f"{plan['trials'][0]['id']}-{skill}"
    harness.write_json(
        folder / "result.json",
        {
            "attempted": True,
            "status": "completed",
            "reported_cost_usd": 0.1,
            "reported_review_status": "passed" if skill == "build" else None,
        },
    )
    harness.write_json(folder / "finished.json", {})
    form = harness.review_form(run_id)
    harness.write_json(folder / "quality.json", form)
    assert not next(r for r in make_report(campaign) if r["run_id"] == run_id)["reviewed"]
    form.update(
        reviewer="reviewer",
        answer_key_reference="key-v1",
        correctness=4,
        completeness=3,
        evidence=3,
        critical_errors=0,
        tool_policy_followed=True,
        skill_workflow_followed=True,
        assigned_tool_used=True,
    )
    harness.write_json(folder / "quality.json", form)
    assert next(r for r in make_report(campaign) if r["run_id"] == run_id)["acceptable"]
    if skill == "build":
        record = harness.read_json(folder / "result.json")
        for status in ("blocked", "missing"):
            record["reported_review_status"] = status
            harness.write_json(folder / "result.json", record)
            assert not next(r for r in make_report(campaign) if r["run_id"] == run_id)["acceptable"]
        record["reported_review_status"] = "passed"
        harness.write_json(folder / "result.json", record)
    form["critical_errors"] = 1
    harness.write_json(folder / "quality.json", form)
    assert not next(r for r in make_report(campaign) if r["run_id"] == run_id)["acceptable"]


def test_actual_skill_reference_saved_without_generic_workflow(experiment):
    _, config, campaign, _ = experiment
    plan = harness.make_plan(config, campaign)
    assert "workflow_prompts" not in plan["config"]
    source = harness.HERE.parents[1] / "developer" / "SKILL.md"
    assert (campaign / "skill-reference/developer/SKILL.md").read_bytes() == source.read_bytes()
    repo = plan["config"]["repositories"][0]
    prompt = harness.prompt_for(plan["config"], repo, plan["trials"][0], repo["tasks"][0])
    assert "Use the installed developer skill" in prompt
    assert "Use the installed task-reviewer skill" in prompt
    assert "do not create a separate reviewer session or subagent" in prompt
    assert "ai/specs/basket-discount/" in prompt
    assert "Do not read CLAUDE.md" not in prompt
    assert "Do not ask questions" not in prompt


def test_normal_authentication_environment_is_preserved(experiment, monkeypatch):
    _, config, campaign, _ = experiment
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", "/test-existing-login")
    original = harness.execute
    observed = []

    def record(*args, **kwargs):
        env = kwargs.get("env") if "env" in kwargs else args[4] if len(args) > 4 else None
        if env is not None:
            observed.append(env)
        return original(*args, **kwargs)

    monkeypatch.setattr(harness, "execute", record)
    data = json.loads(config.read_text())
    data["campaign_budget_usd"] = 2
    config.write_text(json.dumps(data))
    harness.make_plan(config, campaign)
    harness.run_campaign(campaign)
    assert len(observed) == 1
    assert observed[0]["CLAUDE_CONFIG_DIR"] == "/test-existing-login"
    assert "ANTHROPIC_API_KEY" not in observed[0]


def test_output_cannot_contaminate_source_repo(experiment):
    fixture, config, _, _ = experiment
    with pytest.raises(ValueError, match="outside every source"):
        harness.make_plan(config, fixture / "repository" / "campaign")


def test_patch_keeps_changes_if_skill_commits(experiment, tmp_path):
    fixture, _, _, _ = experiment
    repo = fixture / "repository"
    baseline = harness.git(repo, "rev-parse", "HEAD")
    (repo / "new.txt").write_text("committed by the workflow")
    harness.git(repo, "add", "new.txt")
    harness.git(repo, "commit", "-m", "Skill change")
    output = tmp_path / "snapshot"
    output.mkdir()
    harness.snapshot(repo, output, baseline)
    assert "committed by the workflow" in (output / "changes.patch").read_text()


def test_check_command_is_not_shell_interpolated(tmp_path):
    target = tmp_path / "accidental"
    value = harness.execute(
        [sys.executable, "-c", "import sys; print(sys.argv[1])", f"$(touch {target})"],
        tmp_path,
        tmp_path / "output",
        5,
    )
    assert value["exit_code"] == 0
    assert not target.exists()


@pytest.mark.parametrize("arm", ["reveal", "ast-grep"])
def test_matched_efficiency_requires_both_quality_verdicts(arm):
    baseline = {
        "repository": "a",
        "language": "python",
        "skill": "build",
        "mode": "independent",
        "repetition": 1,
        "run_id": "baseline-run",
        "arm": "baseline",
        "acceptable": True,
        "reported_cost_usd": 1,
        "total_tokens": 100,
        "wall_seconds": 20,
    }
    candidate = dict(
        baseline,
        run_id=f"{arm}-run",
        arm=arm,
        acceptable=False,
        reported_cost_usd=0.5,
        total_tokens=50,
        wall_seconds=10,
    )
    pair = paired_rows([baseline, candidate])[0]
    assert pair["reported_cost_usd_delta"] is None
    candidate["acceptable"] = True
    pair = paired_rows([baseline, candidate])[0]
    assert pair["baseline_run_id"] == "baseline-run"
    assert pair["reported_cost_usd_delta"] == -0.5
    assert pair["total_tokens_delta"] == -50
    candidate["total_tokens"] = None
    assert paired_rows([baseline, candidate])[0]["total_tokens_delta"] is None


@pytest.mark.parametrize("review", ["blocked", "missing"])
def test_task_review_blocks_chain_without_external_checks(experiment, review):
    _, config, campaign, fake = experiment
    fake.write_text(
        fake.read_text().replace(
            "EXPERIMENT_REVIEW: passed",
            "EXPERIMENT_REVIEW: blocked" if review == "blocked" else "Review not completed.",
        )
    )
    data = json.loads(config.read_text())
    data["modes"] = ["chained"]
    config.write_text(json.dumps(data))
    harness.make_plan(config, campaign)
    harness.run_campaign(campaign)
    rows = make_report(campaign)
    builds = [r for r in rows if r["skill"] == "build"]
    assert all(r["reported_review_status"] == review for r in builds)
    assert all(r["checks_passed"] is None for r in builds)
    assert sum(r["status"] == "blocked_build" for r in rows) == 6
    assert sum(r["reported_cost_usd"] for r in builds) == pytest.approx(0.3)


@pytest.mark.parametrize(
    "answer",
    [
        "No findings.",
        "EXPERIMENT_REVIEW: passed\nEXPERIMENT_REVIEW: blocked",
        "For example: EXPERIMENT_REVIEW: passed",
    ],
)
def test_review_status_needs_one_explicit_marker(answer):
    assert harness.reported_review_status(answer) == "missing"
