"""Amendment 9 FINAL — project httpx wire path, SDK body parity, retry counts."""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_v2_http_client import (  # noqa: E402
    close_pilot_http_client,
    create_pilot_http_client,
)
from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import (  # noqa: E402
    one_billed_openrouter_attempt,
)
from adapti_guard.evaluation.harness_v2.openrouter_chat_http import (  # noqa: E402
    flatten_chat_completions_payload,
    semantic_payload_diff,
    serialize_chat_completions_wire_body,
)
from adapti_guard.evaluation.harness_v2.openrouter_request_policy import build_harness_v2_extra_body  # noqa: E402
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import run_tools_episode_async  # noqa: E402
from adapti_guard.evaluation.harness_v2.tool_definitions import HARNESS_V2_TOOLS  # noqa: E402
from adapti_guard.evaluation.harness_v2.token_limits import max_tokens_for_model_id  # noqa: E402
from tests.harness_v2_local_openrouter_server import (  # noqa: E402
    LocalFakeOpenRouterServer,
    require_local_loopback,
)
from tests.test_harness_v2_amendment9_round4 import _ForwardHttpProxy  # noqa: E402

MODEL_ID = "meta-llama/llama-3.3-70b-instruct"


def _harness_req_body() -> dict[str, Any]:
    extra = build_harness_v2_extra_body(MODEL_ID)
    messages = [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}]
    cap = max_tokens_for_model_id(MODEL_ID)
    return {
        "model": MODEL_ID,
        "messages": messages,
        "tools": HARNESS_V2_TOOLS,
        "tool_choice": "auto",
        "temperature": 0.0,
        "max_tokens": cap,
        "extra_body": json.loads(json.dumps(extra)),
    }


class _ScenarioTransport(httpx.AsyncBaseTransport):
    def __init__(self, steps: list[str]) -> None:
        self.steps = list(steps)
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        step = self.steps[self.request_count - 1]
        if step == "200":
            return httpx.Response(
                200,
                json={
                    "id": "gen",
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "ok"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                },
            )
        if step == "429":
            return httpx.Response(429, json={"error": {"message": "rate limited", "code": 429}})
        if step == "5xx":
            return httpx.Response(503, json={"error": {"message": "upstream", "code": 503}})
        if step == "hang":
            import asyncio

            await asyncio.sleep(3600)
            return httpx.Response(200, json={"choices": []})
        raise AssertionError(f"unknown step {step!r}")


