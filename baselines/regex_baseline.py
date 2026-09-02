"""Regex-only baseline using PromptInjectionDetector."""

from __future__ import annotations

from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector

from baselines.base import BaselineDecision, BaselineMethod


class RegexBaseline(BaselineMethod):
    name = "regex_detector"

    def __init__(self, threshold: float = 0.25):
        self.detector = PromptInjectionDetector()
        self.threshold = threshold

    def evaluate(self, prompt: str, context: str | None = None) -> BaselineDecision:
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = self.detector.detect(text)
        blocked = detection.injection_probability >= self.threshold
        action = DefenseAction.BLOCK.value if blocked else DefenseAction.NO_INTERVENTION.value
        return BaselineDecision(
            method=self.name,
            allowed=not blocked,
            action=action,
            sanitized_prompt="" if blocked else prompt,
            score=detection.injection_probability,
            blocked=blocked,
            metadata={"indicators": list(detection.indicators)},
        )
