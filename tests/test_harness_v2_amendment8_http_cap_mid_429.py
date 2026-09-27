"""Amendment 8 item N — HTTP cap blocks mid-episode 429 retry (mock pilot)."""
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


class _429ThenOkTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        if self.request_count == 1:
            return httpx.Response(
                200,
                json={"error": {"message": "rate limited", "code": 429}},
            )
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


def test_http_cap_one_blocks_second_attempt_on_429_retry(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59989/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    mod = _load_pilot_module()
    monkeypatch.setattr(mod, "HTTP_CAP", 1)

    transport = _429ThenOkTransport()
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
            tmp_path / "cap1",
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=schedule,
            rate_limit_backoffs=(0.0, 0.0),
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    assert transport.request_count == 1
    stream = [json.loads(ln) for ln in (tmp_path / "cap1" / "http_stream.jsonl").read_text().splitlines() if ln.strip()]
    ledger = [json.loads(ln) for ln in (tmp_path / "cap1" / "ledger_rows.jsonl").read_text().splitlines() if ln.strip()]
    assert len(stream) == len(ledger) == 1 == mod.HTTP_CAP
    row = stream[0]
    assert row.get("retried_after_rate_limit") is not True
    assert row.get("retry_blocked_by_http_cap") is True
    led = json.loads((tmp_path / "cap1" / "running_ledger.json").read_text())
    assert led["http_used"] == 1
    episodes = [json.loads(ln) for ln in (tmp_path / "cap1" / "episodes.jsonl").read_text().splitlines() if ln.strip()]
    assert len(episodes) == 1
    eid = "benign_weather_v1/i0/qwen3/A0"
    assert episodes[0]["episode_id"] == eid
    assert episodes[0]["status"] == "INVALID"
    assert episodes[0].get("reason") == "http_cap"
    assert summary["stopped_reason"] == "http_cap"
