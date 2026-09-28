"""Async OpenRouter HTTP attempts with wall-clock timeout (direct httpx, project wire bytes)."""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from adapti_guard.evaluation.harness_v2.harness_v2_http_client import (
    close_pilot_http_client,
    create_pilot_http_client,
)
from adapti_guard.evaluation.harness_v2.openrouter_chat_http import (
    RequestWireRecord,
    chat_completions_url,
    parse_chat_completions_response,
    serialize_chat_completions_wire_body,
)

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


def _append_wire_out(
    wire_out: list[RequestWireRecord] | None,
    record: RequestWireRecord,
) -> None:
    if wire_out is not None:
        wire_out.append(record)


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
    wire_out: list[RequestWireRecord] | None = None,
) -> Any:
    """One billed HTTP attempt using the run's shared ``httpx.AsyncClient``."""
    rid = request_id or str(uuid.uuid4())
    owned_client = False
    if http_client is None:
        if http_transport is None:
            raise RuntimeError(
                "one_billed_openrouter_attempt requires http_client (shared per pilot run)"
            )
        http_client = create_pilot_http_client(transport=http_transport, trust_env=False)
        owned_client = True

    wire_body = serialize_chat_completions_wire_body(req_body)
    url = chat_completions_url(base_url)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Harness-Request-Id": rid,
    }
    start = time.perf_counter()
    body_write_started = False
    try:
        coro = http_client.post(url, content=wire_body, headers=headers)
        body_write_started = True
        response = await asyncio.wait_for(coro, timeout=wall_timeout_s)
        text = response.text
        if not text.strip():
            _append_wire_out(
                wire_out,
                RequestWireRecord(body=wire_body, sent_unconfirmed=False, not_sent=False),
            )
            return ""
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            _append_wire_out(
                wire_out,
                RequestWireRecord(body=wire_body, sent_unconfirmed=False, not_sent=False),
            )
            return text
        if response.is_error:
            response.raise_for_status()
        _append_wire_out(
            wire_out,
            RequestWireRecord(body=wire_body, sent_unconfirmed=False, not_sent=False),
        )
        if isinstance(raw, dict) and raw.get("error"):
            return raw
        return parse_chat_completions_response(raw)
    except (TimeoutError, asyncio.TimeoutError):
        latency_ms = (time.perf_counter() - start) * 1000.0
        _append_wire_out(
            wire_out,
            RequestWireRecord(
                body=wire_body,
                sent_unconfirmed=body_write_started,
                not_sent=not body_write_started,
            ),
        )
        return CancelledTimeoutAttemptResult(
            request_id=rid,
            latency_ms=latency_ms,
            req_body=req_body,
            billed_placeholder_usd=billed_placeholder_usd,
            prompt_tokens=prompt_tokens,
            max_tokens=int(req_body.get("max_tokens") or 0),
            request_wire_body=wire_body,
            request_sent_unconfirmed=body_write_started,
            request_not_sent=not body_write_started,
        )
    except (httpx.ConnectError, httpx.ConnectTimeout):
        _append_wire_out(
            wire_out,
            RequestWireRecord(body=wire_body, sent_unconfirmed=False, not_sent=True),
        )
        raise
    except httpx.HTTPError:
        _append_wire_out(
            wire_out,
            RequestWireRecord(
                body=wire_body,
                sent_unconfirmed=body_write_started,
                not_sent=False,
            ),
        )
        raise
    finally:
        if owned_client:
            await close_pilot_http_client(http_client)
