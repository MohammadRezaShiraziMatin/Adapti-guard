#!/usr/bin/env python3
"""Monte Carlo power for exact McNemar (Holm-4 adjusted alpha), independent pairs.

Reproducible seed; prints JSON table for PREREG_HARNESS_V2_FULL Revision 2.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any


def exact_mcnemar_pvalue_two_sided(b: int, c: int) -> float:
    """Two-sided exact McNemar on discordant count (min-tail doubling)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, n - b)
    p = 0.0
    for i in range(0, k + 1):
        p += math.comb(n, i) * (0.5**n)
    return min(1.0, 2.0 * p)


def mcnemar_reject(
    b: int,
    c: int,
    *,
    alpha: float,
    direction: str = "B3_reduces_success",
) -> bool:
    """Holm step-1 style: two-sided exact p-value + one-sided direction (b > c)."""
    if direction == "B3_reduces_success" and b <= c:
        return False
    return exact_mcnemar_pvalue_two_sided(b, c) <= alpha


def exact_mcnemar_pvalue_one_sided_b_gt_c(b: int, c: int) -> float:
    """Legacy one-sided (min-tail); retained for reference."""
    n = b + c
    if n == 0:
        return 1.0
    if b <= c:
        return 1.0
    p = 0.0
    for k in range(b, n + 1):
        p += math.comb(n, k) * (0.5**n)
    return min(1.0, p)


def simulate_power(
    *,
    n_pairs: int,
    p0: float,
    p1: float,
    alpha: float,
    n_sim: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    reject = 0
    for _ in range(n_sim):
        b = c = 0
        for _ in range(n_pairs):
            a0 = 1 if rng.random() < p0 else 0
            b3 = 1 if rng.random() < p1 else 0
            if a0 == 1 and b3 == 0:
                b += 1
            elif a0 == 0 and b3 == 1:
                c += 1
        pval = exact_mcnemar_pvalue_two_sided(b, c)
        if mcnemar_reject(b, c, alpha=alpha):
            reject += 1
    return {
        "n_pairs": n_pairs,
        "p0": p0,
        "p1": p1,
        "alpha_holm_step1_two_sided": alpha,
        "direction_rule": "reject if b>c and two_sided_p<=alpha",
        "n_sim": n_sim,
        "seed": seed,
        "power": reject / n_sim,
        "discordant_rate_independent": p0 * (1 - p1) + (1 - p0) * p1,
    }


def build_power_tables(
    *,
    n_sim: int,
    seed: int,
    alpha: float,
) -> dict[str, Any]:
    pair_counts = [24, 48, 96, 120, 168]
    primary_p1 = 0.12
    sens_p1 = 0.18
    holm_family = int(round(0.05 / alpha))
    out: dict[str, Any] = {
        "method": "independent Bernoulli pairs; exact two-sided McNemar p + direction b>c",
        "holm_family": holm_family,
        "alpha_per_model": alpha,
        "p0_attack_success_A0": 0.30,
        "n_sim": n_sim,
        "seed": seed,
        "primary_effect_p1_B3": primary_p1,
        "tables": {},
    }
    rows_primary = []
    for n in pair_counts:
        rows_primary.append(
            simulate_power(
                n_pairs=n,
                p0=0.30,
                p1=primary_p1,
                alpha=alpha,
                n_sim=n_sim,
                seed=seed + n,
            )
        )
    out["tables"]["p1_0.12"] = rows_primary

    rows_sens = []
    for n in pair_counts:
        rows_sens.append(
            simulate_power(
                n_pairs=n,
                p0=0.30,
                p1=sens_p1,
                alpha=alpha,
                n_sim=n_sim,
                seed=seed + 1000 + n,
            )
        )
    out["tables"]["p1_0.18_sensitivity"] = rows_sens
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sim", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20260927)
    parser.add_argument(
        "--alpha",
        type=float,
        default=None,
        help="Holm step-1 two-sided alpha per model (default: 0.05/4)",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON artifact to this path (implies structured output)",
    )
    args = parser.parse_args()

    alpha = args.alpha if args.alpha is not None else 0.05 / 4
    out = build_power_tables(n_sim=args.n_sim, seed=args.seed, alpha=alpha)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    if args.json or args.output is None:
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            rows_primary = out["tables"]["p1_0.12"]
            rows_sens = out["tables"]["p1_0.18_sensitivity"]
            print(f"alpha={alpha} n_sim={args.n_sim} seed={args.seed}")
            print("p1=0.12 (primary):")
            for r in rows_primary:
                print(f"  N={r['n_pairs']:3d}  power={r['power']:.4f}")
            print("p1=0.18 (sensitivity):")
            for r in rows_sens:
                print(f"  N={r['n_pairs']:3d}  power={r['power']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
