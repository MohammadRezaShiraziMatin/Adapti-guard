"""Async OpenRouter HTTP attempts with wall-clock timeout (Amendment 8 §2.5.2)."""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from adapti_guard.evaluation.harness_v2.harness_v2_http_client import (
    begin_wire_capture_attempt,
    end_wire_capture_attempt,
    pop_wire_capture_for_attempt,
)
from adapti_guard.evaluation.harness_v2.wire_request_body import WireCaptureState

DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S = 180.0


@dataclass
class CancelledTimeoutAttemptResult:
    request_id: str
    latency_ms: float
    req_body: dict[str, Any]
    billed_placeholder_usd: float
    prompt_tokens: int
    max_tokens: int
    request_wire_body: bytes | None = None
    request_sent_unconfirmed: bool = False
    request_not_sent: bool = False


async def one_billed_openrouter_attempt(
    *,
    base_url: str,
    api_key: str,
    req_body: dict[str, Any],
    model_id: str,
    prompt_tokens: int,
    billed_placeholder_usd: float,
    http_transport: httpx.AsyncBaseTransport | None = None,
    http_client: httpx.AsyncClient | None = None,
    wall_timeout_s: float = DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S,
    request_id: str | None = None,
    wire_out: list[WireCaptureState] | None = None,
) -> Any:
    """One billed HTTP attempt using the run's shared ``httpx.AsyncClient`` when provided."""
    from openai import AsyncOpenAI

    from adapti_guard.evaluation.harness_v2.harness_v2_http_client import (
        close_pilot_http_client,
        create_pilot_http_client,
    )

    rid = request_id or str(uuid.uuid4())
    owned_client = False
    if http_client is None:
        if http_transport is None:
            raise RuntimeError(
                "one_billed_openrouter_attempt requires http_client (shared per pilot run)"
            )
        http_client = create_pilot_http_client(transport=http_transport)
        owned_client = True
    bucket = begin_wire_capture_attempt()
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
        result = await asyncio.wait_for(coro, timeout=wall_timeout_s)
        state = pop_wire_capture_for_attempt(bucket)
        if wire_out is not None and state is not None:
            wire_out.append(state)
        return result
    except (TimeoutError, asyncio.TimeoutError):  # noqa: UP041 — Py3.10 alias
        latency_ms = (time.perf_counter() - start) * 1000.0
        state = pop_wire_capture_for_attempt(bucket)
        if wire_out is not None and state is not None:
            wire_out.append(state)
        return CancelledTimeoutAttemptResult(
            request_id=rid,
            latency_ms=latency_ms,
            req_body=req_body,
            billed_placeholder_usd=billed_placeholder_usd,
            prompt_tokens=prompt_tokens,
            max_tokens=int(req_body.get("max_tokens") or 0),
            request_wire_body=state.body if state else None,
            request_sent_unconfirmed=state.sent_unconfirmed if state else False,
            request_not_sent=state.not_sent if state else False,
        )
    except BaseException:
        state = pop_wire_capture_for_attempt(bucket)
        if wire_out is not None and state is not None:
            wire_out.append(state)
        raise
    finally:
        end_wire_capture_attempt()
        if owned_client:
            await close_pilot_http_client(http_client)
