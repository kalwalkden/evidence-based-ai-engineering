"""Read Claude's final accounting once; never sum cumulative stream events."""

from __future__ import annotations

import json
import math
from pathlib import Path


def number(value):
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    ):
        return value
    return None


def parse_stream(path: Path) -> dict:
    result = None
    calls = {}
    malformed = 0
    models = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        if not isinstance(event, dict):
            malformed += 1
            continue
        if event.get("type") == "result":
            result = event
        if event.get("type") == "assistant":
            message = event.get("message", {})
            if message.get("model"):
                models.add(message["model"])
            for block in message.get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    calls[block["id"]] = {
                        "name": block.get("name"),
                        "input": block.get("input", {}),
                    }
    data = {
        "has_result": result is not None,
        "malformed_lines": malformed,
        "tool_calls": list(calls.values()),
        "tool_call_count": len(calls),
        "observed_models": sorted(models),
        "reported_cost_usd": None,
        "input_tokens": None,
        "output_tokens": None,
        "cache_read_input_tokens": None,
        "cache_creation_input_tokens": None,
        "total_tokens": None,
        "accounting_source": "missing",
        "accounting_complete": False,
        "answer": "",
        "result": result,
    }
    if result is None:
        return data
    data["answer"] = result.get("result", "")
    # Crash results may contain misleading zeroes. Preserve raw data, mark totals unknown.
    if result.get("subtype") == "error_during_execution":
        data["accounting_source"] = "crash_unreliable"
        return data
    data["reported_cost_usd"] = number(result.get("total_cost_usd"))
    mapping = {
        "input_tokens": "inputTokens",
        "output_tokens": "outputTokens",
        "cache_read_input_tokens": "cacheReadInputTokens",
        "cache_creation_input_tokens": "cacheCreationInputTokens",
    }
    per_model = result.get("modelUsage") or result.get("model_usage")
    if isinstance(per_model, dict) and per_model:
        data["accounting_source"] = "modelUsage"
        for field, camel in mapping.items():
            values = [number(item.get(camel, item.get(field))) for item in per_model.values()]
            if all(value is not None for value in values):
                data[field] = sum(values)
    else:
        data["accounting_source"] = "usage_main_loop_only"
        usage = result.get("usage") or {}
        for field in mapping:
            data[field] = number(usage.get(field))
        # The response that crosses a budget can be missing from top-level usage.
        delegated = any(call["name"] in ("Agent", "Task") for call in calls.values())
        if delegated:
            data["accounting_source"] = "usage_excludes_delegated_work"
        if result.get("subtype") == "error_max_budget_usd" or delegated:
            for field in mapping:
                data[field] = None
    counts = [data[field] for field in mapping]
    if all(value is not None for value in counts):
        data["total_tokens"] = sum(counts)
    data["accounting_complete"] = (
        data["reported_cost_usd"] is not None and data["total_tokens"] is not None
    )
    return data
