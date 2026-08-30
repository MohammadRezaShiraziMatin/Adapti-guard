"""Controlled ExperimentRunner invariants."""

import json
from pathlib import Path

from src.adapti_guard.experiments.experiment_runner import (
    EpisodeResult,
    ExperimentRunner,
)


def _load_stream():
    return json.loads(
        Path("results/common_attack_stream.json").read_text(
            encoding="utf-8"
        )
    )


def test_experiment_runner_api():
    stream = _load_stream()[:5]
    schedule = [False] * 5
    runner = ExperimentRunner(
        attack_stream=stream,
        episode_schedule=schedule,
    )
    assert runner.attack_stream is not None
    assert runner.episode_schedule == schedule
    assert isinstance(runner.run_episode(1), EpisodeResult)


def test_controlled_mode_uses_stream_not_periodic():
    stream = _load_stream()[:8]
    # Explicit schedule: all attacks (no i%4 legitimate).
    schedule = [False] * 8
    runner = ExperimentRunner(
        attack_stream=stream,
        episode_schedule=schedule,
    )
    results = runner.run(8)
    assert all(r.attack_present for r in results)
    assert [r.attack_family for r in results] == [
        e["attack_family"] for e in stream
    ]
    assert [r.payload for r in results] == [
        e["payload"] for e in stream
    ]


def test_historical_ablation_zeroes_signal():
    stream = _load_stream()[:4]
    runner = ExperimentRunner(
        attack_stream=stream,
        episode_schedule=[False] * 4,
    )
    runner.use_historical_signal = False
    runner.historical_successes = 3
    runner.historical_failures = 1
    assert runner._historical_attack_signal() == 0.0
