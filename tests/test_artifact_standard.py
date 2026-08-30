"""Tests for artifact_standard helpers (infrastructure only)."""

from pathlib import Path

from src.adapti_guard.experiments.artifact_standard import (
    build_run_manifest,
    build_validation_record,
    log_structured,
    write_json,
)


def test_build_run_manifest_required_fields():
    manifest = build_run_manifest(
        experiment_name="test_exp",
        experiment_version="test_v1",
        configuration={"episodes": 10},
        methods=["fixed_l0"],
        source_artifacts=["results/common_attack_stream.json"],
        output_artifacts=["results/phase8/test_v1/results.json"],
        status="COMPLETE",
        deterministic=True,
        seed=42,
    )
    assert manifest["artifact_version"] == "v1"
    assert manifest["experiment_name"] == "test_exp"
    assert manifest["methods"] == ["fixed_l0"]
    assert manifest["deterministic"] is True


def test_build_validation_record_fails_on_fail_check():
    record = build_validation_record(
        {
            "artifact_integrity": "PASS",
            "population_integrity": "FAIL",
        }
    )
    assert record["validity"] == "FAIL"
    assert record["checks"]["population_integrity"] == "FAIL"


def test_write_json_archives_existing(tmp_path: Path):
    target = tmp_path / "validation.json"
    write_json(target, {"validity": "PASS"}, overwrite=True)
    write_json(target, {"validity": "FAIL"}, overwrite=False)
    archived = list(tmp_path.glob("validation_*.json"))
    assert archived
    assert target.exists()
