"""Amendment 8 item F — fresh httpx client per attempt; transport not closed by episode."""
from __future__ import annotations

import asyncio

import httpx
import pytest

from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop
from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import one_billed_openrouter_attempt


class _CountingTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        await asyncio.Event().wait()
        return httpx.Response(200, json={})


def test_per_attempt_client_closed_after_wall_timeout():
    transport = _CountingTransport()

    async def _main() -> None:
        req = {
            "model": "m",
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 8,
        }
        await one_billed_openrouter_attempt(
            base_url="http://127.0.0.1:59994/v1",
            api_key="mock-key",
            req_body=req,
            model_id="m",
            prompt_tokens=4,
            billed_placeholder_usd=0.0,
            http_transport=transport,
            wall_timeout_s=0.15,
        )
        await one_billed_openrouter_attempt(
            base_url="http://127.0.0.1:59994/v1",
            api_key="mock-key",
            req_body=req,
            model_id="m",
            prompt_tokens=4,
            billed_placeholder_usd=0.0,
            http_transport=transport,
            wall_timeout_s=0.15,
        )

    run_harness_event_loop(_main)
    assert transport.request_count == 2
