"""Adaptation signal correctness."""

from src.adapti_guard.adaptation.feedback_engine import FeedbackEngine
from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.evaluation.outcome_evaluator import OutcomeEvaluator


def test_blocked_attack_does_not_reduce_defense():
    evaluator = OutcomeEvaluator()
    feedback_engine = FeedbackEngine()

    outcome = evaluator.evaluate(
        action=DefenseAction.BLOCK,
        allowed=False,
        attack_present=True,
        attack_succeeded=False,
        legitimate_task=False,
        legitimate_succeeded=False,
    )

    feedback = feedback_engine.generate(outcome)
    assert feedback.adaptation_signal == "MAINTAIN"


def test_blocked_legitimate_reduces_defense():
    evaluator = OutcomeEvaluator()
    feedback_engine = FeedbackEngine()

    outcome = evaluator.evaluate(
        action=DefenseAction.BLOCK,
        allowed=False,
        attack_present=False,
        attack_succeeded=False,
        legitimate_task=True,
        legitimate_succeeded=False,
    )

    feedback = feedback_engine.generate(outcome)
    assert feedback.adaptation_signal == "REDUCE_DEFENSE"
