"""Shared pilot HTTP client (Amendment 9 round 4): trust_env + wire capture wrapper."""
from __future__ import annotations

import httpx

from adapti_guard.evaluation.harness_v2.wire_request_body import (
    WireCapturingTransport,
    begin_wire_capture_attempt,
    end_wire_capture_attempt,
    pop_wire_capture_for_attempt,
)

__all__ = [
    "WireCapturingTransport",
    "begin_wire_capture_attempt",
    "end_wire_capture_attempt",
    "pop_wire_capture_for_attempt",
    "create_pilot_http_client",
    "close_pilot_http_client",
]


def create_pilot_http_client(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
    trust_env: bool = True,
) -> httpx.AsyncClient:
    """One AsyncClient per pilot run; honours proxy env vars when trust_env=True."""
    if transport is not None:
        wrapped = WireCapturingTransport(transport)
        return httpx.AsyncClient(transport=wrapped, trust_env=trust_env)
    client = httpx.AsyncClient(trust_env=trust_env)
    client._transport = WireCapturingTransport(client._transport)
    return client


async def close_pilot_http_client(client: httpx.AsyncClient | None) -> None:
    if client is not None:
        await client.aclose()
