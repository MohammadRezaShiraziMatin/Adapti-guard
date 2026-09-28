"""Amendment 9 round 4 — main() hits local server; wire bytes match ledger."""
from __future__ import annotations

import base64
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tests.harness_v2_local_openrouter_server import (  # noqa: E402
    LocalFakeOpenRouterServer,
    require_local_loopback,
)
from tests.test_harness_v2_amendment9_round4 import (  # noqa: E402
    _load_pilot_module,
    _patch_pilot_for_local_main,
)


def test_main_local_server_stores_wire_bytes_matching_received_payload(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer()
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        out = tmp_path / "wire_pack"
        _patch_pilot_for_local_main(monkeypatch, mod, out)
        assert mod.main() == 0
        assert server.chat_bodies, "local server must receive chat/completions POST body"
        assert server.server_hits >= 1
        stream_path = out / "http_stream.jsonl"
        assert stream_path.is_file()
        row = json.loads(stream_path.read_text(encoding="utf-8").splitlines()[0])
        assert row.get("request_wire_body_base64")
        stored = base64.standard_b64decode(row["request_wire_body_base64"])
        assert stored == server.chat_bodies[0]
    finally:
        server.stop()


def test_main_local_server_multi_call_tool_episode_wire_order(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer(tool_then_stop=True)
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        out = tmp_path / "wire_multi"
        _patch_pilot_for_local_main(monkeypatch, mod, out)
        schedule = [
            {
                "scenario_id": "indirect_retrieved_doc_v1",
                "instance_index": 0,
                "family": "llama",
                "condition": "A0",
            }
        ]

        def _sched(**kw):
            if kw.get("amendment9_llama_smoke"):
                return mod.pilot_schedule_for_run(**kw)
            return schedule

        monkeypatch.setattr(mod, "pilot_schedule_for_run", _sched)
        assert mod.main() == 0
        assert len(server.chat_bodies) == 2
        lines = (out / "http_stream.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        for idx, line in enumerate(lines):
            row = json.loads(line)
            stored = base64.standard_b64decode(row["request_wire_body_base64"])
            assert stored == server.chat_bodies[idx]
    finally:
        server.stop()
