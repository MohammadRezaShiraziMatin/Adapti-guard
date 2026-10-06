"""AdaptiGuard MVP runtime (historical compatibility).

This path uses the hardened regex detector (a subclass of detector v3) +
``RiskEngine`` + historical ``DefensePolicyEngine`` + a delimiting action
layer. It is **not** the Phase 1 core pipeline and is
**not** used by ``PHASE1-CORE`` / ``VNEXT-ADAPT``.

Active Phase 1 path: ``adapti_guard.core.core_pipeline.CoreDefensePipeline``.
Do not treat ``AdaptiGuard.run`` outcomes as confirmatory security results.
"""

from collections.abc import Callable

from .detector.hardened_detector import HardenedPromptInjectionDetector
from .risk.risk_engine import RiskEngine
from .policy.policy_engine import DefensePolicyEngine
from .defense.action_layer import DefenseActionLayer
from .evaluation.outcome_evaluator import OutcomeEvaluator
from .adaptation.feedback_engine import FeedbackEngine
from .adaptation.policy_update_engine import PolicyUpdateEngine


DEFAULT_BENIGN_STREAK_THRESHOLD = 20
DEFAULT_MIN_DWELL = 10
DEFAULT_BACKOFF_CAP = 4
DETECTION_THRESHOLD = 0.25

_LABEL_KEYS = ("legitimate_task", "legitimate_succeeded", "attack_succeeded")


def _check_bool(name: str, value, *, allow_none: bool = False):
    if value is None and allow_none:
        return None
    if not isinstance(value, bool):
        raise TypeError(
            f"{name} must be a bool"
            f"{' or None' if allow_none else ''}, got {value!r}"
        )
    return value


def _validate_judge_output(judged) -> dict:
    if not isinstance(judged, dict):
        raise TypeError(
            f"outcome_judge must return a dict, got {type(judged).__name__}"
        )
    unknown = set(judged) - set(_LABEL_KEYS)
    if unknown:
        raise ValueError(
            f"outcome_judge returned unknown keys {sorted(unknown)}; "
            f"allowed: {list(_LABEL_KEYS)}"
        )
    for key, value in judged.items():
        _check_bool(key, value, allow_none=True)
    return judged


class AdaptiGuard:
    """MVP runtime with a closed feedback loop.

    Outcome labels. Without an ``outcome_judge`` the loop is only as
    trustworthy as the detector and the caller:

    * ``legitimate_task`` defaults to "derive it": an input the detector
      flags is treated as an attack and a caller claim of "legitimate"
      for such an input is **ignored** (Q1 H-1: a blocked attack must
      never be booked as an over-blocked legitimate task). Unflagged
      input is assumed legitimate unless the caller says otherwise, so
      attacks the detector misses are invisible to the controller.
    * Labels must be ``bool`` (or ``None`` = derive); anything else
      raises ``TypeError``.

    With ``outcome_judge`` the judge's labels override the caller's and
    the detector-derived defaults. It receives a dict with ``text``,
    ``detection``, ``risk``, ``decision`` and ``defense`` and returns a
    dict whose keys are a subset of ``legitimate_task``,
    ``legitimate_succeeded``, ``attack_succeeded`` with ``bool``/``None``
    values; anything else raises.

    Controller defaults here (not those of the bare engine): attack
    escalation after 2 signals, benign-streak de-escalation after 20
    episodes with exponential attack memory (``backoff_cap``), and a
    ``min_dwell`` of 10 episodes before any down-move. The detector is
    :class:`HardenedPromptInjectionDetector` and SANITIZE delimits
    instead of stripping (Q1 H-3, H-4). Instances are not thread-safe as
    a whole (the policy update itself is locked).
    """

    def __init__(
        self,
        outcome_judge: Callable[[dict], dict] | None = None,
        benign_streak_threshold: int | None = DEFAULT_BENIGN_STREAK_THRESHOLD,
        pressure_decay: int = 0,
        *,
        min_dwell: int = DEFAULT_MIN_DWELL,
        backoff_cap: int = DEFAULT_BACKOFF_CAP,
        initial_level: int = 0,
        detector=None,
        action_layer=None,
    ):
        self.outcome_judge = outcome_judge
        self.detector = detector or HardenedPromptInjectionDetector()
        self.risk_engine = RiskEngine()
        self.policy_engine = DefensePolicyEngine()
        self.action_layer = action_layer or DefenseActionLayer(
            sanitize_mode="delimit"
        )
        self.outcome_evaluator = OutcomeEvaluator()
        self.feedback_engine = FeedbackEngine()
        self.initial_level = initial_level
        self.policy_update_engine = PolicyUpdateEngine(
            benign_streak_threshold=benign_streak_threshold,
            pressure_decay=pressure_decay,
            min_dwell=min_dwell,
            backoff_cap=backoff_cap,
        )
        self.reset()

    def reset(self) -> None:
        """Return to ``initial_level`` with fresh controller state."""
        self.policy_update_engine.reset(self.initial_level)

    @property
    def policy_state(self):
        return self.policy_update_engine.state

    def run(
        self,
        text: str,
        legitimate_task: bool | None = None,
        legitimate_succeeded: bool | None = None,
        attack_succeeded: bool | None = None,
        tool_sensitive: bool = False,
    ):
        legitimate_task = _check_bool(
            "legitimate_task", legitimate_task, allow_none=True
        )
        legitimate_succeeded = _check_bool(
            "legitimate_succeeded", legitimate_succeeded, allow_none=True
        )
        attack_succeeded = _check_bool(
            "attack_succeeded", attack_succeeded, allow_none=True
        )

        # 1. Detection
        detection = self.detector.detect(text)
        is_injection = detection.injection_probability >= DETECTION_THRESHOLD

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
            judged = _validate_judge_output(
                self.outcome_judge(
                    {
                        "text": text,
                        "detection": detection,
                        "risk": risk,
                        "decision": decision,
                        "defense": defense,
                    }
                )
            )
            legitimate_task = judged.get("legitimate_task", legitimate_task)
            legitimate_succeeded = judged.get(
                "legitimate_succeeded", legitimate_succeeded
            )
            attack_succeeded = judged.get("attack_succeeded", attack_succeeded)
        elif is_injection:
            # No independent judge: the detector's verdict wins over a
            # caller claim of "legitimate" (Q1 H-1).
            legitimate_task = False

        if legitimate_task is None:
            legitimate_task = not is_injection
        if legitimate_succeeded is None:
            legitimate_succeeded = True

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
