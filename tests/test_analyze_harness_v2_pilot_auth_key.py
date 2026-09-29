"""Offline guard for analyze_harness_v2_pilot /auth/key (Option A freeze)."""
from __future__ import annotations

import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_analyze_module():
    spec = importlib.util.spec_from_file_location(
        "analyze_harness_v2_pilot",
        ROOT / "scripts" / "analyze_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _minimal_summary() -> dict:
    return {"episodes": [], "stopped_reason": "completed"}


def test_analyze_default_never_calls_urlopen(monkeypatch):
    """Default analyze() must not hit the network (b7388512 called /auth/key when key set)."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-offline-test-key")
    urlopen_calls: list[str] = []

    def _fail_urlopen(req, timeout=60):
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        urlopen_calls.append(url)
        raise AssertionError(f"network forbidden without --allow-live-auth-key: {url}")

    monkeypatch.setattr(urllib.request, "urlopen", _fail_urlopen)
    mod = _load_analyze_module()
    analysis = mod.analyze(_minimal_summary())
    assert analysis["auth_key"].get("not_queried") is True
    assert urlopen_calls == []


def test_main_default_never_calls_urlopen(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-offline-test-key")
    (tmp_path / "pilot_summary.json").write_text(
        json.dumps(_minimal_summary()) + "\n",
        encoding="utf-8",
    )
    urlopen_calls: list[str] = []

    def _fail_urlopen(req, timeout=60):
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        urlopen_calls.append(url)
        raise AssertionError(f"network forbidden without --allow-live-auth-key: {url}")

    monkeypatch.setattr(urllib.request, "urlopen", _fail_urlopen)
    monkeypatch.setattr(sys, "argv", ["analyze_harness_v2_pilot.py", str(tmp_path)])
    mod = _load_analyze_module()
    monkeypatch.setattr(mod, "write_report", lambda *args, **kwargs: None)
    assert mod.main() == 0
    assert urlopen_calls == []


def test_analyze_with_flag_calls_auth_key_once(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-offline-test-key")
    urls: list[str] = []

    def _fake_urlopen(req, timeout=60):
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        urls.append(url)
        assert "/auth/key" in url
        payload = json.dumps(
            {"data": {"limit": 2.5, "usage": 1.0, "limit_remaining": 1.5}}
        ).encode("utf-8")

        class _Resp:
            def read(self):
                return payload

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return None

        return _Resp()

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)
    mod = _load_analyze_module()
    analysis = mod.analyze(_minimal_summary(), allow_live_auth_key=True)
    assert len(urls) == 1
    assert urls[0] == "https://openrouter.ai/api/v1/auth/key"
    assert analysis["auth_key"].get("not_queried") is False
    assert analysis["auth_key"].get("limit_remaining") == 1.5
