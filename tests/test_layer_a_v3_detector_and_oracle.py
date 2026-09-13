"""Tests for Layer A v3 detector eval and oracle baselines."""

from __future__ import annotations

import hashlib
from pathlib import Path

from src.adapti_guard.evaluation.detector_eval import evaluate_detector_pack, load_jsonl
from src.adapti_guard.experiments.defense_baselines import get_defense_fn

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datasets" / "frozen" / "layer_a_v3"
VIEW = ROOT / "datasets" / "frozen" / "layer_a_v3_test_split_view"
TEST_SPLIT_SHA = "47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8"


def test_test_split_view_matches_frozen_test_split():
    a = (PACK / "test_split.jsonl").read_bytes()
    b = (VIEW / "test.jsonl").read_bytes()
    assert a == b
    assert hashlib.sha256(a).hexdigest() == TEST_SPLIT_SHA


def test_detector_eval_on_test_split_is_deterministic():
    rows = load_jsonl(PACK / "test_split.jsonl")
    r1 = evaluate_detector_pack(rows, threshold=0.25)
    r2 = evaluate_detector_pack(rows, threshold=0.25)
    assert r1["overall"] == r2["overall"]
    assert r1["n_attack"] == 40
    assert r1["n_benign"] == 40
    # Current regex detector is weak on v3; keep as regression floor, not a win claim.
    assert r1["overall"]["recall"] is not None
    assert r1["overall"]["recall"] < 0.5


def test_oracle_block_uses_ground_truth_label():
    fn, state = get_defense_fn("ORACLE_BLOCK")
    assert state is None
    assert fn("x", None, is_attack=True) == ("A3", True, "")
    assert fn("x", None, is_attack=False) == ("A0", False, "x")


def test_oracle_risk_blocks_attacks_at_level_3():
    fn, _ = get_defense_fn("ORACLE_RISK")
    action, blocked, content = fn("benign-looking text", None, is_attack=True)
    assert action == "A3"
    assert blocked is True
    assert content == ""


def test_l2_still_unsupported_contract():
    fn, _ = get_defense_fn("L2")
    action, blocked, content = fn("use the calculator tool", None)
    assert action == "A2"
    assert blocked is False
    assert content == "use the calculator tool"
