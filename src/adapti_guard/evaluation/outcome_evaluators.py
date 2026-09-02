"""Outcome evaluators — heuristic (legacy) and LLM-judge (primary scientific)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.evaluation.llm_judge import JudgeInput, JudgeVerdict, LLMJudge
from src.adapti_guard.evaluation.outcome_evaluator import OutcomeEvaluator, OutcomeResult


@dataclass
class EvaluatedOutcome:
    outcome: OutcomeResult
    judge_verdict: JudgeVerdict | None = None
    evaluation_mode: str = "heuristic"


class OutcomeEvaluatorBase(ABC):
    @abstractmethod
    def evaluate(self, **kwargs) -> EvaluatedOutcome:
        raise NotImplementedError


class HeuristicOutcomeEvaluator(OutcomeEvaluatorBase):
    """LEGACY_SIMULATION_METRIC — not valid as primary scientific ASR."""

    def __init__(self):
        self._inner = OutcomeEvaluator()

    def evaluate(
        self,
        *,
        action: DefenseAction,
        allowed: bool,
        attack_present: bool,
        attack_succeeded: bool,
        legitimate_task: bool,
        legitimate_succeeded: bool,
    ) -> EvaluatedOutcome:
        outcome = self._inner.evaluate(
            action=action,
            allowed=allowed,
            attack_present=attack_present,
            attack_succeeded=attack_succeeded,
            legitimate_task=legitimate_task,
            legitimate_succeeded=legitimate_succeeded,
        )
        return EvaluatedOutcome(outcome=outcome, evaluation_mode="LEGACY_SIMULATION_ONLY")


class LLMJudgeOutcomeEvaluator(OutcomeEvaluatorBase):
    """Primary scientific evaluator when a real target response exists."""

    def __init__(self, judge: LLMJudge | None = None):
        self.judge = judge or LLMJudge()
        self._cost = OutcomeEvaluator()

    def evaluate(
        self,
        *,
        action: DefenseAction,
        allowed: bool,
        attack_present: bool,
        attack_prompt: str,
        target_response: str,
        attack_category: str = "unknown",
        attack_type: str = "unknown",
        legitimate_task: bool = False,
    ) -> EvaluatedOutcome:
        if not allowed:
            outcome = self._cost.evaluate(
                action=action,
                allowed=False,
                attack_present=attack_present,
                attack_succeeded=False,
                legitimate_task=legitimate_task,
                legitimate_succeeded=False,
            )
            verdict = JudgeVerdict(
                attack_success=False,
                refusal=True,
                policy_violation=False,
                tool_misuse=False,
                utility_success=False,
                confidence=1.0,
                reason="blocked_by_defense",
            )
            return EvaluatedOutcome(
                outcome=outcome,
                judge_verdict=verdict,
                evaluation_mode="LLM_JUDGE",
            )

        verdict = self.judge.judge(
            JudgeInput(
                user_prompt=attack_prompt,
                model_response=target_response,
                is_benign=not attack_present,
            )
        )

        attack_ok = verdict.attack_success if attack_present else False
        legit_ok = verdict.utility_success if legitimate_task else False

        outcome = self._cost.evaluate(
            action=action,
            allowed=True,
            attack_present=attack_present,
            attack_succeeded=attack_ok,
            legitimate_task=legitimate_task,
            legitimate_succeeded=legit_ok,
        )
        return EvaluatedOutcome(
            outcome=outcome,
            judge_verdict=verdict,
            evaluation_mode="LLM_JUDGE",
        )
