"""Amendment 9 LAST PATCH (Option A) — timeout, parser, HTTP error labels."""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_v2_http_client import (  # noqa: E402
    PILOT_HTTP_TIMEOUT,
    close_pilot_http_client,
    create_pilot_http_client,
)
from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import (  # noqa: E402
    one_billed_openrouter_attempt,
)
from adapti_guard.evaluation.harness_v2.openrouter_chat_http import (  # noqa: E402
    parse_chat_completions_response,
)
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import (  # noqa: E402
    run_tools_episode_async,
)
from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call  # noqa: E402
from adapti_guard.evaluation.target_model import (  # noqa: E402
    _openrouter_assistant_text,
    _openrouter_usage_dict,
)
from tests.harness_v2_local_openrouter_server import (  # noqa: E402
    LocalFakeOpenRouterServer,
    require_local_loopback,
)
from tests.test_harness_v2_amendment9_final import _harness_req_body  # noqa: E402


def test_pilot_http_timeout_matches_amendment8():
    assert PILOT_HTTP_TIMEOUT.read == pytest.approx(120.0)
    assert PILOT_HTTP_TIMEOUT.connect == pytest.approx(10.0)


def test_d1fa68b_default_httpx_timeout_fails_on_6s_server(monkeypatch):
    """Regression guard: httpx default ~5s read timeout (d1fa68b client) fails before 6s response."""
    require_local_loopback()
    server = LocalFakeOpenRouterServer(post_read_sleep_s=6.0)
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        client = httpx.AsyncClient(trust_env=True)
        req = _harness_req_body()

        async def _run():
            try:
                return await one_billed_openrouter_attempt(
                    base_url=f"http://127.0.0.1:{server.port}/v1",
                    api_key="local-test-key",
                    req_body=req,
                    model_id=req["model"],
                    prompt_tokens=10,
                    billed_placeholder_usd=0.0,
                    http_client=client,
                    wall_timeout_s=180.0,
                )
            finally:
                await close_pilot_http_client(client)

        with pytest.raises(httpx.ReadTimeout):
            run_harness_event_loop(_run)
    finally:
        server.stop()


def test_shared_pilot_client_120s_timeout_succeeds_on_6s_server(monkeypatch):
    require_local_loopback()
    server = LocalFakeOpenRouterServer(post_read_sleep_s=6.0)
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        client = create_pilot_http_client()
        req = _harness_req_body()

        async def _run():
            try:
                return await one_billed_openrouter_attempt(
                    base_url=f"http://127.0.0.1:{server.port}/v1",
                    api_key="local-test-key",
                    req_body=req,
                    model_id=req["model"],
                    prompt_tokens=10,
                    billed_placeholder_usd=0.0,
                    http_client=client,
                    wall_timeout_s=180.0,
                )
            finally:
                await close_pilot_http_client(client)

        outcome = run_harness_event_loop(_run)
        assert hasattr(outcome, "choices")
        assert server.chat_bodies
    finally:
        server.stop()


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_gemma_pilot3_fixture_reasoning_tokens_in_usage_dict():
    raw = _load_fixture("pilot3_gemma_reasoning_tokens_2_raw_response.json")
    parsed = parse_chat_completions_response(raw)
    usage = _openrouter_usage_dict(parsed.usage)
    assert usage.get("reasoning_tokens") == 2
    assert usage.get("cost") == pytest.approx(6.947e-05)


def test_parser_matches_openai_sdk_on_gemma_pilot3_fixture():
    openai = pytest.importorskip("openai")
    from openai.types.chat.chat_completion import ChatCompletion

    raw = _load_fixture("pilot3_gemma_reasoning_tokens_2_raw_response.json")
    sdk = ChatCompletion.model_validate(raw)
    project = parse_chat_completions_response(raw)
    sdk_usage = _openrouter_usage_dict(sdk.usage)
    proj_usage = _openrouter_usage_dict(project.usage)
    assert proj_usage == sdk_usage
    assert project.choices[0].finish_reason == sdk.choices[0].finish_reason
    assert _openrouter_assistant_text(project.choices[0].message) == _openrouter_assistant_text(
        sdk.choices[0].message
    )


def test_empty_content_reasoning_fallback_matches_sdk():
    openai = pytest.importorskip("openai")
    from openai.types.chat.chat_completion import ChatCompletion

    raw = _load_fixture("synthetic_empty_content_reasoning_raw_response.json")
    sdk = ChatCompletion.model_validate(raw)
    project = parse_chat_completions_response(raw)
    assert _openrouter_assistant_text(project.choices[0].message) == _openrouter_assistant_text(
        sdk.choices[0].message
    )
    assert _openrouter_assistant_text(project.choices[0].message).strip()


class _StatusTransport(httpx.AsyncBaseTransport):
    def __init__(self, status: int, body: dict, *, counter: list[str] | None = None) -> None:
        self.status = status
        self.body = body
        self.counter = counter
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        if self.counter is not None:
            self.counter.append(request.headers.get("X-Harness-Request-Id", ""))
        return httpx.Response(self.status, json=self.body)


def test_http_504_response_not_sent_unconfirmed_has_error_body(monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://mock.invalid/v1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    transport = _StatusTransport(
        504,
        {"error": {"message": "gateway timeout", "code": 504}},
    )
    client = create_pilot_http_client(transport=transport, trust_env=False)
    from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor

    async def _run():
        try:
            return await run_tools_episode_async(
                scenario_id="benign_weather_v1",
                model_id="meta-llama/llama-3.3-70b-instruct",
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
    rec = traj.calls[0]
    assert rec.request_sent_unconfirmed is False
    assert rec.request_not_sent is False
    assert rec.raw_response.get("error", {}).get("code") == 504
    row = serialize_trajectory_call(rec, http_index=1)
    assert "sent_unconfirmed" not in row


class _Http429Then200Transport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.request_ids: list[str] = []
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        self.request_ids.append(request.headers.get("X-Harness-Request-Id", ""))
        if self.request_count == 1:
            return httpx.Response(
                429,
                json={"error": {"message": "rate limited", "code": 429}},
            )
        return httpx.Response(
            200,
            json={
                "id": "gen-ok",
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "ok"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        )


def test_http_429_status_retry_distinct_request_ids_not_sent_unconfirmed(monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://mock.invalid/v1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    transport = _Http429Then200Transport()
    client = create_pilot_http_client(transport=transport, trust_env=False)
    from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor

    async def _run():
        try:
            return await run_tools_episode_async(
                scenario_id="benign_weather_v1",
                model_id="meta-llama/llama-3.3-70b-instruct",
                config_key="llama",
                system_prompt="sys",
                initial_user="hi",
                executor=HarnessV2MockToolExecutor(),
                family="llama",
                max_rounds=1,
                http_client=client,
                rate_limit_max_retries=1,
                rate_limit_backoffs=(0.0,),
            )
        finally:
            await close_pilot_http_client(client)

    traj = run_harness_event_loop(_run)
    assert transport.request_count == 2
    assert len(traj.calls) == 2
    assert traj.calls[0].retried_after_rate_limit is True
    assert traj.calls[0].request_sent_unconfirmed is False
    assert len(set(transport.request_ids)) == 2
    assert all(rid for rid in transport.request_ids)
