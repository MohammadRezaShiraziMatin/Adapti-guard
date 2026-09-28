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


def test_analyze_without_flag_never_calls_urlopen(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-offline-test-key")
    calls: list[str] = []

    def _fail_urlopen(*args, **kwargs):
        calls.append("urlopen")
        raise AssertionError("network forbidden without --allow-live-auth-key")

    monkeypatch.setattr(urllib.request, "urlopen", _fail_urlopen)
    mod = _load_analyze_module()
    analysis = mod.analyze(_minimal_summary(), allow_live_auth_key=False)
    assert analysis["auth_key"].get("not_queried") is True
    assert not calls


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
    assert analysis["auth_key"].get("not_queried") is False
    assert analysis["auth_key"].get("limit_remaining") == 1.5
