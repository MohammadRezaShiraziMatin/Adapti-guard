"""Tests for harness v2 trajectory request persistence (Amendment 4)."""
from __future__ import annotations

from adapti_guard.evaluation.harness_v2.openrouter_request_policy import (
    build_harness_v2_extra_body,
    reasoning_off_fields_for_model,
)
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import HarnessV2CallRecord
from adapti_guard.evaluation.harness_v2.tool_definitions import HARNESS_V2_TOOLS
from adapti_guard.evaluation.harness_v2.trajectory_store import (
    assert_request_snapshot_complete,
    serialize_trajectory_call,
)


def test_serialize_trajectory_call_includes_full_request() -> None:
    req = {
        "model": "qwen/qwen3-30b-a3b",
        "messages": [{"role": "user", "content": "hi"}],
        "tools": HARNESS_V2_TOOLS,
        "tool_choice": "auto",
        "temperature": 0.0,
        "max_tokens": 2048,
        "extra_body": {
            "provider": {"order": ["DeepInfra"], "allow_fallbacks": False, "require_parameters": True},
            "include_reasoning": False,
            "reasoning": {"effort": "none"},
        },
    }
    rec = HarnessV2CallRecord(
        call_index=1,
        scenario_id="indirect_tool_injection_v1",
        model_id="qwen/qwen3-30b-a3b",
        messages_before=req["messages"],
        request=req,
        raw_response={"choices": [{"message": {"content": "ok"}}]},
        assistant_content="ok",
        tool_calls=[],
        usage={"prompt_tokens": 1, "completion_tokens": 2},
        cost_usd=0.0,
        provider_error=None,
        latency_ms=1.0,
        episode_round=1,
    )
    row = serialize_trajectory_call(rec, http_index=7)
    assert row["request"]["tools"] == HARNESS_V2_TOOLS
    assert row["request"]["extra_body"]["include_reasoning"] is False
    assert row["request"]["messages"] == req["messages"]
    assert_request_snapshot_complete(row["request"])


def test_reasoning_off_skipped_for_llama_in_metadata() -> None:
    meta = {
        "targets": {
            "meta-llama/llama-3.3-70b-instruct": {
                "deepinfra_supported_parameters": ["tools", "tool_choice", "max_tokens"],
            }
        }
    }
    fields, audit = reasoning_off_fields_for_model("meta-llama/llama-3.3-70b-instruct", metadata=meta)
    assert fields == {}
    assert "include_reasoning" in audit["reasoning_off_skipped"]
    extra = build_harness_v2_extra_body("meta-llama/llama-3.3-70b-instruct", metadata=meta)
    assert extra["provider"]["require_parameters"] is True
    assert "include_reasoning" not in extra


def test_reasoning_off_applied_for_qwen3_in_metadata() -> None:
    meta = {
        "targets": {
            "qwen/qwen3-30b-a3b": {
                "deepinfra_supported_parameters": ["include_reasoning", "reasoning", "tools"],
            }
        }
    }
    extra = build_harness_v2_extra_body("qwen/qwen3-30b-a3b", metadata=meta)
    assert extra["include_reasoning"] is False
    assert extra["reasoning"] == {"effort": "none"}
