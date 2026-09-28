"""Capture exact HTTP request bytes as seen by httpx transport (Amendment 9)."""
from __future__ import annotations

import base64
from typing import Any

import httpx


def encode_wire_body_base64(body: bytes) -> str:
    return base64.standard_b64encode(body).decode("ascii")


def decode_wire_body_base64(encoded: str) -> bytes:
    return base64.standard_b64decode(encoded.encode("ascii"))


class WireCapturingTransport(httpx.AsyncBaseTransport):
    """Append exact request.content bytes for each outbound HTTP call."""

    def __init__(
        self,
        inner: httpx.AsyncBaseTransport | None,
        captured: list[bytes],
    ) -> None:
        self._inner = inner
        self._captured = captured

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self._captured.append(bytes(request.content))
        if self._inner is None:
            raise RuntimeError("WireCapturingTransport requires an inner transport for mock runs")
        return await self._inner.handle_async_request(request)


def wrap_transport_for_wire_capture(
    transport: httpx.AsyncBaseTransport | None,
    captured: list[bytes],
) -> httpx.AsyncBaseTransport:
    return WireCapturingTransport(transport, captured)
