"""Amendment 8 item P — deprecated sync run_tools_episode wrapper."""
from __future__ import annotations

from pathlib import Path

import pytest

from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import run_tools_episode


def test_run_tools_episode_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="deprecated, use run_pilot_async"):
        run_tools_episode(
            scenario_id="s",
            model_id="m",
            config_key="c",
            system_prompt="sys",
            initial_user="u",
            executor=HarnessV2MockToolExecutor(),
        )


def test_pilot_module_does_not_call_legacy_wrapper():
    root = Path(__file__).resolve().parents[1]
    text = (root / "scripts" / "run_harness_v2_pilot.py").read_text(encoding="utf-8")
    assert "run_tools_episode_async" in text
    assert "run_tools_episode(" not in text
