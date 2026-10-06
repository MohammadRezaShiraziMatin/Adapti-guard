"""Intervals for the E1 judge-vs-execution quantities, from the committed per-arm counts only (offline; no new data).

The stored artifact has no intervals. For each arm the 2x2 table (judge success x executed) is rebuilt from its counts and bootstrapped
(multinomial resampling of the 61 episodes, 10,000 draws, fixed seed) for Cohen's kappa; for each track the paired effect (B0 minus
treatment, judge-scored and execution-scored) is bootstrapped from the discordant counts. Intervals are percentile 95% and descriptive:
one frozen pack, 61 episodes per arm, one judge.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs/research/artifacts/tracks_ab_deterministic_rescoring_20260930.json"
OUT = ROOT / "docs/research/artifacts/e1_interval_estimates_20261006.json"
NB, SEED = 10000, 20261006


def kappa(a, b, c, d):
    n = a + b + c + d
    po = (a + d) / n
    pe = ((a + b) * (a + c) + (c + d) * (b + d)) / n**2
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def main() -> None:
    src = json.loads(SRC.read_text())
    rng = np.random.default_rng(SEED)
    out: dict = {"bootstrap_draws": NB, "seed": SEED, "interval": "percentile 95%", "arms": {}, "paired_effects": {}}
    for track, key in (("A", "A_VNEXT"), ("B", "B_PHASE1")):
        for arm, v in src[key]["arms"].items():
            n, a_, b_, c_ = v["attack_n"], v["deterministic_success"] - v["judge_false_det_true"], v["judge_true_det_false"], v["judge_false_det_true"]
            cell = [a_, b_, c_, n - a_ - b_ - c_]
            ks = [kappa(*rng.multinomial(n, np.array(cell) / n)) for _ in range(NB)]
            ks = np.array([k for k in ks if not np.isnan(k)])
            out["arms"][f"{track}:{arm}"] = {"cells_both_judgeonly_execonly_neither": cell, "kappa": round(kappa(*cell), 4) if kappa(*cell) == kappa(*cell) else None,
                                              "kappa_ci95": [round(float(np.percentile(ks, 2.5)), 3), round(float(np.percentile(ks, 97.5)), 3)] if len(ks) > 100 else None,
                                              "valid_resamples": int(len(ks))}
        for kind in ("paired_judge", "paired_deterministic"):
            p = src[key][kind]
            n, b10, b01 = p["pairs"], p["b10_treatment_wins"], p["b01_b0_wins"]
            draws = rng.multinomial(n, np.array([b10, b01, n - b10 - b01]) / n, size=NB)
            delta = (draws[:, 0] - draws[:, 1]) / n
            out["paired_effects"][f"{track}:{kind}"] = {"pairs": n, "b10": b10, "b01": b01, "delta_hat": round((b10 - b01) / n, 4),
                                                       "ci95": [round(float(np.percentile(delta, 2.5)), 3), round(float(np.percentile(delta, 97.5)), 3)]}
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
