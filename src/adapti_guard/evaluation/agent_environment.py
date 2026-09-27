"""Reproducible agent/tool environment (mock; not AgentDojo)."""
from __future__ import annotations

# Explicit execution label — not AgentDojo / not live tool execution.
EXECUTION_MODE = "OFFLINE_MOCK"
import hashlib, json
from dataclasses import dataclass, field
from typing import Any
from adapti_guard.core.models import DefenseAction
from adapti_guard.defense.tool_loop import MockToolRegistry, ToolCall, run_tool_turn

@dataclass
class EnvironmentState:
    step: int = 0
    privileged_executions: int = 0
    tool_log: list[dict[str, Any]] = field(default_factory=list)

@dataclass(frozen=True)
class AgentStepResult:
    step: int
    defense_action: str
    tool_executed: bool
    privileged_executed: bool
    state_hash: str

class AgentEnvironment:
    execution_mode = EXECUTION_MODE

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.registry = MockToolRegistry()
        self.state = EnvironmentState()
        self._privileged = frozenset({"send_email", "create_record", "retrieve_document"})

    def step(self, tool_request: ToolCall | None, defense_action: DefenseAction | str) -> AgentStepResult:
        turn = run_tool_turn(requested=tool_request, action=defense_action, registry=self.registry)
        self.state.step += 1
        priv = bool(turn.executed and tool_request and tool_request.name in self._privileged)
        if priv:
            self.state.privileged_executions += 1
        self.state.tool_log.append({"step": self.state.step, "executed": turn.executed, "priv": priv})
        sh = hashlib.sha256(json.dumps(self.state.tool_log, sort_keys=True).encode()).hexdigest()[:16]
        return AgentStepResult(self.state.step, turn.defense_action, turn.executed, priv, sh)
