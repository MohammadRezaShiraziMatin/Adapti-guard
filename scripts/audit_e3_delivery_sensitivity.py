"""Offline delivery-restriction sensitivity for E3 (reads committed traces only; API=0; changes no evidence).

The primary E3 analysis pairs every assigned instance (all-assigned-episodes estimand). Here the same pairs are
re-counted after dropping episodes whose injection marker did not reach the model (delivery_detail not
'post_injection_*'), to show whether the null result depends on that choice.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "experiments/harness_v2"
OUT = ROOT / "docs/research/artifacts/e3_delivery_sensitivity_20261003.json"


def load(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def key(r: dict) -> tuple:
    return (r["scenario_id"], r["instance_index"], r["model_id"])


def delivered(r: dict) -> bool:
    return str(r["C2"]["delivery_detail"]).startswith("post_injection")


def executed(r: dict) -> bool:
    return bool(r["C2"].get("exec_executed"))


def main() -> None:
    scr = load(H / "HARNESS_V2_INDEPENDENT_SCREEN_20260930/episodes.jsonl")
    dfd = load(H / "HARNESS_V2_INDEPENDENT_DEFENDED_20260930/episodes.jsonl")
    a0 = {key(r): r for r in scr if r["condition"] == "A0"}
    out: dict = {
        "a0_not_delivered": sum(not delivered(r) for r in a0.values()),
        "a0_not_delivered_but_scored_executed": sum((not delivered(r)) and executed(r) for r in a0.values()),
        "a0_delivery_detail": dict(Counter(r["C2"]["delivery_detail"] for r in a0.values())),
        "arms": {},
    }
    rules = {
        "all_assigned": lambda a, d: True,
        "a0_delivered": lambda a, d: delivered(a),
        "both_delivered": lambda a, d: delivered(a) and delivered(d),
    }
    for arm in ("B3", "CORE"):
        d_all = {key(r): r for r in dfd if r["condition"] == arm and r["status"] == "COMPLETE"}
        out["arms"][arm] = {}
        for name, f in rules.items():
            ks = [k for k in a0 if k in d_all and f(a0[k], d_all[k])]
            a = [executed(a0[k]) for k in ks]
            d = [executed(d_all[k]) for k in ks]
            out["arms"][arm][name] = {
                "pairs": len(ks), "a0_executed": sum(a), "arm_executed": sum(d),
                "b10_a0_only": sum(x and not y for x, y in zip(a, d)),
                "b01_arm_only": sum(y and not x for x, y in zip(a, d)),
            }
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
