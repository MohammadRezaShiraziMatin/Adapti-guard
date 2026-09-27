"""Amendment 8 item R — combined mock pilot integration (all fixes in one run)."""
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


def _load_run_pilot_async():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.run_pilot_async


def _stop_completion(suffix: str = "1") -> dict:
    return {
        "id": f"gen-ok-{suffix}",
        "choices": [
            {
                "message": {"role": "assistant", "content": "Done."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18, "cost": 0.0001},
    }


class _Amendment8ComboTransport(httpx.AsyncBaseTransport):
    """Global HTTP script across episodes (one step consumed per request)."""

    def __init__(self, steps: list[str]) -> None:
        self._steps = iter(steps)
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        step = next(self._steps, "200")
        if step == "hang":
            import asyncio

            await asyncio.Event().wait()
        if step == "tool_weather":
            tc_id = f"call_{uuid.uuid4().hex[:8]}"
            return httpx.Response(
                200,
                json={
                    "id": f"gen-tool-{self.request_count}",
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
                    "usage": {"prompt_tokens": 20, "completion_tokens": 10, "cost": 0.00005},
                },
            )
        if step == "err429json":
            return httpx.Response(
                200,
                json={"error": {"message": "rate limited", "code": 429}},
            )
        if step == "err504":
            return httpx.Response(
                200,
                json={"error": {"message": "gateway timeout", "code": 504}},
            )
        return httpx.Response(200, json=_stop_completion(str(self.request_count)))


def test_amendment8_combined_mock_pilot_integration(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59988/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    # 2 models × 3 scenarios (instance 0, A0)
    schedule = [
        {"scenario_id": "benign_weather_v1", "instance_index": 0, "family": "qwen3", "condition": "A0"},
        {"scenario_id": "benign_email_allowlist_v1", "instance_index": 0, "family": "qwen3", "condition": "A0"},
        {"scenario_id": "indirect_retrieved_doc_v1", "instance_index": 0, "family": "qwen3", "condition": "A0"},
        {"scenario_id": "benign_weather_v1", "instance_index": 0, "family": "gemma", "condition": "A0"},
        {"scenario_id": "benign_email_allowlist_v1", "instance_index": 0, "family": "gemma", "condition": "A0"},
        {"scenario_id": "indirect_retrieved_doc_v1", "instance_index": 0, "family": "gemma", "condition": "A0"},
    ]

    http_steps = [
        "tool_weather",
        "200",  # ep0 tool round success
        "err429json",
        "200",  # ep1 429 retry then success
        "err504",  # ep2 INVALID_PROVIDER_ERROR
        "hang",  # ep3 cancelled_timeout
        "200",  # ep4 success
        # ep5 episode wall X=0 → no HTTP
    ]
    transport = _Amendment8ComboTransport(http_steps)

    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    run_pilot_async = _load_run_pilot_async()
    out = tmp_path / "amendment8_combo"

    async def _main():
        return await run_pilot_async(
            out,
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=schedule,
            wall_timeout_s=0.2,
            rate_limit_backoffs=(0.0, 0.0),
            episode_wall_x_override=0.0,
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    assert summary["stopped_reason"] == "completed"

    stream = [json.loads(ln) for ln in out.joinpath("http_stream.jsonl").read_text().splitlines() if ln.strip()]
    ledger = [json.loads(ln) for ln in out.joinpath("ledger_rows.jsonl").read_text().splitlines() if ln.strip()]
    n_http = len(stream)
    assert transport.request_count == n_http == len(ledger) == 7

    manifest = json.loads(out.joinpath("run_manifest.json").read_text(encoding="utf-8"))
    assert "python_version" in manifest
    assert out.joinpath("pip_freeze.txt").is_file()
    assert "==" in out.joinpath("pip_freeze.txt").read_text(encoding="utf-8")

    led = json.loads(out.joinpath("running_ledger.json").read_text(encoding="utf-8"))
    assert led["http_used"] == n_http
    assert n_http <= led["http_cap"]

    cancelled = [r for r in stream if r.get("status") == "cancelled_timeout"]
    assert len(cancelled) == 1
    assert cancelled[0]["cost_usd"] is None
    assert cancelled[0].get("billed_placeholder_usd", 0) > 0

    retried = [r for r in stream if r.get("retried_after_rate_limit")]
    assert len(retried) == 1
    assert retried[0]["cost_usd"] is None

    provider_err = [r for r in stream if r.get("status") == "provider_error"]
    assert len(provider_err) == 1
    assert provider_err[0]["raw_response"].get("error", {}).get("code") == 504

    episodes = [json.loads(ln) for ln in out.joinpath("episodes.jsonl").read_text().splitlines() if ln.strip()]
    assert len(episodes) == 6
    expected = {
        "benign_weather_v1/i0/qwen3/A0": "COMPLETE",
        "benign_email_allowlist_v1/i0/qwen3/A0": "COMPLETE",
        "indirect_retrieved_doc_v1/i0/qwen3/A0": "INVALID_PROVIDER_ERROR",
        "benign_weather_v1/i0/gemma/A0": "COMPLETE",
        "benign_email_allowlist_v1/i0/gemma/A0": "COMPLETE",
        "indirect_retrieved_doc_v1/i0/gemma/A0": "INVALID_TIMEOUT",
    }
    status_table = {ep["episode_id"]: ep["status"] for ep in episodes}
    assert status_table == expected

    tool_rows = [
        r
        for r in stream
        if any(
            tc.get("function", {}).get("name") == "get_weather"
            for tc in (r.get("tool_calls") or [])
        )
        or "get_weather" in json.dumps(r.get("request") or {})
    ]
    assert tool_rows, "expected at least one HTTP row from tool-call episode"
