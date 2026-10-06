"""Harness v2 B3 pre-target wrapper (does not modify historical Q1 B3 code)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from adapti_guard.evaluation.b2_matrix_contract import build_pre_target_defense_bundle

DefenseFn = Callable[[str, str | None], tuple[str, bool, str]]

# Locked verbatim replacements from DefenseActionLayer (see PREREG Rev 3).
B3_BLOCK_REPLACEMENT_CONTENT = ""
B3_SANITIZE_EMPTY_RESIDUAL = "[SANITIZED]"

# Exploratory static tool-permission arm: side-effecting tools are denied, read tools allowed.
TOOLDENY_STATIC_TOOLS = frozenset({"send_email", "create_record"})
TOOLDENY_OBSERVATION = '{"error": "tool_denied_by_static_policy"}'


@dataclass
class HarnessV2B3EpisodeContext:
    """One defense_fn invocation per append of user/tool only."""

    condition: str  # "A0" | "B3" | "CORE" | "TOOLDENY" | "ARGALLOW" (last three: exploratory arms)
    defense_fn: DefenseFn | None = None
    adaptive_state: Any | None = None
    denied_tools: frozenset[str] = frozenset()
    arg_policy: Any | None = None
    b3_log: list[dict[str, Any]] = field(default_factory=list)
    defense_fn_call_count: int = 0

    @classmethod
    def for_condition(cls, condition: str) -> HarnessV2B3EpisodeContext:
        cond = condition.upper()
        if cond == "A0":
            return cls(condition="A0", defense_fn=None, adaptive_state=None)
        if cond == "B3":
            bundle = build_pre_target_defense_bundle("B3")
            if bundle.state is not None and hasattr(bundle.state, "reset"):
                bundle.state.reset()
            return cls(
                condition="B3",
                defense_fn=bundle.defense_fn,
                adaptive_state=bundle.state,
            )
        if cond == "CORE":
            from adapti_guard.experiments.defense_baselines import make_core_defense

            fn, pipeline = make_core_defense()
            return cls(condition="CORE", defense_fn=fn, adaptive_state=pipeline)
        if cond == "TOOLDENY":
            return cls(
                condition="TOOLDENY",
                defense_fn=None,
                denied_tools=TOOLDENY_STATIC_TOOLS,
            )
        if cond == "ARGALLOW":
            from adapti_guard.evaluation.harness_v2.argallow_policy import default_policy

            return cls(condition="ARGALLOW", defense_fn=None, arg_policy=default_policy())
        raise ValueError(f"unknown condition {condition!r}")

    def tool_denied(self, tool_name: str, arguments: dict[str, Any] | None = None) -> bool:
        if tool_name in self.denied_tools:
            return True
        return self.arg_policy is not None and self.arg_policy.denies(tool_name, arguments)

    def denial_observation(self) -> str:
        if self.arg_policy is not None:
            from adapti_guard.evaluation.harness_v2.argallow_policy import ARGALLOW_OBSERVATION

            return ARGALLOW_OBSERVATION
        return TOOLDENY_OBSERVATION


def append_user_message(
    messages: list[dict[str, Any]],
    content: str,
    ctx: HarnessV2B3EpisodeContext | None,
) -> int:
    """Append user message; B3 transform runs once here (never on resend)."""
    if ctx is None or ctx.condition == "A0" or ctx.defense_fn is None:
        messages.append({"role": "user", "content": content})
        return len(messages) - 1
    return _append_defended(messages, role="user", content=content, ctx=ctx)


def append_tool_message(
    messages: list[dict[str, Any]],
    *,
    tool_call_id: str,
    content: str,
    ctx: HarnessV2B3EpisodeContext | None,
) -> int:
    if ctx is None or ctx.condition == "A0" or ctx.defense_fn is None:
        messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": content})
        return len(messages) - 1
    idx = _append_defended(messages, role="tool", content=content, ctx=ctx, tool_call_id=tool_call_id)
    messages[-1]["tool_call_id"] = tool_call_id
    return idx


def _append_defended(
    messages: list[dict[str, Any]],
    *,
    role: str,
    content: str,
    ctx: HarnessV2B3EpisodeContext,
    tool_call_id: str | None = None,
) -> int:
    action, blocked, transformed = ctx.defense_fn(content, None)  # type: ignore[misc]
    out_text = B3_BLOCK_REPLACEMENT_CONTENT if blocked else transformed
    ctx.defense_fn_call_count += 1
    message_index = len(messages)
    entry: dict[str, Any] = {
        "message_index": message_index,
        "role": role,
        "defense_action": action,
        "blocked": blocked,
        "defense_fn_call_ordinal": ctx.defense_fn_call_count,
    }
    ctx.b3_log.append(entry)
    msg: dict[str, Any] = {"role": role, "content": out_text}
    if tool_call_id is not None:
        msg["tool_call_id"] = tool_call_id
    messages.append(msg)
    return message_index


def count_user_tool_messages(messages: list[dict[str, Any]]) -> int:
    return sum(1 for m in messages if m.get("role") in ("user", "tool"))
