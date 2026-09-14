"""Minimal mock tool loop with A2 permission enforcement.

This is infrastructure for Layer A L2. It is not a live LLM evaluation.
A2 must actually deny tool execution; A3 denies the turn; A0/A1 allow tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.adapti_guard.core.models import DefenseAction


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolLoopTurn:
    requested: ToolCall | None
    defense_action: str
    permission_allowed: bool
    executed: bool
    observation: str
    log: dict[str, Any] = field(default_factory=dict)


class MockToolRegistry:
    def __init__(self) -> None:
        self.calls: list[ToolCall] = []

    def search(self, query: str) -> str:
        return f"search_hits: {query}"

    def retrieve_document(self, doc_id: str) -> str:
        return f"document[{doc_id}]=lorem"

    def send_email(self, to: str, body: str) -> str:
        return f"queued email to {to}: {body[:40]}"

    def create_record(self, kind: str, payload: str) -> str:
        return f"created {kind} record"

    def execute(self, call: ToolCall) -> str:
        self.calls.append(call)
        fn = getattr(self, call.name, None)
        if fn is None:
            return f"unknown_tool:{call.name}"
        return str(fn(**call.arguments))


def tool_allowed(action: DefenseAction | str) -> bool:
    value = action.value if isinstance(action, DefenseAction) else str(action)
    if value in {"A2", "A3"}:
        return False
    return True


def run_tool_turn(
    *,
    requested: ToolCall | None,
    action: DefenseAction | str,
    registry: MockToolRegistry,
) -> ToolLoopTurn:
    value = action.value if isinstance(action, DefenseAction) else str(action)
    if requested is None:
        return ToolLoopTurn(
            requested=None,
            defense_action=value,
            permission_allowed=True,
            executed=False,
            observation="",
            log={"reason": "no_tool_requested"},
        )
    if value == "A3":
        return ToolLoopTurn(
            requested=requested,
            defense_action=value,
            permission_allowed=False,
            executed=False,
            observation="",
            log={"reason": "turn_blocked"},
        )
    if not tool_allowed(action):
        return ToolLoopTurn(
            requested=requested,
            defense_action=value,
            permission_allowed=False,
            executed=False,
            observation="TOOL_DENIED",
            log={"reason": "a2_tool_restriction", "tool": requested.name},
        )
    output = registry.execute(requested)
    return ToolLoopTurn(
        requested=requested,
        defense_action=value,
        permission_allowed=True,
        executed=True,
        observation=output,
        log={"reason": "executed", "tool": requested.name},
    )
