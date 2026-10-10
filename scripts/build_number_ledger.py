"""Build NUMBERS_LEDGER.md: every key number quoted in the manuscript, recomputed from committed artifacts.

Scope: only the evidence base of docs/CASE_STUDY_SCOPE.md (E2, E3, the InjecAgent run of 2026-09-30 on llama-3.3-70b,
the 2026-10-01 external test and calibration). The accompanying test asserts that each ledger string also appears in
MANUSCRIPT_DRAFT_v1.md, so prose and data cannot drift apart silently. API=0.
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
    """(label, string that must appear in the manuscript, source as 'file · key k')."""
    e: list[tuple[str, str, str]] = []

    # E2 (2026-09-30 exploratory harness): every tabulated cell of Fig. 1
    s = "figures/fig1_scoring_flip.csv"
    for r in csv.DictReader((FIG / "fig1_scoring_flip.csv").open()):
        e.append((f"E2 {r['rule']} {r['arm']}", f"{r['successes']}/{r['n']}", f"{s} · key {r['rule']}.{r['arm']}.successes/n"))

    # E2 benign utility and per-scenario execution (exploratory analysis)
    ex = json.loads((ROOT / "experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json").read_text())
    s = "experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/exploratory_analysis.json"
    for arm in ("A0", "B3", "CORE", "TOOLDENY"):
        b = ex["benign"][arm]
        e.append((f"E2 benign {arm}", f"{b['utility_k']}/{b['n']}", f"{s} · key benign.{arm}.utility_k/n"))
    e.append(("E2 direct-override CORE executed", ex["per_scenario_exec_executed"]["direct_user_override_v1"]["CORE"], f"{s} · key per_scenario_exec_executed.direct_user_override_v1.CORE"))
    e.append(("E2 create-record A0 executed", ex["per_scenario_exec_executed"]["create_record_exfil_v1"]["A0"], f"{s} · key per_scenario_exec_executed.create_record_exfil_v1.A0"))
    e.append(("E2 B3 paired b10/b01", f"{ex['paired_vs_A0']['B3']['b10_arm_wins']}/{ex['paired_vs_A0']['B3']['b01_A0_wins']}", f"{s} · key paired_vs_A0.B3.b10_arm_wins/b01_A0_wins"))

    # E3 (2026-09-30 independent set): paired counts, noise floor, delivery audit, per-model susceptibility
    p = json.loads((ROOT / "experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json").read_text())["arms"]
    s = "experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json"
    for arm in ("B3", "CORE"):
        v = p[arm]
        e.append((f"E3 {arm} undefended executed", f"{v['a0_executed']}/{v['pairs']}", f"{s} · key arms.{arm}.a0_executed/pairs"))
        e.append((f"E3 {arm} defended executed", f"{v['arm_executed']}/{v['pairs']}", f"{s} · key arms.{arm}.arm_executed/pairs"))
        e.append((f"E3 {arm} b10/b01", f"{v['b10_arm_wins']}/{v['b01_a0_wins']}", f"{s} · key arms.{arm}.b10_arm_wins/b01_a0_wins"))
    e.append(("E3 CORE blocked episodes", f"{p['CORE']['episodes_with_block']}/{p['CORE']['episodes']}", f"{s} · key arms.CORE.episodes_with_block/episodes"))

    da = json.loads((ART / "e3_delivery_audit_20261003.json").read_text())
    s = "docs/research/artifacts/e3_delivery_audit_20261003.json"
    e += [("E3 A0 non-delivered episodes", f"{da['a0']['non_delivered']} of the 168 undefended episodes", f"{s} · key a0.non_delivered"),
          ("E3 A0 carrier tool never ran", f"{da['a0']['carrier_tool_never_ran']} of them", f"{s} · key a0.carrier_tool_never_ran")]
    for arm in ("B3", "CORE"):
        v = da["arms"][arm]["drop_pairs_where_carrier_tool_never_ran"]
        e.append((f"E3 {arm} delivered-only pairs", f"{v['pairs']} {arm} pairs", f"{s} · key arms.{arm}.drop_pairs_where_carrier_tool_never_ran.pairs"))
        e.append((f"E3 {arm} delivered-only b10/b01", f"b10/b01 = {v['b10_a0_only']}/{v['b01_arm_only']}", f"{s} · key arms.{arm}.drop_pairs_where_carrier_tool_never_ran.b10_a0_only/b01_arm_only"))
    for arm in ("B3", "CORE"):
        lo, hi = da["arms"][arm]["instance_cluster_bootstrap"]["ci95"]
        e.append((f"E3 {arm} instance-cluster CI", f"{lo:+.3f} to {hi:+.3f}".replace("-", "−"), f"{s} · key arms.{arm}.instance_cluster_bootstrap.ci95"))
    fig2 = list(csv.DictReader((FIG / "fig2_susceptibility.csv").open()))
    pooled_model = {r["model"]: f"{r['executed']}/{r['n']}" for r in fig2 if r["family"] == "ALL_FAMILIES"}
    e += [(f"E3 susceptibility {m}", pooled_model[m], "figures/fig2_susceptibility.csv · key ALL_FAMILIES." + m) for m in ("deepseek", "qwen3", "gemma")]

    # InjecAgent 2026-09-30, llama-3.3-70b only (Appendix A)
    ia = json.loads((ROOT / "docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json").read_text())
    f = "docs/research/artifacts/injecagent_live_analysis_20260930_llama-3.3-70b.json"
    e += [
        ("InjecAgent llama-3.3-70b A0", f"{ia['arms']['A0|first_attacker_tool|ALL']['k']}/{ia['arms']['A0|first_attacker_tool|ALL']['n']}", f"{f} · key arms.A0|first_attacker_tool|ALL"),
        ("InjecAgent llama-3.3-70b A0 replicate", f"{ia['arms']['A0_REP|first_attacker_tool|ALL']['k']}/{ia['arms']['A0_REP|first_attacker_tool|ALL']['n']}", f"{f} · key arms.A0_REP|first_attacker_tool|ALL"),
        ("InjecAgent llama-3.3-70b NOINJ", f"{ia['arms']['NOINJ|first_attacker_tool|ALL']['k']}/{ia['arms']['NOINJ|first_attacker_tool|ALL']['n']}", f"{f} · key arms.NOINJ|first_attacker_tool|ALL"),
        ("InjecAgent llama-3.3-70b SPOT", f"{ia['arms']['SPOT_TOOL|first_attacker_tool|ALL']['k']}/{ia['arms']['SPOT_TOOL|first_attacker_tool|ALL']['n']}", f"{f} · key arms.SPOT_TOOL|first_attacker_tool|ALL"),
        ("InjecAgent llama-3.3-70b SPOT minus A0 mean", f"{ia['cluster_bootstrap_spot_minus_a0']['mean_diff']:+.3f}", f"{f} · key cluster_bootstrap_spot_minus_a0.mean_diff"),
        ("InjecAgent llama-3.3-70b A0-only/SPOT-only", f"{ia['paired_vs_A0']['SPOT_TOOL|first_attacker_tool']['b10_A0_only']}/{ia['paired_vs_A0']['SPOT_TOOL|first_attacker_tool']['b01_arm_only']}", f"{f} · key paired_vs_A0.SPOT_TOOL|first_attacker_tool"),
        ("InjecAgent llama-3.3-70b cluster CI", "[{:.3f}, {:.3f}]".format(*ia["cluster_bootstrap_spot_minus_a0"]["ci95"]), f"{f} · key cluster_bootstrap_spot_minus_a0.ci95"),
    ]

    # 2026-10-01 external test and calibration (§6.3, §6.4), recomputed from raw records
    e += external_test_rows()
    return e


def main() -> None:
    es = entries()
    lines = ["# Number ledger", "", "Each row is recomputed from committed artifacts by `scripts/build_number_ledger.py` (and `scripts/recompute_external_test.py`); "
             "`tests/test_manuscript_number_ledger.py` checks that the string appears in `MANUSCRIPT_DRAFT_v1.md`, and `tests/test_external_ledger_raw.py` recomputes the external-test rows from the raw records.", "",
             "| quantity | string in manuscript | source |", "|---|---|---|"]
    lines += [f"| {a} | `{b}` | `{c}` |" for a, b, c in es]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.name} ({len(es)} entries)")


if __name__ == "__main__":
    main()
