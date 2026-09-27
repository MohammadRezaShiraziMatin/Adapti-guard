"""Amendment 8 item 3 — python version manifest + timeout exception on runtime."""
from __future__ import annotations

import asyncio
import sys

import httpx
import pytest

from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop
from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import (
    CancelledTimeoutAttemptResult,
    one_billed_openrouter_attempt,
)
from adapti_guard.evaluation.harness_v2.run_manifest import write_run_manifest


class _HangTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        await asyncio.Event().wait()
        return httpx.Response(200, json={})


def test_run_manifest_records_sys_version_verbatim(tmp_path):
    path = write_run_manifest(tmp_path, pilot="test")
    data = path.read_text(encoding="utf-8")
    assert sys.version in data
    loaded = __import__("json").loads(data)
    assert loaded["python_version"] == sys.version


def test_wall_timeout_caught_on_current_interpreter():
    async def _main() -> CancelledTimeoutAttemptResult:
        result = await one_billed_openrouter_attempt(
            base_url="http://127.0.0.1:59998/v1",
            api_key="mock",
            req_body={"model": "m", "messages": [{"role": "user", "content": "x"}], "max_tokens": 8},
            model_id="m",
            prompt_tokens=4,
            billed_placeholder_usd=0.01,
            http_transport=_HangTransport(),
            wall_timeout_s=0.15,
        )
        assert isinstance(result, CancelledTimeoutAttemptResult)
        return result

    run_harness_event_loop(_main)
