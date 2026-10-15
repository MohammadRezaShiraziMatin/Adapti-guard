"""Offline checks for scripts/build_exploratory_plan.py (EXPLORATORY, outside the frozen protocol)."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("bep", ROOT / "scripts" / "build_exploratory_plan.py")
B = importlib.util.module_from_spec(_spec)
sys.modules["bep"] = B
_spec.loader.exec_module(B)

GPT = "openai/gpt-5.6-sol"


def _case(cid, arms):
    return {"case_id": cid, "kind": "dh", "attacker_tools": ["X"], "tools": [{"t": cid}], "messages": [{"m": "A0"}],
            "arms": {a: {"messages": [{"m": a + cid}], "denied_tools": []} for a in arms}}


def _r2():
    return {"run": "R2", "request": {"max_tokens": 512, "temperature": 0.0, "tool_call_id": "call00001"},
            "models": [{"model_id": "a/b", "route": "openrouter", "reasoning": None}],
            "cases": [_case("c1", ["A0", "A0_REP", "NOINJ", "SPOT_TOOL"]), _case("c2", ["A0", "A0_REP", "SPOT_TOOL"])]}


def _r3():
    return {"run": "R3", "request": {"max_tokens": 512, "temperature": 0.0, "tool_call_id": "call00001"},
            "models": [{"model_id": GPT, "route": "openrouter", "reasoning": {"enabled": False}}],
            "cases": [_case("c2", ["A0"])]}


def test_model_extension_keeps_r2_design_and_is_labelled():
    r2 = _r2()
    p = B.model_extension(r2, "haiku", "anthropic/claude-haiku-5.5", "x")
    assert p["cases"] == r2["cases"] and p["request"] == r2["request"]
    assert p["models"] == [{"model_id": "anthropic/claude-haiku-5.5", "route": "openrouter", "reasoning": {"enabled": False}}]
    assert p["exploratory"] is True and "EXPLORATORY" in p["label"] and p["run"].startswith("EXPL-")
    assert B.episodes(p)["per_model_per_arm"] == {"A0": 2, "A0_REP": 2, "NOINJ": 1, "SPOT_TOOL": 2}
    assert r2["models"][0]["model_id"] == "a/b"  # base not mutated


def test_model_extension_refuses_non_r2_base():
    with pytest.raises(ValueError):
        B.model_extension(_r3(), "x", "y/z", "x")


def test_gpt_spot_tool_uses_r3_cases_and_r2_spot_messages():
    r2, r3 = _r2(), _r3()
    p = B.gpt_spot_tool(r2, r3, "a", "b")
    assert [c["case_id"] for c in p["cases"]] == ["c2"]
    assert p["cases"][0]["arms"] == {"SPOT_TOOL": r2["cases"][1]["arms"]["SPOT_TOOL"]}
    assert p["models"] == r3["models"] and p["exploratory"] is True


def test_gpt_spot_tool_refuses_mismatched_inputs():
    r2, r3 = _r2(), _r3()
    r3["cases"][0]["tools"] = [{"t": "other"}]
    with pytest.raises(ValueError):
        B.gpt_spot_tool(r2, r3, "a", "b")


@pytest.mark.skipif(not (B.R2_PLAN.exists() and B.R3_PLAN.exists()), reason="build/ launcher plans not present")
def test_real_plans_match_frozen_hashes_and_counts():
    plans = B.build_all(*B.load_bases())
    for n in B.EXT_MODELS:
        assert B.episodes(plans[f"expl_{n}.json"]) == {
            "per_model": 490, "total": 490, "per_model_per_arm": {"A0": 150, "A0_REP": 150, "NOINJ": 40, "SPOT_TOOL": 150}}
    assert B.episodes(plans["expl_gpt_spot_tool.json"])["per_model_per_arm"] == {"SPOT_TOOL": 72}


def _expl():
    p = B.model_extension(_r2(), "x", "a/b", "s")
    return p


def _ep(cid, arm, err=None):
    return {"case_id": cid, "arm": arm, "model": "a/b", "error": err}


def test_topup_contains_only_unsent_and_excludes_errored():
    p = _expl()
    eps = [_ep("c1", "A0"), _ep("c1", "A0_REP", "transport:timeout"), _ep("c1", "NOINJ"), _ep("c1", "SPOT_TOOL"),
           _ep("c2", "A0")]
    t = B.topup(p, eps, "s", "experiments/external/X")
    assert t["run"] == "EXPL-x-topup" and t["exploratory"] is True and "EXPLORATORY" in t["label"]
    assert [(c["case_id"], sorted(c["arms"])) for c in t["cases"]] == [("c2", ["A0_REP", "SPOT_TOOL"])]
    assert t["cases"][0]["arms"]["SPOT_TOOL"] == p["cases"][1]["arms"]["SPOT_TOOL"]
    assert t["derived_from"]["sha256"] == "s" and t["derived_from"]["parent_run"] == "EXPL-x"
    assert t["models"] == p["models"] and t["request"] == p["request"]
    assert B.episodes(t)["total"] == 2


def test_topup_refuses_unknown_or_duplicate_episodes():
    p = _expl()
    with pytest.raises(ValueError):
        B.topup(p, [_ep("zz", "A0")], "s", "d")
    with pytest.raises(ValueError):
        B.topup(p, [_ep("c1", "A0"), _ep("c1", "A0")], "s", "d")
    with pytest.raises(ValueError):
        B.topup(_r2(), [], "s", "d")
