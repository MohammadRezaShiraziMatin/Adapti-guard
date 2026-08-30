from src.adapti_guard.adaptation.feedback_engine import (
    FeedbackSignal,
)
from src.adapti_guard.adaptation.policy_update_engine import (
    PolicyState,
    PolicyUpdateEngine,
)
from src.adapti_guard.core.models import DefenseAction


def increase_feedback():
    return FeedbackSignal(
        reward=0.0,
        security_feedback=0.0,
        utility_feedback=0.0,
        cost_penalty=0.0,
        attack_success=False,
        legitimate_success=False,
        adaptation_signal="INCREASE_DEFENSE",
    )


def reduce_feedback():
    return FeedbackSignal(
        reward=0.0,
        security_feedback=1.0,
        utility_feedback=1.0,
        cost_penalty=0.5,
        attack_success=False,
        legitimate_success=True,
        adaptation_signal="REDUCE_DEFENSE",
    )


def test_policy_does_not_change_before_threshold():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
    )

    state = PolicyState()

    state = engine.update(
        state,
        increase_feedback(),
    )

    assert state.defense_level == 0
    assert state.attack_pressure == 1


def test_policy_increases_after_threshold():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
    )

    state = PolicyState()

    state = engine.update(state, increase_feedback())
    state = engine.update(state, increase_feedback())

    assert state.defense_level == 1
    assert state.attack_pressure == 0
    assert state.total_updates == 1


def test_policy_levels_map_to_actions():
    engine = PolicyUpdateEngine()

    assert (
        engine.action_for_level(0)
        == DefenseAction.NO_INTERVENTION
    )

    assert (
        engine.action_for_level(1)
        == DefenseAction.SANITIZE
    )

    assert (
        engine.action_for_level(2)
        == DefenseAction.TOOL_RESTRICTION
    )

    assert (
        engine.action_for_level(3)
        == DefenseAction.BLOCK
    )


def test_policy_can_reduce():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
        legitimate_threshold=2,
    )

    state = PolicyState(defense_level=2)

    state = engine.update(state, reduce_feedback())
    state = engine.update(state, reduce_feedback())

    assert state.defense_level == 1


def test_cp0341_transition_history_matches_actual_level_changes():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
        legitimate_threshold=2,
    )

    state = PolicyState()

    # 0 -> 1
    state = engine.update(state, increase_feedback())
    state = engine.update(state, increase_feedback())

    # 1 -> 2
    state = engine.update(state, increase_feedback())
    state = engine.update(state, increase_feedback())

    # 2 -> 3
    state = engine.update(state, increase_feedback())
    state = engine.update(state, increase_feedback())

    # 3 -> 2
    state = engine.update(state, reduce_feedback())
    state = engine.update(state, reduce_feedback())

    assert state.transition_history == [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 2),
    ]

    assert state.total_updates == len(state.transition_history)


def test_cp0341_no_transition_without_level_change():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
        legitimate_threshold=2,
    )

    state = PolicyState()

    state = engine.update(state, reduce_feedback())
    state = engine.update(state, reduce_feedback())

    assert state.defense_level == 0
    assert state.total_updates == 0
    assert state.transition_history == []


def test_cp0341_transition_is_only_recorded_on_real_change():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
        legitimate_threshold=2,
    )

    state = PolicyState(defense_level=3)

    state = engine.update(state, increase_feedback())
    state = engine.update(state, increase_feedback())

    assert state.defense_level == 3
    assert state.total_updates == 0
    assert state.transition_history == []
