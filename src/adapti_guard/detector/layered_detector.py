"""Layered detector: hardened regex plus an optional semantic guard.

The regex layer is fast and free but only recognises phrasings it was
designed against. The semantic layer is any callable ``str -> bool``
(typically a small LLM classifier prompted to answer INJECTION/SAFE); it
is supplied by the caller, so the library makes no network calls itself.
A text is flagged when either layer flags it.
"""

from __future__ import annotations

from collections.abc import Callable

from adapti_guard.core.models import DetectionResult
from adapti_guard.detector.hardened_detector import (
    EXTRA_SCORE,
    HardenedPromptInjectionDetector,
)

SEMANTIC_INDICATOR = "semantic_guard"
SEMANTIC_ERROR_INDICATOR = "semantic_guard_error"


class LayeredPromptInjectionDetector(HardenedPromptInjectionDetector):
    def __init__(
        self,
        semantic_guard: Callable[[str], bool] | None = None,
        *,
        fail_closed: bool = False,
    ):
        super().__init__()
        self.semantic_guard = semantic_guard
        self.fail_closed = fail_closed

    def detect(self, text: str) -> DetectionResult:
        result = super().detect(text)
        if self.semantic_guard is None:
            return result
        try:
            flagged = bool(self.semantic_guard(text))
        except Exception:  # noqa: BLE001 - a guard outage must not crash the pipeline
            indicators = [*result.indicators, SEMANTIC_ERROR_INDICATOR]
            score = max(result.injection_probability, EXTRA_SCORE) if self.fail_closed else result.injection_probability
            return DetectionResult(injection_probability=score, indicators=indicators)
        if not flagged:
            return result
        return DetectionResult(
            injection_probability=max(result.injection_probability, EXTRA_SCORE),
            indicators=[*result.indicators, SEMANTIC_INDICATOR],
        )
