"""Episode input, context builder, and inspectable traces (Phase 1 core).

Runtime objects here must not carry gold labels. Privilege is inferred from
the declared/requested tool name only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

_FORBIDDEN_GOLD_KEYS = frozenset(
    {"is_attack", "label", "gold_label", "category", "attack_family"}
)

PRIVILEGED_TOOLS = frozenset({"send_email", "create_record", "retrieve_document"})


def _reject_gold(mapping: Mapping[str, Any] | None) -> None:
    if not mapping:
        return
    leaked = _FORBIDDEN_GOLD_KEYS.intersection(mapping.keys())
    if leaked:
        raise ValueError(f"gold keys are forbidden in core episode input: {sorted(leaked)}")


@dataclass(frozen=True)
class EpisodeInput:
    prompt: str
    context: str = ""
    tool_name: str | None = None
    tool_arguments: dict[str, Any] = field(default_factory=dict)
    tool_output: str | None = None

    def __post_init__(self) -> None:
        _reject_gold(self.tool_arguments)


@dataclass(frozen=True)
class BuiltContext:
    prompt: str
    context: str
    tool_name: str | None
    tool_arguments: dict[str, Any]
    tool_output: str | None
    privileged_tool: bool
    tool_sensitive: bool


class ContextBuilder:
    """Structured view of one episode. Label-blind."""

    privileged_tools = PRIVILEGED_TOOLS

    def build(
        self,
        inp: EpisodeInput | Mapping[str, Any],
        **kwargs: Any,
    ) -> BuiltContext:
        _reject_gold(kwargs)
        if isinstance(inp, Mapping):
            _reject_gold(inp)
            prompt = str(inp.get("prompt", ""))
            context = str(inp.get("context") or "")
            tool_name = inp.get("tool_name")
            tool_arguments = dict(inp.get("tool_arguments") or {})
            tool_output = inp.get("tool_output")
            blob = inp.get("tool_call")
            if tool_name is None and isinstance(blob, Mapping):
                tool_name = blob.get("name")
                tool_arguments = dict(blob.get("arguments") or blob.get("args") or {})
        else:
            prompt = inp.prompt
            context = inp.context
            tool_name = inp.tool_name
            tool_arguments = dict(inp.tool_arguments or {})
            tool_output = inp.tool_output
        name = str(tool_name) if tool_name else None
        privileged = bool(name and name in self.privileged_tools)
        return BuiltContext(
            prompt=prompt or "",
            context=context or "",
            tool_name=name,
            tool_arguments=tool_arguments,
            tool_output=str(tool_output) if tool_output else None,
            privileged_tool=privileged,
            tool_sensitive=privileged,
        )


@dataclass
class EpisodeTrace:
    prompt: str
    context_present: bool
    tool_name: str | None
    privileged_tool: bool
    detector_probability: float
    detector_indicators: list[str]
    detector_hit: bool
    risk_score: float
    risk_level: str
    risk_reasons: list[str]
    risk_features: dict[str, Any]
    policy_action: str
    policy_reason: str
    defense_level: int
    blocked: bool
    allowed: bool
    content: str
    tool_access: bool
    tool_requested: str | None
    tool_permission_allowed: bool | None
    tool_executed: bool
    tool_observation: str
    tool_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "privileged_tool": self.privileged_tool,
            "detector_probability": self.detector_probability,
            "detector_indicators": list(self.detector_indicators),
            "detector_hit": self.detector_hit,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "risk_reasons": list(self.risk_reasons),
            "risk_features": dict(self.risk_features),
            "policy_action": self.policy_action,
            "policy_reason": self.policy_reason,
            "defense_level": self.defense_level,
            "blocked": self.blocked,
            "allowed": self.allowed,
            "tool_access": self.tool_access,
            "tool_requested": self.tool_requested,
            "tool_permission_allowed": self.tool_permission_allowed,
            "tool_executed": self.tool_executed,
            "tool_observation": self.tool_observation,
            "tool_reason": self.tool_reason,
        }
