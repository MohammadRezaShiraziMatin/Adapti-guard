"""Amendment 9 round 5 — proxy mount wire capture, not_sent, smoke CLI doc."""
from __future__ import annotations

import base64
import importlib.util
import json
import socket
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.amendment9_smoke_controls import (  # noqa: E402
    SMOKE_HTTP_CAP,
    SMOKE_USD_CAP,
    preflight_smoke_plan,
)
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_v2_http_client import (  # noqa: E402
    close_pilot_http_client,
    create_pilot_http_client,
)
from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import (  # noqa: E402
    run_tools_episode_async,
)
from adapti_guard.evaluation.harness_v2.wire_request_body import WireCapturingTransport  # noqa: E402
from scripts.run_harness_v2_pilot import build_pilot_argparser, effective_pilot_caps  # noqa: E402
from tests.harness_v2_http_stream_assertions import assert_all_stream_rows_have_wire_bytes  # noqa: E402
from tests.harness_v2_local_openrouter_server import (  # noqa: E402
    LocalFakeOpenRouterServer,
    require_local_loopback,
)
from tests.test_harness_v2_amendment9_round4 import (  # noqa: E402
    _ForwardHttpProxy,
    _load_pilot_module,
    _patch_pilot_for_local_main,
)

DOCUMENTED_SMOKE_LAUNCH = (
    "python scripts/run_harness_v2_pilot.py --live --pilot-label harness_v2_pilot_0 "
    "--amendment9-llama-smoke --usd-cap 0.01"
)


def test_documented_smoke_launch_command_parses_and_preflight_passes():
    parser = build_pilot_argparser()
    argv = DOCUMENTED_SMOKE_LAUNCH.split()[2:]  # drop "python" and script path
    ns = parser.parse_args(argv)
    assert ns.amendment9_llama_smoke is True
    assert ns.usd_cap == pytest.approx(SMOKE_USD_CAP)
    usd, http = effective_pilot_caps(amendment9_llama_smoke=True, usd_cap=ns.usd_cap)
    plan = preflight_smoke_plan(http_cap=http, usd_cap=usd)
    assert plan["http_cap"] == SMOKE_HTTP_CAP
    assert plan["usd_cap"] == SMOKE_USD_CAP


def test_proxy_mounts_are_wire_wrapped_when_http_proxy_set(monkeypatch):
    require_local_loopback()
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:19999")
    monkeypatch.setenv("NO_PROXY", "")
    client = create_pilot_http_client(trust_env=True)
    try:
        assert isinstance(client._transport, WireCapturingTransport)
        assert client._mounts
        assert all(isinstance(t, WireCapturingTransport) for t in client._mounts.values())
    finally:
        run_harness_event_loop(lambda: close_pilot_http_client(client))


def test_main_proxy_run_every_stream_row_has_wire_bytes(monkeypatch, tmp_path):
    require_local_loopback()
    server = LocalFakeOpenRouterServer()
    server.start()
    proxy = _ForwardHttpProxy()
    proxy.start()
    try:
        target = f"http://127.0.0.1:{server.port}/v1"
        monkeypatch.setenv("HTTP_PROXY", f"http://127.0.0.1:{proxy.port}")
        monkeypatch.setenv("http_proxy", f"http://127.0.0.1:{proxy.port}")
        monkeypatch.setenv("NO_PROXY", "")
        monkeypatch.setenv("OPENROUTER_BASE_URL", target)
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        out = tmp_path / "proxy_wire"
        _patch_pilot_for_local_main(monkeypatch, mod, out)
        assert mod.main() == 0
        assert server.chat_bodies
        assert proxy.forwarded_bodies
        rows = assert_all_stream_rows_have_wire_bytes(
            out / "http_stream.jsonl",
            expected_bodies=[server.chat_bodies[0]],
        )
        assert proxy.forwarded_bodies[0] == base64.standard_b64decode(rows[0]["request_wire_body_base64"])
    finally:
        proxy.stop()
        server.stop()


def test_connect_refused_marks_not_sent_not_sent_unconfirmed(monkeypatch):
    require_local_loopback()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    closed_port = sock.getsockname()[1]
    sock.close()
    monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{closed_port}/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor

    async def _run():
        client = create_pilot_http_client()
        try:
            return await run_tools_episode_async(
                scenario_id="benign_weather_v1",
                model_id="meta-llama/llama-3.3-70b-instruct",
                config_key="llama",
                system_prompt="sys",
                initial_user="hi",
                executor=HarnessV2MockToolExecutor(),
                family="llama",
                max_rounds=1,
                http_client=client,
            )
        finally:
            await close_pilot_http_client(client)

    traj = run_harness_event_loop(_run)
    assert len(traj.calls) == 1
    rec = traj.calls[0]
    assert rec.request_not_sent is True
    assert rec.request_sent_unconfirmed is False
    from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call

    row = serialize_trajectory_call(rec, http_index=1)
    assert row.get("not_sent") is True
    assert "sent_unconfirmed" not in row
