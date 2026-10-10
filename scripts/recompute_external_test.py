"""Recompute the external-test (§6.3) and calibration (§6.4) numbers from committed per-episode records.

Offline: reads only experiments/external/**. Nothing is called over the network.
Not recomputed here: the cluster-bootstrap intervals of §6.3. Their producer is not in the tree, so they are read
from experiments/external/injecagent_registered_20261001/ANALYSIS.json and flagged as artifact-only in the ledger.
The Hard-set hit field is `goal_met` in phase2_calibration_20261001/calibration.json; the file does not state its endpoint.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = "experiments/external/injecagent_registered_20261001"
CAL = "experiments/external/injecagent_panel_calib_20261001"
P2 = "experiments/external/phase2_calibration_20261001/calibration.json"

REG_FILE = {"meta-llama/llama-4-maverick": "meta-llama__llama-4-maverick.json", "qwen/qwen3.8-flash": "qwen__qwen3.8-flash.json"}
CAL_FILE = {
    "meta-llama/llama-4-maverick": "meta-llama__llama-4-maverick.json",
    "deepseek/deepseek-v4.1-flash": "deepseek__deepseek-v4.1-flash.json",
    "openai/gpt-5.6-sol": "openai__gpt-5.6-sol.json",
    "qwen/qwen3.8-flash": "qwen__qwen3.8-flash.json",
    "z-ai/glm-4.7": "z-ai__glm-4.7.json",
}
REG_LABEL = {"meta-llama/llama-4-maverick": "llama-4-maverick", "qwen/qwen3.8-flash": "qwen3.8-flash"}


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def cp_upper_zero(n: int) -> float:
    """Two-sided 95% Clopper-Pearson upper bound for 0 events in n trials."""
    return 1 - 0.025 ** (1 / n)


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def registered_arms(model: str) -> dict[str, dict[str, dict]]:
    arms: dict[str, dict[str, dict]] = {}
    for e in _load(f"{REG}/{REG_FILE[model]}")["episodes"]:
        arms.setdefault(e["arm"], {})[e["case_id"]] = e
    return arms


def paired_mean(a: dict, b: dict) -> float:
    """Mean of (b - a) over the case ids of a, on first_attacker_tool."""
    d = [int(b[c]["first_attacker_tool"]) - int(a[c]["first_attacker_tool"]) for c in a]
    return sum(d) / len(d)


def calib_injecagent(model: str, arm: str) -> tuple[int, int]:
    """(hits, scored) over the dh and ds kinds of the panel calibration file."""
    eps = _load(f"{CAL}/{CAL_FILE[model]}")["episodes"]
    rows = [e for e in eps if e["arm"] == arm and e["kind"] in ("dh", "ds") and e["http"] == 200]
    return sum(1 for e in rows if e["first_attacker_tool"]), len(rows)


def calib_hard(model: str) -> tuple[int, int]:
    """(hits, scored) for the human-written Hard set, undefended arm, from calibration.json."""
    res = next(r for r in _load(P2)["results"] if r["model"] == model)
    rows = [e for e in res["episodes"] if e["origin"] == "human" and e["arm"] == "A0" and e["http"] == 200]
    return sum(1 for e in rows if e.get("goal_met") is True), len(rows)


def ledger_rows() -> list[tuple[str, str, str]]:
    """(quantity, string as it appears in the manuscript, source as "file · key k")."""
    out: list[tuple[str, str, str]] = []
    analysis = f"{REG}/ANALYSIS.json"
    art = _load(analysis)
    for model in REG_FILE:
        arms = registered_arms(model)
        name = REG_LABEL[model]
        src = f"{REG}/{REG_FILE[model]}"
        for arm, lab in (("A0", "A0"), ("A0_REP", "A0 replicate"), ("SPOT_TOOL", "SPOT_TOOL"), ("NOINJ", "NOINJ")):
            rows = arms[arm]
            k = sum(1 for e in rows.values() if e["first_attacker_tool"])
            out.append((f"§6.3 {name} {lab} hits", f"{k}/{len(rows)}", f"{src} · key {arm}.hits/n"))
        lo, hi = wilson(sum(1 for e in arms["A0"].values() if e["first_attacker_tool"]), len(arms["A0"]))
        out.append((f"§6.3 {name} A0 Wilson 95%", f"{100 * lo:.1f} to {100 * hi:.1f}", f"{src} · key A0.wilson95"))
        out.append((f"§6.3 {name} SPOT_TOOL minus A0 mean", f"{paired_mean(arms['A0'], arms['SPOT_TOOL']):.3f}", f"{src} · key SPOT_TOOL-A0.mean"))
        out.append((f"§6.3 {name} replicate minus A0 mean", f"{paired_mean(arms['A0'], arms['A0_REP']):.3f}", f"{src} · key A0_REP-A0.mean"))
        a = art[model]
        s = a["SPOT_TOOL_minus_A0"]
        out.append((f"§6.3 {name} SPOT_TOOL minus A0 cluster 95% CI", f"[{s['ci95'][0]:.3f}, {s['ci95'][1]:.3f}]", f"{analysis} · key {model}.SPOT_TOOL_minus_A0.ci95"))
        out.append((f"§6.3 {name} SPOT_TOOL minus A0 Bonferroni α/4 CI", f"[{s['ci98.75_holm'][0]:.3f}, {s['ci98.75_holm'][1]:.3f}]", f"{analysis} · key {model}.SPOT_TOOL_minus_A0.ci98.75_holm"))
        r = a["A0_REP_minus_A0"]
        out.append((f"§6.3 {name} replicate minus A0 cluster 95% CI", f"[{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}]", f"{analysis} · key {model}.A0_REP_minus_A0.ci95"))

    for model in CAL_FILE:
        name = REG_LABEL.get(model, model)
        k, n = calib_injecagent(model, "A0")
        out.append((f"§6.4 {name} InjecAgent A0", f"{k}/{n}", f"{CAL}/{CAL_FILE[model]} · key InjecAgent.A0.hits/scored"))
        k, n = calib_injecagent(model, "NOINJ")
        out.append((f"§6.4 {name} InjecAgent NOINJ", f"{k}/{n}", f"{CAL}/{CAL_FILE[model]} · key InjecAgent.NOINJ.hits/scored"))
        k, n = calib_hard(model)
        out.append((f"§6.4 {name} Hard set A0", f"{k}/{n}", f"{P2} · key {model}.Hard.A0.hits/scored"))
    out.append(("§6.4 Clopper-Pearson upper bound, 0 of 40", f"{100 * cp_upper_zero(40):.1f}%", f"{CAL}/{CAL_FILE['openai/gpt-5.6-sol']} · key InjecAgent.A0.scored"))
    out.append(("§6.4 Clopper-Pearson upper bound, 0 of 68", f"{100 * cp_upper_zero(68):.1f}%", f"{P2} · key deepseek/deepseek-v4.1-flash.Hard.A0.scored"))
    return out


def main() -> None:
    for q, v, s in ledger_rows():
        print(f"{q:55s} {v:22s} {s}")


if __name__ == "__main__":
    main()
