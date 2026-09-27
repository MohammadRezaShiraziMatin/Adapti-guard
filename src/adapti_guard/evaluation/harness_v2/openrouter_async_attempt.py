"""Async OpenRouter HTTP attempts with wall-clock timeout (Amendment 8 §2.5.2)."""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S = 180.0


@dataclass
class CancelledTimeoutAttemptResult:
    request_id: str
    latency_ms: float
    req_body: dict[str, Any]
    billed_placeholder_usd: float
    prompt_tokens: int
    max_tokens: int


async def one_billed_openrouter_attempt(
    *,
    base_url: str,
    api_key: str,
    req_body: dict[str, Any],
    model_id: str,
    prompt_tokens: int,
    billed_placeholder_usd: float,
    http_client: httpx.AsyncClient | None = None,
    wall_timeout_s: float = DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S,
    request_id: str | None = None,
) -> Any:
    """Run one chat completion; on wall timeout return ``CancelledTimeoutAttemptResult``."""
    from openai import AsyncOpenAI

    rid = request_id or str(uuid.uuid4())
    owns_client = http_client is None
    if http_client is None:
        http_client = httpx.AsyncClient()
    client = AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        max_retries=0,
        timeout=httpx.Timeout(120.0, connect=10.0),
        http_client=http_client,
    )
    start = time.perf_counter()
    try:
        coro = client.chat.completions.create(
            **req_body,
            extra_headers={"X-Harness-Request-Id": rid},
        )
        return await asyncio.wait_for(coro, timeout=wall_timeout_s)
    except (TimeoutError, asyncio.TimeoutError):  # noqa: UP041 — Py3.10 alias
        latency_ms = (time.perf_counter() - start) * 1000.0
        return CancelledTimeoutAttemptResult(
            request_id=rid,
            latency_ms=latency_ms,
            req_body=req_body,
            billed_placeholder_usd=billed_placeholder_usd,
            prompt_tokens=prompt_tokens,
            max_tokens=int(req_body.get("max_tokens") or 0),
        )
    finally:
        await client.close()
        if owns_client:
            await http_client.aclose()
