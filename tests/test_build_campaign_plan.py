"""Checks for scripts/build_campaign_plan.py (protocol §9A items 10–13). Offline. Reads only committed files."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("bcp", ROOT / "scripts" / "build_campaign_plan.py")
B = importlib.util.module_from_spec(_spec)
sys.modules["bcp"] = B
_spec.loader.exec_module(B)

RET = json.loads(B.RETAINED.read_text())
PLAN = json.loads(B.OUT.read_text())
RUNS = {r["run"]: r for r in PLAN["runs"]}


def test_committed_plan_is_exactly_what_the_builder_produces():
    assert B.plan_text(B.build_plan()) == B.OUT.read_text()


def test_run_episode_and_http_counts():
    assert RUNS["R1"]["episodes"] == 60 and RUNS["R1"]["http_cap"] == 60
    assert RUNS["R2"]["episodes"] == 980 and RUNS["R2"]["http_cap"] == 980
    assert RUNS["R3"]["episodes"] == 72 and RUNS["R3"]["http_cap"] == 72
    assert PLAN["confirmatory_episodes"] == 1052


def test_r2_arms_include_a0_rep_and_noinj_only_for_the_noinj_subset():
    noinj = set(PLAN["noinj_cases"])
    for c in RUNS["R2"]["cases"]:
        assert c["arms"][:3] == ["A0", "A0_REP", "SPOT_TOOL"]
        assert ("NOINJ" in c["arms"]) == (c["case_id"] in noinj)


def test_noinj_is_the_first_40_sorted_retained_ids_for_both_targets():
    retained = sorted(RET["retained_case_ids_n150"])
    assert PLAN["noinj_cases"] == retained[:40]
    assert len(PLAN["noinj_cases"]) == 40
    r2_noinj = sorted(c["case_id"] for c in RUNS["R2"]["cases"] if "NOINJ" in c["arms"])
    assert r2_noinj == retained[:40]


def test_r2_covers_exactly_the_retained_150_and_r3_the_retained_72():
    assert sorted(c["case_id"] for c in RUNS["R2"]["cases"]) == sorted(RET["retained_case_ids_n150"])
    gpt = sorted(c["case_id"] for c in RUNS["R3"]["cases"])
    assert gpt == sorted(RET["retained_case_ids_gpt_n72"])
    assert set(gpt) <= set(RET["retained_case_ids_n150"])
    assert all(c["arms"] == ["A0"] for c in RUNS["R3"]["cases"])


def test_pilot_is_disjoint_from_the_confirmatory_set_and_uses_a0_and_spot():
    pilot_ids = {c["case_id"] for c in RUNS["R1"]["cases"]}
    assert len(pilot_ids) == 30
    assert not pilot_ids & set(RET["retained_case_ids_n150"])
    assert all(c["arms"] == ["A0", "SPOT_TOOL"] for c in RUNS["R1"]["cases"])
    assert RUNS["R1"]["models"] == ["llama"]


def test_soft_caps_sum_to_the_campaign_cap():
    total = sum(r["soft_cap_usd"] for r in PLAN["runs"])
    assert abs(total - PLAN["campaign_cap_usd"]) < 1e-9
    assert RUNS["R1"]["soft_cap_usd"] == 0.02


def test_estimates_follow_the_committed_rates():
    rate = B.RATE
    assert RUNS["R1"]["estimate_usd"] == round(60 * rate["llama"], 4)
    assert RUNS["R3"]["estimate_usd"] == round(72 * rate["gpt"], 4)
    assert PLAN["campaign_cap_usd"] == 0.50


def test_plan_is_not_marked_launcher_ready_and_is_not_signed_off():
    assert PLAN["launcher_input_ready"] is False
    assert PLAN["status"].startswith("PROPOSED")
