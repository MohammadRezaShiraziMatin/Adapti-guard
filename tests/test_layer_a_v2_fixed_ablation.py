"""Offline semantic checks for Layer A v2 fixed L2/L3 interventions."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.defense.action_layer import DefenseActionLayer
from src.adapti_guard.evaluation.attack_success import load_benchmark_mixed_records
from src.adapti_guard.experiments.defense_baselines import get_defense_fn
from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
from src.adapti_guard.risk.risk_engine import RiskEngine

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datasets" / "frozen" / "layer_a_v2"
EXPECTED_PACK_SHA256 = (
    "76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33"
)


def test_frozen_pack_hash_unchanged():
    digest = hashlib.sha256((PACK / "test.jsonl").read_bytes()).hexdigest()
    assert digest == EXPECTED_PACK_SHA256


def test_action_layer_a2_does_not_block_or_rewrite_prompt():
    layer = DefenseActionLayer()
    result = layer.execute(DefenseAction.TOOL_RESTRICTION, "keep this prompt")
    assert result.allowed is True
    assert result.tool_access is False
    assert result.content == "keep this prompt"
    assert result.reason == "tool_access_restricted"


def test_action_layer_a3_blocks_and_clears_content():
    layer = DefenseActionLayer()
    result = layer.execute(DefenseAction.BLOCK, "malicious")
    assert result.allowed is False
    assert result.tool_access is False
    assert result.content == ""
    assert result.reason == "interaction_blocked"


def test_l3_factory_is_unconditional_block():
    fn, state = get_defense_fn("L3")
    assert state is None
    action, blocked, content = fn("any prompt", "any context")
    assert action == "A3"
    assert blocked is True
    assert content == ""


def test_l2_factory_is_unconditional_a2_and_not_blocked():
    fn, state = get_defense_fn("L2")
    assert state is None
    action, blocked, content = fn("any prompt", "any context")
    assert action == "A2"
    assert blocked is False
    assert content == "any prompt"


def test_defense_fn_contract_cannot_carry_tool_access():
    """Layer A evaluate_episode only consumes (action, blocked, prompt)."""
    fn, _ = get_defense_fn("L2")
    result = fn("tool time", None)
    assert result == ("A2", False, "tool time")
    assert len(result) == 3


def test_seed42_sample_ids_match_historical_layer_a_v2_draw():
    records, meta = load_benchmark_mixed_records(
        split="test",
        attack_n=20,
        benign_n=20,
        seed=42,
        benchmark_dir=PACK,
    )
    assert meta["n_total"] == 40
    assert [r["id"] for r in records] == [
        "la_v2_atk_035",
        "la_v2_atk_030",
        "la_v2_ben_009",
        "la_v2_ben_011",
        "la_v2_atk_024",
        "la_v2_atk_005",
        "la_v2_atk_017",
        "la_v2_ben_029",
        "la_v2_ben_031",
        "la_v2_ben_022",
        "la_v2_ben_003",
        "la_v2_ben_019",
        "la_v2_atk_023",
        "la_v2_atk_036",
        "la_v2_atk_026",
        "la_v2_atk_007",
        "la_v2_atk_039",
        "la_v2_ben_036",
        "la_v2_ben_007",
        "la_v2_atk_037",
        "la_v2_ben_035",
        "la_v2_atk_031",
        "la_v2_ben_002",
        "la_v2_ben_016",
        "la_v2_atk_019",
        "la_v2_ben_034",
        "la_v2_atk_006",
        "la_v2_ben_037",
        "la_v2_atk_015",
        "la_v2_ben_010",
        "la_v2_ben_017",
        "la_v2_atk_004",
        "la_v2_atk_002",
        "la_v2_ben_033",
        "la_v2_atk_003",
        "la_v2_ben_012",
        "la_v2_ben_028",
        "la_v2_atk_009",
        "la_v2_atk_014",
        "la_v2_ben_038",
    ]


def test_risk_gated_b2_l3_blocks_only_detector_medium_on_seed42():
    """Existing B2_L3 is risk-gated, not unconditional A3."""
    records, _ = load_benchmark_mixed_records(
        split="test",
        attack_n=20,
        benign_n=20,
        seed=42,
        benchmark_dir=PACK,
    )
    fn, _ = get_defense_fn("B2_L3")
    actions = []
    blocked_ids = []
    for rec in records:
        action, blocked, _ = fn(rec["prompt"], rec["context"] or None)
        actions.append(action)
        if blocked:
            blocked_ids.append(rec["id"])
    assert Counter(actions) == {"A1": 38, "A3": 2}
    assert blocked_ids == ["la_v2_atk_004", "la_v2_atk_002"]


def test_detector_misses_most_seed42_attacks():
    records, _ = load_benchmark_mixed_records(
        split="test",
        attack_n=20,
        benign_n=20,
        seed=42,
        benchmark_dir=PACK,
    )
    detector = PromptInjectionDetector()
    risk_engine = RiskEngine()
    policy = DefensePolicyEngine()
    levels = Counter()
    medium_ids = []
    for rec in records:
        if rec["label"] != "attack":
            continue
        text = f"{rec['context']}\n\n{rec['prompt']}" if rec["context"] else rec["prompt"]
        detection = detector.detect(text)
        risk = risk_engine.assess(detection)
        level = risk.level.value if hasattr(risk.level, "value") else str(risk.level)
        levels[level] += 1
        if level == "MEDIUM":
            medium_ids.append(rec["id"])
            decision = policy.decide(risk=risk, tool_sensitive=False, defense_level=3)
            assert decision.action == DefenseAction.BLOCK
    assert levels["LOW"] == 18
    assert levels["MEDIUM"] == 2
    assert "HIGH" not in levels
    assert medium_ids == ["la_v2_atk_004", "la_v2_atk_002"]
