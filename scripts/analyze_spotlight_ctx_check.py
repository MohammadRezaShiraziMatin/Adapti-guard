"""Offline analysis of the SPOTLIGHT_CTX live check vs stored MT1 r1 arms. API=0.

Compares, on the same attack records (seed 42 sample), for each target model present:
  B0 (MT1 r1)  B0_REP (fresh replicate)  SPOTLIGHT (r1, prompt wrapped)  SPOTLIGHT_CTX (new, context wrapped)
Endpoints: judge verdict and canary-token emission. Channel split: direct (canary in user prompt),
indirect (canary in context), encoded/other. Pairs by record id. Missing records are reported, not imputed.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R1 = ROOT / "experiments/real_llm_eval/MT1/r1"
NEW = ROOT / "experiments/real_llm_eval/MT1/spotlight_ctx_check_20260930"
DS = ROOT / "datasets/frozen/layer_a_v2/dataset.jsonl"
OUT = ROOT / "docs/research/artifacts/spotlight_ctx_check_20260930.json"


def load(p: Path) -> dict:
    if not p.is_file():
        return {}
    return {json.loads(x)["id"]: json.loads(x) for x in p.read_text().splitlines() if x.strip()}


def mcnemar_exact(b10: int, b01: int) -> float:
    n = b10 + b01
    if n == 0:
        return 1.0
    k = min(b10, b01)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def main() -> None:
    ds = {json.loads(x)["id"]: json.loads(x) for x in DS.read_text().splitlines() if x.strip()}
    canary = {i: r["metadata"].get("canary") for i, r in ds.items() if r["label"] == "attack" and r["metadata"].get("canary")}

    def channel(i: str) -> str:
        r, c = ds[i], canary[i]
        return "direct" if c in (r.get("prompt") or "") else "indirect" if c in (r.get("context") or "") else "encoded"

    judge = lambda r, i: r["attack_succeeded"] is True
    can = lambda r, i: canary[i] in (r.get("target_response") or "")
    arms = {
        "B0_r1": lambda m: load(R1 / m / "B0" / "B0_predictions.jsonl"),
        "B0_rep": lambda m: load(NEW / m / "B0_REP" / "B0_predictions.jsonl"),
        "SPOT_prompt_r1": lambda m: load(R1 / m / "SPOTLIGHT" / "SPOTLIGHT_predictions.jsonl"),
        "SPOT_ctx": lambda m: load(NEW / m / "SPOTLIGHT_CTX" / "SPOTLIGHT_CTX_predictions.jsonl"),
    }
    models = sorted(p.name for p in NEW.iterdir() if p.is_dir())
    res: dict = {"models": models, "cells": {}, "missing": {}}
    tab = defaultdict(lambda: [0, 0, 0, 0])  # (arm,channel)->[n, judge, canary, err]
    paired = defaultdict(lambda: {"judge": [0, 0, 0], "canary": [0, 0, 0]})  # (arm_vs_B0r1,channel) -> b10,b01,n
    for m in models:
        d = {a: f(m) for a, f in arms.items()}
        for a, rows in d.items():
            ids = [i for i, r in rows.items() if r["label"] == "attack" and i in canary]
            res["missing"][f"{m}|{a}"] = 20 - len([i for i in ids]) if a != "B0_rep" else max(0, 19 - len(ids))
            for i in ids:
                r = rows[i]
                err = "TARGET_ERROR" in (r.get("target_response") or "") or r.get("judge_failure")
                ch = channel(i)
                for c in (ch, "ALL"):
                    t = tab[(a, c)]
                    t[0] += 1
                    t[1] += judge(r, i)
                    t[2] += can(r, i)
                    t[3] += bool(err)
        base = d["B0_r1"]
        for a in ("B0_rep", "SPOT_prompt_r1", "SPOT_ctx"):
            for i in set(base) & set(d[a]):
                if i not in canary or base[i]["label"] != "attack":
                    continue
                ch = channel(i)
                for c in (ch, "ALL"):
                    for rule, fn in (("judge", judge), ("canary", can)):
                        p = paired[(a, c)][rule]
                        b, x = fn(base[i], i), fn(d[a][i], i)
                        p[0] += b and not x
                        p[1] += x and not b
                        p[2] += 1
    res["cells"] = {f"{a}|{c}": {"n": v[0], "judge": v[1], "canary": v[2], "errors": v[3]} for (a, c), v in sorted(tab.items())}
    res["paired_vs_B0_r1"] = {f"{a}|{c}": {rule: {"b10": v[0], "b01": v[1], "n": v[2], "p": mcnemar_exact(v[0], v[1])} for rule, v in d_.items()}
                              for (a, c), d_ in sorted(paired.items())}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print("models:", models)
    for c in ("direct", "indirect", "encoded", "ALL"):
        print(f"\n[{c}]")
        for a in arms:
            v = tab.get((a, c))
            if v:
                print(f"  {a:15} n={v[0]:3} judge={v[1]:3} canary={v[2]:3} errors={v[3]}")
        for a in ("B0_rep", "SPOT_prompt_r1", "SPOT_ctx"):
            p = paired.get((a, c))
            if p:
                print(f"  vs B0_r1 {a:15} judge b10/b01={p['judge'][0]}/{p['judge'][1]} (n={p['judge'][2]})  canary {p['canary'][0]}/{p['canary'][1]}")


if __name__ == "__main__":
    main()
