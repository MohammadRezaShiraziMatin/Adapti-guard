"""Build NUMBERS_LEDGER.md: every key number quoted in the manuscript, recomputed from committed artifacts.

The accompanying test asserts that each ledger string also appears in MANUSCRIPT_DRAFT_v1.md, so prose and
data cannot drift apart silently. API=0.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from recompute_external_test import ledger_rows as external_test_rows

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs/research/artifacts"
FIG = ROOT / "docs/paper/negative_result/figures"
OUT = ROOT / "docs/paper/negative_result/NUMBERS_LEDGER.md"


def entries() -> list[tuple[str, str, str]]:
    """(label, string that must appear in the manuscript, source)."""
    e: list[tuple[str, str, str]] = []
    t = json.loads((ART / "tracks_ab_deterministic_rescoring_20260930.json").read_text())
    a, b = t["A_VNEXT"], t["B_PHASE1"]
    src = "artifacts/tracks_ab_deterministic_rescoring_20260930.json"
    e += [
        ("Track A B0 judge", f"{a['arms']['B0']['judge_success']}/61", src),
        ("Track A B0 executed", f"{a['arms']['B0']['deterministic_success']}/61", src),
        ("Track A VNEXT judge", f"{a['arms']['VNEXT-ADAPT']['judge_success']}/61", src),
        ("Track A VNEXT executed", f"{a['arms']['VNEXT-ADAPT']['deterministic_success']}/61", src),
        ("Track B CORE judge", f"{b['arms']['PHASE1-CORE']['judge_success']}/61", src),
        ("Track B CORE executed", f"{b['arms']['PHASE1-CORE']['deterministic_success']}/61", src),
        ("Track B executed b10", f"{b['paired_deterministic']['b10_treatment_wins']}/0", src),
        ("Track B executed delta", f"{b['paired_deterministic']['delta_hat']:.4f}", src),
        ("Track B judge delta", f"{b['paired_judge']['delta_hat']:.4f}", src),
        ("Track B CORE utility executed", f"{b['arms']['PHASE1-CORE']['benign_judge_utility'] - b['arms']['PHASE1-CORE']['benign_tool_denied_but_judged_useful']}/61", src),
        ("Track B CORE tool-required executed", f"{b['arms']['PHASE1-CORE']['benign_tool_executed']}/40", src),
    ]
    rows = list(csv.DictReader((FIG / "fig1_scoring_flip.csv").open()))
    f1 = {(r["rule"], r["arm"]): f"{r['successes']}/{r['n']}" for r in rows}
    s = "figures/fig1_scoring_flip.csv"
    e += [("E2 R1 TOOLDENY proposed", f1[("R1", "TOOLDENY")], s), ("E2 R2 TOOLDENY executed", f1[("R2", "TOOLDENY")], s),
          ("E2 R2 A0", f1[("R2", "A0")], s), ("E2 R2 CORE", f1[("R2", "CORE")], s), ("E2 R3 CORE", f1[("R3", "CORE")], s),
          ("E2 R4 A0", f1[("R4", "A0")], s), ("E2 R4 B3", f1[("R4", "B3")], s)]
    p = json.loads((ROOT / "experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json").read_text())["arms"]
    s = "HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json"
    for arm in ("B3", "CORE"):
        v = p[arm]
        e.append((f"E3 {arm} pairs", f"{v['pairs']} pairs", s))
        e.append((f"E3 {arm} b10/b01", f"{v['b10_arm_wins']}/{v['b01_a0_wins']}", s))
    da = json.loads((ART / "e3_delivery_audit_20261003.json").read_text())
    s = "artifacts/e3_delivery_audit_20261003.json"
    e += [("E3 A0 non-delivered episodes", f"{da['a0']['non_delivered']} of the 168 undefended episodes", s),
          ("E3 A0 carrier tool never ran", f"{da['a0']['carrier_tool_never_ran']} of them", s)]
    for arm in ("B3", "CORE"):
        v = da["arms"][arm]["drop_pairs_where_carrier_tool_never_ran"]
        e.append((f"E3 {arm} delivered-only pairs", f"{v['pairs']} {arm} pairs", s))
        e.append((f"E3 {arm} delivered-only b10/b01", f"b10/b01 = {v['b10_a0_only']}/{v['b01_arm_only']}", s))
    for arm in ("B3", "CORE"):
        lo, hi = da["arms"][arm]["instance_cluster_bootstrap"]["ci95"]
        e.append((f"E3 {arm} instance-cluster CI", f"{lo:+.3f} to {hi:+.3f}".replace("-", "−"), s))
    fig2 = list(csv.DictReader((FIG / "fig2_susceptibility.csv").open()))
    pooled_model = {r["model"]: f"{r['executed']}/{r['n']}" for r in fig2 if r["family"] == "ALL_FAMILIES"}
    e += [(f"E3 susceptibility {m}", pooled_model[m], "figures/fig2_susceptibility.csv") for m in ("deepseek", "qwen3", "gemma")]
    mt = json.loads((ART / "mt1_second_dataset_rules_20260930.json").read_text())
    sp = mt["paired"]["SPOTLIGHT"]["pooled"]
    e += [("MT1 SPOTLIGHT judge b10/b01", f"{sp['judge']['b10']}/{sp['judge']['b01']}", "artifacts/mt1_second_dataset_rules_20260930.json")]
    sc = json.loads((ART / "spotlight_ctx_check_20260930.json").read_text())["cells"]
    s = "artifacts/spotlight_ctx_check_20260930.json"
    e += [("SPOT_ctx indirect judge", f"{sc['SPOT_ctx|indirect']['judge']} of {sc['SPOT_ctx|indirect']['n']}", s),
          ("SPOT_ctx direct judge", f"{sc['SPOT_ctx|direct']['judge']} to {sc['SPOT_ctx|direct']['judge']}", s),
          ("SPOT_prompt direct judge", f"{sc['B0_r1|direct']['judge']} to {sc['SPOT_prompt_r1|direct']['judge']}", s)]
    for slug in ("qwen-2.5-7b", "llama-3.1-8b", "llama-3.3-70b", "mistral-small-3.2-24b"):
        suffix = "" if slug == "qwen-2.5-7b" else f"_{slug}"
        f = f"artifacts/injecagent_live_analysis_20260930{suffix}.json"
        ia = json.loads((ROOT / "docs/research" / f).read_text())
        a0 = ia["arms"]["A0|first_attacker_tool|ALL"]
        pr = ia["paired_vs_A0"]["SPOT_TOOL|first_attacker_tool"]
        e += [(f"InjecAgent {slug} A0", f"{a0['k']}/{a0['n']}", f),
              (f"InjecAgent {slug} SPOT A0-only/SPOT-only", f"{pr['b10_A0_only']}/{pr['b01_arm_only']}", f),
              (f"InjecAgent {slug} cluster CI", "[{:.3f}, {:.3f}]".format(*ia["cluster_bootstrap_spot_minus_a0"]["ci95"]), f)]
    e += external_test_rows()
    return e


def main() -> None:
    es = entries()
    lines = ["# Number ledger", "", "Each row is recomputed from committed artifacts by `scripts/build_number_ledger.py`; "
             "`tests/test_manuscript_number_ledger.py` checks that the string appears in `MANUSCRIPT_DRAFT_v1.md`.", "",
             "| quantity | string in manuscript | source |", "|---|---|---|"]
    lines += [f"| {a} | `{b}` | `{c}` |" for a, b, c in es]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.name} ({len(es)} entries)")


if __name__ == "__main__":
    main()
