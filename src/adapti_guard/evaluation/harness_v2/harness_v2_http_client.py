"""Shared pilot HTTP client (Amendment 9 final): trust_env, no transport wrapping."""
from __future__ import annotations

import httpx

# Match Amendment 8 / pre-FINAL SDK transport hint (AsyncOpenAI used httpx.Timeout(120, connect=10)).
PILOT_HTTP_TIMEOUT = httpx.Timeout(120.0, connect=10.0)


def create_pilot_http_client(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
    trust_env: bool = True,
    timeout: httpx.Timeout | None = PILOT_HTTP_TIMEOUT,
) -> httpx.AsyncClient:
    """One AsyncClient per pilot run; honours proxy env vars when trust_env=True."""
    kwargs: dict = {"trust_env": trust_env, "timeout": timeout}
    if transport is not None:
        return httpx.AsyncClient(transport=transport, **kwargs)
    return httpx.AsyncClient(**kwargs)


async def close_pilot_http_client(client: httpx.AsyncClient | None) -> None:
    if client is not None:
        await client.aclose()
