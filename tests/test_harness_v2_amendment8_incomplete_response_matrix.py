"""Amendment 8 item M — incomplete OpenRouter responses via run_pilot_async (mock)."""
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


def _stop_completion() -> dict:
    return {
        "id": "gen-ok",
        "choices": [
            {
                "message": {"role": "assistant", "content": "Done."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "cost": 0.0001},
    }


class _MatrixTransport(httpx.AsyncBaseTransport):
    def __init__(self, *, first_response: httpx.Response) -> None:
        self._first = first_response
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        if self.request_count == 1:
            return self._first
        return httpx.Response(200, json=_stop_completion())


def _two_episode_schedule(prefix: str) -> list[dict]:
    return [
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


def _run_matrix(tmp_path: Path, monkeypatch, transport: _MatrixTransport) -> None:
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59990/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    run_pilot_async = _load_run_pilot_async()
    out = tmp_path / "pack"

    async def _main():
        return await run_pilot_async(
            out,
            usd_cap=0.05,
            http_transport=transport,
            schedule_override=_two_episode_schedule("x"),
            rate_limit_backoffs=(0.0, 0.0),
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    assert summary["stopped_reason"] == "completed"
    stream = [json.loads(ln) for ln in out.joinpath("http_stream.jsonl").read_text().splitlines() if ln.strip()]
    ledger = [json.loads(ln) for ln in out.joinpath("ledger_rows.jsonl").read_text().splitlines() if ln.strip()]
    assert transport.request_count == len(stream) == len(ledger) == 2
    pe = [r for r in stream if r.get("status") == "provider_error"]
    assert len(pe) == 1
    episodes = [json.loads(ln) for ln in out.joinpath("episodes.jsonl").read_text().splitlines() if ln.strip()]
    by_status = {e["episode_id"]: e["status"] for e in episodes}
    assert by_status["benign_weather_v1/i0/qwen3/A0"] == "INVALID_PROVIDER_ERROR"
    assert by_status["benign_weather_v1/i1/qwen3/A0"] == "COMPLETE"


def test_incomplete_matrix_504_body_without_choices(tmp_path: Path, monkeypatch):
    transport = _MatrixTransport(
        first_response=httpx.Response(
            200,
            json={"error": {"message": "gateway timeout", "code": 504}},
        )
    )
    _run_matrix(tmp_path, monkeypatch, transport)
    row = json.loads((tmp_path / "pack" / "http_stream.jsonl").read_text().splitlines()[0])
    assert row["raw_response"]["error"]["code"] == 504


def test_incomplete_matrix_empty_body(tmp_path: Path, monkeypatch):
    transport = _MatrixTransport(first_response=httpx.Response(200, content=b""))
    _run_matrix(tmp_path, monkeypatch, transport)


def test_incomplete_matrix_invalid_json_body(tmp_path: Path, monkeypatch):
    transport = _MatrixTransport(first_response=httpx.Response(200, content=b"{bad"))
    _run_matrix(tmp_path, monkeypatch, transport)


def test_incomplete_matrix_error_code_503_no_retry(tmp_path: Path, monkeypatch):
    transport = _MatrixTransport(
        first_response=httpx.Response(
            200,
            json={"error": {"message": "upstream unavailable", "code": 503}},
        )
    )
    _run_matrix(tmp_path, monkeypatch, transport)
    assert transport.request_count == 2
