"""Bootstrap confidence intervals and paired statistical tests."""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np


def bootstrap_ci(
    values: Sequence[float],
    *,
    n_bootstrap: int = 5000,
    ci: float = 0.95,
    seed: int = 42,
    stat: Callable[[np.ndarray], float] = np.mean,
) -> tuple[float, float, float]:
    """Return (point_estimate, lower, upper) for the chosen statistic."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return 0.0, 0.0, 0.0
    point = float(stat(arr))
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=arr.size, replace=True)
        boots.append(float(stat(sample)))
    alpha = (1.0 - ci) / 2.0
    lower, upper = np.quantile(boots, [alpha, 1.0 - alpha])
    return point, float(lower), float(upper)


def mcnemar_test(
    a_success: Sequence[bool],
    b_success: Sequence[bool],
) -> dict[str, float | int | str]:
    """Paired binary outcomes for two methods on the same samples."""
    if len(a_success) != len(b_success):
        raise ValueError("paired sequences must have equal length")

    b01 = sum(1 for x, y in zip(a_success, b_success) if (not x) and y)
    b10 = sum(1 for x, y in zip(a_success, b_success) if x and (not y))

    from scipy import stats

    if b01 + b10 == 0:
        return {
            "b01": b01,
            "b10": b10,
            "statistic": 0.0,
            "p_value": 1.0,
            "method": "mcnemar_exact",
        }

    result = stats.binomtest(b01, n=b01 + b10, p=0.5, alternative="two-sided")
    return {
        "b01": b01,
        "b10": b10,
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "method": "mcnemar_exact",
    }


def wilcoxon_signed_rank(
    a: Sequence[float],
    b: Sequence[float],
) -> dict[str, float | str]:
    from scipy import stats

    diff = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    if diff.size == 0:
        return {"statistic": 0.0, "p_value": 1.0, "method": "wilcoxon"}
    if np.allclose(diff, 0):
        return {"statistic": 0.0, "p_value": 1.0, "method": "wilcoxon"}
    stat = stats.wilcoxon(diff, alternative="two-sided")
    return {
        "statistic": float(stat.statistic),
        "p_value": float(stat.pvalue),
        "method": "wilcoxon",
    }


def cohens_d(a: Sequence[float], b: Sequence[float]) -> float:
    """Effect size for paired or independent samples (here: independent means)."""
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    if x.size == 0 or y.size == 0:
        return 0.0
    pooled_std = np.sqrt((np.var(x, ddof=1) + np.var(y, ddof=1)) / 2.0)
    if pooled_std < 1e-12:
        return 0.0
    return float((np.mean(x) - np.mean(y)) / pooled_std)


def holm_correction(p_values: Sequence[float]) -> list[dict[str, float]]:
    """Holm-Bonferroni correction for multiple comparisons.

    Returns list of dicts with raw_p, adjusted_p, rank (sorted by raw p-value).
    """
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    m = len(indexed)
    adjusted: list[dict[str, float]] = [{} for _ in range(m)]
    prev_adj = 0.0
    for rank, (orig_idx, p) in enumerate(indexed, start=1):
        adj = min(1.0, max(prev_adj, (m - rank + 1) * p))
        prev_adj = adj
        adjusted[orig_idx] = {
            "raw_p": float(p),
            "adjusted_p": float(adj),
            "rank": float(rank),
        }
    return adjusted


def proportion_ci_wilson(
    successes: int,
    n: int,
    ci: float = 0.95,
) -> tuple[float, float, float]:
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0, 0.0
    from scipy import stats

    alpha = 1.0 - ci
    p = successes / n
    z = stats.norm.ppf(1 - alpha / 2)
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return float(p), float(max(0.0, centre - margin)), float(min(1.0, centre + margin))
