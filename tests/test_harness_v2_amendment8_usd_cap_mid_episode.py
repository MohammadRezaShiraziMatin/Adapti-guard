"""Amendment 8 — USD cap mid-episode persists cut + remaining schedule rows (mock pilot)."""
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


class _StopTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
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


def test_usd_cap_mid_episode_invalid_and_remaining_not_run(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59991/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    mod = _load_pilot_module()

    eid1 = "benign_weather_v1/i0/qwen3/A0"
    eid2 = "benign_weather_v1/i0/gemma/A0"
    eid3 = "benign_weather_v1/i0/llama/A0"
    schedule = [
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "qwen3",
            "condition": "A0",
        },
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "gemma",
            "condition": "A0",
        },
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "llama",
            "condition": "A0",
        },
    ]

    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    async def _main():
        return await mod.run_pilot_async(
            tmp_path / "usd_cap",
            usd_cap=0.00015,
            http_transport=_StopTransport(),
            schedule_override=schedule,
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    assert summary["stopped_reason"] == "budget_cap"

    episodes = [
        json.loads(ln)
        for ln in (tmp_path / "usd_cap" / "episodes.jsonl").read_text().splitlines()
        if ln.strip()
    ]
    assert len(episodes) == 3
    by_id = {ep["episode_id"]: ep for ep in episodes}
    assert set(by_id) == {eid1, eid2, eid3}
    assert by_id[eid1]["status"] == "COMPLETE"
    assert by_id[eid2]["status"] == "INVALID"
    assert by_id[eid2].get("reason") == "usd_cap"
    assert by_id[eid3]["status"] == "NOT_RUN"
    assert by_id[eid3].get("reason") == "usd_cap"
