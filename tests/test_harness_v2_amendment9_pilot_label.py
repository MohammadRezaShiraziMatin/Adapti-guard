"""Amendment 9 — pilot label comes from CLI / run_pilot_async, not hardcoded."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

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


def test_run_manifest_writes_pilot_label_from_argument(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59993/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    mod = _load_pilot_module()
    label = "harness_v2_pilot_3"
    schedule = [
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "qwen3",
            "condition": "A0",
        },
    ]

    class _OneShotTransport:
        pass

    import httpx

    class T(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            return httpx.Response(
                200,
                json={
                    "id": "gen-1",
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "ok"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2, "cost": 0.0},
                },
            )

    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop

    out = tmp_path / "manifest_pack"

    async def _main():
        return await mod.run_pilot_async(
            out,
            pilot_label=label,
            usd_cap=0.05,
            http_transport=T(),
            schedule_override=schedule,
            skip_preflight=True,
            reconcile_at_end=False,
        )

    summary = run_harness_event_loop(_main)
    manifest = json.loads((out / "run_manifest.json").read_text())
    assert manifest["pilot"] == label
    assert manifest["pilot_number"] == 3
    assert summary["pilot"] == label
    assert summary["pilot_number"] == 3


def test_pilot_module_has_no_hardcoded_pilot_run_label_constant():
    text = (ROOT / "scripts" / "run_harness_v2_pilot.py").read_text(encoding="utf-8")
    assert "PILOT_RUN_LABEL" not in text
    assert '"pilot_number": 2' not in text
