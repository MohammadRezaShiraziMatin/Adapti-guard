from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.outcome_evaluator import (
    OutcomeEvaluator,
)
from adapti_guard.adaptation.feedback_engine import (
    FeedbackEngine,
)


def test_failed_attack_increases_defense():
    evaluator = OutcomeEvaluator()
    feedback_engine = FeedbackEngine()

    outcome = evaluator.evaluate(
        action=DefenseAction.NO_INTERVENTION,
        allowed=True,
        attack_present=True,
        attack_succeeded=True,
        legitimate_task=False,
        legitimate_succeeded=False,
    )

    feedback = feedback_engine.generate(outcome)

    assert feedback.adaptation_signal == "INCREASE_DEFENSE"
    assert feedback.security_feedback == 0.0


def test_successful_legitimate_task():
    evaluator = OutcomeEvaluator()
    feedback_engine = FeedbackEngine()

    outcome = evaluator.evaluate(
        action=DefenseAction.NO_INTERVENTION,
        allowed=True,
        attack_present=False,
        attack_succeeded=False,
        legitimate_task=True,
        legitimate_succeeded=True,
    )

    feedback = feedback_engine.generate(outcome)

    assert feedback.adaptation_signal == "MAINTAIN"
    assert feedback.utility_feedback == 1.0


def test_expensive_defense():
    evaluator = OutcomeEvaluator()
    feedback_engine = FeedbackEngine()

    outcome = evaluator.evaluate(
        action=DefenseAction.BLOCK,
        allowed=False,
        attack_present=False,
        attack_succeeded=False,
        legitimate_task=True,
        legitimate_succeeded=True,
    )

    feedback = feedback_engine.generate(outcome)

    assert feedback.adaptation_signal == "REDUCE_DEFENSE"
