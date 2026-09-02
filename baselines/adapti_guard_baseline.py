"""ADAPTI-GUARD baseline wrapper."""

from __future__ import annotations

from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.defense.action_layer import DefenseActionLayer
from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
from src.adapti_guard.risk.risk_engine import RiskEngine

from baselines.base import BaselineDecision, BaselineMethod


class AdaptiGuardBaseline(BaselineMethod):
    name = "adapti_guard"

    def __init__(self, defense_level: int = 1):
        self.defense_level = defense_level
        self.detector = PromptInjectionDetector()
        self.risk_engine = RiskEngine()
        self.policy_engine = DefensePolicyEngine()
        self.action_layer = DefenseActionLayer()

    def evaluate(self, prompt: str, context: str | None = None) -> BaselineDecision:
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = self.detector.detect(text)
        risk = self.risk_engine.assess(detection)
        decision = self.policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=self.defense_level
        )
        defense = self.action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)
        return BaselineDecision(
            method=self.name,
            allowed=not blocked,
            action=action,
            sanitized_prompt=defense.content if not blocked else "",
            score=detection.injection_probability,
            blocked=blocked,
            metadata={"risk_level": risk.level if hasattr(risk, "level") else str(risk)},
        )
