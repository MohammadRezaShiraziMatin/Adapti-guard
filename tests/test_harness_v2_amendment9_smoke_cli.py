"""Amendment 9 — llama smoke schedule, caps, auth preflight, CLI."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.harness_v2.amendment9_smoke_controls import (  # noqa: E402
    SMOKE_HTTP_CAP,
    SMOKE_USD_CAP,
)
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop  # noqa: E402
from scripts.run_harness_v2_pilot import (  # noqa: E402
    HTTP_CAP,
    USD_CAP,
    _episode_id,
    build_pilot_argparser,
    effective_pilot_caps,
    pilot_episode_schedule,
    pilot_schedule_for_run,
)
from tests.harness_v2_local_openrouter_server import LocalFakeOpenRouterServer  # noqa: E402

AMENDMENT9_SMOKE_EPISODE_IDS: list[str] = [
    "indirect_retrieved_doc_v1/i0/llama/A0",
    "indirect_retrieved_doc_v1/i0/llama/B3",
    "poisoned_benign_tool_v1/i0/llama/A0",
    "poisoned_benign_tool_v1/i0/llama/B3",
    "direct_user_override_v1/i0/llama/A0",
    "direct_user_override_v1/i0/llama/B3",
    "create_record_exfil_v1/i0/llama/A0",
    "create_record_exfil_v1/i0/llama/B3",
    "multi_step_chain_v1/i0/llama/A0",
    "multi_step_chain_v1/i0/llama/B3",
    "delayed_second_turn_v1/i0/llama/A0",
    "delayed_second_turn_v1/i0/llama/B3",
    "obfuscated_instruction_v1/i0/llama/A0",
    "obfuscated_instruction_v1/i0/llama/B3",
    "benign_weather_v1/i0/llama/A0",
    "benign_weather_v1/i0/llama/B3",
    "benign_email_allowlist_v1/i0/llama/A0",
    "benign_email_allowlist_v1/i0/llama/B3",
    "benign_create_record_v1/i0/llama/A0",
    "benign_create_record_v1/i0/llama/B3",
]


def _load_pilot_module():
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        ROOT / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_effective_smoke_caps_override_defaults():
    usd, http = effective_pilot_caps(amendment9_llama_smoke=True, usd_cap=USD_CAP)
    assert usd == SMOKE_USD_CAP
    assert http == SMOKE_HTTP_CAP
    usd2, http2 = effective_pilot_caps(amendment9_llama_smoke=False, usd_cap=USD_CAP)
    assert usd2 == USD_CAP
    assert http2 == HTTP_CAP


def test_pilot_schedule_smoke_matches_hardcoded_twenty_ids():
    schedule = pilot_schedule_for_run(amendment9_llama_smoke=True)
    assert len(schedule) == 20
    assert [_episode_id(r) for r in schedule] == AMENDMENT9_SMOKE_EPISODE_IDS
    full = pilot_episode_schedule()
    assert len(full) > 20


def test_build_pilot_argparser_amendment9_llama_smoke_flag():
    parser = build_pilot_argparser()
    ns = parser.parse_args(
        ["--live", "--pilot-label", "harness_v2_pilot_0", "--amendment9-llama-smoke"]
    )
    assert ns.amendment9_llama_smoke is True


def test_smoke_auth_preflight_aborts_with_zero_chat_hits_out_of_band(monkeypatch, tmp_path):
    server = LocalFakeOpenRouterServer(auth_limit_remaining=0.5, auth_usage=1.6877)
    server.start()
    try:
        monkeypatch.setenv("OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.port}/v1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "local-test-key")
        mod = _load_pilot_module()
        out = tmp_path / "smoke_abort"

        def _run():
            return run_harness_event_loop(
                lambda: mod.run_pilot_async(
                    out,
                    pilot_label="harness_v2_pilot_0",
                    amendment9_llama_smoke=True,
                    skip_preflight=False,
                    reconcile_at_end=False,
                )
            )

        summary = _run()
        assert summary["stopped_reason"] == "auth_preflight_abort"
        assert summary["http_used"] == 0
        assert server.server_hits == 0
        assert (out / "preflight_auth_key_launch.json").is_file()
    finally:
        server.stop()


def test_main_refuses_dirty_worktree_and_records_manifest(monkeypatch, tmp_path):
    mod = _load_pilot_module()
    monkeypatch.setattr(mod, "is_worktree_dirty", lambda _root: True)
    out = tmp_path / "dirty_refused"
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
    assert mod.main() == 3
    manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["live_launch_refused"] is True
    assert manifest["runner_worktree_dirty"] is True
