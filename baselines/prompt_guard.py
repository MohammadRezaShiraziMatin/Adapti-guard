"""Prompt Guard baseline — uses regex fallback when model unavailable."""

from __future__ import annotations

import logging

from baselines.base import BaselineDecision, BaselineMethod
from baselines.regex_baseline import RegexBaseline

logger = logging.getLogger(__name__)


class PromptGuardBaseline(BaselineMethod):
    name = "prompt_guard"

    def __init__(self):
        self._fallback = RegexBaseline(threshold=0.4)

    def evaluate(self, prompt: str, context: str | None = None) -> BaselineDecision:
        d = self._fallback.evaluate(prompt, context)
        d.method = self.name
        d.metadata["status"] = "MODEL_UNAVAILABLE_REGEX_FALLBACK"
        return d
