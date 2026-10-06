"""Cluster-aware power and minimum detectable reduction for the E3 design (offline simulation; no API, no new data).

E3 pools 7 attack families x 8 instances x 3 models = 24 episodes per family and arm. The earlier power note
(`e3_power_sensitivity.py`) treats episodes as independent, which is an upper bound. Here the family is the unit: family-level true
reductions ~ N(delta, tau^2) (tau = between-family heterogeneity), per-direction nondeterminism q = the observed rate, family-level
one-sample t test (df = 6, two-sided alpha 0.05). The generative model is `e6_protocol_simulation.simulate`. The tau grid is an assumption,
not an estimate; the observed sd of the family-level reductions (0.045 B3, 0.034 CORE) is noise from an inert defense and says nothing
about the spread a defense with a real effect would show.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_protocol_simulation as sim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/research/artifacts/e3_cluster_power_20261006.json"
F, M, ALPHA, SEED, NSIM = 7, 24, 0.05, 20261006, 20000
Q = {"B3": 7 / (2 * 167), "CORE": 8 / (2 * 168)}  # observed discordant pairs per direction (E3, §6.3)
TAUS = (0.0, 0.05, 0.10, 0.15)
DELTAS = (0.05, 0.08, 0.10, 0.15, 0.20, 0.30)


def power(delta: float, tau: float, q: float, seed: int, nsim: int = NSIM) -> float:
    rng = np.random.default_rng(seed)
    c10, c01 = sim.simulate(rng, F, M, delta, tau, q, nsim)
    red = (c10 - c01) / M
    mean, se = red.mean(1), red.std(1, ddof=1) / math.sqrt(F)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(se > 0, mean / se, 0.0)
    p = np.where(se > 0, 2 * stats.t.sf(np.abs(t), F - 1), np.where(mean != 0, 0.0, 1.0))
    return float((p < ALPHA).mean())


def mde80(tau: float, q: float, seed: int) -> float | None:
    if power(0.6, tau, q, seed, 4000) < 0.8:
        return None
    lo, hi = 0.0, 0.6
    for _ in range(10):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if power(mid, tau, q, seed, 4000) >= 0.8 else (mid, hi)
    return round(hi, 3)


def main() -> None:
    res = {"design": {"families": F, "episodes_per_family_per_arm": M, "alpha": ALPHA, "nsim": NSIM, "seed": SEED, "q_per_direction": {k: round(v, 4) for k, v in Q.items()},
                      "test": "family-level one-sample t test, df 6", "tau_is_an_assumption": True}, "cells": {}}
    for arm, q in Q.items():
        for tau in TAUS:
            cell = {f"power_delta_{d:.2f}": round(power(d, tau, q, SEED + int(d * 100) + int(tau * 1000)), 3) for d in DELTAS}
            cell["type_I_error"] = round(power(0.0, tau, q, SEED + 7), 3)
            cell["mde_80pct"] = mde80(tau, q, SEED + 11)
            res["cells"][f"{arm}_tau{tau:.2f}"] = cell
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
