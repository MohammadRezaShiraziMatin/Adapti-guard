"""Amendment 8 — single asyncio event loop for an entire harness run."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")


def run_harness_event_loop(async_main: Callable[[], Awaitable[T]]) -> T:
    """Run the pilot/full harness under exactly one ``asyncio.run`` (one loop per process run)."""
    return asyncio.run(async_main())


async def run_sequential_async_attempts(
    n: int,
    attempt: Callable[[int], Awaitable[None]],
) -> list[int]:
    """Await ``n`` attempts on the current running loop; return ``id(loop)`` per attempt."""
    loop_ids: list[int] = []
    loop = asyncio.get_running_loop()
    for i in range(n):
        loop_ids.append(id(loop))
        await attempt(i)
    return loop_ids
