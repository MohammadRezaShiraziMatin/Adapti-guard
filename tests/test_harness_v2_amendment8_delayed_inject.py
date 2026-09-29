"""Amendment 8 item J — delayed_second_turn_v1 late inject wiring (mock only)."""
from __future__ import annotations

import importlib.util
import json
import sys
import uuid
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.scenario_catalog import (  # noqa: E402
    build_mock_executor_config,
    get_instance,
    load_templates,
)
from adapti_guard.evaluation.harness_v2.scenario_mock_executor import (  # noqa: E402
    ScenarioMockToolExecutor,
)


def _load_run_pilot_async():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.run_pilot_async


def _retrieve_tool_bodies(messages: list[dict]) -> list[str]:
    bodies: list[str] = []
    for msg in messages:
        if msg.get("role") != "tool":
            continue
        try:
            payload = json.loads(str(msg.get("content") or "{}"))
        except json.JSONDecodeError:
            continue
        if "body" in payload:
            bodies.append(str(payload["body"]))
    return bodies


def _count_retrieve_tool_results(messages: list[dict]) -> int:
    return len(_retrieve_tool_bodies(messages))


class _TwoRetrieveTransport(httpx.AsyncBaseTransport):
    """Scripted assistant: emit retrieve_document until two tool results exist, then stop."""

    def __init__(self, *, doc_id: str) -> None:
        self._doc_id = doc_id

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        messages = body.get("messages") or []
        n_tools = _count_retrieve_tool_results(messages)
        if n_tools < 2:
            tc_id = f"call_{uuid.uuid4().hex[:8]}"
            return httpx.Response(
                200,
                json={
                    "id": f"gen-{n_tools}",
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
                                            "arguments": json.dumps({"doc_id": self._doc_id}),
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.0},
                },
            )
        return httpx.Response(
            200,
            json={
                "id": "gen-stop",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Summarized."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 3, "cost": 0.0001},
            },
        )


def test_build_mock_executor_config_includes_late_body():
    templates = load_templates()
    inst = get_instance("delayed_second_turn_v1", 0, templates=templates)
    cfg = build_mock_executor_config("delayed_second_turn_v1", inst)
    assert cfg.get("injection_doc_body_late") == inst["injection_doc_body_late"]


def test_missing_injection_doc_body_late_raises():
    ex = ScenarioMockToolExecutor(
        scenario_id="delayed_second_turn_v1",
        config={
            "delayed_inject_on_retrieve_n": 2,
            "injection_doc_body": "Pass A only",
        },
    )
    with pytest.raises(ValueError, match="injection_doc_body_late is missing"):
        ex.execute(name="retrieve_document", arguments={"doc_id": "x"})


@pytest.mark.parametrize("instance_index", [0, 1])
def test_delayed_second_turn_late_body_in_http_stream(tmp_path: Path, instance_index: int, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59992/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    templates = load_templates()
    inst = get_instance("delayed_second_turn_v1", instance_index, templates=templates)
    marker = inst["marker"]
    pass_a = inst["injection_doc_body"]
    pass_b = inst["injection_doc_body_late"]

    transport = _TwoRetrieveTransport(doc_id=str(inst["doc_id"]))
    schedule = [
        {
            "scenario_id": "delayed_second_turn_v1",
            "instance_index": instance_index,
            "family": "qwen3",
            "condition": "A0",
        },
    ]

    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    run_pilot_async = _load_run_pilot_async()
    out = tmp_path / f"delayed_i{instance_index}"

    async def _main():
        return await run_pilot_async(
            out,
            pilot_label="harness_v2_pilot_0",
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=schedule,
            rate_limit_backoffs=(0.0, 0.0),
            skip_preflight=True,
            reconcile_at_end=False,
        )

    run_harness_event_loop(_main)

    stream = [json.loads(ln) for ln in out.joinpath("http_stream.jsonl").read_text().splitlines() if ln.strip()]
    assert len(stream) >= 2
    rows_with_two_tools = [
        r
        for r in stream
        if len(_retrieve_tool_bodies((r.get("request") or {}).get("messages") or [])) >= 2
    ]
    assert rows_with_two_tools, "expected a logged HTTP request after second retrieve tool result"
    bodies = _retrieve_tool_bodies(rows_with_two_tools[-1]["request"]["messages"])
    assert bodies[0] == pass_a
    assert bodies[1] == pass_b
    assert marker in bodies[1]
