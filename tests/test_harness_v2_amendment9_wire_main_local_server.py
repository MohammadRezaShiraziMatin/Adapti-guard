"""Amendment 9 round 3 — main() hits local server; wire bytes match ledger."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tests.harness_v2_local_openrouter_server import LocalFakeOpenRouterServer  # noqa: E402


def _load_pilot_module():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_main_local_server_stores_wire_bytes_matching_received_payload(monkeypatch, tmp_path):
    server = LocalFakeOpenRouterServer()
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        monkeypatch.setenv("HARNESS_V2_WIRE_MAIN_TEST", "1")
        monkeypatch.setenv("HARNESS_V2_ALLOW_DIRTY_LIVE", "1")
        mod = _load_pilot_module()
        monkeypatch.setattr(
            mod.PilotRunLock,
            "try_acquire",
            lambda **kwargs: type("L", (), {"release": lambda self: None})(),
        )
        out = tmp_path / "wire_pack"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_harness_v2_pilot.py",
                "--live",
                "--pilot-label",
                "harness_v2_pilot_0",
                "--out-dir",
                str(out),
            ],
        )
        assert mod.main() == 0
        assert server.server_hits >= 1, "local server must receive chat/completions POST"
        stream_path = out / "http_stream.jsonl"
        assert stream_path.is_file()
        row = json.loads(stream_path.read_text(encoding="utf-8").splitlines()[0])
        assert row.get("request_wire_body_base64")
        stored = __import__("base64").standard_b64decode(row["request_wire_body_base64"])
        assert stored == server.chat_bodies[0]
    finally:
        server.stop()
