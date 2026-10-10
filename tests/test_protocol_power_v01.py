"""Checks for scripts/power_protocol_v01.py. Expected values come from independent routes: SciPy's beta quantile,
the textbook McNemar formula written out here, and direct sums and counts over the committed raw files. None of the
expected values is computed with the functions under test."""
import importlib.util
import json
import math
from pathlib import Path

from scipy.stats import beta, norm

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("power", ROOT / "scripts" / "power_protocol_v01.py")
power = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(power)

REG = ROOT / "experiments/external/injecagent_registered_20261001"
CAL = ROOT / "experiments/external/injecagent_panel_calib_20261001"


def _episodes(path):
    return json.loads(path.read_text())["episodes"]


def test_cp_upper_zero_matches_scipy_beta_quantile():
    for n in (40, 72, 100, 186):
        assert abs(power.cp_upper_zero(n) - beta.ppf(0.975, 1, n)) < 1e-12


def test_min_n_is_72_and_is_tight():
    assert power.min_n_zero_events(0.05) == 72
    assert beta.ppf(0.975, 1, 72) < 0.05 <= beta.ppf(0.975, 1, 71)


def test_mcnemar_pairs_matches_textbook_formula():
    delta, pd = 0.10, 0.20
    za, zb = norm.ppf(0.975), norm.ppf(0.80)
    assert power.mcnemar_pairs(delta, pd, 0.05) == math.ceil(((za * math.sqrt(pd) + zb * math.sqrt(pd - delta * delta)) / delta) ** 2)


def test_llama_proposal_discordance_matches_direct_count():
    eps = _episodes(REG / "meta-llama__llama-4-maverick.json")
    a0 = {e["case_id"]: e["first_attacker_tool"] for e in eps if e["arm"] == "A0"}
    sp = {e["case_id"]: e["first_attacker_tool"] for e in eps if e["arm"] == "SPOT_TOOL"}
    expected = (len(a0), sum(1 for k in a0 if a0[k] and not sp[k]), sum(1 for k in a0 if not a0[k] and sp[k]))
    assert power.proposal_discordance(REG / "meta-llama__llama-4-maverick.json") == expected == (186, 21, 3)


def test_qwen_proposal_discordance_matches_direct_count():
    eps = _episodes(REG / "qwen__qwen3.8-flash.json")
    a0 = {e["case_id"]: e["first_attacker_tool"] for e in eps if e["arm"] == "A0"}
    sp = {e["case_id"]: e["first_attacker_tool"] for e in eps if e["arm"] == "SPOT_TOOL"}
    expected = (len(a0), sum(1 for k in a0 if a0[k] and not sp[k]), sum(1 for k in a0 if not a0[k] and sp[k]))
    assert power.proposal_discordance(REG / "qwen__qwen3.8-flash.json") == expected == (186, 22, 3)


def test_no_executed_call_field_in_registered_records():
    # If this fails, an executed-call field exists now: update executed_discordance and the protocol.
    for name in ("meta-llama__llama-4-maverick.json", "qwen__qwen3.8-flash.json"):
        keys = {k for e in _episodes(REG / name) for k in e}
        assert not any("executed" in k for k in keys), name
        assert power.executed_discordance(REG / name) is None


def test_only_two_targets_have_a_spot_tool_arm_in_committed_records():
    arms = {}
    for p in list(REG.glob("*.json")) + list(CAL.glob("*.json")):
        if p.name in ("ANALYSIS.json", "MANIFEST.json"):
            continue
        arms[p.relative_to(ROOT).as_posix()] = {e["arm"] for e in _episodes(p)}
    with_spot = sorted(n for n, a in arms.items() if "SPOT_TOOL" in a)
    assert with_spot == [
        "experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json",
        "experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json",
    ]


def test_per_episode_cost_matches_direct_sum_for_every_target():
    direct = {
        "meta-llama/llama-4-maverick": REG / "meta-llama__llama-4-maverick.json",
        "qwen/qwen3.8-flash": REG / "qwen__qwen3.8-flash.json",
        "deepseek/deepseek-v4.1-flash": CAL / "deepseek__deepseek-v4.1-flash.json",
        "z-ai/glm-4.7": CAL / "z-ai__glm-4.7.json",
        "openai/gpt-5.6-sol": CAL / "openai__gpt-5.6-sol.json",
    }
    for target, path in direct.items():
        priced = [e["cost"] for e in _episodes(path) if "cost" in e]
        assert power.COST_FILE[target] == path
        assert power.per_episode_cost(path)[2] == sum(priced)
        assert power.per_episode_cost(path)[3] == sum(priced) / len(priced)


def test_unpriced_episode_counts_are_disclosed_values():
    assert power.per_episode_cost(CAL / "qwen__qwen3.8-flash.json")[:2] == (80, 73)
    priced_reg = [e for e in _episodes(REG / "qwen__qwen3.8-flash.json") if "cost" in e]
    assert len(priced_reg) == 598


def test_hard_set_split_is_recorded_in_freeze_record_and_manifest():
    freeze = json.loads((ROOT / "datasets/attackset_hard_v1/FREEZE_RECORD.json").read_text())
    manifest = json.loads((ROOT / "datasets/attackset_hard_v1/MANIFEST.json").read_text())
    assert freeze["human_written"]["splits"] == {"test": 170, "calibration": 68}
    assert manifest["report"]["split"] == {"test": 170, "calibration": 68}
    labels = [item["split"] for item in manifest["items"]]
    assert labels.count("test") == 170 and labels.count("calibration") == 68
