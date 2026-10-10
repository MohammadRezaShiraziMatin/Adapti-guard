"""Analysis functions for protocol §6 (DRAFT, NOT FROZEN): exact McNemar test and cluster bootstrap. Pure Python, offline.

Nothing here chooses a protocol value. The number of bootstrap resamples, the seed and the interval level have no
defaults: the caller must pass them, and they must be the values fixed in the frozen protocol text.

Sign convention for the paired difference: A0 minus SPOT_TOOL, so a positive value means the defense reduced the event.
"""
from __future__ import annotations

import math
import random
from collections.abc import Sequence


def exact_mcnemar_p(b: int, c: int) -> float:
    """Two-sided exact McNemar test on discordant counts: b = A0 only, c = SPOT_TOOL only.
    Under H0 each discordant pair falls either way with probability 1/2, so X ~ Binomial(b + c, 1/2)."""
    if b < 0 or c < 0:
        raise ValueError("discordant counts must be non-negative")
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2**n
    return min(1.0, 2.0 * tail)


def discordance(pairs: Sequence[tuple[bool, bool]]) -> tuple[int, int]:
    """(b, c) for paired outcomes (a0_event, spot_event): b = A0 only, c = SPOT only."""
    b = sum(1 for a0, spot in pairs if a0 and not spot)
    c = sum(1 for a0, spot in pairs if spot and not a0)
    return b, c


def cluster_bootstrap_interval(clusters: Sequence[Sequence[tuple[bool, bool]]], *, resamples: int, seed: int,
                               level: float) -> tuple[float, float, float]:
    """Point estimate and percentile cluster-bootstrap interval for the paired event-rate difference A0 - SPOT.

    clusters: one sequence of (a0_event, spot_event) pairs per cluster (for InjecAgent, the attacker instruction).
    Clusters are resampled with replacement; each resample pools all cases in the drawn clusters. The random generator
    is local (random.Random(seed)), so the global random state is not touched.
    Returns (point, lower, upper) at the given two-sided level."""
    if not isinstance(resamples, int) or resamples < 1:
        raise ValueError("resamples must be a positive integer (fixed in the protocol)")
    if not isinstance(seed, int):
        raise ValueError("seed must be an integer (fixed in the protocol)")
    if not 0 < level < 1:
        raise ValueError("level must be between 0 and 1 (fixed in the protocol)")
    if not clusters or any(len(c) == 0 for c in clusters):
        raise ValueError("every cluster must contain at least one case")

    totals = [(sum(int(a0) - int(spot) for a0, spot in c), len(c)) for c in clusters]
    point = sum(d for d, _ in totals) / sum(m for _, m in totals)

    rng = random.Random(seed)
    k = len(totals)
    stats = []
    for _ in range(resamples):
        drawn = [totals[rng.randrange(k)] for _ in range(k)]
        stats.append(sum(d for d, _ in drawn) / sum(m for _, m in drawn))
    stats.sort()

    alpha = 1.0 - level
    lower = stats[math.floor(alpha / 2 * resamples)]
    upper = stats[min(resamples - 1, math.ceil((1 - alpha / 2) * resamples) - 1)]
    return point, lower, upper
