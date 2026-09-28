"""Project-built OpenRouter chat/completions HTTP (Amendment 9 final — no SDK on wire path)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
from urllib.parse import urljoin


def flatten_chat_completions_payload(req_body: dict[str, Any]) -> dict[str, Any]:
    """Merge ``extra_body`` the same way the OpenAI SDK does for OpenRouter."""
    payload: dict[str, Any] = {}
    for key, value in req_body.items():
        if key == "extra_body":
            continue
        payload[key] = value
    extra = req_body.get("extra_body")
    if isinstance(extra, dict):
        payload.update(extra)
    return payload


def serialize_chat_completions_wire_body(req_body: dict[str, Any]) -> bytes:
    """Single canonical JSON bytes for storage and ``content=`` on the wire."""
    payload = flatten_chat_completions_payload(req_body)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def chat_completions_url(base_url: str) -> str:
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        return f"{root}/chat/completions"
    return urljoin(root + "/", "v1/chat/completions")


@dataclass
class RequestWireRecord:
    body: bytes
    sent_unconfirmed: bool = False
    not_sent: bool = False


class _Function:
    def __init__(self, data: dict[str, Any]) -> None:
        self.name = data.get("name")
        self.arguments = data.get("arguments")


class _ToolCall:
    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data.get("id")
        self.type = data.get("type", "function")
        fn = data.get("function") or {}
        self.function = _Function(fn if isinstance(fn, dict) else {})


class _Message:
    def __init__(self, data: dict[str, Any]) -> None:
        self.role = data.get("role")
        self.content = data.get("content")
        tcs = data.get("tool_calls")
        self.tool_calls = [_ToolCall(tc) for tc in tcs] if tcs else None


class _Choice:
    def __init__(self, data: dict[str, Any]) -> None:
        msg = data.get("message") or {}
        self.message = _Message(msg if isinstance(msg, dict) else {})
        self.finish_reason = data.get("finish_reason")


class ChatCompletionResponse:
    """Minimal shape compatible with harness v2 (``choices``, ``usage``, ``model_dump``)."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self._raw = raw
        self.choices = [_Choice(c) for c in raw.get("choices") or []]
        usage = raw.get("usage") or {}
        self.usage = SimpleNamespace(**usage) if usage else None

    def model_dump(self, *, exclude_none: bool = False) -> dict[str, Any]:
        return dict(self._raw)


def parse_chat_completions_response(raw: dict[str, Any]) -> ChatCompletionResponse:
    return ChatCompletionResponse(raw)


def semantic_payload_diff(
    project: dict[str, Any],
    sdk: dict[str, Any],
    *,
    keys: tuple[str, ...] = (
        "model",
        "messages",
        "tools",
        "tool_choice",
        "temperature",
        "max_tokens",
        "provider",
        "include_reasoning",
        "reasoning",
    ),
) -> list[str]:
    diffs: list[str] = []
    all_keys = set(project.keys()) | set(sdk.keys()) | set(keys)
    for key in sorted(all_keys):
        in_project = key in project
        in_sdk = key in sdk
        if not in_project and not in_sdk:
            continue
        pv = project.get(key, "<missing>")
        sv = sdk.get(key, "<missing>")
        if pv != sv:
            diffs.append(f"{key}: project={pv!r} sdk={sv!r}")
    return diffs
