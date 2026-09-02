"""Validated resume semantics for multi-model real-LLM experiments."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ResumeExpectation:
    model_id: str
    model_config_key: str
    baseline: str
    n_samples: int
    seed: int
    dataset_hash: str
    cache_enabled: bool
    config_version: str
    sample_ids: tuple[str, ...]
    experiment_id: str = "EXP-004"


@dataclass
class ResumeValidationResult:
    valid: bool
    reasons: list[str] = field(default_factory=list)

    def message(self) -> str:
        if self.valid:
            return "resume validation passed"
        return "; ".join(self.reasons)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_predictions(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _provenance_from_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    prov = metrics.get("provenance")
    if isinstance(prov, dict):
        return prov
    return metrics


def validate_baseline_resume(
    *,
    metrics_path: Path,
    predictions_path: Path,
    expected: ResumeExpectation,
) -> ResumeValidationResult:
    """Return whether an on-disk baseline run may be safely skipped."""
    reasons: list[str] = []

    if not metrics_path.exists():
        reasons.append(f"missing metrics artifact: {metrics_path}")
    if not predictions_path.exists():
        reasons.append(f"missing predictions artifact: {predictions_path}")

    if reasons:
        return ResumeValidationResult(valid=False, reasons=reasons)

    metrics = _load_json(metrics_path)
    predictions = _load_predictions(predictions_path)
    prov = _provenance_from_metrics(metrics)

    stored_baseline = prov.get("baseline") or metrics.get("baseline")
    if stored_baseline != expected.baseline:
        reasons.append(
            f"baseline mismatch: artifact={stored_baseline!r} expected={expected.baseline!r}"
        )

    stored_model_key = prov.get("model_config_key") or metrics.get("model_config_key")
    if stored_model_key != expected.model_config_key:
        reasons.append(
            f"model_config_key mismatch: artifact={stored_model_key!r} "
            f"expected={expected.model_config_key!r}"
        )

    stored_model_id = prov.get("model_id") or metrics.get("model_id")
    if stored_model_id and stored_model_id != expected.model_id:
        reasons.append(
            f"model_id mismatch: artifact={stored_model_id!r} expected={expected.model_id!r}"
        )

    stored_n = prov.get("n_samples") or metrics.get("n_samples")
    if int(stored_n or 0) != expected.n_samples:
        reasons.append(
            f"n_samples mismatch: artifact={stored_n!r} expected={expected.n_samples}"
        )

    stored_seed = prov.get("seed") or metrics.get("seed")
    if int(stored_seed or -1) != expected.seed:
        reasons.append(f"seed mismatch: artifact={stored_seed!r} expected={expected.seed}")

    stored_hash = prov.get("dataset_hash") or metrics.get("dataset_hash")
    if stored_hash != expected.dataset_hash:
        reasons.append(
            f"dataset_hash mismatch: artifact={stored_hash!r} expected={expected.dataset_hash!r}"
        )

    stored_cache = prov.get("cache_enabled")
    if stored_cache is None:
        stored_cache = metrics.get("cache_enabled")
    if bool(stored_cache) != expected.cache_enabled:
        reasons.append(
            f"cache_enabled mismatch: artifact={stored_cache!r} expected={expected.cache_enabled!r}"
        )

    stored_version = prov.get("config_version") or metrics.get("config_version")
    if stored_version != expected.config_version:
        reasons.append(
            f"config_version mismatch: artifact={stored_version!r} "
            f"expected={expected.config_version!r}"
        )

    stored_experiment = prov.get("experiment_id") or metrics.get("experiment_id")
    if stored_experiment and stored_experiment != expected.experiment_id:
        reasons.append(
            f"experiment_id mismatch: artifact={stored_experiment!r} "
            f"expected={expected.experiment_id!r}"
        )

    if len(predictions) != expected.n_samples:
        reasons.append(
            f"prediction count mismatch: artifact={len(predictions)} "
            f"expected={expected.n_samples}"
        )

    pred_ids = [str(r.get("sample_id") or r.get("id", "")) for r in predictions]
    if len(set(pred_ids)) != len(pred_ids):
        reasons.append("duplicate sample IDs in predictions artifact")

    stored_ids = prov.get("sample_ids")
    if stored_ids is not None:
        if list(stored_ids) != list(expected.sample_ids):
            reasons.append("sample_ids mismatch between metrics provenance and current run")
    elif pred_ids != list(expected.sample_ids):
        reasons.append("prediction sample_ids/order mismatch vs expected protocol order")

    return ResumeValidationResult(valid=not reasons, reasons=reasons)
