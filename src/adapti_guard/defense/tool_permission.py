"""Explicit tool-permission gate (enforcement, not policy)."""

from __future__ import annotations

from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.defense.tool_loop import (
    MockToolRegistry,
    ToolCall,
    ToolLoopTurn,
    run_tool_turn,
    tool_allowed,
)


class ToolPermissionGate:
    """Allow/deny tool execution from the selected action, outside prompt text."""

    def apply(
        self,
        *,
        requested: ToolCall | None,
        action: DefenseAction | str,
        registry: MockToolRegistry,
    ) -> ToolLoopTurn:
        return run_tool_turn(requested=requested, action=action, registry=registry)

    @staticmethod
    def allows(action: DefenseAction | str) -> bool:
        return tool_allowed(action)
