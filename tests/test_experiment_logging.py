"""Tests for experiment logging (no API)."""

from pathlib import Path

from src.adapti_guard.evaluation.experiment_logging import (
    ExperimentRunContext,
    redact_env,
)


def test_redact_env_no_key():
    env = redact_env()
    assert env["openrouter_api_key"] is None or env["openrouter_api_key"] == "***REDACTED***"
    assert "key_present" in env


def test_experiment_run_context_creates_artifacts(tmp_path):
    with ExperimentRunContext.create(
        "EXP-TEST",
        config={"foo": "bar"},
        runs_root=tmp_path,
    ) as ctx:
        ctx.write_metrics({"status": "PASS"})
        assert (ctx.run_dir / "config.json").exists()
        assert (ctx.run_dir / "metrics.json").exists()
        assert (ctx.run_dir / "git_commit.txt").exists()
