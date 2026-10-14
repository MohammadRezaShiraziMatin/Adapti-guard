"""Checks for scripts/analyze_exploratory.py on small synthetic records (offline)."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("analyze_exploratory", ROOT / "scripts" / "analyze_exploratory.py")
E = importlib.util.module_from_spec(_spec)
sys.modules["analyze_exploratory"] = E
_spec.loader.exec_module(E)
LL, QW, GPT = E.C.MODELS["llama"], E.C.MODELS["qwen"], E.C.MODELS["gpt"]


def rec(model, arm, cid, prop, exe=None, finish="stop", error=None, log=(), http=(200,)):
    exe = prop if exe is None and prop is not None else exe
    return {"model": model, "arm": arm, "case_id": cid, "any_attacker_tool": prop, "executed_attacker_call": exe,
            "finish": finish, "error": error, "http_statuses": list(http), "tool_calls": [], "executor_log": list(log)}


def r2_set():
    out = []
    for m in (LL, QW):
        for i in range(10):
            cid = f"dh-{i:04d}"
            out += [rec(m, "A0", cid, i < 4), rec(m, "A0_REP", cid, i < 4), rec(m, "SPOT_TOOL", cid, i < 1)]
        out.append(rec(m, "NOINJ", "dh-0000", False))
    out.append(rec(LL, "A0", "ds-0440", False, finish="length"))
    out.append(rec(LL, "A0_REP", "ds-0440", False))
    out.append(rec(LL, "SPOT_TOOL", "ds-0440", False))
    return out


def r3_set():
    return [rec(GPT, "A0", "dh-0016", False, finish="tool_calls"), rec(GPT, "A0", "dh-0001", None, error="transport:x",
                                                                       http=("transport:x",), finish=None)]


def test_proposal_counts_and_mcnemar():
    res = E.analyze(r2_set(), r3_set())
    p = res["1_proposal_endpoint"]
    assert p["rates"]["R2|llama|A0"]["proposed"] == 4 and p["rates"]["R2|llama|A0"]["n_resolved"] == 11
    pr = p["a0_vs_spot_tool"]["llama"]
    assert (pr["a0_only"], pr["spot_only"], pr["both"]) == (3, 0, 1)
    assert pr["exact_mcnemar_p_unadjusted"] == pytest.approx(0.25)
    assert p["rates"]["R3|gpt|A0"] == {**p["rates"]["R3|gpt|A0"], "n_resolved": 1, "unresolved": 1, "proposed": 0}


def test_proposed_not_executed_listed():
    r = r2_set()
    r[0]["executed_attacker_call"] = False
    r[0]["executor_log"] = [{"tool": "X", "status": "blocked"}]
    res = E.analyze(r, r3_set())
    assert res["1_proposal_endpoint"]["rates"]["R2|llama|A0"]["proposed_not_executed"] == ["dh-0000"]
    assert res["2_noinj_benign_interference"]["table"]["R2|llama|A0"]["episodes_with_blocked_or_rejected_call"] == 1


def test_error_table_and_notables():
    res = E.analyze(r2_set(), r3_set())["3_error_finish"]
    assert res["table"]["R3|gpt|A0"]["transport_errors"] == {"transport:x": 1}
    assert res["table"]["R2|llama|A0"]["finish"] == {"length": 1, "stop": 10}
    ids = {(n["run"], n["case_id"]) for n in res["notable_episodes"]}
    assert ("R2", "ds-0440") in ids and ("R3", "dh-0016") in ids and ("R3", "dh-0001") in ids


def test_ds0440_sensitivity():
    s = E.analyze(r2_set(), r3_set())["4_ds0440_sensitivity_H2_llama"]
    assert (s["non_event_main"]["a0_only"], s["non_event_main"]["n_pairs"]) == (3, 11)
    assert (s["event"]["a0_only"], s["event"]["spot_only"]) == (4, 0)
    assert s["excluded"]["n_pairs"] == 10
    assert s["event"]["exact_mcnemar_p"] == pytest.approx(0.125)


def test_missing_field_refused():
    r = r2_set()
    del r[0]["any_attacker_tool"]
    with pytest.raises(E.C.AnalysisError):
        E.analyze(r, r3_set())


def test_status_and_determinism():
    a, b = E.analyze(r2_set(), r3_set()), E.analyze(r2_set(), r3_set())
    assert a == b and a["status"] == "EXPLORATORY - NOT CONFIRMATORY, NOT REGISTERED"
