"""Offline simulation behind the E6 draft protocol's sample-size decision (no data, no API, fixed seed).

Generative model (stated assumptions, not estimates of any real defense): F families with m instances each. Family f has a
true reduction delta_f ~ N(delta, tau^2). For every instance the paired outcome (A0 executed, defended executed) is
(1,0) with probability q + max(delta_f, 0), (0,1) with probability q + max(-delta_f, 0), and concordant otherwise, so q is
the per-direction nondeterminism rate and E[reduction_f] = delta_f. q = 0.04 is above the rates seen for deepseek in E3
(about 0.03); q = 0.07 is the single-turn MT1 replicate rate. Primary analysis: one-sample t test on the F family-level
reductions at two-sided alpha = 0.025 (two primary defenses, Bonferroni). Reported: Type I error, power, coverage of the
97.5% t interval, minimum detectable effect at 80% power, the exact sign-flip test (subset), pooled episode-level McNemar
(secondary; shown to justify demotion) and TOST for the optional equivalence analysis.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/research/artifacts/e6_protocol_simulation_20261004.json"
ALPHA = 0.025
SEED = 20261004
DESIGNS = [(10, 20), (20, 10), (24, 10), (30, 10), (40, 5)]
TAUS = [0.05, 0.10, 0.15, 0.20]
QS = [0.04, 0.07]
DELTAS = [0.0, 0.10, 0.15, 0.20]
NSIM = 5000


def simulate(rng, F, m, delta, tau, q, nsim, floor_share=0.0):
    d = delta + tau * rng.standard_normal((nsim, F))
    qf = np.full((nsim, F), q)
    if floor_share:
        qf = np.where(rng.random((nsim, F)) < floor_share, 0.0, q / (1 - floor_share))
    p10 = qf + np.clip(d, 0, None)
    p01 = qf + np.clip(-d, 0, None)
    u = rng.random((nsim, F, m))
    b10 = u < p10[..., None]
    b01 = (u >= p10[..., None]) & (u < (p10 + p01)[..., None])
    return b10.sum(2), b01.sum(2)


def analyze(c10, c01, m, delta, margins=(0.10, 0.15)):
    red = (c10 - c01) / m
    F = red.shape[1]
    mean = red.mean(1)
    sd = red.std(1, ddof=1)
    se = sd / math.sqrt(F)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(se > 0, mean / se, 0.0)
    p = np.where(se > 0, 2 * stats.t.sf(np.abs(t), F - 1), np.where(mean != 0, 0.0, 1.0))
    q975 = stats.t.ppf(1 - ALPHA / 2, F - 1)
    cover = np.abs(mean - delta) <= q975 * se
    B10, B01 = c10.sum(1), c01.sum(1)
    D = B10 + B01
    pm = np.where(D > 0, np.minimum(1.0, 2 * stats.binom.cdf(np.minimum(B10, B01), np.maximum(D, 1), 0.5)), 1.0)
    out = {"t_reject": float((p < ALPHA).mean()), "mcnemar_reject": float((pm < ALPHA).mean()), "ci_coverage": float(cover.mean())}
    for mg in margins:
        with np.errstate(divide="ignore", invalid="ignore"):
            pl = np.where(se > 0, stats.t.sf((mean + mg) / se, F - 1), np.where(mean > -mg, 0.0, 1.0))
            pu = np.where(se > 0, stats.t.cdf((mean - mg) / se, F - 1), np.where(mean < mg, 0.0, 1.0))
        out[f"tost_equiv_margin_{mg:.2f}"] = float((np.maximum(pl, pu) < ALPHA).mean())
    return out


def sign_flip_rate(rng, c10, c01, m, nsub=400, nperm=4000):
    red = ((c10 - c01) / m)[:nsub]
    F = red.shape[1]
    signs = rng.choice([-1.0, 1.0], size=(nperm, F))
    perm = np.abs(signs @ red.T) / F
    stat = np.abs(red.mean(1))
    p = (1 + (perm >= stat[None, :] - 1e-12).sum(0)) / (nperm + 1)
    return float((p < ALPHA).mean())


def mde80(F, m, tau, q, seed):
    def power(delta):
        r = np.random.default_rng(seed)
        c10, c01 = simulate(r, F, m, delta, tau, q, 3000)
        return analyze(c10, c01, m, delta)["t_reject"]
    lo, hi = 0.0, 0.5
    if power(hi) < 0.8:
        return None
    for _ in range(9):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if power(mid) >= 0.8 else (mid, hi)
    return round(hi, 3)


def main() -> None:
    rng = np.random.default_rng(SEED)
    res: dict = {"alpha_per_defense": ALPHA, "nsim": NSIM, "seed": SEED, "model_note": __doc__.strip().split("\n")[0], "cells": {}}
    for F, m in DESIGNS:
        for tau in TAUS:
            for q in QS:
                key = f"F{F}_m{m}_tau{tau:.2f}_q{q:.2f}"
                cell: dict = {"instances_per_arm": F * m}
                for delta in DELTAS:
                    c10, c01 = simulate(rng, F, m, delta, tau, q, NSIM)
                    cell[f"delta_{delta:.2f}"] = analyze(c10, c01, m, delta)
                    if delta in (0.0, 0.15):
                        cell[f"delta_{delta:.2f}"]["sign_flip_reject_400sims"] = sign_flip_rate(rng, c10, c01, m)
                cell["mde_80pct_t"] = mde80(F, m, tau, q, SEED + F * 100 + m)
                res["cells"][key] = cell
    res["noise_floor_sensitivity"] = {}
    for F, m in ((20, 10), (24, 10)):
        for tau in (0.10, 0.15):
            for delta in (0.0, 0.15):
                c10, c01 = simulate(rng, F, m, delta, tau, 0.04, NSIM, floor_share=0.3)
                res["noise_floor_sensitivity"][f"F{F}_m{m}_tau{tau:.2f}_delta{delta:.2f}_30pct_families_with_no_noise"] = analyze(c10, c01, m, delta)
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
