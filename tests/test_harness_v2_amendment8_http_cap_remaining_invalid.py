"""Amendment 8 — HTTP cap 640 stop: remaining episodes status INVALID (Matin decision)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_pilot_module():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class _OkTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "ok"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0.0001},
            },
        )


def test_http_cap_exhausted_marks_remaining_episodes_invalid(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59987/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    mod = _load_pilot_module()
    monkeypatch.setattr(mod, "HTTP_CAP", 1)

    schedule = [
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "qwen3",
            "condition": "A0",
        },
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 1,
            "family": "qwen3",
            "condition": "A0",
        },
    ]

    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    transport = _OkTransport()

    async def _main():
        return await mod.run_pilot_async(
            tmp_path / "cap_invalid",
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=schedule,
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    assert summary["stopped_reason"] == "http_cap"
    assert transport.request_count == 1
    episodes = [json.loads(ln) for ln in (tmp_path / "cap_invalid" / "episodes.jsonl").read_text().splitlines() if ln.strip()]
    assert len(episodes) == 2
    by_id = {e["episode_id"]: e for e in episodes}
    assert by_id["benign_weather_v1/i0/qwen3/A0"]["status"] == "COMPLETE"
    skipped = by_id["benign_weather_v1/i1/qwen3/A0"]
    assert skipped["status"] == "INVALID"
    assert skipped.get("reason") == "http_cap"
