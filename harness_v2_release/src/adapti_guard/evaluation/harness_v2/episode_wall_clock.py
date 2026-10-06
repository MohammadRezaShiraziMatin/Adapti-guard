"""Per-model episode wall clock before each round (Amendment 8 §2.5.3)."""
from __future__ import annotations

import time
from typing import Final

# Longest COMPLETE episode wall (pilot-2 progress.log episode_begin → episode_complete).
EPISODE_WALL_X_BEFORE_ROUND_S: Final[dict[str, float]] = {
    "qwen3": 222.944787,
    "gemma": 237.158873,
    "deepseek": 254.816364,
    "llama": 543.263164,
}

HTTP_ATTEMPT_WALL_S: Final[float] = 180.0
HARNESS_RETRY_BACKOFF_RESERVE_S: Final[float] = 40.0


def worst_episode_wall_seconds(family: str) -> float:
    """Realized worst ≈ X + one 180s attempt + 40s backoff reserve."""
    return (
        EPISODE_WALL_X_BEFORE_ROUND_S[family]
        + HTTP_ATTEMPT_WALL_S
        + HARNESS_RETRY_BACKOFF_RESERVE_S
    )


WORST_EPISODE_WALL_SECONDS: Final[dict[str, float]] = {
    fam: worst_episode_wall_seconds(fam) for fam in EPISODE_WALL_X_BEFORE_ROUND_S
}


class EpisodeWallClock:
    def __init__(self, family: str, *, t0: float | None = None) -> None:
        if family not in EPISODE_WALL_X_BEFORE_ROUND_S:
            raise KeyError(f"unknown harness family {family!r}")
        self.family = family
        self.t0 = time.monotonic() if t0 is None else t0
        self.x_seconds = EPISODE_WALL_X_BEFORE_ROUND_S[family]

    def elapsed_s(self) -> float:
        return time.monotonic() - self.t0

    def before_round_allowed(self) -> bool:
        return self.elapsed_s() <= self.x_seconds

    def worst_bound_seconds(self) -> float:
        return worst_episode_wall_seconds(self.family)
