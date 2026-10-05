"""AdaptiGuard MVP runtime (historical compatibility).

This path uses regex detector v3 + ``RiskEngine`` + historical
``DefensePolicyEngine``. It is **not** the Phase 1 core pipeline and is
**not** used by ``PHASE1-CORE`` / ``VNEXT-ADAPT``.

Active Phase 1 path: ``adapti_guard.core.core_pipeline.CoreDefensePipeline``.
Do not treat ``AdaptiGuard.run`` outcomes as confirmatory security results.
"""

from .detector.prompt_injection_detector import PromptInjectionDetector
from .risk.risk_engine import RiskEngine
from .policy.policy_engine import DefensePolicyEngine
from .defense.action_layer import DefenseActionLayer
from .evaluation.outcome_evaluator import OutcomeEvaluator
from .adaptation.feedback_engine import FeedbackEngine
from .adaptation.policy_update_engine import PolicyUpdateEngine


class AdaptiGuard:

    def __init__(self):

        self.detector = PromptInjectionDetector()
        self.risk_engine = RiskEngine()
        self.policy_engine = DefensePolicyEngine()
        self.action_layer = DefenseActionLayer()
        self.outcome_evaluator = OutcomeEvaluator()
        self.feedback_engine = FeedbackEngine()
        self.policy_update_engine = PolicyUpdateEngine()

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

        # -------------------------------------------------
        # Outcome model
        # -------------------------------------------------
        #
        # Infer an MVP outcome from the guard's own decision:
        #
        # malicious + blocked => attack prevented
        # malicious + not blocked => attack succeeds
        #
        # This avoids treating BLOCK as a successful attack.
        #
        # Caller-supplied labels are advisory and can only make the
        # controller more conservative, never less: a caller cannot
        # relabel a detected injection as a legitimate task, nor
        # declare an allowed injection harmless. Otherwise any adapter
        # forwarding user-influenced labels could lower the defense
        # level.
        # -------------------------------------------------

        for name, value in (
            ("legitimate_task", legitimate_task),
            ("legitimate_succeeded", legitimate_succeeded),
            ("attack_succeeded", attack_succeeded),
        ):
            if value is not None and not isinstance(value, bool):
                raise TypeError(
                    f"{name} must be a bool or None, "
                    f"got {type(value).__name__}"
                )

        effective_attack_success = is_injection and defense.allowed

        effective_legitimate_task = legitimate_task and not is_injection

        effective_legitimate_success = (
            effective_legitimate_task
            and legitimate_succeeded
            and defense.allowed
        )

        # 5. Evaluation
        outcome = self.outcome_evaluator.evaluate(
            action=defense.action,
            allowed=defense.allowed,
            attack_present=is_injection,
            attack_succeeded=effective_attack_success,
            legitimate_task=effective_legitimate_task,
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
