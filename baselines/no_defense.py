"""No-defense baseline — passes all prompts through."""

from __future__ import annotations

from baselines.base import BaselineDecision, BaselineMethod


class NoDefenseBaseline(BaselineMethod):
    name = "no_defense"

    def evaluate(self, prompt: str, context: str | None = None) -> BaselineDecision:
        return BaselineDecision(
            method=self.name,
            allowed=True,
            action="A0",
            sanitized_prompt=prompt,
            score=0.0,
            blocked=False,
        )
