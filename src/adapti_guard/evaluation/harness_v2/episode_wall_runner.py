"""Drive multi-round episodes with per-model wall clock checks."""
from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from adapti_guard.evaluation.harness_v2.episode_wall_clock import EpisodeWallClock


@dataclass
class EpisodeWallRunResult:
    status: str
    rounds_completed: int
    elapsed_s: float


async def run_episode_rounds_with_wall_clock(
    *,
    family: str,
    max_rounds: int,
    round_fn: Callable[[int], Awaitable[Any]],
    wall: EpisodeWallClock | None = None,
    monotonic_fn: Callable[[], float] | None = None,
) -> EpisodeWallRunResult:
    """Check ``X`` only immediately before each round (not mid-HTTP)."""
    clock = wall or EpisodeWallClock(family)
    mono = monotonic_fn or time.monotonic
    rounds_done = 0
    for round_idx in range(max_rounds):
        if mono() - clock.t0 > clock.x_seconds:
            return EpisodeWallRunResult(
                status="INVALID_TIMEOUT",
                rounds_completed=rounds_done,
                elapsed_s=mono() - clock.t0,
            )
        await round_fn(round_idx)
        rounds_done += 1
    return EpisodeWallRunResult(
        status="COMPLETE",
        rounds_completed=rounds_done,
        elapsed_s=mono() - clock.t0,
    )
