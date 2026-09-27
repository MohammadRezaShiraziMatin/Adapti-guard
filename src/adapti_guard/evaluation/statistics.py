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


def mcnemar_exact_power_vnext_planning(
    n_attack: int,
    *,
    p10: float,
    p01: float,
    alpha: float = 0.05,
) -> dict[str, float | int | str]:
    """Per-comparison exact McNemar power (VNEXT_POWER_MEMO §5 planning model).

    Episode-level categories are mutually exclusive with probabilities
    ``p10`` (b10), ``p01`` (b01), and ``1 - p10 - p01`` (concordant). Discordant
    total ``D ~ Bin(n_attack, p10 + p01)``; ``B10 | D=d ~ Bin(d, p10/(p10+p01))``.
    Reject when two-sided exact ``p < alpha`` on ``(b10, b01)``.

    This is **one** paired comparison (one target × one arm pair), not a
    multiplicity-adjusted family.
    """
    if n_attack <= 0:
        raise ValueError("n_attack must be positive")
    if p10 < 0 or p01 < 0 or p10 + p01 > 1.0:
        raise ValueError("invalid planning probabilities")
    psi = p10 + p01
    from scipy import stats

    power = 0.0
    for d in range(0, n_attack + 1):
        p_d = float(stats.binom.pmf(d, n_attack, psi))
        if d == 0:
            continue
        p_b10_given_d = p10 / psi
        for b10 in range(0, d + 1):
            b01 = d - b10
            p_cond = float(stats.binom.pmf(b10, d, p_b10_given_d))
            if mcnemar_exact_p_value(b10, b01) < alpha:
                power += p_d * p_cond
    return {
        "label": "vnext_planning_discordant_pair_model",
        "n_attack": n_attack,
        "p10": p10,
        "p01": p01,
        "psi": psi,
        "alpha_two_sided": alpha,
        "per_comparison_power": round(power, 6),
        "reference": "docs/experiments/protocols/VNEXT_POWER_MEMO.md §5",
    }


def holm_mcnemar_family_power_planning(
    n_tests: int,
    n_attack: int,
    *,
    p10: float,
    p01: float,
    alpha: float = 0.05,
    mc_replicates: int = 20_000,
    seed: int = 42,
) -> dict[str, float | int | str | dict]:
    """Holm family power under an **explicit independence** assumption across tests.

    Each of ``n_tests`` comparisons draws its own episode-level multinomial
    ``(b10, b01, concordant)`` with planning ``(p10, p01)``. Cross-target
    dependence is **not** modeled; without Owner-stated correlation structure,
    rigorous joint family power is **UNRESOLVED** (see ``dependence_note``).

    Also reports a **perfect positive correlation** bound: one shared draw
    replicated across all tests (Holm on identical raw p-values).
    """
    if n_tests <= 0:
        raise ValueError("n_tests must be positive")
    base = mcnemar_exact_power_vnext_planning(
        n_attack, p10=p10, p01=p01, alpha=alpha
    )
    probs = np.array([p10, p01, 1.0 - p10 - p01], dtype=float)
    if probs.sum() <= 0 or np.any(probs < 0):
        raise ValueError("invalid planning probabilities")

    def _holm_rejects(raw_ps: Sequence[float]) -> list[bool]:
        holm = holm_correction(raw_ps)
        return [row["adjusted_p"] < alpha for row in holm]

    rng = np.random.default_rng(seed)
    any_rej = all_rej = 0
    for _ in range(mc_replicates):
        raw: list[float] = []
        for _ in range(n_tests):
            counts = rng.multinomial(n_attack, probs)
            raw.append(mcnemar_exact_p_value(int(counts[0]), int(counts[1])))
        rej = _holm_rejects(raw)
        if any(rej):
            any_rej += 1
        if all(rej):
            all_rej += 1

    # Perfect correlation: one multinomial, same p-value on every test.
    perfect_any = 0.0
    from scipy import stats

    psi = p10 + p01
    for d in range(0, n_attack + 1):
        p_d = float(stats.binom.pmf(d, n_attack, psi))
        if d == 0:
            continue
        p_b10_given_d = p10 / psi
        for b10 in range(0, d + 1):
            b01 = d - b10
            p_cond = float(stats.binom.pmf(b10, d, p_b10_given_d))
            p_val = mcnemar_exact_p_value(b10, b01)
            if any(_holm_rejects([p_val] * n_tests)):
                perfect_any += p_d * p_cond

    return {
        "label": "holm_family_power_planning_requires_dependence_assumption",
        "n_tests": n_tests,
        "n_attack": n_attack,
        "p10": p10,
        "p01": p01,
        "alpha_two_sided": alpha,
        "per_comparison_power": base["per_comparison_power"],
        "independence_assumption": {
            "mc_replicates": mc_replicates,
            "seed": seed,
            "power_any_holm_reject": round(any_rej / mc_replicates, 6),
            "power_all_holm_reject": round(all_rej / mc_replicates, 6),
        },
        "perfect_positive_correlation_bound": {
            "power_any_holm_reject": round(perfect_any, 6),
            "note": (
                "Same discordant counts on all tests; conservative vs independence "
                "when outcomes move together across targets."
            ),
        },
        "dependence_note": (
            "Q1 runs the same 61 attack IDs on 6 targets; cross-target correlation "
            "is not identified from frozen data. Family-wise power is UNRESOLVED "
            "unless Owner accepts independence, a correlation model, or a "
            "family estimand (any vs all targets)."
        ),
        "family_wise_target_80pct_met": "UNRESOLVED",
        "reference": "docs/experiments/protocols/VNEXT_POWER_MEMO.md §5; holm_correction()",
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
