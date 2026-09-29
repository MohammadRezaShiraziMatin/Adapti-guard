"""Amendment 8 item E — provider error body path via run_pilot_async (mock transport only)."""
from __future__ import annotations

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


class _ProviderErrorTransport(httpx.AsyncBaseTransport):
    def __init__(self, steps: list[str]) -> None:
        self._steps = iter(steps)
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        step = next(self._steps, "200")
        if step == "err504":
            return httpx.Response(
                200,
                json={"error": {"message": "upstream gateway timeout", "code": 504}},
            )
        if step == "err429":
            return httpx.Response(
                200,
                json={"error": {"message": "rate limited", "code": 429}},
            )
        return httpx.Response(200, json=_stop_completion(str(self.request_count)))


def test_pilot_provider_error_504_and_json_429_retry(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59995/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    transport = _ProviderErrorTransport(["err504", "err429", "200"])
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

    run_pilot_async = _load_run_pilot_async()
    out = tmp_path / "pack"

    async def _main():
        return await run_pilot_async(
            out,
            pilot_label="harness_v2_pilot_0",
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=schedule,
            rate_limit_backoffs=(0.0, 0.0),
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    assert summary["stopped_reason"] == "completed"

    stream = [json.loads(ln) for ln in out.joinpath("http_stream.jsonl").read_text().splitlines() if ln.strip()]
    ledger = [json.loads(ln) for ln in out.joinpath("ledger_rows.jsonl").read_text().splitlines() if ln.strip()]
    assert transport.request_count == len(stream) == len(ledger) == 3

    pe_rows = [r for r in stream if r.get("status") == "provider_error"]
    assert len(pe_rows) == 1
    assert pe_rows[0]["cost_usd"] is None
    assert pe_rows[0]["raw_response"].get("error", {}).get("code") == 504
    assert pe_rows[0]["provider_error"]

    rl_rows = [r for r in stream if r.get("retried_after_rate_limit")]
    assert len(rl_rows) == 1
    assert rl_rows[0]["cost_usd"] is None
    assert rl_rows[0]["billed_placeholder_usd"] == 0.0
    assert rl_rows[0]["reconciliation_source"] == "assumed_unbilled_429"

    episodes = [json.loads(ln) for ln in out.joinpath("episodes.jsonl").read_text().splitlines() if ln.strip()]
    statuses = {e["episode_id"]: e["status"] for e in episodes}
    assert statuses["benign_weather_v1/i0/qwen3/A0"] == "INVALID_PROVIDER_ERROR"
    assert statuses["benign_weather_v1/i1/qwen3/A0"] == "COMPLETE"
