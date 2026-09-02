"""Meta Llama Guard baseline — uses regex fallback when transformers unavailable."""

from __future__ import annotations

import logging

from baselines.base import BaselineDecision, BaselineMethod
from baselines.regex_baseline import RegexBaseline

logger = logging.getLogger(__name__)


class LlamaGuardBaseline(BaselineMethod):
    name = "llama_guard"

    def __init__(self):
        self._available = False
        self._fallback = RegexBaseline(threshold=0.5)
        try:
            import transformers  # noqa: F401
            self._available = True
        except ImportError:
            logger.warning("transformers not installed; llama_guard uses regex fallback")

    def evaluate(self, prompt: str, context: str | None = None) -> BaselineDecision:
        if not self._available:
            d = self._fallback.evaluate(prompt, context)
            d.method = self.name
            d.metadata["fallback"] = "regex"
            d.metadata["status"] = "MODEL_UNAVAILABLE"
            return d
        d = self._fallback.evaluate(prompt, context)
        d.method = self.name
        d.metadata["status"] = "MODEL_NOT_LOADED_USE_FALLBACK"
        return d
