"""Amendment 8 item 1 — single event loop for whole harness run."""
from __future__ import annotations

import asyncio
from unittest.mock import patch

from adapti_guard.evaluation.harness_v2.harness_event_loop import (
    run_harness_event_loop,
    run_sequential_async_attempts,
)


async def _noop_attempt(_i: int) -> None:
    await asyncio.sleep(0)


def test_single_running_loop_across_n_sequential_attempts():
    async def _main() -> list[int]:
        return await run_sequential_async_attempts(5, _noop_attempt)

    loop_ids = run_harness_event_loop(_main)
    assert len(loop_ids) == 5
    assert len(set(loop_ids)) == 1


def test_no_asyncio_run_per_attempt_only_at_entry():
    run_calls: list[int] = []
    real_run = asyncio.run

    def counting_run(coro):
        run_calls.append(1)
        return real_run(coro)

    async def _main() -> None:
        await run_sequential_async_attempts(3, _noop_attempt)

    with patch.object(asyncio, "run", side_effect=counting_run):
        run_harness_event_loop(_main)
    assert len(run_calls) == 1


def test_new_event_loop_not_used_per_attempt():
    new_loop_calls: list[int] = []
    real_new = asyncio.new_event_loop

    def counting_new():
        new_loop_calls.append(1)
        return real_new()

    async def _main() -> None:
        await run_sequential_async_attempts(4, _noop_attempt)

    with patch.object(asyncio, "new_event_loop", side_effect=counting_new):
        run_harness_event_loop(_main)
    assert len(new_loop_calls) <= 1
