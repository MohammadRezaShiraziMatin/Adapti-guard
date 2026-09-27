"""Regression: smoke entrypoints pass required ``family`` to run_tools_episode_async."""
from __future__ import annotations

import importlib.util
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


def test_run_harness_v2_smoke_mock_episode(tmp_path: Path) -> None:
    mod = _load_script("scripts/run_harness_v2_smoke.py", "run_harness_v2_smoke")
    summary = mod.run_smoke(tmp_path / "smoke1", http_transport=_StopTransport())
    assert summary.get("api_calls", 0) >= 1


def test_run_harness_v2_smoke2_mock_episode(tmp_path: Path) -> None:
    mod = _load_script("scripts/run_harness_v2_smoke2.py", "run_harness_v2_smoke2")
    summary = mod.run_smoke2(tmp_path / "smoke2", http_transport=_StopTransport())
    assert summary.get("http_requests_used", 0) >= 1


def test_run_harness_v2_smoke3_mock_episode(tmp_path: Path) -> None:
    mod = _load_script("scripts/run_harness_v2_smoke3.py", "run_harness_v2_smoke3")
    summary = mod.run_smoke3(tmp_path / "smoke3", http_transport=_StopTransport())
    assert summary.get("http_requests_used", 0) >= 1


def test_run_harness_v2_reasoning_smoke_mock_episode(tmp_path: Path) -> None:
    mod = _load_script("scripts/run_harness_v2_reasoning_smoke.py", "run_harness_v2_reasoning_smoke")
    summary = mod.run_reasoning_smoke(tmp_path / "rsmoke", http_transport=_StopTransport())
    assert summary.get("http_used", 0) >= 1


def test_amendment7b_obfuscated_mock_episode() -> None:
    mod = _load_script(
        "experiments/harness_v2/amendment7b_obfuscated_mock_test.py",
        "amendment7b_obfuscated_mock_test",
    )
    from adapti_guard.evaluation.harness_v2.scenario_catalog import load_templates

    templates = load_templates()
    chunks: list[str] = []
    mod.run_episode(
        inst=0,
        condition="A0",
        templates=templates,
        chunks=chunks,
        http_transport=_StopTransport(),
    )
    assert chunks
