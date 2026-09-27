"""B2 adaptive + B1 defense-before-target execution (no API)."""
from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner
from adapti_guard.experiments.defense_baselines import make_b1_rule_based


def _legacy_defense(**_kwargs):
    return DefenseAction.TOOL_RESTRICTION, {}


def test_case_a_b1_block_zero_target_calls():
    calls = {"n": 0}

    def target(_history, msg):
        calls["n"] += 1
        return "should not run"

    b1 = make_b1_rule_based()
    result = AdaptiveEpisodeRunner(1).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=b1,
        target=target,
    )
    assert result.execution_mode == "b1_pre_target"
    assert len(result.turns) == 1
    tr = result.turns[0]
    assert tr.blocked is True
    assert tr.target_called is False
    assert tr.verdict_reason == "blocked_by_defense"
    assert tr.outcome_source == "rule_based_blocked_by_defense"
    assert calls["n"] == 0


def test_case_b_allowed_reaches_target():
    calls = {"n": 0}

    def target(_history, msg):
        calls["n"] += 1
        return f"ok:{msg[:8]}"

    b1 = make_b1_rule_based(threshold=0.99)
    result = AdaptiveEpisodeRunner(1).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=b1,
        target=target,
    )
    tr = result.turns[0]
    assert tr.blocked is False
    assert tr.target_called is True
    assert calls["n"] == 1
    assert tr.model_response.startswith("ok:")


def test_case_c_mid_episode_block():
    calls = {"n": 0}
    turn = {"i": 0}
    real_b1 = make_b1_rule_based()

    def selective_b1(prompt: str, context: str | None):
        turn["i"] += 1
        if turn["i"] == 1:
            return "A0", False, prompt
        return real_b1(prompt, context)

    def target(_history, msg):
        calls["n"] += 1
        return "response"

    result = AdaptiveEpisodeRunner(2).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=selective_b1,
        target=target,
    )
    assert len(result.turns) == 2
    assert result.turns[0].target_called is True
    assert result.turns[1].blocked is True
    assert result.turns[1].target_called is False
    assert calls["n"] == 1


def test_max_turn_termination():
    calls = {"n": 0}

    def target(_history, msg):
        calls["n"] += 1
        return "r"

    b1 = make_b1_rule_based(threshold=0.99)
    result = AdaptiveEpisodeRunner(4).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        baseline_defense_fn=b1,
        target=target,
    )
    assert result.n_turns == 4
    assert len(result.turns) == 4
    assert calls["n"] == sum(1 for t in result.turns if t.target_called)


def test_legacy_stateful_path_unchanged():
    result = AdaptiveEpisodeRunner(4).run(
        attacker=AdaptiveAttacker(),
        defense=_legacy_defense,
        seed=0,
    )
    assert result.execution_mode == "stateful_legacy"
    assert result.strategy_changed
    assert result.turns == ()
