"""Protect accounting boundaries and preflight against the wrong executable."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_native import collect, locate, preflight, save_new  # noqa: E402


def record(kind, **payload):
    return {"type": kind, "payload": payload}


def usage(**changes):
    return {
        "input_tokens": 100,
        "cached_input_tokens": 80,
        "cache_write_input_tokens": 0,
        "output_tokens": 20,
        "reasoning_output_tokens": 10,
        "total_tokens": 120,
        **changes,
    }


def rollout(tmp_path, *records):
    path = tmp_path / "rollout.jsonl"
    path.write_text(
        "\n".join(
            json.dumps(r)
            for r in [
                record("session_meta", id="worker", base_instructions="PRIVATE INSTRUCTIONS"),
                *records,
            ]
        )
    )
    return path


def token(response_id="response", **values):
    return record(
        "token_usage_record",
        thread_id="worker",
        session_id="worker",
        response_id=response_id,
        usage=usage(**values),
        thread_token_usage={"total_tokens": 99999},
    )


def test_duplicate_subset_accounting_and_visible_evidence(tmp_path):
    source = rollout(
        tmp_path,
        token(),
        token(),
        token("second"),
        record("turn_context", model="test-model", effort="high", secret="PRIVATE"),
        record("response_item", type="reasoning", encrypted_content="PRIVATE"),
        record("response_item", type="message", role="developer", content="PRIVATE"),
        record(
            "response_item",
            type="message",
            role="assistant",
            content=[{"type": "output_text", "text": "Done"}],
        ),
        record(
            "response_item",
            type="function_call",
            call_id="c1",
            name="tool",
            arguments='{"path":"file"}',
            internal_metadata="PRIVATE",
        ),
        record("response_item", type="function_call_output", call_id="c1", output="OK"),
    )
    result = collect(source, "worker")
    assert result["usage"]["total_tokens"] == 240
    assert result["usage"]["input_tokens"] == 200
    assert result["usage"]["cached_input_tokens"] == 160
    assert len(result["evidence"]) == 3
    assert result["reported_cost_usd"] is None
    assert "PRIVATE" not in json.dumps(result)


@pytest.mark.parametrize(
    "extra",
    [
        token(output_tokens=21, total_tokens=121),
        record("token_usage_record", thread_id="other", response_id="foreign", usage=usage()),
        token("second", total_tokens=1),
        record("token_usage_record", thread_id="worker", response_id="second", usage={}),
    ],
)
def test_uncertain_usage_is_never_reported_as_complete(tmp_path, extra):
    result = collect(rollout(tmp_path, token(), extra), "worker")
    assert result["usage"] is None
    assert result["usage_issues"]


def test_no_cumulative_fallback_or_wrong_session(tmp_path):
    path = rollout(
        tmp_path, record("event_msg", type="token_count", info={"total_token_usage": usage()})
    )
    assert collect(path, "worker")["usage"] is None
    with pytest.raises(ValueError, match="identity"):
        collect(path, "other")
    with path.open("a") as stream:
        stream.write("\nnot json\n")
    assert "Malformed" in collect(path, "worker")["usage_issues"][0]


def test_child_usage_has_root_session_id(tmp_path):
    item = token()
    item["payload"]["session_id"] = "parent"
    result = collect(rollout(tmp_path, item), "worker")
    assert result["usage"]["total_tokens"] == 120
    assert result["responses"][0]["root_session_id"] == "parent"


def test_locate_uses_parent_and_task_not_recency(tmp_path):
    meta = record(
        "session_meta",
        id="worker",
        source={
            "subagent": {
                "thread_spawn": {"parent_thread_id": "parent", "agent_path": "/root/smoke"}
            }
        },
    )
    (tmp_path / "one.jsonl").write_text(json.dumps(meta))
    assert locate(tmp_path, "parent", "/root/smoke")["worker_id"] == "worker"
    with pytest.raises(ValueError, match="found 0"):
        locate(tmp_path, "other", "/root/smoke")
    (tmp_path / "two.jsonl").write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="found 2"):
        locate(tmp_path, "parent", "/root/smoke")


def test_never_overwrite_evidence(tmp_path):
    target = tmp_path / "result.json"
    save_new(target, {"original": True})
    with pytest.raises(FileExistsError):
        save_new(target, {"original": False})
    assert json.loads(target.read_text())["original"] is True


def test_wrong_version_missing_skills_and_dirty_source_block(tmp_path, monkeypatch):
    def fake(argv, cwd):
        output = ""
        if "--version" in argv:
            output = "reveal 0.112.0"
        elif "status" in argv:
            output = " M source.py"
        return {"exit_code": 0, "stdout": output, "stderr": ""}

    monkeypatch.setattr("codex_native.command", fake)
    result = preflight(
        tmp_path, tmp_path / "skills", {"reveal": {"argv": ["reveal"], "version": "0.127.0"}}
    )
    assert not result["local_checks_passed"]
    assert any("version" in p for p in result["blockers"])
    assert any("uncommitted" in p for p in result["blockers"])
    assert any("Missing installed skill" in p for p in result["blockers"])


def test_preflight_success_still_requires_native_smoke(tmp_path, monkeypatch):
    from codex_native import SKILLS

    for name in SKILLS:
        folder = tmp_path / "skills" / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text("Skill instructions")

    def fake(argv, cwd):
        return {
            "exit_code": 0,
            "stdout": "reveal 0.127.0" if "--version" in argv else "",
            "stderr": "",
        }

    monkeypatch.setattr("codex_native.command", fake)
    result = preflight(
        tmp_path, tmp_path / "skills", {"reveal": {"argv": ["reveal"], "version": "0.127.0"}}
    )
    assert result["local_checks_passed"]
    assert not result["ready_for_measured_trials"]
    assert len(result["skills"]) == len(SKILLS)
