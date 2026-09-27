"""Amendment 8 wired integration — mock transport, real async pilot path."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_run_pilot_async():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.run_pilot_async


def _stop_completion(gen_suffix: str = "1") -> dict:
    return {
        "id": f"gen-mock-{gen_suffix}",
        "choices": [
            {
                "message": {"role": "assistant", "content": "Done."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "cost": 0.0001},
    }


class _PilotIntegrationTransport(httpx.AsyncBaseTransport):
    def __init__(self, steps: list[str]) -> None:
        self._steps = iter(steps)
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        step = next(self._steps, "200")
        if step == "hang":
            await asyncio.Event().wait()
        if step == "429":
            return httpx.Response(
                429,
                json={"error": {"message": "rate limited", "code": 429}},
            )
        return httpx.Response(200, json=_stop_completion(str(self.request_count)))


def test_wired_pilot_run_pack_mock_transport(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59997/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    transport = _PilotIntegrationTransport(["hang", "429", "200", "200"])
    loop_ids: list[int] = []

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
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "qwen3",
            "condition": "B3",
        },
    ]

    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    run_pilot_async = _load_run_pilot_async()
    out = tmp_path / "pack"

    async def _main():
        return await run_pilot_async(
            out,
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=schedule,
            wall_timeout_s=0.25,
            rate_limit_backoffs=(0.0, 0.0),
            loop_id_probe=loop_ids,
            episode_wall_x_override=0.0,
            skip_preflight=True,
            reconcile_at_end=False,
        )

    run_harness_event_loop(_main)

    stream = [json.loads(ln) for ln in out.joinpath("http_stream.jsonl").read_text().splitlines() if ln.strip()]
    ledger = [json.loads(ln) for ln in out.joinpath("ledger_rows.jsonl").read_text().splitlines() if ln.strip()]
    assert len(stream) == len(ledger)
    assert transport.request_count == len(stream)

    cancelled = [r for r in stream if r.get("status") == "cancelled_timeout"]
    assert len(cancelled) == 1
    assert cancelled[0]["cost_usd"] is None
    assert cancelled[0]["billed_placeholder_usd"] > 0
    assert cancelled[0]["reconciliation_source"] == "pending"

    rate_limited = [r for r in stream if r.get("retried_after_rate_limit")]
    assert len(rate_limited) == 1
    rl_idx = stream.index(rate_limited[0])
    assert rate_limited[0]["request_id"] != stream[rl_idx + 1]["request_id"]

    episodes = [json.loads(ln) for ln in out.joinpath("episodes.jsonl").read_text().splitlines() if ln.strip()]
    invalid = [e for e in episodes if e.get("status") == "INVALID_TIMEOUT"]
    assert len(invalid) == 1

    assert len(set(loop_ids)) == 1
