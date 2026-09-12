"""Recovery never changes live results, and streamed accounting is counted once."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collect_desktop_evidence import analyze_transcript, collect  # noqa: E402


def event(output=1, **extra):
    return {
        "type": "assistant",
        "agentId": "worker1",
        "requestId": "request1",
        "effort": "high",
        "message": {
            "id": "message1",
            "model": "model1",
            "usage": {
                "input_tokens": 2,
                "cache_creation_input_tokens": 3,
                "cache_read_input_tokens": 40,
                "output_tokens": output,
            },
            "content": [
                {
                    "type": "tool_use",
                    "id": "tool1",
                    "name": "Bash",
                    "input": {"command": "npm test"},
                }
            ],
        },
        **extra,
    }


def test_streaming_blocks_count_once_and_results_survive():
    result = {
        "type": "user",
        "agentId": "worker1",
        "uuid": "result1",
        "message": {
            "content": [
                {"type": "tool_result", "tool_use_id": "tool1", "content": "42 tests passed"}
            ],
        },
    }
    raw = "\n".join(map(json.dumps, [event(), event(10), event(10), result, result]))
    data = analyze_transcript(raw, "worker1")
    assert data["counters"]["total_tokens"] == 55
    assert data["request_count"] == 1
    assert len(data["tool_calls"]) == 1
    assert len(data["tool_results"]) == 1
    assert data["tool_results"][0]["content"] == "42 tests passed"
    assert data["observed_efforts"] == ["high"]


@pytest.mark.parametrize(
    "raw",
    [
        json.dumps(event(10)) + "\n" + json.dumps(event(1)),
        json.dumps(event(10)) + '\n{"partial":',
    ],
)
def test_regressed_or_partial_usage_is_not_treated_as_complete(raw):
    data = analyze_transcript(raw, "worker1")
    assert data["counters"]["total_tokens"] is None
    assert data["issues"]


def test_missing_counter_and_wrong_worker():
    e = event()
    del e["message"]["usage"]["output_tokens"]
    assert analyze_transcript(json.dumps(e), "worker1")["counters"]["total_tokens"] is None
    with pytest.raises(ValueError, match="worker ID"):
        analyze_transcript(json.dumps(event(agentId="someone-else")), "worker1")


def test_recovery_embeds_artifacts_without_mutating_live_results(tmp_path):
    campaign = tmp_path / "campaign"
    attempts = campaign / "reports/attempts"
    attempts.mkdir(parents=True)
    (attempts / "build.report.txt").write_text("No findings.")
    skill = campaign / "skill-reference/developer/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Installed developer instructions")
    inline = "Another installed skill"
    inline_hash = hashlib.sha256(inline.encode()).hexdigest()
    transcripts = tmp_path / "native"
    transcripts.mkdir()
    transcript = transcripts / "agent-worker1.jsonl"
    transcript.write_text(json.dumps(event(10)))
    original = {
        "format": "evidence-based-ai-engineering-desktop-experiment",
        "skill_references": {
            "developer/SKILL.md": hashlib.sha256(skill.read_bytes()).hexdigest(),
            "review/SKILL.md": {"sha256": inline_hash, "text": inline},
        },
        "accounting_capabilities": {"cost": False},
        "runs": [
            {
                "run_id": "baseline-build-1",
                "attempts": [
                    {
                        "native_worker_id": "worker1",
                        "status": "completed",
                        "usage": {"subagent_tokens": 123, "reported_cost_usd": None},
                        "files": {"answer": "reports/attempts/build.report.txt"},
                    }
                ],
            }
        ],
    }
    original["runs"].append(
        {"run_id": "pending-flow-1", "attempts": [{"native_worker_id": None, "status": "running"}]}
    )
    live = campaign / "reports/results.json"
    live.write_text(json.dumps(original))
    original["plan"] = {"runs": [{"run_id": "unlinked-flow", "checkout_dir": "/fixture/unlinked"}]}
    live.write_text(json.dumps(original))
    orphan = {
        "type": "user",
        "agentId": "worker2",
        "message": {"content": "Assigned checkout: /fixture/unlinked"},
    }
    (transcripts / "agent-worker2.jsonl").write_text(
        json.dumps(orphan) + "\n" + json.dumps(event(agentId="worker2"))
    )
    before = live.read_bytes()
    output = campaign / "reports/recovered/results.json"
    recovered = collect(campaign, transcripts, output)
    assert live.read_bytes() == before
    assert recovered["unlinked_worker_evidence"][0]["native_worker_id"] == "worker2"
    assert recovered["unlinked_worker_evidence"][0]["candidate_run_id"] == "unlinked-flow"
    attempt = recovered["runs"][0]["attempts"][0]
    assert attempt["files"]["answer"] == "No findings."
    assert attempt["files"]["native-transcript.jsonl"] == transcript.read_text()
    assert attempt["usage"] == original["runs"][0]["attempts"][0]["usage"]
    assert attempt["recovered_request_usage"]["counters"]["total_tokens"] == 55
    assert recovered["skill_references"]["developer/SKILL.md"] == skill.read_text()
    assert recovered["original_accounting_capabilities"] == {"cost": False}
    assert recovered["skill_references"]["review/SKILL.md"] == inline
    with pytest.raises(ValueError, match="never overwritten"):
        collect(campaign, transcripts, output)
    original["runs"][0]["attempts"][0]["files"]["answer"] = "reports/../../outside"
    live.write_text(json.dumps(original))
    with pytest.raises(ValueError, match="escapes"):
        collect(campaign, transcripts, campaign / "reports/other.json")
