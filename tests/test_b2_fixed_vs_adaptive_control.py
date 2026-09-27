"""Fixed vs adaptive attacker control (offline; no API)."""
from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.attacker.fixed_sequence_attacker import (
    FixedSequenceAttacker,
    default_fixed_family_sequence,
)
from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
from adapti_guard.evaluation.b2_attack_mode_contract import (
    B2_ATTACK_MODE_ADAPTIVE,
    B2_ATTACK_MODE_FIXED,
    build_attacker_for_mode,
    extract_turn_supplementary_metrics,
)
from adapti_guard.experiments.defense_baselines import make_b1_rule_based


def _legacy_defense(**_kwargs):
    return DefenseAction.TOOL_RESTRICTION, {}


def _families_from_runner(attacker, *, max_turns: int, b1_threshold: float = 0.25):
    result = AdaptiveEpisodeRunner(max_turns).run(
        attacker=attacker,
        defense=_legacy_defense,
        baseline_defense_fn=make_b1_rule_based(threshold=b1_threshold),
        target=lambda _h, _m: "ok",
        seed=42,
    )
    return tuple(t.user_message for t in result.turns), result


def test_fixed_determinism_same_sequence_twice():
    seq = default_fixed_family_sequence(3)
    a1 = FixedSequenceAttacker(seq)
    a2 = FixedSequenceAttacker(seq)
    p1, _ = _families_from_runner(a1, max_turns=3)
    p2, _ = _families_from_runner(a2, max_turns=3)
    assert p1 == p2
    assert len(p1) == 3


def test_adaptive_determinism_same_trajectory_without_seed_in_policy():
    a1 = AdaptiveAttacker()
    a2 = AdaptiveAttacker()
    p1, _ = _families_from_runner(a1, max_turns=3)
    p2, _ = _families_from_runner(a2, max_turns=3)
    assert p1 == p2


def test_build_attacker_modes():
    assert isinstance(build_attacker_for_mode(B2_ATTACK_MODE_ADAPTIVE), AdaptiveAttacker)
    assert isinstance(build_attacker_for_mode(B2_ATTACK_MODE_FIXED), FixedSequenceAttacker)


def test_fixed_ignores_feedback_sequence_unchanged_on_block():
    seq = ("direct_injection", "indirect_injection", "context_manipulation")
    attacker = FixedSequenceAttacker(seq)
    payloads = []
    for _ in range(3):
        att = attacker.generate()
        payloads.append(att.payload)
        attacker.record(att)
        attacker.observe_defense(blocked=True, harmful_outcome=False)
    assert payloads == [
        AdaptiveAttacker.PAYLOADS["direct_injection"][0],
        AdaptiveAttacker.PAYLOADS["indirect_injection"][0],
        AdaptiveAttacker.PAYLOADS["context_manipulation"][0],
    ]


def test_adaptive_changes_family_after_block():
    attacker = AdaptiveAttacker()
    families = []
    for _ in range(3):
        att = attacker.generate()
        families.append(att.family)
        attacker.record(att)
        attacker.observe_defense(blocked=True, harmful_outcome=False)
    assert families[0] == "direct_injection"
    assert families[1] == "indirect_injection"
    assert families[2] == "context_manipulation"


def _family_sequence_under_blocks(attacker, max_turns: int) -> tuple[str, ...]:
    families = []
    for _ in range(max_turns):
        att = attacker.generate()
        families.append(att.family)
        attacker.record(att)
        attacker.observe_defense(blocked=True, harmful_outcome=False)
    return tuple(families)


def test_same_family_sequence_under_block_feedback_fixed_vs_adaptive():
    seq = default_fixed_family_sequence(3)
    assert _family_sequence_under_blocks(FixedSequenceAttacker(seq), 3) == _family_sequence_under_blocks(
        AdaptiveAttacker(), 3
    )


def test_supplementary_metrics_from_turns():
    _, result = _families_from_runner(AdaptiveAttacker(), max_turns=3, b1_threshold=0.25)
    m = extract_turn_supplementary_metrics(result.turns)
    assert m["evaluated_turns"] == 3
    assert m["turn_block_rate"] == 2 / 3
    assert m["first_allow_turn"] == 2
    assert m["target_calls"] == 1