@pytest.mark.parametrize(
    "steps,expected_count",
    [
        (["200"], 1),
        (["429", "200"], 2),
        (["5xx"], 1),
    ],
)
def test_transport_request_count_matches_max_retries_zero(steps, expected_count, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://mock.invalid/v1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    transport = _ScenarioTransport(steps)
    client = create_pilot_http_client(transport=transport, trust_env=False)
    req = _harness_req_body()

    async def _run():
        try:
            await run_tools_episode_async(
                scenario_id="benign_weather_v1",
                model_id=MODEL_ID,
                config_key="llama",
                system_prompt="sys",
                initial_user="hi",
                executor=__import__(
                    "adapti_guard.evaluation.harness_v2.mock_tool_executor",
                    fromlist=["HarnessV2MockToolExecutor"],
                ).HarnessV2MockToolExecutor(),
                family="llama",
                max_rounds=1,
                http_client=client,
                rate_limit_max_retries=1 if "429" in steps else 0,
            )
        finally:
            await close_pilot_http_client(client)

    run_harness_event_loop(_run)
    assert transport.request_count == expected_count


def test_timeout_single_transport_request_with_wait_for(monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://mock.invalid/v1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    transport = _ScenarioTransport(["hang"])
    client = create_pilot_http_client(transport=transport, trust_env=False)
    req = _harness_req_body()

    async def _one():
        try:
            return await one_billed_openrouter_attempt(
                base_url="http://mock.invalid/v1",
                api_key="k",
                req_body=req,
                model_id=MODEL_ID,
                prompt_tokens=10,
                billed_placeholder_usd=0.0,
                http_client=client,
                wall_timeout_s=0.15,
            )
        finally:
            await close_pilot_http_client(client)

    outcome = run_harness_event_loop(_one)
    assert transport.request_count == 1
    assert outcome.request_sent_unconfirmed is True


def test_sdk_wire_body_semantic_parity_with_project_builder():
    openai = pytest.importorskip("openai")
    req = _harness_req_body()
    project_payload = flatten_chat_completions_payload(req)
    project_bytes = serialize_chat_completions_wire_body(req)
    captured: list[bytes] = []

    class _CaptureTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            captured.append(bytes(request.content))
            return httpx.Response(
                200,
                json={
                    "id": "x",
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "ok"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {},
                },
            )

    async def _sdk_call():
        req_copy = _harness_req_body()
        extra = req_copy["extra_body"]
        http_client = httpx.AsyncClient(transport=_CaptureTransport())
        client = openai.AsyncOpenAI(
            base_url="http://mock.invalid/v1",
            api_key="k",
            http_client=http_client,
            max_retries=0,
        )
        try:
            await client.chat.completions.create(
                model=req_copy["model"],
                messages=req_copy["messages"],
                tools=req_copy["tools"],
                tool_choice=req_copy["tool_choice"],
                temperature=req_copy["temperature"],
                max_tokens=req_copy["max_tokens"],
                extra_body=extra,
            )
        finally:
            await http_client.aclose()

    run_harness_event_loop(_sdk_call)
    assert captured
    sdk_payload = json.loads(captured[0].decode("utf-8"))
    diffs = semantic_payload_diff(project_payload, sdk_payload)
    if diffs:
        pytest.fail("SDK vs project payload differences:\n" + "\n".join(diffs))
    assert json.loads(project_bytes) == sdk_payload


def test_all_proxy_forwards_body_with_wire_rows(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer()
    server.start()
    proxy = _ForwardHttpProxy()
    proxy.start()
    try:
        monkeypatch.setenv("ALL_PROXY", f"http://127.0.0.1:{proxy.port}")
        monkeypatch.setenv("all_proxy", f"http://127.0.0.1:{proxy.port}")
        monkeypatch.setenv("NO_PROXY", "")
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        client = create_pilot_http_client(trust_env=True)

        async def _post():
            try:
                body = serialize_chat_completions_wire_body(_harness_req_body())
                resp = await client.post(
                    f"http://127.0.0.1:{server.port}/v1/chat/completions",
                    content=body,
                    headers={
                        "Authorization": "Bearer local-test-key",
                        "Content-Type": "application/json",
                    },
                )
                resp.raise_for_status()
            finally:
                await close_pilot_http_client(client)

        run_harness_event_loop(_post)
        assert server.chat_bodies
        assert proxy.forwarded_bodies
        assert proxy.forwarded_bodies[0] == server.chat_bodies[0]
    finally:
        proxy.stop()
        server.stop()


def test_server_close_after_full_body_marks_sent_unconfirmed(monkeypatch):
    require_local_loopback()
    server = LocalFakeOpenRouterServer(close_connection_after_read=True)
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor

        async def _run():
            client = create_pilot_http_client()
            try:
                return await run_tools_episode_async(
                    scenario_id="benign_weather_v1",
                    model_id=MODEL_ID,
                    config_key="llama",
                    system_prompt="sys",
                    initial_user="hi",
                    executor=HarnessV2MockToolExecutor(),
                    family="llama",
                    max_rounds=1,
                    http_client=client,
                )
            finally:
                await close_pilot_http_client(client)

        traj = run_harness_event_loop(_run)
        assert len(server.chat_bodies) == 1
        rec = traj.calls[0]
        assert rec.request_sent_unconfirmed is True
        assert rec.request_not_sent is False
    finally:
        server.stop()
