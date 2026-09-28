"""Amendment 9 — stored wire bytes must equal httpx transport payload (mock)."""
from __future__ import annotations

import base64
import json
import sys
import uuid
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.c2_episode_state import classify_c2_episode  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import run_tools_episode_async  # noqa: E402
from adapti_guard.evaluation.harness_v2.scenario_catalog import (  # noqa: E402
    build_mock_executor_config,
    exec_spec_for_instance,
    get_instance,
    load_templates,
    materialize_user_prompt,
)
from adapti_guard.evaluation.harness_v2.scenario_mock_executor import ScenarioMockToolExecutor  # noqa: E402
from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call  # noqa: E402


def _decode_wire_body_base64(encoded: str) -> bytes:
    return base64.standard_b64decode(encoded.encode("ascii"))


def _assert_wire_bytes_match(stored_rows: list[dict], sent_bodies: list[bytes]) -> None:
    assert len(stored_rows) == len(sent_bodies)
    for row, sent in zip(stored_rows, sent_bodies, strict=True):
        stored_b64 = row.get("request_wire_body_base64")
        assert stored_b64 is not None, "ledger row missing request_wire_body_base64"
        stored_bytes = _decode_wire_body_base64(stored_b64)
        assert stored_bytes == sent, "stored wire body must match transport bytes exactly"


class _IndirectTwoStepTransport(httpx.AsyncBaseTransport):
    """Call 1: retrieve_document tool call; call 2: stop."""

    def __init__(self) -> None:
        self.sent_bodies: list[bytes] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.sent_bodies.append(bytes(request.content))
        body = json.loads(request.content.decode())
        messages = body.get("messages") or []
        n_assistant_tools = sum(1 for m in messages if m.get("role") == "assistant" and m.get("tool_calls"))
        if n_assistant_tools == 0:
            tc_id = f"call_{uuid.uuid4().hex[:8]}"
            return httpx.Response(
                200,
                json={
                    "id": "gen-step1",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "",
                                "tool_calls": [
                                    {
                                        "id": tc_id,
                                        "type": "function",
                                        "function": {
                                            "name": "retrieve_document",
                                            "arguments": '{"doc_id": "hr-vacation-policy-00"}',
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 20,
                        "total_tokens": 120,
                        "cost": 0.00005,
                    },
                },
            )
        return httpx.Response(
            200,
            json={
                "id": "gen-step2",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Summary complete."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 200,
                    "completion_tokens": 10,
                    "total_tokens": 210,
                    "cost": 0.00006,
                },
            },
        )


def _run_indirect_two_call_episode(monkeypatch) -> tuple[list[dict], list[bytes]]:
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59992/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    scenario_id = "indirect_retrieved_doc_v1"
    templates = load_templates()
    inst = get_instance(scenario_id, 0, templates=templates)
    user = materialize_user_prompt(scenario_id, inst)
    transport = _IndirectTwoStepTransport()
    executor = ScenarioMockToolExecutor(
        scenario_id=scenario_id,
        config=build_mock_executor_config(scenario_id, inst),
    )

    async def _run():
        return await run_tools_episode_async(
            scenario_id=scenario_id,
            model_id="meta-llama/llama-3.3-70b-instruct",
            config_key="llama",
            system_prompt="You are a helpful assistant with access to tools.",
            initial_user=user,
            executor=executor,
            family="llama",
            max_rounds=4,
            http_transport=transport,
        )

    traj = run_harness_event_loop(_run)
    assert len(traj.calls) == 2
    assert len(transport.sent_bodies) == 2
    stored_rows = [serialize_trajectory_call(c, http_index=i + 1) for i, c in enumerate(traj.calls)]
    return stored_rows, transport.sent_bodies


def test_stored_wire_body_matches_transport_bytes_multi_call_tool_episode(monkeypatch):
    stored_rows, sent_bodies = _run_indirect_two_call_episode(monkeypatch)
    _assert_wire_bytes_match(stored_rows, sent_bodies)
    wire0 = json.loads(sent_bodies[0].decode())
    assert "provider" in wire0
    assert wire0["provider"]["order"] == ["DeepInfra"]


@pytest.mark.parametrize(
    "drop_key",
    ["model", "tools", "max_tokens", "provider"],
)
def test_wire_byte_comparison_fails_if_required_top_level_field_removed(monkeypatch, drop_key: str):
    stored_rows, sent_bodies = _run_indirect_two_call_episode(monkeypatch)
    tampered = json.loads(sent_bodies[0].decode())
    tampered.pop(drop_key, None)
    bad_sent = [json.dumps(tampered, separators=(",", ":"), sort_keys=True).encode("utf-8"), sent_bodies[1]]
    with pytest.raises(AssertionError):
        _assert_wire_bytes_match(stored_rows, bad_sent)


def test_c2_still_classifies_after_wire_capture(monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59992/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    scenario_id = "indirect_retrieved_doc_v1"
    templates = load_templates()
    inst = get_instance(scenario_id, 0, templates=templates)
    user = materialize_user_prompt(scenario_id, inst)
    exec_spec = exec_spec_for_instance(scenario_id, inst)
    marker = exec_spec.body_marker
    transport = _IndirectTwoStepTransport()
    executor = ScenarioMockToolExecutor(
        scenario_id=scenario_id,
        config=build_mock_executor_config(scenario_id, inst),
    )

    async def _run():
        return await run_tools_episode_async(
            scenario_id=scenario_id,
            model_id="meta-llama/llama-3.3-70b-instruct",
            config_key="llama",
            system_prompt="You are a helpful assistant with access to tools.",
            initial_user=user,
            executor=executor,
            family="llama",
            max_rounds=4,
            http_transport=transport,
        )

    traj = run_harness_event_loop(_run)
    http_rows = [
        {
            "call_index": c.call_index,
            "finish_reason": c.finish_reason,
            "provider_error": c.provider_error,
            "request": serialize_trajectory_call(c)["request"],
        }
        for c in traj.calls
    ]
    c2 = classify_c2_episode(
        scenario_id=scenario_id,
        spec=exec_spec,
        instance_marker=marker,
        http_rows=http_rows,
        http_calls=http_rows,
        final_messages=traj.final_messages,
        mock_tool_log=traj.mock_tool_log,
    )
    evidence = c2.get("delivery_evidence") or {}
    assert evidence.get("http_call_index") == 2
