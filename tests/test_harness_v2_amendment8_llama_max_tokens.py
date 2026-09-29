"""Amendment 8 item K — llama max_tokens=1024 (mock request bodies)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import run_tools_episode_async
from adapti_guard.evaluation.harness_v2.token_limits import (
    DEFAULT_HARNESS_MAX_TOKENS,
    LLAMA_HARNESS_MAX_TOKENS,
    QWEN3_HARNESS_MAX_TOKENS,
    max_tokens_for_model_id,
)


def test_max_tokens_caps_by_family():
    assert max_tokens_for_model_id("qwen/qwen3-30b-a3b") == QWEN3_HARNESS_MAX_TOKENS == 2048
    assert max_tokens_for_model_id("meta-llama/llama-3.3-70b-instruct") == LLAMA_HARNESS_MAX_TOKENS == 1024
    assert max_tokens_for_model_id("google/gemma-4-31b-it") == DEFAULT_HARNESS_MAX_TOKENS == 512
    assert max_tokens_for_model_id("deepseek/deepseek-v3.2") == DEFAULT_HARNESS_MAX_TOKENS == 512


def test_run_tools_episode_request_carries_llama_1024(monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59991/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    captured: list[dict] = []

    class _StopTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            captured.append(json.loads(request.content.decode()))
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "done"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0.0},
                },
            )

    async def _main():
        await run_tools_episode_async(
            scenario_id="s",
            model_id="meta-llama/llama-3.3-70b-instruct",
            config_key="ck",
            system_prompt="sys",
            initial_user="hi",
            executor=HarnessV2MockToolExecutor(),
            family="llama",
            max_rounds=1,
            http_transport=_StopTransport(),
        )

    run_harness_event_loop(_main)
    assert captured
    assert captured[0]["max_tokens"] == 1024
