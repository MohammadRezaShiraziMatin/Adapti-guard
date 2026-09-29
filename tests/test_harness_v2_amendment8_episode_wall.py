"""Amendment 8 item 4 — episode wall X checked before rounds only."""
from __future__ import annotations

import asyncio

import pytest

from adapti_guard.evaluation.harness_v2.episode_wall_clock import (
    WORST_EPISODE_WALL_SECONDS,
    worst_episode_wall_seconds,
)
from adapti_guard.evaluation.harness_v2.episode_wall_runner import run_episode_rounds_with_wall_clock
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop


def test_worst_episode_wall_exact_per_model():
    assert worst_episode_wall_seconds("qwen3") == pytest.approx(442.944787)
    assert worst_episode_wall_seconds("gemma") == pytest.approx(457.158873)
    assert worst_episode_wall_seconds("deepseek") == pytest.approx(474.816364)
    assert worst_episode_wall_seconds("llama") == pytest.approx(763.263164)


def test_last_round_starts_just_before_x_finishes_within_x_plus_220():
    x = 100.0
    t_values = [0.0, 0.0, x - 0.05, x - 0.05 + 0.08]
    it = iter(t_values)

    def mono() -> float:
        return next(it, t_values[-1] + 0.02)

    from adapti_guard.evaluation.harness_v2.episode_wall_clock import EpisodeWallClock

    wall = EpisodeWallClock("qwen3", t0=0.0)
    wall.x_seconds = x

    async def round_fn(_idx: int) -> None:
        await asyncio.sleep(0.05)

    async def _main():
        return await run_episode_rounds_with_wall_clock(
            family="qwen3",
            max_rounds=2,
            round_fn=round_fn,
            wall=wall,
            monotonic_fn=mono,
        )

    result = run_harness_event_loop(_main)
    assert result.status == "COMPLETE"
    assert result.rounds_completed == 2
    assert result.elapsed_s <= x + 220


def test_exceeds_x_before_round_is_invalid_timeout():
    x = 50.0
    t_values = [0.0, x + 1.0]
    it = iter(t_values)

    def mono() -> float:
        try:
            return next(it)
        except StopIteration:
            return x + 5.0

    from adapti_guard.evaluation.harness_v2.episode_wall_clock import EpisodeWallClock

    wall = EpisodeWallClock("gemma", t0=0.0)
    wall.x_seconds = x

    async def round_fn(_idx: int) -> None:
        await asyncio.sleep(0)

    async def _main():
        return await run_episode_rounds_with_wall_clock(
            family="gemma",
            max_rounds=3,
            round_fn=round_fn,
            wall=wall,
            monotonic_fn=mono,
        )

    result = run_harness_event_loop(_main)
    assert result.status == "INVALID_TIMEOUT"
    assert result.rounds_completed == 1
