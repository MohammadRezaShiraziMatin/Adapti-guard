"""Paired analysis: defended arms vs the A0 screening on the independent attack set. API=0.

Pairs are (scenario, instance, model) present in both runs. Endpoint: exec_executed.
Reports per-arm rates, paired b10/b01 with exact McNemar (descriptive, clustered data),
and per family x model tables. Episodes not COMPLETE are dropped from pairing and counted.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def mcnemar_exact(b10: int, b01: int) -> float:
    n = b10 + b01
    if n == 0:
        return 1.0
    k = min(b10, b01)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def _load(d: Path) -> list[dict]:
    return [json.loads(x) for x in (d / "episodes.jsonl").read_text().splitlines() if x.strip()]


def analyze(a0_rows: list[dict], def_rows: list[dict]) -> dict:
    def key(r):
        return (r["scenario_id"], r["instance_index"], r["family"])

    def ex(r):
        return (r["C2"] or {}).get("exec_executed") is True

    a0 = {key(r): r for r in a0_rows if r["condition"] == "A0" and r["status"] == "COMPLETE"}
    out: dict = {"n_a0": len(a0), "arms": {}}
    for arm in sorted({r["condition"] for r in def_rows}):
        rows = [r for r in def_rows if r["condition"] == arm]
        comp = [r for r in rows if r["status"] == "COMPLETE"]
        pairs = [(a0[key(r)], r) for r in comp if key(r) in a0]
        b10 = sum(ex(x) and not ex(y) for x, y in pairs)
        b01 = sum(ex(y) and not ex(x) for x, y in pairs)
        cell = defaultdict(lambda: [0, 0, 0])  # scenario,model -> [A0 exec, arm exec, n]
        for x, y in pairs:
            c = cell[(y["scenario_id"], y["family"])]
            c[0] += ex(x)
            c[1] += ex(y)
            c[2] += 1
        blocked = sum(any(b.get("blocked") for b in (r.get("b3_log") or [])) for r in comp)
        out["arms"][arm] = {
            "episodes": len(rows), "complete": len(comp), "pairs": len(pairs),
            "a0_executed": sum(ex(x) for x, _ in pairs), "arm_executed": sum(ex(y) for _, y in pairs),
            "b10_arm_wins": b10, "b01_a0_wins": b01, "mcnemar_exact_p": mcnemar_exact(b10, b01),
            "episodes_with_block": blocked,
            "cells": {f"{s}|{m}": v for (s, m), v in sorted(cell.items())},
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a0_dir", type=Path)
    ap.add_argument("defended_dir", type=Path)
    a = ap.parse_args()
    res = analyze(_load(a.a0_dir), _load(a.defended_dir))
    (a.defended_dir / "paired_vs_a0_analysis.json").write_text(json.dumps(res, indent=2) + "\n")
    for arm, v in res["arms"].items():
        print(f"{arm}: pairs={v['pairs']} A0 executed={v['a0_executed']} arm executed={v['arm_executed']} "
              f"b10={v['b10_arm_wins']} b01={v['b01_a0_wins']} p={v['mcnemar_exact_p']:.3g} blocks={v['episodes_with_block']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
