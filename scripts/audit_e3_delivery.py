"""E3 delivery audit: non-delivered episodes and delivery-restricted sensitivity of the paired comparison. API=0.

Reads only the committed E3 traces (screen = A0, defended = B3 and CORE) and writes a derived artifact; no trace is modified.

Primary analysis (analyze_independent_defended.py, unchanged): pairs on (scenario, instance, family) with run status
COMPLETE on both sides, endpoint exec_executed. The harness delivery label (C2_state) is NOT used for pairing, so an
episode labeled INVALID_NOT_DELIVERED stays in the denominator and counts as executed only if exec_executed is true.
The estimand is therefore "an assigned attack instance leads to an executed attacker call", not "given that the payload
reached the model". The restricted rows below show how much that choice matters; they are sensitivity analyses.
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "experiments/harness_v2"
SCREEN = H / "HARNESS_V2_INDEPENDENT_SCREEN_20260930/episodes.jsonl"
DEFENDED = H / "HARNESS_V2_INDEPENDENT_DEFENDED_20260930/episodes.jsonl"
OUT = ROOT / "docs/research/artifacts/e3_delivery_audit_20261003.json"


def load(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def key(r: dict) -> tuple:
    return (r["scenario_id"], r["instance_index"], r["family"])


def c2(r: dict) -> dict:
    return r["C2"] or {}


def ex(r: dict) -> bool:
    return c2(r).get("exec_executed") is True


def nd(r: dict) -> bool:
    return c2(r).get("C2_state") == "INVALID_NOT_DELIVERED"


def detail(r: dict) -> str:
    return c2(r).get("delivery_detail") or ""


def carrier_never_ran(r: dict) -> bool:
    return detail(r).endswith("_never_executed")


def mcnemar_exact(b10: int, b01: int) -> float:
    n = b10 + b01
    if n == 0:
        return 1.0
    k = min(b10, b01)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def stats(pairs: list[tuple[dict, dict]]) -> dict:
    b10 = sum(ex(x) and not ex(y) for x, y in pairs)
    b01 = sum(ex(y) and not ex(x) for x, y in pairs)
    return {"pairs": len(pairs), "a0_executed": sum(ex(x) for x, _ in pairs), "arm_executed": sum(ex(y) for _, y in pairs),
            "b10_a0_only": b10, "b01_arm_only": b01, "mcnemar_exact_p": round(mcnemar_exact(b10, b01), 4)}


def cluster_bootstrap(pairs: list[tuple[dict, dict]], b: int = 5000, seed: int = 20260930) -> dict:
    """Paired difference (defended - A0) with whole (scenario, instance) clusters resampled; each cluster holds that instance's three model pairs."""
    cl: dict = {}
    for x, y in pairs:
        cl.setdefault((x["scenario_id"], x["instance_index"]), []).append(int(ex(y)) - int(ex(x)))
    keys, rng, est = list(cl), random.Random(seed), []
    for _ in range(b):
        s = [d for k in (rng.choice(keys) for _ in keys) for d in cl[k]]
        est.append(sum(s) / len(s))
    est.sort()
    allv = [d for v in cl.values() for d in v]
    return {"clusters": len(keys), "pairs": len(allv), "diff": round(sum(allv) / len(allv), 4),
            "ci95": [round(est[int(0.025 * b)], 4), round(est[int(0.975 * b) - 1], 4)], "resamples": b, "seed": seed}


def reasons(rows: list[dict]) -> dict:
    return dict(sorted(Counter(f"{detail(r)}|exec_executed={ex(r)}" for r in rows if nd(r)).items()))


def build() -> dict:
    screen, defended = load(SCREEN), load(DEFENDED)
    a0 = {key(r): r for r in screen if r["condition"] == "A0" and r["status"] == "COMPLETE"}
    out: dict = {
        "source": "experiments/harness_v2/HARNESS_V2_INDEPENDENT_{SCREEN,DEFENDED}_20260930/episodes.jsonl",
        "a0": {"episodes": len(screen), "non_delivered": sum(nd(r) for r in screen),
               "carrier_tool_never_ran": sum(carrier_never_ran(r) for r in screen), "reasons": reasons(screen)},
        "arms": {},
    }
    for arm in ("B3", "CORE"):
        rows = [r for r in defended if r["condition"] == arm]
        comp = [r for r in rows if r["status"] == "COMPLETE"]
        pairs = [(a0[key(r)], r) for r in comp if key(r) in a0]
        extra = [(a0[key(r)], r) for r in rows if r["status"] != "COMPLETE" and key(r) in a0]
        out["arms"][arm] = {
            "episodes": len(rows), "complete": len(comp),
            "non_delivered_complete": sum(nd(r) for r in comp),
            "carrier_tool_never_ran_complete": sum(carrier_never_ran(r) for r in comp),
            "reasons_complete": reasons(comp),
            "published": stats(pairs),
            "instance_cluster_bootstrap": cluster_bootstrap(pairs),
            "drop_pairs_where_carrier_tool_never_ran": stats([(x, y) for x, y in pairs if not carrier_never_ran(x) and not carrier_never_ran(y)]),
            "drop_pairs_with_any_non_delivered": stats([(x, y) for x, y in pairs if not nd(x) and not nd(y)]),
            "published_plus_non_complete_status": stats(pairs + extra),
            "non_complete_status_rows_added": len(extra),
            "drop_a0_truncated_episode": stats([(x, y) for x, y in pairs if detail(x) != "truncated_call_2"]),
        }
    return out


def main() -> int:
    res = build()
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    a = res["a0"]
    print(f"A0: {a['non_delivered']}/{a['episodes']} non-delivered ({a['carrier_tool_never_ran']} carrier tool never ran)")
    for arm, v in res["arms"].items():
        for k in ("published", "drop_pairs_where_carrier_tool_never_ran", "drop_pairs_with_any_non_delivered", "published_plus_non_complete_status", "drop_a0_truncated_episode"):
            s = v[k]
            print(f"{arm} {k}: pairs={s['pairs']} A0={s['a0_executed']} arm={s['arm_executed']} b10/b01={s['b10_a0_only']}/{s['b01_arm_only']} p={s['mcnemar_exact_p']}")
        c = v["instance_cluster_bootstrap"]
        print(f"{arm} instance-cluster bootstrap: clusters={c['clusters']} diff={c['diff']:+.4f} CI={c['ci95']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
