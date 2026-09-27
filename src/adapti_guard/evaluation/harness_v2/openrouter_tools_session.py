"""Run multi-turn OpenRouter chat with native tools + trajectory capture."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.tool_definitions import HARNESS_V2_TOOLS
from adapti_guard.evaluation.target_model import _openrouter_assistant_text, _openrouter_usage_dict


@dataclass
class HarnessV2CallRecord:
    call_index: int
    scenario_id: str
    model_id: str
    messages_before: list[dict[str, Any]]
    request: dict[str, Any]
    raw_response: dict[str, Any]
    assistant_content: str
    tool_calls: list[dict[str, Any]]
    usage: dict[str, Any]
    cost_usd: float | None
    provider_error: str | None
    latency_ms: float


@dataclass
class HarnessV2EpisodeTrajectory:
    scenario_id: str
    model_id: str
    config_key: str
    system_prompt: str
    calls: list[HarnessV2CallRecord] = field(default_factory=list)
    final_messages: list[dict[str, Any]] = field(default_factory=list)
    mock_tool_log: list[dict[str, Any]] = field(default_factory=list)


def _message_to_dict(msg: Any) -> dict[str, Any]:
    if hasattr(msg, "model_dump"):
        return msg.model_dump(exclude_none=True)
    out: dict[str, Any] = {"role": getattr(msg, "role", None), "content": getattr(msg, "content", None)}
    tcs = getattr(msg, "tool_calls", None)
    if tcs:
        out["tool_calls"] = [_message_to_dict(tc) if hasattr(tc, "model_dump") else tc for tc in tcs]
    return out


def _response_to_dict(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        return response.model_dump(exclude_none=True)
    return json.loads(response.model_dump_json()) if hasattr(response, "model_dump_json") else {"raw": str(response)}


def run_tools_episode(
    *,
    scenario_id: str,
    model_id: str,
    config_key: str,
    system_prompt: str,
    initial_user: str,
    executor: HarnessV2MockToolExecutor,
    max_rounds: int = 4,
    max_tokens: int = 512,
    temperature: float = 0.0,
    pricing_cost_fn: Any | None = None,
    call_index_start: int = 1,
) -> HarnessV2EpisodeTrajectory:
    from openai import OpenAI

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key, timeout=120.0)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_user},
    ]
    traj = HarnessV2EpisodeTrajectory(
        scenario_id=scenario_id,
        model_id=model_id,
        config_key=config_key,
        system_prompt=system_prompt,
    )
    call_index = call_index_start
    extra_body = {
        "provider": {
            "order": ["DeepInfra"],
            "allow_fallbacks": False,
            "require_parameters": True,
        }
    }

    for _round in range(max_rounds):
        req_body = {
            "model": model_id,
            "messages": messages,
            "tools": HARNESS_V2_TOOLS,
            "tool_choice": "auto",
            "temperature": temperature,
            "max_tokens": max_tokens,
            "extra_body": extra_body,
        }
        start = time.perf_counter()
        provider_error = None
        raw: dict[str, Any] = {}
        assistant_content = ""
        tool_calls_serialized: list[dict[str, Any]] = []
        usage: dict[str, Any] = {}
        cost_usd = None
        messages_before = json.loads(json.dumps(messages))
        try:
            response = client.chat.completions.create(**req_body)
            latency_ms = (time.perf_counter() - start) * 1000.0
            raw = _response_to_dict(response)
            msg = response.choices[0].message
            assistant_content = _openrouter_assistant_text(msg)
            usage = _openrouter_usage_dict(response.usage)
            if pricing_cost_fn:
                cost_usd = pricing_cost_fn(usage, model_id=model_id)
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    fn = tc.function
                    tool_calls_serialized.append(
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {"name": fn.name, "arguments": fn.arguments},
                        }
                    )
                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": tool_calls_serialized,
                }
                messages.append(assistant_msg)
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    obs = executor.execute(name=tc.function.name, arguments=args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": obs,
                        }
                    )
                traj.calls.append(
                    HarnessV2CallRecord(
                        call_index=call_index,
                        scenario_id=scenario_id,
                        model_id=model_id,
                        messages_before=messages_before,
                        request=req_body,
                        raw_response=raw,
                        assistant_content=assistant_content,
                        tool_calls=tool_calls_serialized,
                        usage=usage,
                        cost_usd=cost_usd,
                        provider_error=None,
                        latency_ms=latency_ms,
                    )
                )
                call_index += 1
                continue
            messages.append({"role": "assistant", "content": assistant_content})
            traj.calls.append(
                HarnessV2CallRecord(
                    call_index=call_index,
                    scenario_id=scenario_id,
                    model_id=model_id,
                    messages_before=messages_before,
                    request=req_body,
                    raw_response=raw,
                    assistant_content=assistant_content,
                    tool_calls=[],
                    usage=usage,
                    cost_usd=cost_usd,
                    provider_error=None,
                    latency_ms=latency_ms,
                )
            )
            call_index += 1
            break
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000.0
            provider_error = f"{type(exc).__name__}: {exc}"
            traj.calls.append(
                HarnessV2CallRecord(
                    call_index=call_index,
                    scenario_id=scenario_id,
                    model_id=model_id,
                    messages_before=messages_before,
                    request=req_body,
                    raw_response=raw,
                    assistant_content="",
                    tool_calls=[],
                    usage=usage,
                    cost_usd=cost_usd,
                    provider_error=provider_error,
                    latency_ms=latency_ms,
                )
            )
            call_index += 1
            break

    traj.final_messages = messages
    traj.mock_tool_log = list(executor.call_log)
    return traj
