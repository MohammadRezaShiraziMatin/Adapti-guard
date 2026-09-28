"""HTTP cap mid-episode during tool round -> INVALID + reason http_cap."""
from __future__ import annotations

import importlib.util
import json
import sys
import uuid
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

EPISODE_ID = "benign_weather_v1/i0/qwen3/A0"


class _ToolThenStopTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        if self.request_count == 1:
            tc_id = f"call_{uuid.uuid4().hex[:8]}"
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "",
                                "tool_calls": [
                                    {
                                        "id": tc_id,
                                        "type": "function",
                                        "function": {
                                            "name": "get_weather",
                                            "arguments": json.dumps({"city": "Boston"}),
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.00005},
                },
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Done."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0.0001},
            },
        )


def _load_pilot_module():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_http_cap_blocks_second_tool_round_request(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59986/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    mod = _load_pilot_module()
    monkeypatch.setattr(mod, "HTTP_CAP", 1)

    transport = _ToolThenStopTransport()
    schedule = [
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "qwen3",
            "condition": "A0",
        },
    ]

    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    async def _main():
        return await mod.run_pilot_async(
            tmp_path / "tool_cut",
            pilot_label="harness_v2_pilot_0",
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=schedule,
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    assert transport.request_count == 1
    assert summary["stopped_reason"] == "http_cap"
    episodes = [json.loads(ln) for ln in (tmp_path / "tool_cut" / "episodes.jsonl").read_text().splitlines() if ln.strip()]
    assert len(episodes) == 1
    ep = episodes[0]
    assert ep["episode_id"] == EPISODE_ID
    assert ep["status"] == "INVALID"
    assert ep.get("reason") == "http_cap"
