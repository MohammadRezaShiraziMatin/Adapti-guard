"""Amendment 8 item I — legacy run_tools_episode guard + pilot uses async entry only."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import run_tools_episode


def test_run_tools_episode_rejects_running_loop():
    async def _inner():
        with pytest.raises(RuntimeError, match="must not be called inside a running event loop"):
            run_tools_episode(
                scenario_id="s",
                model_id="m",
                config_key="c",
                system_prompt="sys",
                initial_user="u",
                executor=HarnessV2MockToolExecutor(),
            )

    asyncio.run(_inner())


def test_pilot_module_does_not_reference_legacy_wrapper():
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "run_harness_v2_pilot.py").read_text(encoding="utf-8")
    assert "run_tools_episode_async" in text
    assert "run_tools_episode(" not in text
