"""Defense baseline factories for real LLM evaluation (B0–B3)."""

from __future__ import annotations

from typing import Callable

DefenseFn = Callable[[str, str | None], tuple[str, bool, str]]


def make_b0_no_defense() -> DefenseFn:
    def fn(prompt: str, context: str | None = None):
        return "A0", False, prompt

    return fn


def make_b1_rule_based(threshold: float = 0.25) -> DefenseFn:
    from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector

    detector = PromptInjectionDetector()

    def fn(prompt: str, context: str | None = None):
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = detector.detect(text)
        blocked = detection.injection_probability >= threshold
        action = "A3" if blocked else "A0"
        return action, blocked, "" if blocked else prompt

    return fn


def make_b2_fixed_defense(level: int) -> DefenseFn:
    from src.adapti_guard.defense.action_layer import DefenseActionLayer
    from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
    from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
    from src.adapti_guard.risk.risk_engine import RiskEngine

    detector = PromptInjectionDetector()
    risk_engine = RiskEngine()
    policy_engine = DefensePolicyEngine()
    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None):
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = detector.detect(text)
        risk = risk_engine.assess(detection)
        decision = policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=level
        )
        defense = action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)
        return action, blocked, defense.content if not blocked else ""

    return fn


class AdaptiveDefenseState:
    """Stateful B3 adaptive defense for sequential evaluation."""

    def __init__(self, initial_level: int = 1):
        from src.adapti_guard.adaptation.feedback_engine import FeedbackEngine
        from src.adapti_guard.adaptation.policy_update_engine import PolicyUpdateEngine
        from src.adapti_guard.defense.action_layer import DefenseActionLayer
        from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
        from src.adapti_guard.evaluation.attack_outcome import attack_succeeded
        from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
        from src.adapti_guard.risk.risk_engine import RiskEngine

        self.detector = PromptInjectionDetector()
        self.risk_engine = RiskEngine()
        self.policy_engine = DefensePolicyEngine()
        self.action_layer = DefenseActionLayer()
        self.feedback_engine = FeedbackEngine()
        self.policy_update = PolicyUpdateEngine()
        self.policy_update.state.defense_level = initial_level
        self._attack_succeeded = attack_succeeded
        self._last_outcome: dict | None = None

    def reset(self) -> None:
        from src.adapti_guard.adaptation.policy_update_engine import PolicyState

        self.policy_update.state = PolicyState(defense_level=1)
        self._last_outcome = None

    def evaluate(self, prompt: str, context: str | None, *, is_attack: bool, category: str):
        from src.adapti_guard.core.models import DefenseAction
        from src.adapti_guard.evaluation.outcome_evaluator import OutcomeResult

        if self._last_outcome is not None:
            prev = self._last_outcome
            outcome = OutcomeResult(
                attack_success=prev["attack_success"],
                legitimate_success=prev["legitimate_success"],
                attack_present=prev["is_attack"],
                legitimate_task=not prev["is_attack"],
                defense_cost=prev["defense_cost"],
                security_score=0.0 if prev["attack_success"] else 1.0,
                utility_score=1.0 if prev["legitimate_success"] else 0.0,
            )
            feedback = self.feedback_engine.generate(outcome)
            self.policy_update.update(feedback)

        level = self.policy_update.state.defense_level
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = self.detector.detect(text)
        risk = self.risk_engine.assess(detection)
        decision = self.policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=level
        )
        defense = self.action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)

        cost_map = {"A0": 0.0, "A1": 0.1, "A2": 0.25, "A3": 0.5}
        attack_success = (
            self._attack_succeeded(decision.action, category, defense) if is_attack else False
        )
        legitimate_success = (not blocked) and action in {"A0", "A1", "A2"}

        self._last_outcome = {
            "is_attack": is_attack,
            "attack_success": attack_success,
            "legitimate_success": legitimate_success,
            "defense_cost": cost_map.get(action, 0.0),
        }

        return action, blocked, defense.content if not blocked else ""


def make_b3_adaptive() -> tuple[DefenseFn, AdaptiveDefenseState]:
    state = AdaptiveDefenseState()

    def fn(prompt: str, context: str | None = None, **_kwargs):
        is_attack = _kwargs.get("is_attack", True)
        category = _kwargs.get("category", "unknown")
        return state.evaluate(prompt, context, is_attack=is_attack, category=category)

    return fn, state


BASELINE_FACTORIES: dict[str, Callable[[], DefenseFn]] = {
    "B0": make_b0_no_defense,
    "B1": make_b1_rule_based,
    "B2_L1": lambda: make_b2_fixed_defense(1),
    "B2_L2": lambda: make_b2_fixed_defense(2),
    "B2_L3": lambda: make_b2_fixed_defense(3),
}


def get_defense_fn(baseline_key: str) -> tuple[DefenseFn, object | None]:
    """Return defense function and optional state object (B3/B6 adaptive only)."""
    if baseline_key in ("B3", "B6"):
        return make_b3_adaptive()
    if baseline_key not in BASELINE_FACTORIES:
        raise KeyError(f"Unknown baseline: {baseline_key}")
    return BASELINE_FACTORIES[baseline_key](), None
