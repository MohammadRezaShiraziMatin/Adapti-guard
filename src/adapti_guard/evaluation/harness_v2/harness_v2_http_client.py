"""Shared pilot HTTP client (Amendment 9 final): trust_env, no transport wrapping."""
from __future__ import annotations

import httpx


def create_pilot_http_client(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
    trust_env: bool = True,
) -> httpx.AsyncClient:
    """One AsyncClient per pilot run; honours proxy env vars when trust_env=True."""
    if transport is not None:
        return httpx.AsyncClient(transport=transport, trust_env=trust_env)
    return httpx.AsyncClient(trust_env=trust_env)


async def close_pilot_http_client(client: httpx.AsyncClient | None) -> None:
    if client is not None:
        await client.aclose()
