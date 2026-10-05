"""AdaptiGuard MVP runtime (historical compatibility).

This path uses regex detector v3 + ``RiskEngine`` + historical
``DefensePolicyEngine``. It is **not** the Phase 1 core pipeline and is
**not** used by ``PHASE1-CORE`` / ``VNEXT-ADAPT``.

Active Phase 1 path: ``adapti_guard.core.core_pipeline.CoreDefensePipeline``.
Do not treat ``AdaptiGuard.run`` outcomes as confirmatory security results.
"""

from collections.abc import Callable

from .detector.prompt_injection_detector import PromptInjectionDetector
from .risk.risk_engine import RiskEngine
from .policy.policy_engine import DefensePolicyEngine
from .defense.action_layer import DefenseActionLayer
from .evaluation.outcome_evaluator import OutcomeEvaluator
from .adaptation.feedback_engine import FeedbackEngine
from .adaptation.policy_update_engine import PolicyUpdateEngine


DEFAULT_BENIGN_STREAK_THRESHOLD = 20


class AdaptiGuard:
    """MVP runtime with a closed feedback loop.

    Outcome labels (``legitimate_task``, ``legitimate_succeeded``,
    ``attack_succeeded``) are *caller-supplied ground truth* unless an
    ``outcome_judge`` is given (Q1 F5). Do not forward labels that an
    attacker can influence: a caller that labels an evasive prompt as
    legitimate can drive the level down. With ``outcome_judge`` set,
    caller labels are ignored and the judge decides. The judge receives a
    dict with ``text``, ``detection``, ``risk``, ``decision`` and
    ``defense`` and returns a dict with any of ``legitimate_task``,
    ``legitimate_succeeded``, ``attack_succeeded``.

    De-escalation: after ``benign_streak_threshold`` consecutive allowed,
    successful legitimate episodes the level drops by one (Q1 F1);
    pass ``None`` to restore the legacy one-way behaviour. Instances are
    not thread-safe as a whole (the policy update itself is locked).
    """

    def __init__(
        self,
        outcome_judge: Callable[[dict], dict] | None = None,
        benign_streak_threshold: int | None = DEFAULT_BENIGN_STREAK_THRESHOLD,
        pressure_decay: int = 0,
    ):
        self.outcome_judge = outcome_judge

        self.detector = PromptInjectionDetector()
        self.risk_engine = RiskEngine()
        self.policy_engine = DefensePolicyEngine()
        self.action_layer = DefenseActionLayer()
        self.outcome_evaluator = OutcomeEvaluator()
        self.feedback_engine = FeedbackEngine()
        self.policy_update_engine = PolicyUpdateEngine(
            benign_streak_threshold=benign_streak_threshold,
            pressure_decay=pressure_decay,
        )

    @property
    def policy_state(self):
        return self.policy_update_engine.state

    def run(
        self,
        text: str,
        legitimate_task: bool = True,
        legitimate_succeeded: bool = True,
        attack_succeeded: bool | None = None,
        tool_sensitive: bool = False,
    ):

        # 1. Detection
        detection = self.detector.detect(text)
        is_injection = detection.injection_probability >= 0.25

        # 2. Risk
        risk = self.risk_engine.assess(detection)

        # 3. Policy
        decision = self.policy_engine.decide(
            risk=risk,
            tool_sensitive=tool_sensitive,
            defense_level=self.policy_state.defense_level,
        )

        # 4. Defense
        defense = self.action_layer.execute(
            decision.action,
            text,
        )

        if self.outcome_judge is not None:
            judged = self.outcome_judge(
                {
                    "text": text,
                    "detection": detection,
                    "risk": risk,
                    "decision": decision,
                    "defense": defense,
                }
            )
            legitimate_task = judged.get("legitimate_task", legitimate_task)
            legitimate_succeeded = judged.get(
                "legitimate_succeeded", legitimate_succeeded
            )
            attack_succeeded = judged.get("attack_succeeded", attack_succeeded)

        # -------------------------------------------------
        # Outcome model
        # -------------------------------------------------
        #
        # If caller provides attack_succeeded, use it.
        # Otherwise infer an MVP outcome:
        #
        # malicious + blocked => attack prevented
        # malicious + not blocked => attack succeeds
        #
        # This avoids treating BLOCK as a successful attack.
        # -------------------------------------------------

        if is_injection:

            if attack_succeeded is None:
                effective_attack_success = defense.allowed
            else:
                effective_attack_success = (
                    attack_succeeded
                    and defense.allowed
                )

        else:
            effective_attack_success = False

        effective_legitimate_success = (
            legitimate_task
            and legitimate_succeeded
            and defense.allowed
        )

        # 5. Evaluation
        outcome = self.outcome_evaluator.evaluate(
            action=defense.action,
            allowed=defense.allowed,
            attack_present=is_injection,
            attack_succeeded=effective_attack_success,
            legitimate_task=legitimate_task,
            legitimate_succeeded=effective_legitimate_success,
        )

        # 6. Feedback
        feedback = self.feedback_engine.generate(
            outcome
        )

        # 7. Adaptation
        policy_update = self.policy_update_engine.update(
            feedback
        )

        return {
            "detection": detection,
            "risk": risk,
            "decision": decision,
            "defense": defense,
            "outcome": outcome,
            "feedback": feedback,
            "policy_update": policy_update,
        }


__all__ = ["AdaptiGuard"]
