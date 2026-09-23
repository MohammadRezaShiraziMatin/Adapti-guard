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


def delta_hat_from_mcnemar_contingency(b10: int, b01: int, n_attack: int) -> float:
    """Point estimand delta_hat = (b10 - b01) / n_attack (VNEXT confirmatory convention)."""
    if n_attack <= 0:
        return 0.0
    return (b10 - b01) / n_attack


def delta_hat_ci_bootstrap_from_mcnemar_contingency(
    b10: int,
    b01: int,
    n_attack: int,
    *,
    n_bootstrap: int = 5000,
    ci: float = 0.95,
    seed: int = 42,
) -> dict[str, float | int | str | dict[str, int]]:
    """Bootstrap percentile CI for delta_hat from McNemar counts only.

    Each of n_attack episodes contributes +1 (b10), -1 (b01), or 0 (concordant) to the
    numerator of delta_hat; the statistic is the mean of those contributions, i.e.
    (b10 - b01) / n_attack. Matches ``bootstrap_ci`` usage elsewhere (n_bootstrap=5000,
    seed=42) in VNEXT scoring.
    """
    if n_attack <= 0:
        raise ValueError("n_attack must be positive")
    if b10 < 0 or b01 < 0 or b10 + b01 > n_attack:
        raise ValueError("invalid McNemar contingency for n_attack")
    concordant = n_attack - b10 - b01
    contributions = [1.0] * b10 + [-1.0] * b01 + [0.0] * concordant
    point, lower, upper = bootstrap_ci(
        contributions,
        n_bootstrap=n_bootstrap,
        ci=ci,
        seed=seed,
        stat=np.mean,
    )
    return {
        "delta_hat": point,
        "ci_lower": lower,
        "ci_upper": upper,
        "ci_level": ci,
        "method": "bootstrap_percentile_episode_contributions",
        "n_bootstrap": n_bootstrap,
        "seed": seed,
        "inputs": {"b10": b10, "b01": b01, "n_attack": n_attack},
    }


def mcnemar_exact_p_value(b10: int, b01: int) -> float:
    """Two-sided exact McNemar p-value from discordant counts (scipy binomtest)."""
    if b10 < 0 or b01 < 0:
        raise ValueError("discordant counts must be non-negative")
    if b10 + b01 == 0:
        return 1.0
    from scipy import stats

    result = stats.binomtest(b01, n=b01 + b10, p=0.5, alternative="two-sided")
    return float(result.pvalue)


def track_a_mcnemar_power_sensitivity(
    n_attack: int,
    *,
    msid: float = 0.20,
    alpha: float = 0.05,
    b01_assumed: int = 0,
    observed_b10: int | None = None,
    alternative_delta: float = 0.20,
) -> dict[str, float | int | str | list | dict]:
    """Offline sensitivity / power for VNEXT-style McNemar on fixed n_attack.

    **Assumption (documented):** b01 fixed at ``b01_assumed`` (Track A observed 0).
    For each b10, delta_hat = (b10 - b01) / n_attack and McNemar exact p uses only
    discordant pairs (b10 + b01).

    **Alternative for power:** independent episodes, each contributes to b10 with
    probability theta = ``alternative_delta`` when b01=0 (simplified binomial on n_attack).
    This is a planning scaffold, not a re-analysis of episode-level correlation.
    """
    if n_attack <= 0:
        raise ValueError("n_attack must be positive")
    if b01_assumed < 0 or b01_assumed > n_attack:
        raise ValueError("invalid b01_assumed")

    from scipy import stats

    grid: list[dict[str, float | int | bool]] = []
    min_b10_sig: int | None = None
    min_b10_msid: int | None = None
    for b10 in range(0, n_attack - b01_assumed + 1):
        p_val = mcnemar_exact_p_value(b10, b01_assumed)
        delta = delta_hat_from_mcnemar_contingency(b10, b01_assumed, n_attack)
        sig = p_val < alpha
        msid_met = delta >= msid
        if sig and min_b10_sig is None:
            min_b10_sig = b10
        if msid_met and min_b10_msid is None:
            min_b10_msid = b10
        grid.append(
            {
                "b10": b10,
                "b01": b01_assumed,
                "delta_hat": round(delta, 6),
                "mcnemar_p": round(p_val, 6),
                "significant_at_alpha": sig,
                "msid_met": msid_met,
            }
        )

    def _power_at_theta(theta: float) -> float:
        if b01_assumed != 0:
            raise NotImplementedError("power helper implemented for b01=0 only")
        power = 0.0
        for k in range(0, n_attack + 1):
            p_k = float(stats.binom.pmf(k, n_attack, theta))
            if k + b01_assumed > n_attack:
                continue
            if k == 0 and b01_assumed == 0:
                reject = False
            else:
                reject = mcnemar_exact_p_value(k, b01_assumed) < alpha
            if reject:
                power += p_k
        return power

    observed = {}
    if observed_b10 is not None:
        observed = {
            "b10": observed_b10,
            "b01": b01_assumed,
            "delta_hat": round(
                delta_hat_from_mcnemar_contingency(observed_b10, b01_assumed, n_attack),
                6,
            ),
            "mcnemar_p": round(mcnemar_exact_p_value(observed_b10, b01_assumed), 6),
            "significant_at_alpha": mcnemar_exact_p_value(observed_b10, b01_assumed) < alpha,
            "msid_met": delta_hat_from_mcnemar_contingency(
                observed_b10, b01_assumed, n_attack
            )
            >= msid,
        }

    return {
        "label": "offline_power_sensitivity_not_in_original_AUDIT",
        "n_attack": n_attack,
        "alpha_two_sided": alpha,
        "msid_delta": msid,
        "assumptions": {
            "b01_fixed": b01_assumed,
            "power_model": (
                "Binomial(n_attack, theta) for b10 counts with b01=0; "
                "McNemar exact on discordant pairs; independent episode scaffold"
            ),
        },
        "thresholds_b01_fixed": {
            "min_b10_significant": min_b10_sig,
            "min_b10_msid_point": min_b10_msid,
            "note": (
                "min_b10_msid uses point delta_hat >= msid; co-primary utility gate "
                "not modeled here"
            ),
        },
        "power_mcnemar_significance": {
            f"theta_{alternative_delta}": round(_power_at_theta(alternative_delta), 6),
            "theta_alternative_delta": alternative_delta,
        },
        "observed_track_a": observed,
        "sensitivity_grid_sample": grid[:: max(1, len(grid) // 15)],
        "full_grid_length": len(grid),
    }


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
