"""Analysis functions for protocol §6 (DRAFT, NOT FROZEN): exact McNemar test, cluster bootstrap, Holm. Pure Python, offline.

Nothing here chooses a protocol value. The number of bootstrap resamples, the seed and the interval level have no
defaults: the caller must pass them, and they must be the values fixed in the frozen protocol text. Which test is the
confirmatory one (unclustered McNemar or a cluster-adjusted test) is an open decision in the protocol; this module
implements the unclustered exact McNemar and the cluster bootstrap, and does not choose between them.

Sign convention for the paired difference: A0 minus SPOT_TOOL, so a positive value means the defense reduced the event.
"""
from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence


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


def _check_bool(x: object, what: str) -> bool:
    if type(x) is not bool:
        raise ValueError(f"{what} must be a bool, got {x!r} (an errored or unpriced episode must not be counted)")
    return x


def discordance(pairs: Sequence[tuple[str, bool, bool]]) -> tuple[int, int]:
    """(b, c) from pairs as returned by pair_by_case_id: (case_id, a0_event, spot_event).
    b = A0 only, c = SPOT_TOOL only. Outcomes must be strict bools."""
    b = c = 0
    for triple in pairs:
        if len(triple) != 3:
            raise ValueError("discordance expects (case_id, a0_event, spot_event) triples from pair_by_case_id")
        case_id, a0, spot = triple
        a0 = _check_bool(a0, f"A0 outcome for {case_id!r}")
        spot = _check_bool(spot, f"SPOT_TOOL outcome for {case_id!r}")
        if a0 and not spot:
            b += 1
        elif spot and not a0:
            c += 1
    return b, c


def _index_arm(records: Sequence[tuple[str, object]], arm: str) -> dict[str, bool]:
    indexed: dict[str, bool] = {}
    for case_id, outcome in records:
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"{arm}: every case_id must be a non-empty string")
        if type(outcome) is not bool:
            raise ValueError(f"{arm}: outcome for {case_id!r} must be a bool, got {outcome!r} "
                             "(an errored or unpriced episode must not be counted as a result)")
        if case_id in indexed:
            raise ValueError(f"{arm}: duplicate case_id {case_id!r}")
        indexed[case_id] = outcome
    return indexed


def pair_by_case_id(a0: Sequence[tuple[str, object]], spot: Sequence[tuple[str, object]]) -> list[tuple[str, bool, bool]]:
    """Pair two arms by case_id, not by position. Returns (case_id, a0_event, spot_event) sorted by case_id.
    Refuses duplicate ids, non-bool outcomes (None, 0, 1 and so on), and arms whose case_id sets differ."""
    a_idx = _index_arm(a0, "A0")
    s_idx = _index_arm(spot, "SPOT_TOOL")
    if a_idx.keys() != s_idx.keys():
        missing_in_spot = sorted(a_idx.keys() - s_idx.keys())
        missing_in_a0 = sorted(s_idx.keys() - a_idx.keys())
        raise ValueError(f"arms have different case_id sets: only in A0 {missing_in_spot}, only in SPOT_TOOL {missing_in_a0}")
    return [(cid, a_idx[cid], s_idx[cid]) for cid in sorted(a_idx)]


def attacker_instruction_clusters(pairs: Sequence[tuple[str, bool, bool]],
                                  instruction_of: Mapping[str, str]) -> list[list[tuple[bool, bool]]]:
    """Group paired cases into clusters by attacker instruction (protocol §6 cluster unit).
    instruction_of maps every case_id in pairs to its attacker-instruction id; a missing id is an error.
    Clusters are returned in sorted instruction-id order, so the grouping is deterministic."""
    missing = sorted({cid for cid, _, _ in pairs if cid not in instruction_of})
    if missing:
        raise ValueError(f"no attacker instruction for case_id(s) {missing}")
    groups: dict[str, list[tuple[bool, bool]]] = {}
    for cid, a0, spot in pairs:
        groups.setdefault(instruction_of[cid], []).append((a0, spot))
    return [groups[k] for k in sorted(groups)]


