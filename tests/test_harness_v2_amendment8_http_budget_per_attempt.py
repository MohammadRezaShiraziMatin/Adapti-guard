"""Amendment 8 item G — HttpCompletionBudget.acquire once per HTTP attempt (429 retries included)."""
from __future__ import annotations

import json

import httpx
import pytest

from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop
from adapti_guard.evaluation.harness_v2.http_budget import HttpCompletionBudget
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import run_tools_episode_async


class _Json429ThenOkTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        if self.request_count == 1:
            return httpx.Response(
                200,
                json={"error": {"message": "rate limited", "code": 429}},
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "ok"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0.0},
            },
        )


def test_http_budget_acquires_per_attempt_including_429_retry(monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59993/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    transport = _Json429ThenOkTransport()
    budget = HttpCompletionBudget(2)
    rows: list[dict] = []

    async def _main():
        traj = await run_tools_episode_async(
            scenario_id="s",
            model_id="openrouter/qwen-test",
            config_key="ck",
            system_prompt="sys",
            initial_user="hi",
            executor=HarnessV2MockToolExecutor(),
            family="qwen3",
            max_rounds=1,
            http_budget=budget,
            http_transport=transport,
            rate_limit_backoffs=(0.0,),
            rate_limit_max_retries=1,
            on_http_record=lambda rec: rows.append(
                {"retried": rec.retried_after_rate_limit, "idx": rec.call_index}
            ),
        )
        return traj

    traj = run_harness_event_loop(_main)
    assert transport.request_count == 2
    assert budget.used == 2
    assert len(traj.calls) == 2
    assert rows[0]["retried"] is True
