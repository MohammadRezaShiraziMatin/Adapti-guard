"""Reproducibility helpers."""

from pathlib import Path

from src.adapti_guard.experiments.experiment_runner import ExperimentRunner


def test_save_results_versions_existing_artifact(tmp_path):
    runner = ExperimentRunner()
    results = runner.run(2)

    out = tmp_path / "episodes.json"
    ExperimentRunner.save_results(results, out, overwrite=True)
    assert out.exists()

    first = out.read_text(encoding="utf-8")
    ExperimentRunner.save_results(results, out, overwrite=False)

    archived = list(tmp_path.glob("episodes_*.json"))
    assert archived
    assert out.exists()
    assert archived[0].read_text(encoding="utf-8") == first


def test_save_manifest_contains_trace_fields(tmp_path):
    path = tmp_path / "run_manifest.json"
    ExperimentRunner.save_manifest(
        {
            "experiment": "phase7",
            "seed": 42,
            "episodes": 100,
            "attack_stream": "common_attack_stream_v1",
            "defense_levels": [0, 1, 2, 3],
            "adaptive": True,
        },
        path,
        overwrite=True,
    )
    text = path.read_text(encoding="utf-8")
    assert "phase7" in text
    assert "python_version" in text
    assert "timestamp_utc" in text