def holm(pvalues: Sequence[float], alpha: float) -> list[bool]:
    """Holm step-down at family level alpha. Sorted ascending, the i-th smallest p (i = 1..k) is rejected when
    p <= alpha / (k - i + 1); the first non-rejection stops the procedure. Returns rejections in the input order.
    For two targets and alpha = 0.05 the thresholds are 0.025 then 0.05."""
    k = len(pvalues)
    if k == 0:
        raise ValueError("holm needs at least one p-value")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if any(not 0 <= p <= 1 for p in pvalues):
        raise ValueError("p-values must be in [0, 1]")
    rejected = [False] * k
    for rank, i in enumerate(sorted(range(k), key=lambda j: pvalues[j])):
        if pvalues[i] <= alpha / (k - rank):
            rejected[i] = True
        else:
            break
    return rejected


def _is_int(x: object) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _order_statistic_bounds(stats: Sequence[float], level: float) -> tuple[float, float]:
    """Percentile bounds from sorted resample statistics, 0-based, with B = len(stats) and alpha = 1 - level:
        lower = stats[floor(alpha/2 * B)]
        upper = stats[min(B - 1, ceil((1 - alpha/2) * B) - 1)]
    For B = 1000 and level = 0.95 these are the 26th and 975th smallest values. The products are rounded to 9 decimals
    before floor and ceil, so an exact boundary is not moved by floating-point noise."""
    stats = sorted(stats)
    b = len(stats)
    alpha = 1.0 - level
    lower_index = math.floor(round(alpha / 2 * b, 9))
    upper_index = min(b - 1, math.ceil(round((1 - alpha / 2) * b, 9)) - 1)
    return stats[lower_index], stats[upper_index]


def cluster_bootstrap_interval(clusters: Sequence[Sequence[tuple[bool, bool]]], *, resamples: int, seed: int,
                               level: float) -> tuple[float, float, float]:
    """Point estimate and percentile cluster-bootstrap interval for the paired event-rate difference A0 - SPOT.

    clusters: one sequence of (a0_event, spot_event) pairs per cluster (for InjecAgent, the attacker instruction).
    At least two clusters are required; with one cluster the resampled interval has zero width and is not returned.
    Clusters are resampled with replacement; each resample pools all cases in the drawn clusters. The random generator
    is local (random.Random(seed)), so the global random state is not touched.
    Returns (point, lower, upper) at the given two-sided level; the bounds follow _order_statistic_bounds."""
    if not _is_int(resamples) or resamples < 1:
        raise ValueError("resamples must be a positive integer (fixed in the protocol)")
    if not _is_int(seed):
        raise ValueError("seed must be an integer, not a bool (fixed in the protocol)")
    if isinstance(level, bool) or not 0 < level < 1:
        raise ValueError("level must be a float between 0 and 1 (fixed in the protocol)")
    for cluster in clusters:
        for a0, spot in cluster:
            _check_bool(a0, "A0 outcome")
            _check_bool(spot, "SPOT_TOOL outcome")
    if len(clusters) < 2:
        raise ValueError("at least two clusters are required for a cluster bootstrap")
    if any(len(c) == 0 for c in clusters):
        raise ValueError("every cluster must contain at least one case")

    totals = [(sum(int(a0) - int(spot) for a0, spot in c), len(c)) for c in clusters]  # outcomes already checked above
    point = sum(d for d, _ in totals) / sum(m for _, m in totals)

    rng = random.Random(seed)
    k = len(totals)
    stats = []
    for _ in range(resamples):
        drawn = [totals[rng.randrange(k)] for _ in range(k)]
        stats.append(sum(d for d, _ in drawn) / sum(m for _, m in drawn))
    lower, upper = _order_statistic_bounds(stats, level)
    return point, lower, upper
