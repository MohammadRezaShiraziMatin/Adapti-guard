"""E3 sensitivity of the paired null to (a) the endpoint and (b) what effect size the design could detect. API=0.

Reads only the committed E3 traces (same pairing as scripts/analyze_independent_defended.py). It adds no confirmatory
test: it reports exact McNemar results under an alternative text-level endpoint, and the exact unconditional power of
the paired design to detect a given reduction in executed attacks, assuming episodes are independent (they are
clustered by family and instance, so the reported power is an upper bound).
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from statistics import mean, stdev

from scipy.stats import binom, t as t_dist

from analyze_independent_defended import _load, mcnemar_exact as _mcnemar_exact

mcnemar_exact = lru_cache(maxsize=None)(_mcnemar_exact)

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "experiments/harness_v2"
OUT = ROOT / "docs/research/artifacts/e3_power_sensitivity_20261003.json"
ALPHA, TARGET_POWER = 0.05, 0.8


def executed(r: dict) -> bool:
    return (r["C2"] or {}).get("exec_executed") is True


def text_or_executed(r: dict) -> bool:
    return executed(r) or (r["C2"] or {}).get("C2_state") == "DELIVERED_TEXT_CLAIM_ONLY"


def power(n: int, p10: float, p01: float) -> float:
    """Exact unconditional power of the two-sided exact McNemar test at ALPHA."""
    pd = p10 + p01
    if pd <= 0:
        return 0.0
    ratio = p10 / pd
    reject = {}
    total = 0.0
    for d in range(n + 1):
        wd = binom.pmf(d, n, pd)
        if wd < 1e-15:
            continue
        for b in range(d + 1):
            if mcnemar_exact(b, d - b) <= ALPHA:
                total += wd * binom.pmf(b, d, ratio)
    return total


def mde(n: int, noise: float) -> float:
    """Smallest reduction (grid 0.001) with power >= TARGET_POWER; power is monotone in the reduction."""
    hi = int((1 - 2 * noise) * 1000)
    if hi < 1 or power(n, noise + hi / 1000, noise) < TARGET_POWER:
        return math.nan
    lo = 1
    while lo < hi:
        mid = (lo + hi) // 2
        if power(n, noise + mid / 1000, noise) >= TARGET_POWER:
            hi = mid
        else:
            lo = mid + 1
    return lo / 1000


def pairs_for(a0_rows: list[dict], def_rows: list[dict], arm: str) -> list[tuple[dict, dict]]:
    key = lambda r: (r["scenario_id"], r["instance_index"], r["family"])
    a0 = {key(r): r for r in a0_rows if r["condition"] == "A0" and r["status"] == "COMPLETE"}
    return [(a0[key(r)], r) for r in def_rows if r["condition"] == arm and r["status"] == "COMPLETE" and key(r) in a0]


def main() -> None:
    scr = _load(H / "HARNESS_V2_INDEPENDENT_SCREEN_20260930")
    dfd = _load(H / "HARNESS_V2_INDEPENDENT_DEFENDED_20260930")
    out: dict = {"alpha": ALPHA, "target_power": TARGET_POWER, "arms": {}}
    for arm in ("B3", "CORE"):
        ps = pairs_for(scr, dfd, arm)
        n = len(ps)
        res: dict = {"pairs": n, "endpoints": {}}
        for name, f in (("executed", executed), ("executed_or_text_claim", text_or_executed)):
            a = [f(x) for x, _ in ps]
            d = [f(y) for _, y in ps]
            b10 = sum(x and not y for x, y in zip(a, d))
            b01 = sum(y and not x for x, y in zip(a, d))
            res["endpoints"][name] = {"a0": sum(a), "arm": sum(d), "b10_a0_only": b10, "b01_arm_only": b01,
                                      "mcnemar_exact_p": mcnemar_exact(b10, b01)}
        e = res["endpoints"]["executed"]
        noise = (e["b10_a0_only"] + e["b01_arm_only"]) / (2 * n)
        base = e["a0"] / n
        res["noise_discordance_per_direction"] = noise
        res["a0_rate"] = base
        res["mde_absolute_reduction"] = mde(n, noise)
        res["mde_relative_reduction"] = res["mde_absolute_reduction"] / base
        res["power_at_relative_reduction"] = {
            str(r): power(n, noise + r * base, noise) for r in (0.1, 0.25, 0.5, 0.75)}
        fam: dict = defaultdict(list)
        for x, y in ps:
            fam[x["scenario_id"]].append(int(executed(x)) - int(executed(y)))
        red = [sum(v) / len(v) for v in fam.values()]
        se = stdev(red) / math.sqrt(len(red))
        tq = t_dist.ppf(0.975, len(red) - 1)
        res["family_cluster"] = {
            "clusters": len(red), "mean_reduction": mean(red),
            "ci95_t": [mean(red) - tq * se, mean(red) + tq * se],
            "families_with_reduction": sum(r > 0 for r in red), "families_with_increase": sum(r < 0 for r in red),
            "families_unchanged": sum(r == 0 for r in red),
        }
        by_model: dict = defaultdict(list)
        for x, y in ps:
            by_model[y["family"]].append((x, y))
        res["per_model"] = {}
        for m, mp in sorted(by_model.items()):
            k = len(mp)
            b10 = sum(executed(x) and not executed(y) for x, y in mp)
            b01 = sum(executed(y) and not executed(x) for x, y in mp)
            nz = max((b10 + b01) / (2 * k), 1 / (2 * k))
            res["per_model"][m] = {"pairs": k, "a0": sum(executed(x) for x, _ in mp), "arm": sum(executed(y) for _, y in mp),
                                   "b10_a0_only": b10, "b01_arm_only": b01, "mde_absolute_reduction": mde(k, nz)}
        out["arms"][arm] = res
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
