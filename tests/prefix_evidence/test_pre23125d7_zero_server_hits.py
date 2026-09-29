"""Run inside a 23125d7 git worktree (see tests/prefix_evidence/README.md)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import os

import pytest

ROOT = Path(os.environ.get("ADAPTI_GUARD_WORKTREE_ROOT", str(Path(__file__).resolve().parents[2])))
sys.path.insert(0, str(ROOT / "src"))

from tests.harness_v2_local_openrouter_server import (  # noqa: E402
    LocalFakeOpenRouterServer,
    require_local_loopback,
)


def _load_pilot_module():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_pre23125d7_main_local_server_receives_zero_chat_requests(monkeypatch):
    """Old runner @ 23125d7: local server must see zero POST bodies (pre-fix evidence)."""
    if os.environ.get("ADAPTI_GUARD_WORKTREE_ROOT") is None:
        pytest.skip("set ADAPTI_GUARD_WORKTREE_ROOT to a 23125d7 worktree (see README)")
    require_local_loopback()
    server = LocalFakeOpenRouterServer()
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        monkeypatch.setenv("HARNESS_V2_WIRE_MAIN_TEST", "1")
        monkeypatch.setenv("HARNESS_V2_ALLOW_DIRTY_LIVE", "1")
        mod = _load_pilot_module()
        if hasattr(mod, "is_worktree_dirty"):
            monkeypatch.setattr(mod, "is_worktree_dirty", lambda _root: False)
        monkeypatch.setattr(
            mod.PilotRunLock,
            "try_acquire",
            lambda **kwargs: type("L", (), {"release": lambda self: None})(),
        )
        out = ROOT / "experiments" / "harness_v2" / "_prefix_evidence_out"
        out.mkdir(parents=True, exist_ok=True)
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
        mod.main()
        assert len(server.chat_bodies) > 0, "server received 0 chat/completions requests"
    finally:
        server.stop()
