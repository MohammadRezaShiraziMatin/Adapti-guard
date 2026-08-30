from src.adapti_guard.adaptation.feedback_engine import FeedbackSignal
from src.adapti_guard.adaptation.policy_update_engine import (
    PolicyState,
    PolicyUpdateEngine,
)


def increase_feedback():
    return FeedbackSignal(
        reward=0.0,
        security_feedback=0.0,
        utility_feedback=0.0,
        cost_penalty=0.0,
        attack_success=True,
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


def test_defense_level_never_exceeds_maximum():
    engine = PolicyUpdateEngine(
        attack_threshold=1,
    )

    state = PolicyState(defense_level=3)

    for _ in range(10):
        state = engine.update(state, increase_feedback())

    assert state.defense_level == 3
    assert 0 <= state.defense_level <= 3


def test_defense_level_never_goes_below_zero():
    engine = PolicyUpdateEngine(
        legitimate_threshold=1,
    )

    state = PolicyState(defense_level=0)

    for _ in range(10):
        state = engine.update(state, reduce_feedback())

    assert state.defense_level == 0
    assert 0 <= state.defense_level <= 3


def test_pressure_resets_after_increase():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
    )

    state = PolicyState()

    state = engine.update(state, increase_feedback())
    assert state.attack_pressure == 1

    state = engine.update(state, increase_feedback())

    assert state.defense_level == 1
    assert state.attack_pressure == 0


def test_pressure_resets_after_reduction():
    engine = PolicyUpdateEngine(
        legitimate_threshold=2,
    )

    state = PolicyState(defense_level=2)

    state = engine.update(state, reduce_feedback())
    assert state.legitimate_pressure == 1

    state = engine.update(state, reduce_feedback())

    assert state.defense_level == 1
    assert state.legitimate_pressure == 0


def test_opposite_pressure_is_cleared():
    engine = PolicyUpdateEngine(
        attack_threshold=3,
        legitimate_threshold=3,
    )

    state = PolicyState(
        defense_level=2,
        attack_pressure=2,
        legitimate_pressure=1,
    )

    state = engine.update(state, reduce_feedback())

    assert state.legitimate_pressure == 2
    assert state.attack_pressure == 0


def test_maintain_does_not_create_pressure():
    engine = PolicyUpdateEngine()

    state = PolicyState(
        defense_level=2,
        attack_pressure=1,
        legitimate_pressure=1,
    )

    feedback = FeedbackSignal(
        reward=0.0,
        security_feedback=1.0,
        utility_feedback=1.0,
        cost_penalty=0.1,
        adaptation_signal="MAINTAIN",
        attack_success=False,
        legitimate_success=True,
    )

    state = engine.update(state, feedback)

    assert state.attack_pressure == 1
    assert state.legitimate_pressure == 1


def test_total_updates_only_changes_on_level_transition():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
    )

    state = PolicyState()

    state = engine.update(state, increase_feedback())

    assert state.total_updates == 0

    state = engine.update(state, increase_feedback())

    assert state.total_updates == 1

    state = engine.update(state, increase_feedback())

    assert state.total_updates == 1


def test_repeated_alternating_feedback_keeps_valid_state():
    engine = PolicyUpdateEngine(
        attack_threshold=2,
        legitimate_threshold=2,
    )

    state = PolicyState()

    for i in range(100):
        feedback = (
            increase_feedback()
            if i % 2 == 0
            else reduce_feedback()
        )

        state = engine.update(state, feedback)

        assert 0 <= state.defense_level <= 3
        assert state.attack_pressure >= 0
        assert state.legitimate_pressure >= 0

    assert 0 <= state.defense_level <= 3
