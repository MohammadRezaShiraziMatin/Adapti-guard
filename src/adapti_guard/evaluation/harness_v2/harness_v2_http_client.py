"""Shared pilot HTTP client (Amendment 9): trust_env + wire capture on all transports."""
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


def _wrap_wire_capture(client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Wrap default transport and every proxy mount (httpx 0.28 routes proxies via _mounts)."""
    if not isinstance(client._transport, WireCapturingTransport):
        client._transport = WireCapturingTransport(client._transport)
    for pattern, transport in list(client._mounts.items()):
        if not isinstance(transport, WireCapturingTransport):
            client._mounts[pattern] = WireCapturingTransport(transport)
    return client


def create_pilot_http_client(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
    trust_env: bool = True,
) -> httpx.AsyncClient:
    """One AsyncClient per pilot run; honours proxy env vars when trust_env=True."""
    if transport is not None:
        client = httpx.AsyncClient(
            transport=WireCapturingTransport(transport),
            trust_env=trust_env,
        )
    else:
        client = httpx.AsyncClient(trust_env=trust_env)
    return _wrap_wire_capture(client)


async def close_pilot_http_client(client: httpx.AsyncClient | None) -> None:
    if client is not None:
        await client.aclose()
