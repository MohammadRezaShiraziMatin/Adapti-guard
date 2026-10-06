"""Cluster-aware power and minimum detectable reduction for the E3 design (offline simulation; no API, no new data).

E3 pools 7 attack families x 8 instances x 3 models = 24 episodes per family and arm. The earlier power note (`e3_power_sensitivity.py`)
treats episodes as independent, an upper bound. Here the family is the unit (family-level one-sample t test, df 6, two-sided alpha 0.05).

Main model (`ceiling`): a family cannot show a larger reduction than its undefended rate b_f (observed A0 rates, 0/24 to 23/24, mean 0.339).
The true reduction is d_f = r_f * b_f with the relative effect r_f ~ N(rho, sigma^2) clipped to [0, 1] (rho = mean relative reduction, sigma =
between-family spread of the relative effect; sigma is an assumption, not an estimate). Per instance the paired outcome is (A0 executed,
defended not) with probability min(q + d_f, b_f) and the reverse with probability min(q, 1 - b_f), where q is the observed per-direction
nondeterminism of the CORE arm, which presents the model with the same input as A0 (8 discordant pairs of 168); families with b_f = 0 have no
room for either direction. The model does not split the family by model (susceptibility is concentrated in one model), so it is, if anything,
still generous. The `uncapped` cells (the earlier model, no ceiling) are kept as an upper bound on power.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_analysis as an  # noqa: E402
import e6_protocol_simulation as sim  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/research/artifacts/e3_cluster_power_20261006.json"
SCREEN = ROOT / "experiments/harness_v2/HARNESS_V2_INDEPENDENT_SCREEN_20260930/episodes.jsonl"
F, M, ALPHA, SEED, NSIM = 7, 24, 0.05, 20261006, 20000
Q = 8 / (2 * 168)  # per-direction nondeterminism: CORE vs A0 (identical model input)
RHOS = (0.25, 0.50, 0.75, 1.00)
SIGMAS = (0.0, 0.25, 0.50)
TAUS = (0.0, 0.05, 0.10, 0.15)
DELTAS = (0.05, 0.08, 0.10, 0.15, 0.20, 0.30)


def baselines() -> np.ndarray:
    """Observed undefended execution rate per family (mechanical predicate, A0 arm of E3)."""
    rows = [json.loads(x) for x in SCREEN.read_text().splitlines() if x.strip()]
    fam: dict = {}
    for r in rows:
        if r.get("condition") == "A0" and r.get("exec_spec"):
            fam.setdefault(r["scenario_id"], []).append(an.episode_executed(r))
    return np.array([sum(v) / len(v) for _, v in sorted(fam.items())])


def _t_reject(red: np.ndarray) -> np.ndarray:
    mean, se = red.mean(1), red.std(1, ddof=1) / math.sqrt(red.shape[1])
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(se > 0, mean / se, 0.0)
    p = np.where(se > 0, 2 * stats.t.sf(np.abs(t), red.shape[1] - 1), np.where(mean != 0, 0.0, 1.0))
    return p < ALPHA


def simulate_ceiling(rng, b: np.ndarray, m: int, rho: float, sigma: float, q: float, nsim: int) -> np.ndarray:
    """Family-level reductions (nsim x F) under the ceiling model."""
    f = len(b)
    r = np.clip(rho + sigma * rng.standard_normal((nsim, f)), 0.0, 1.0)
    d = r * b
    room = (b > 0) & (b < 1)
    p10 = np.minimum(np.where(room, q, 0.0) + d, b)
    p01 = np.where(room, np.minimum(q, 1 - b), 0.0)
    u = rng.random((nsim, f, m))
    b10 = u < p10[..., None]
    b01 = (u >= p10[..., None]) & (u < (p10 + p01)[..., None])
    return (b10.sum(2) - b01.sum(2)) / m


def power_ceiling(b, rho, sigma, q, seed, nsim=NSIM) -> float:
    return float(_t_reject(simulate_ceiling(np.random.default_rng(seed), b, M, rho, sigma, q, nsim)).mean())


def power_uncapped(delta, tau, q, seed, nsim=NSIM) -> float:
    c10, c01 = sim.simulate(np.random.default_rng(seed), F, M, delta, tau, q, nsim)
    return float(_t_reject((c10 - c01) / M).mean())


def rho80(b, sigma, q, seed) -> float | None:
    """Smallest mean relative reduction detected with 80% power (bisection on rho in [0, 1])."""
    if power_ceiling(b, 1.0, sigma, q, seed, 4000) < 0.8:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(10):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if power_ceiling(b, mid, sigma, q, seed, 4000) >= 0.8 else (mid, hi)
    return round(hi, 3)


def main() -> None:
    b = baselines()
    res = {"design": {"families": F, "episodes_per_family_per_arm": M, "alpha": ALPHA, "nsim": NSIM, "seed": SEED, "q_per_direction": round(Q, 4),
                      "baselines_by_family_sorted_by_id": [round(float(x), 4) for x in b], "mean_baseline": round(float(b.mean()), 4),
                      "test": "family-level one-sample t test, df 6", "sigma_and_tau_are_assumptions": True}, "ceiling": {}, "uncapped": {}}
    for sg in SIGMAS:
        cell = {f"power_rho_{r:.2f}": round(power_ceiling(b, r, sg, Q, SEED + int(r * 100) + int(sg * 1000)), 3) for r in RHOS}
        # rho = 0 with sigma > 0 is not a null (clipping at 0 gives a positive mean effect), so the type-I error is reported only for sigma = 0
        cell["type_I_error"] = round(power_ceiling(b, 0.0, sg, Q, SEED + 7), 3) if sg == 0 else None
        r80 = rho80(b, sg, Q, SEED + 11)
        cell["rho_80pct"] = r80
        cell["abs_points_80pct"] = None if r80 is None else round(r80 * float(b.mean()), 3)
        res["ceiling"][f"sigma{sg:.2f}"] = cell
    for tau in TAUS:
        cell = {f"power_delta_{d:.2f}": round(power_uncapped(d, tau, Q, SEED + int(d * 100) + int(tau * 1000)), 3) for d in DELTAS}
        cell["type_I_error"] = round(power_uncapped(0.0, tau, Q, SEED + 7), 3)
        res["uncapped"][f"tau{tau:.2f}"] = cell
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
