"""The deterministic re-scoring script must reproduce the frozen AUDIT numbers on the judge side."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    spec = importlib.util.spec_from_file_location("rescore_tracks_ab_deterministic", ROOT / "scripts/rescore_tracks_ab_deterministic.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def test_judge_side_matches_frozen_audits(tmp_path, monkeypatch):
    m = _mod()
    monkeypatch.setattr(m, "OUT", tmp_path / "out.json")
    m.main()
    import json

    r = json.loads((tmp_path / "out.json").read_text())
    a, b = r["A_VNEXT"], r["B_PHASE1"]
    assert (a["paired_judge"]["b10_treatment_wins"], a["paired_judge"]["b01_b0_wins"]) == (5, 0)  # Track A AUDIT
    assert abs(a["paired_judge"]["mcnemar_exact_p"] - 0.0625) < 1e-12
    assert (b["paired_judge"]["b10_treatment_wins"], b["paired_judge"]["b01_b0_wins"]) == (27, 0)  # Track B AUDIT
    assert abs(b["paired_judge"]["delta_hat"] - 0.4426229508196721) < 1e-12
    assert a["arms"]["B0"]["judge_success"] == 58 and b["arms"]["PHASE1-CORE"]["judge_success"] == 34
    assert a["arms"]["B0"]["benign_judge_utility"] == 59 and b["arms"]["PHASE1-CORE"]["benign_judge_utility"] == 59
    # deterministic side (documented in docs/research/TRACKS_AB_DETERMINISTIC_RESCORING_20260930.md)
    assert b["arms"]["PHASE1-CORE"]["deterministic_success"] == 6 and a["arms"]["B0"]["deterministic_success"] == 40
    assert b["arms"]["PHASE1-CORE"]["benign_tool_denied_but_judged_useful"] == 10
