"""Minimal mock tool loop with A2 permission enforcement.

This is infrastructure for Layer A L2. It is not a live LLM evaluation.
A2 must actually deny tool execution; A3 denies the turn; A0/A1 allow tools.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from src.adapti_guard.core.models import DefenseAction

_TOOL_REQUEST_RE = re.compile(r"TOOL_REQUEST:\s*(\{.*\})", re.DOTALL)


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


def _coerce_tool_call(blob: Any) -> ToolCall | None:
    if blob is None:
        return None
    if isinstance(blob, ToolCall):
        return blob
    if isinstance(blob, Mapping) and blob.get("name"):
        args = blob.get("arguments") or blob.get("args") or {}
        if not isinstance(args, dict):
            args = {}
        return ToolCall(name=str(blob["name"]), arguments=args)
    return None


def _parse_tool_request_text(text: str) -> dict[str, Any] | None:
    match = _TOOL_REQUEST_RE.search(text or "")
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def extract_tool_request(
    *,
    model_response: str = "",
    generation_raw: Mapping[str, Any] | None = None,
    record: Mapping[str, Any] | None = None,
) -> ToolCall | None:
    """Resolve a tool request from model output first, then the episode record."""
    blob: Any = None
    if generation_raw and generation_raw.get("tool_call"):
        blob = generation_raw.get("tool_call")
    if blob is None:
        blob = _parse_tool_request_text(model_response)
    if blob is None and record is not None:
        blob = record.get("tool_call")
        if blob is None:
            meta = record.get("metadata")
            if isinstance(meta, Mapping):
                blob = meta.get("tool_call")
    return _coerce_tool_call(blob)


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
