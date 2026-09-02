"""Multi-model real LLM evaluation orchestrator for Q1 manuscript evidence.

Pipeline (per model):
    Dataset → Defense (B0–B3) → Target LLM → Independent Judge → Metrics

Cross-model statistical analysis runs after all models complete.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.adapti_guard.evaluation.experiment_logging import (
    ExperimentRunContext,
    git_commit,
    sha256_file,
    update_registry_row,
)
from src.adapti_guard.evaluation.multi_model_statistics import (
    analyze_multi_model_results,
    save_statistical_report,
)
from src.adapti_guard.evaluation.provenance import (
    ExperimentValidity,
    classify_real_llm_validity,
)
from src.adapti_guard.evaluation.prediction_provenance import PROVENANCE_SCHEMA_VERSION
from src.adapti_guard.evaluation.target_model import load_model_config
from src.adapti_guard.experiments.real_llm_pipeline import (
    DEFAULT_BASELINES,
    BaselineRunContext,
    EvaluationBackend,
    PipelineConfig,
    UNIFIED_DATASET_DEFAULT,
    build_models,
    load_records,
    resolve_backend,
    run_baseline_evaluation,
)
from src.adapti_guard.experiments.resume_validation import (
    ResumeExpectation,
    validate_baseline_resume,
)

DEFAULT_TARGET_KEYS = ["model_a", "model_b", "model_c"]
OPTIONAL_TARGET_KEYS = ["model_d"]


@dataclass
class MultiModelConfig:
    experiment_id: str = "EXP-004"
    output_dir: Path = Path("experiments/EXP004_MULTI_MODEL")
    target_keys: list[str] = field(default_factory=lambda: list(DEFAULT_TARGET_KEYS))
    judge_config_key: str = "judge_primary"
    models_config: str = "configs/models.yaml"
    backend: EvaluationBackend = EvaluationBackend.AUTO
    baselines: list[str] = field(default_factory=lambda: list(DEFAULT_BASELINES))
    split: str = "test"
    n_samples: int | None = 500
    attack_n: int = 1500
    benign_n: int = 500
    seed: int = 42
    benchmark_dir: str = "datasets/benchmark_q1"
    unified_dataset: str | None = None
    use_unified_dataset: bool = False
    reference_baseline: str = "B0"
    treatment_baseline: str = "B6"
    skip_existing: bool = False
    frozen_dataset: str | None = None
    use_frozen_eval: bool = False
    publication_mode: bool = False
    cache_enabled: bool | None = None


def resolve_cache_enabled(config: MultiModelConfig) -> bool:
    """Resolve effective LLM cache setting for a multi-model run."""
    if config.cache_enabled is not None:
        return config.cache_enabled
    if config.publication_mode:
        return False
    cache_cfg = load_model_config(config.models_config).get("cache", {})
    return bool(cache_cfg.get("enabled", True))


def _model_version_info(target_key: str, models_config: str) -> dict[str, str]:
    cfg = load_model_config(models_config)
    spec = cfg.get("models", {}).get(target_key, {})
    return {
        "config_key": target_key,
        "provider": str(spec.get("provider", "")),
        "model": str(spec.get("model", "")),
        "temperature": str(spec.get("temperature", 0.0)),
        "max_tokens": str(spec.get("max_tokens", 512)),
    }


def run_multi_model_evaluation(config: MultiModelConfig) -> dict[str, Any]:
    """Execute multi-model × multi-baseline real LLM evaluation."""
    config.output_dir.mkdir(parents=True, exist_ok=True)

    backend, block_reason = resolve_backend(config.backend)
    timestamp = datetime.now(timezone.utc).isoformat()
    effective_cache = resolve_cache_enabled(config)

    run_config = {
        "experiment_id": config.experiment_id,
        "target_keys": config.target_keys,
        "judge": config.judge_config_key,
        "backend": backend.value,
        "baselines": config.baselines,
        "seed": config.seed,
        "n_samples": config.n_samples,
        "attack_n": config.attack_n,
        "benign_n": config.benign_n,
        "split": config.split,
        "benchmark_dir": config.benchmark_dir,
        "use_unified_dataset": config.use_unified_dataset,
        "evaluation_mode": "real_llm_judge",
        "publication_mode": config.publication_mode,
        "cache_enabled": effective_cache,
        "config_version": PROVENANCE_SCHEMA_VERSION,
        "timestamp": timestamp,
        "git_commit": git_commit() or "UNKNOWN",
    }
    (config.output_dir / "config.json").write_text(
        json.dumps(run_config, indent=2), encoding="utf-8"
    )

    if block_reason:
        blocked = {
            "status": "BLOCKED",
            "reason": block_reason,
            "experiment_id": config.experiment_id,
            "backend": backend.value,
            "timestamp": timestamp,
            "git_commit": run_config["git_commit"],
            "models_requested": config.target_keys,
            "evaluation_mode": "real_llm_judge",
            "note": "No metrics fabricated. Fix API key or start Ollama and re-run.",
        }
        (config.output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
        (config.output_dir / "statistical_analysis.json").write_text(json.dumps({
            "status": "BLOCKED",
            "reason": block_reason,
        }, indent=2))
        return blocked

    records, dataset_meta = load_records(PipelineConfig(
        split=config.split,
        n_samples=config.n_samples,
        attack_n=config.attack_n,
        benign_n=config.benign_n,
        seed=config.seed,
        benchmark_dir=config.benchmark_dir,
        unified_dataset=config.unified_dataset,
        use_unified_dataset=config.use_unified_dataset,
        frozen_dataset=config.frozen_dataset,
        use_frozen_eval=config.use_frozen_eval,
    ))

    if not records:
        blocked = {"status": "BLOCKED", "reason": "no evaluation records", "timestamp": timestamp}
        (config.output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
        return blocked

    if config.use_frozen_eval:
        ds_path = Path(config.frozen_dataset or "datasets/frozen/eval_v1/dataset.jsonl")
    elif config.use_unified_dataset:
        ds_path = Path(config.unified_dataset or UNIFIED_DATASET_DEFAULT)
    else:
        ds_path = Path(config.benchmark_dir) / f"{config.split}.jsonl"

    dataset_hash = sha256_file(ds_path) if ds_path.exists() else ""
    sample_ids = tuple(str(r.get("id", "")) for r in records)

    with ExperimentRunContext.create(
        config.experiment_id,
        config={**run_config, "n_samples": len(records), "dataset_meta": dataset_meta},
    ) as ctx:
        model_results: dict[str, Any] = {}
        t_start = time.perf_counter()
        any_valid = False
        all_invalid = True

        for target_key in config.target_keys:
            ctx.log_stdout(f"=== Target model: {target_key} ===")
            model_dir = config.output_dir / target_key
            model_dir.mkdir(parents=True, exist_ok=True)

            model_info = _model_version_info(target_key, config.models_config)
            (model_dir / "model_info.json").write_text(
                json.dumps(model_info, indent=2), encoding="utf-8"
            )

            pipe_config = PipelineConfig(
                target_config_key=target_key,
                judge_config_key=config.judge_config_key,
                models_config=config.models_config,
                backend=config.backend,
            )

            try:
                target, judge = build_models(
                    pipe_config, backend, cache_enabled=effective_cache
                )
            except Exception as exc:
                model_results[target_key] = {
                    "status": "BLOCKED",
                    "reason": str(exc),
                    "model_info": model_info,
                }
                ctx.log_stderr(f"  BLOCKED: {exc}")
                continue

            baseline_metrics: dict[str, Any] = {}
            model_start = time.perf_counter()

            for baseline_key in config.baselines:
                baseline_dir = model_dir / baseline_key
                metrics_file = baseline_dir / f"{baseline_key}_metrics.json"
                predictions_file = baseline_dir / f"{baseline_key}_predictions.jsonl"

                if config.skip_existing:
                    resume_check = validate_baseline_resume(
                        metrics_path=metrics_file,
                        predictions_path=predictions_file,
                        expected=ResumeExpectation(
                            model_id=model_info["model"],
                            model_config_key=target_key,
                            baseline=baseline_key,
                            n_samples=len(records),
                            seed=config.seed,
                            dataset_hash=dataset_hash,
                            cache_enabled=effective_cache,
                            config_version=PROVENANCE_SCHEMA_VERSION,
                            sample_ids=sample_ids,
                            experiment_id=config.experiment_id,
                        ),
                    )
                    if resume_check.valid:
                        ctx.log_stdout(f"  Skipping {baseline_key} (validated resume)")
                        baseline_metrics[baseline_key] = json.loads(
                            metrics_file.read_text(encoding="utf-8")
                        )
                        continue
                    ctx.log_stderr(
                        f"  Resume validation failed for {baseline_key}: "
                        f"{resume_check.message()}; rerunning baseline"
                    )

                ctx.log_stdout(f"  Running {baseline_key} ({len(records)} episodes)")
                run_context = BaselineRunContext(
                    experiment_id=config.experiment_id,
                    model_id=model_info["model"],
                    model_config_key=target_key,
                    git_commit=run_config["git_commit"],
                    seed=config.seed,
                    dataset_hash=dataset_hash,
                    cache_enabled=effective_cache,
                )
                result = run_baseline_evaluation(
                    baseline_key,
                    records,
                    target=target,
                    judge=judge,
                    output_dir=baseline_dir,
                    run_context=run_context,
                )

                validity, issues = classify_real_llm_validity(
                    {
                        "status": result.status,
                        "metrics": result.metrics,
                        "n_samples": result.n_samples,
                        "evaluation_mode": "real_llm_judge",
                    },
                    min_samples=1,
                )

                entry = {
                    **result.metrics,
                    "validity": validity.value,
                    "validity_issues": issues,
                    "asr_bootstrap_ci": result.asr_bootstrap_ci,
                    "model_key": target_key,
                    "model_info": model_info,
                }
                baseline_metrics[baseline_key] = entry

                if validity == ExperimentValidity.VALID:
                    any_valid = True
                    all_invalid = False
                elif validity != ExperimentValidity.INVALID:
                    all_invalid = False

            model_elapsed = round(time.perf_counter() - model_start, 2)
            model_results[target_key] = {
                "status": "COMPLETED",
                "model_info": model_info,
                "elapsed_seconds": model_elapsed,
                "baselines": baseline_metrics,
            }
            (model_dir / "metrics.json").write_text(
                json.dumps(model_results[target_key], indent=2), encoding="utf-8"
            )

        # Statistical analysis across models
        stat_report = analyze_multi_model_results(
            config.output_dir,
            models=config.target_keys,
            baselines=config.baselines,
            experiment_id=config.experiment_id,
            seed=config.seed,
            reference_baseline=config.reference_baseline,
            treatment_baseline=config.treatment_baseline,
        )

        if all_invalid and model_results:
            overall_status = "INVALID"
            stat_report.status = "INVALID"
            stat_report.notes.append("All model runs produced invalid metrics (e.g. API errors)")
        elif any_valid:
            overall_status = "COMPLETED"
        elif not model_results:
            overall_status = "BLOCKED"
            stat_report.status = "BLOCKED"
        else:
            overall_status = "PARTIAL"
            stat_report.status = "PARTIAL"

        save_statistical_report(stat_report, config.output_dir)

        summary = {
            "status": overall_status,
            "experiment_id": config.experiment_id,
            "evaluation_mode": "real_llm_judge",
            "backend": backend.value,
            "timestamp": timestamp,
            "git_commit": run_config["git_commit"],
            "seed": config.seed,
            "n_samples": len(records),
            "models": config.target_keys,
            "baselines": config.baselines,
            "dataset_meta": dataset_meta,
            "publication_mode": config.publication_mode,
            "cache_enabled": effective_cache,
            "config_version": PROVENANCE_SCHEMA_VERSION,
            "elapsed_seconds": round(time.perf_counter() - t_start, 2),
            "model_results": model_results,
            "statistical_analysis_status": stat_report.status,
            "run_dir": str(ctx.run_dir),
        }

        if ds_path.exists():
            summary["dataset_hash"] = dataset_hash
            summary["dataset_path"] = str(ds_path)
            ctx.write_dataset_manifest({
                "path": str(ds_path),
                "sha256": dataset_hash,
                "n_samples": len(records),
                **dataset_meta,
            })

        (config.output_dir / "raw_results.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        (config.output_dir / "metrics.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        ctx.write_metrics(summary)

        update_registry_row(
            Path("experiments/registry.csv"),
            {
                "experiment_id": config.experiment_id,
                "run_id": ctx.run_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": overall_status,
                "git_commit": run_config["git_commit"],
                "dataset": str(ds_path) if ds_path.exists() else config.benchmark_dir,
                "dataset_hash": summary.get("dataset_hash", ""),
                "target_model": ",".join(config.target_keys),
                "judge_model": config.judge_config_key,
                "n_samples": str(len(records)),
                "seed": str(config.seed),
                "metrics_path": str(config.output_dir / "metrics.json"),
                "run_dir": str(ctx.run_dir),
                "notes": f"multi_model;backend={backend.value}",
            },
        )
        return summary
