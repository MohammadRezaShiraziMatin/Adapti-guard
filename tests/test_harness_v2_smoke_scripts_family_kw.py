"""Regression: smoke scripts pass required ``family`` kw-only to run_tools_episode_async."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


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


def _load_script(relpath: str, mod_name: str):
    spec = importlib.util.spec_from_file_location(mod_name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _mock_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59980/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)


def test_run_harness_v2_smoke_mock_episode() -> None:
    mod = _load_script("scripts/run_harness_v2_smoke.py", "run_harness_v2_smoke")
    traj = mod.run_mock_episode_with_transport(
        _StopTransport(), family="qwen3", scenario_id="benign_weather_v1"
    )
    assert traj.calls


def test_run_harness_v2_smoke2_mock_episode() -> None:
    mod = _load_script("scripts/run_harness_v2_smoke2.py", "run_harness_v2_smoke2")
    traj = mod.run_mock_episode_with_transport(
        _StopTransport(), family="gemma", scenario_id="benign_weather_v1"
    )
    assert traj.calls


def test_run_harness_v2_smoke3_mock_episode() -> None:
    mod = _load_script("scripts/run_harness_v2_smoke3.py", "run_harness_v2_smoke3")
    traj = mod.run_mock_episode_with_transport(_StopTransport(), family="qwen3")
    assert traj.calls


def test_run_harness_v2_reasoning_smoke_mock_episode() -> None:
    mod = _load_script("scripts/run_harness_v2_reasoning_smoke.py", "run_harness_v2_reasoning_smoke")
    traj = mod.run_mock_episode_with_transport(_StopTransport())
    assert traj.calls


def test_amendment7b_obfuscated_mock_episode() -> None:
    mod = _load_script(
        "experiments/harness_v2/amendment7b_obfuscated_mock_test.py",
        "amendment7b_obfuscated_mock_test",
    )
    traj = mod.run_mock_episode_with_transport(_StopTransport())
    assert traj.calls
