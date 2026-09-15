from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.outcome_evaluator import (
    OutcomeEvaluator,
)


def test_successful_defense():
    evaluator = OutcomeEvaluator()

    result = evaluator.evaluate(
        action=DefenseAction.BLOCK,
        allowed=False,
        attack_present=True,
        attack_succeeded=False,
        legitimate_task=False,
        legitimate_succeeded=False,
    )

    assert result.attack_success is False
    assert result.security_score == 1.0
    assert result.utility_score == 0.0
    assert result.defense_cost == 0.50


def test_legitimate_request():
    evaluator = OutcomeEvaluator()

    result = evaluator.evaluate(
        action=DefenseAction.NO_INTERVENTION,
        allowed=True,
        attack_present=False,
        attack_succeeded=False,
        legitimate_task=True,
        legitimate_succeeded=True,
    )

    assert result.attack_success is False
    assert result.legitimate_success is True
    assert result.security_score == 1.0
    assert result.utility_score == 1.0
    assert result.defense_cost == 0.0


def test_successful_attack():
    evaluator = OutcomeEvaluator()

    result = evaluator.evaluate(
        action=DefenseAction.NO_INTERVENTION,
        allowed=True,
        attack_present=True,
        attack_succeeded=True,
        legitimate_task=False,
        legitimate_succeeded=False,
    )

    assert result.attack_success is True
    assert result.security_score == 0.0
