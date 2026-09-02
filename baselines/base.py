"""Baseline defense method interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaselineDecision:
    method: str
    allowed: bool
    action: str
    sanitized_prompt: str
    score: float = 0.0
    blocked: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class BaselineMethod(ABC):
    name: str = "baseline"

    @abstractmethod
    def evaluate(self, prompt: str, context: str | None = None) -> BaselineDecision:
        ...
