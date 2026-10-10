#!/usr/bin/env python3
"""Analyse the InjecAgent live run: Wilson CIs, exact McNemar vs A0, noise floor, validity control."""
from __future__ import annotations

import collections
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = sys.argv[1] if len(sys.argv) > 1 else "qwen-2.5-7b"
RUN = ROOT / "experiments/external/injecagent_live_20260930" / ("" if SLUG == "qwen-2.5-7b" else "")
if SLUG != "qwen-2.5-7b":
    RUN = ROOT / f"experiments/external/injecagent_live_20260930_{SLUG}"
OUT = ROOT / "docs/research/artifacts" / ("injecagent_live_analysis_20260930.json" if SLUG == "qwen-2.5-7b" else f"injecagent_live_analysis_20260930_{SLUG}.json")


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def mcnemar_exact(b10, b01):
    n = b10 + b01
    if n == 0:
        return 1.0
    k = min(b10, b01)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return round(min(1.0, 2 * p), 4)


def main() -> int:
    rows = [json.loads(l) for l in (RUN / "episodes.jsonl").read_text().splitlines() if l.strip()]
    by = collections.defaultdict(dict)
    for r in rows:
        by[r["arm"]][r["case_id"]] = r
    res = {"n_rows": len(rows), "errors": sum(1 for r in rows if r["error"]), "arms": {}, "paired_vs_A0": {}}
    for arm, d in by.items():
        for ep in ("first_attacker_tool", "any_attacker_tool"):
            for kind in ("ALL", "dh", "ds"):
                sel = [r for r in d.values() if not r["error"] and (kind == "ALL" or r["kind"] == kind)]
                k = sum(bool(r[ep]) for r in sel)
                res["arms"][f"{arm}|{ep}|{kind}"] = {"k": k, "n": len(sel), "rate": round(k / len(sel), 3) if sel else None, "wilson95": wilson(k, len(sel))}
    for arm in by:
        if arm == "A0":
            continue
        for ep in ("first_attacker_tool", "any_attacker_tool"):
            ids = [i for i in by["A0"] if i in by[arm] and not by["A0"][i]["error"] and not by[arm][i]["error"]]
            b10 = sum(bool(by["A0"][i][ep]) and not by[arm][i][ep] for i in ids)
            b01 = sum(not by["A0"][i][ep] and bool(by[arm][i][ep]) for i in ids)
            res["paired_vs_A0"][f"{arm}|{ep}"] = {"pairs": len(ids), "b10_A0_only": b10, "b01_arm_only": b01, "exact_p": mcnemar_exact(b10, b01)}
    # per-user-tool concentration (cluster view)
    cl = collections.defaultdict(lambda: [0, 0])
    for r in by["A0"].values():
        cl[r["user_tool"]][0] += bool(r["first_attacker_tool"])
        cl[r["user_tool"]][1] += 1
    res["A0_first_by_user_tool"] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(cl.items())}
    # cluster bootstrap over attacker instruction (InjecAgent is 62 instructions x 17 contexts)
    import random
    sys.path.insert(0, str(ROOT / "src"))
    from adapti_guard.evaluation.external import injecagent as ia

    cases = {c["case_id"]: c for c in ia.load_cases()}
    ids = [i for i in by["A0"] if i in by["SPOT_TOOL"] and not by["A0"][i]["error"] and not by["SPOT_TOOL"][i]["error"]]
    groups = collections.defaultdict(list)
    for i in ids:
        groups[cases[i]["Attacker Instruction"]].append(int(bool(by["SPOT_TOOL"][i]["first_attacker_tool"])) - int(bool(by["A0"][i]["first_attacker_tool"])))
    keys, rng, bs = list(groups), random.Random(7), []
    for _ in range(4000):
        samp = [groups[rng.choice(keys)] for _ in keys]
        bs.append(sum(sum(g) for g in samp) / sum(len(g) for g in samp))
    bs.sort()
    res["cluster_bootstrap_spot_minus_a0"] = {"clusters": len(keys), "mean_diff": round(sum(sum(g) for g in groups.values()) / len(ids), 3),
                                              "ci95": [round(bs[100], 3), round(bs[3899], 3)], "resamples": 4000, "seed": 7}
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "A0_first_by_user_tool"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
