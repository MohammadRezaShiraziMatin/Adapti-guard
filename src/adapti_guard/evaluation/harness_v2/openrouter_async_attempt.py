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
    http_transport: httpx.AsyncBaseTransport | None = None,
    wall_timeout_s: float = DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S,
    request_id: str | None = None,
    wire_body_out: list[bytes] | None = None,
) -> Any:
    """One billed HTTP attempt — fresh ``AsyncOpenAI`` + ``httpx.AsyncClient``; always ``aclose`` in ``finally``."""
    from openai import AsyncOpenAI

    from adapti_guard.evaluation.harness_v2.wire_request_body import wrap_transport_for_wire_capture

    rid = request_id or str(uuid.uuid4())
    transport = http_transport
    if wire_body_out is not None:
        transport = wrap_transport_for_wire_capture(http_transport, wire_body_out)
    http_client = httpx.AsyncClient(transport=transport) if transport else httpx.AsyncClient()
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
        await http_client.aclose()
