"""Detector interface for scientific extensibility."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.adapti_guard.core.models import DetectionResult
from src.adapti_guard.detector.prompt_injection_detector import (
    PromptInjectionDetector,
)


class Detector(ABC):
    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        raise NotImplementedError

    @property
    def version(self) -> str:
        return "unknown"


class RegexDetector(Detector):
    """Production regex/heuristic detector (current default)."""

    def __init__(self):
        self._inner = PromptInjectionDetector()

    @property
    def version(self) -> str:
        return "regex_v18"

    def detect(self, text: str) -> DetectionResult:
        return self._inner.detect(text)


class ClassifierDetector(Detector):
    """Placeholder for ML classifier detector."""

    def detect(self, text: str) -> DetectionResult:
        raise NotImplementedError("ClassifierDetector not implemented")


class LLMDetector(Detector):
    """Placeholder for LLM-based moderation detector."""

    def detect(self, text: str) -> DetectionResult:
        raise NotImplementedError("LLMDetector not implemented")
