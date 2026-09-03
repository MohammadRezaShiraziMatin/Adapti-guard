"""Publication-grade real LLM evaluation pipeline.

Scientific contract:
- Target LLM generates responses for non-blocked prompts.
- Independent LLM judge determines ASR and utility.
- Simulation/regex ASR is NEVER used in this module.
- All runs produce full provenance artifacts.
"""

from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from src.adapti_guard.evaluation.attack_success import (
    EvalEpisode,
    compute_real_metrics,
    episode_judge_failed,
    evaluate_episode,
    load_benchmark_mixed_records,
    load_benchmark_records,
    load_frozen_eval_records,
    load_unified_dataset_records,
)
from src.adapti_guard.evaluation.experiment_logging import (
    ExperimentRunContext,
    git_commit,
    sha256_file,
    update_registry_row,
)
from src.adapti_guard.evaluation.prediction_provenance import (
    PROVENANCE_SCHEMA_VERSION,
    build_prediction_row,
)
from src.adapti_guard.evaluation.evaluation_modes import REAL_LLM_JUDGE
from src.adapti_guard.evaluation.llm_judge import LLMJudge, build_judge
from src.adapti_guard.evaluation.statistics import bootstrap_ci
from src.adapti_guard.evaluation.target_model import (
    OllamaTargetModel,
    TargetModel,
    build_target_model,
)
from src.adapti_guard.experiments.defense_baselines import get_defense_fn
from src.adapti_guard.experiments.env_loader import (
    validate_gemini_key,
    validate_groq_key,
    validate_openrouter_key,
)


class EvaluationBackend(str, Enum):
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    GROQ = "groq"
    AUTO = "auto"


DEFAULT_BASELINES = ["B0", "B1", "B2_L1", "B2_L2", "B2_L3", "B3"]

UNIFIED_DATASET_DEFAULT = (
    Path.home()
    / "datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl"
)


@dataclass
class PipelineConfig:
    experiment_id: str = "REAL-LLM-EVAL"
    output_dir: Path = Path("experiments/REAL_LLM_EVAL")
    target_config_key: str = "target_2"
    judge_config_key: str = "judge_primary"
    models_config: str = "configs/models.yaml"
    backend: EvaluationBackend = EvaluationBackend.AUTO
    baselines: list[str] = field(default_factory=lambda: list(DEFAULT_BASELINES))
    split: str = "test"
    n_samples: int | None = None
    attack_n: int | None = None
    benign_n: int | None = None
    seed: int = 42
    benchmark_dir: str = "datasets/benchmark_q1"
    unified_dataset: str | None = None
    use_unified_dataset: bool = False
    frozen_dataset: str | None = None
    use_frozen_eval: bool = False


@dataclass
class BaselineRunContext:
    experiment_id: str
    model_id: str
    model_config_key: str
    git_commit: str
    seed: int
    dataset_hash: str
    cache_enabled: bool
    config_version: str = PROVENANCE_SCHEMA_VERSION


@dataclass
class BaselineRunResult:
    baseline: str
    status: str
    n_samples: int
    metrics: dict[str, Any]
    episodes_path: str
    asr_bootstrap_ci: dict[str, float] | None = None
    notes: list[str] = field(default_factory=list)


def resolve_backend(backend: EvaluationBackend) -> tuple[EvaluationBackend, str | None]:
    """Select evaluation backend. Returns (backend, block_reason)."""
    if backend == EvaluationBackend.OLLAMA:
        if not OllamaTargetModel.is_available():
            return backend, "Ollama not available at localhost:11434"
        return backend, None

    if backend == EvaluationBackend.GEMINI:
        valid, reason = validate_gemini_key()
        if not valid:
            return backend, reason
        return backend, None

    if backend == EvaluationBackend.GROQ:
        valid, reason = validate_groq_key()
        if not valid:
            return backend, reason
        return backend, None

    if backend == EvaluationBackend.OPENROUTER:
        valid, reason = validate_openrouter_key()
        if not valid:
            return backend, reason
        return backend, None

    # AUTO: prefer Gemini if key valid, else OpenRouter, else Ollama.
    # Groq is intentionally NOT an AUTO default — primary Groq runs must set backend=groq.
    gemini_ok, gemini_reason = validate_gemini_key()
    if gemini_ok:
        return EvaluationBackend.GEMINI, None
    valid, reason = validate_openrouter_key()
    if valid:
        return EvaluationBackend.OPENROUTER, None
    if OllamaTargetModel.is_available():
        return EvaluationBackend.OLLAMA, None
    groq_ok, groq_reason = validate_groq_key()
    return EvaluationBackend.AUTO, (
        f"No AUTO backend available. Gemini: {gemini_reason}. "
        f"OpenRouter: {reason}. Ollama: not running. "
        f"Groq key present={groq_ok} ({groq_reason}; use backend=groq explicitly)."
    )


def _resolve_independent_judge(
    config: PipelineConfig,
    *,
    cache_enabled: bool | None,
    target_provider: str,
) -> LLMJudge:
    """Build a judge that is not the same provider+model as the Groq target.

    Preference: OpenRouter primary → Gemini judge → Ollama.
    Raises RuntimeError if none available (caller should BLOCK).
    """
    or_ok, or_reason = validate_openrouter_key()
    if or_ok and target_provider != "openrouter":
        return build_judge(config_path=config.models_config, cache_enabled=cache_enabled)

    gem_ok, gem_reason = validate_gemini_key()
    if gem_ok and target_provider != "google":
        judge_model = build_target_model(
            "gemini_judge",
            config_path=config.models_config,
            cache_enabled=cache_enabled,
        )
        return LLMJudge(
            model=judge_model,
            config_key="gemini_judge",
            fallback_config_key="gemini_judge",
            config_path=config.models_config,
            cache_enabled=cache_enabled,
            use_fallback=False,
        )

    if OllamaTargetModel.is_available() and target_provider != "ollama":
        judge_model = build_target_model(
            "ollama_target",
            config_path=config.models_config,
            cache_enabled=cache_enabled,
        )
        return LLMJudge(
            model=judge_model,
            config_path=config.models_config,
            cache_enabled=cache_enabled,
            use_fallback=False,
        )

    raise RuntimeError(
        "Independent judge unavailable for Groq target. "
        f"OpenRouter: {or_reason}. Gemini: {gem_reason}. "
        "Ollama: not running. Refusing to use Groq as both target and judge. "
        "Experiment must be marked BLOCKED."
    )


def build_models(
    config: PipelineConfig,
    backend: EvaluationBackend,
    *,
    cache_enabled: bool | None = None,
) -> tuple[TargetModel, LLMJudge]:
    target_key = config.target_config_key
    if backend == EvaluationBackend.OLLAMA:
        target_key = "ollama_target"

    if backend == EvaluationBackend.GEMINI and target_key in (
        "target_1",
        "target_2",
        "target_3",
        "model_a",
        "model_b",
        "model_c",
    ):
        target_key = "gemini_target"

    if backend == EvaluationBackend.GROQ:
        if target_key in (
            "target_1",
            "target_2",
            "target_3",
            "model_a",
            "model_b",
            "model_c",
            "gemini_target",
            "ollama_target",
        ):
            target_key = "groq_target"

    target = build_target_model(
        target_key,
        config_path=config.models_config,
        cache_enabled=cache_enabled,
    )

    if backend == EvaluationBackend.OLLAMA:
        judge_model = build_target_model(
            "ollama_target",
            config_path=config.models_config,
            cache_enabled=cache_enabled,
        )
        judge = LLMJudge(model=judge_model, config_path=config.models_config)
    elif backend == EvaluationBackend.GEMINI:
        judge_key = config.judge_config_key
        if judge_key in ("judge_primary", "judge", "judge_fallback"):
            judge_key = "gemini_judge"
        judge_model = build_target_model(
            judge_key,
            config_path=config.models_config,
            cache_enabled=cache_enabled,
        )
        judge = LLMJudge(
            model=judge_model,
            config_key=judge_key,
            fallback_config_key=judge_key,
            config_path=config.models_config,
            cache_enabled=cache_enabled,
            use_fallback=False,
        )
    elif backend == EvaluationBackend.GROQ:
        judge_model = build_target_model(
            "groq_target",
            config_path=config.models_config,
            cache_enabled=cache_enabled,
        )
        judge = LLMJudge(
            model=judge_model,
            config_key="groq_target",
            fallback_config_key="groq_target",
            config_path=config.models_config,
            cache_enabled=cache_enabled,
            use_fallback=False,
        )
    else:
        judge = build_judge(config_path=config.models_config, cache_enabled=cache_enabled)

    return target, judge


def load_records(config: PipelineConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if config.use_frozen_eval:
        records, meta = load_frozen_eval_records(
            frozen_path=config.frozen_dataset or "datasets/frozen/eval_v1/dataset.jsonl",
            n_samples=config.n_samples,
            seed=config.seed,
        )
        return records, meta

    if config.use_unified_dataset:
        path = Path(config.unified_dataset or UNIFIED_DATASET_DEFAULT)
        records, meta = load_unified_dataset_records(
            dataset_path=path,
            attack_n=config.attack_n if config.attack_n is not None else 1500,
            benign_n=config.benign_n if config.benign_n is not None else 500,
            seed=config.seed,
        )
        if config.n_samples is not None:
            records = records[: config.n_samples]
        return records, meta

    # Mixed attack+benign sampling for benchmark_q1 when --attack-n/--benign-n set.
    if config.attack_n is not None or config.benign_n is not None:
        records, meta = load_benchmark_mixed_records(
            split=config.split,
            attack_n=config.attack_n or 0,
            benign_n=config.benign_n or 0,
            seed=config.seed,
            benchmark_dir=config.benchmark_dir,
        )
        return records, meta

    records = load_benchmark_records(
        split=config.split,
        limit=config.n_samples,
        benchmark_dir=config.benchmark_dir,
    )
    return records, {"split": config.split, "benchmark_dir": config.benchmark_dir}


def run_baseline_evaluation(
    baseline_key: str,
    records: list[dict[str, Any]],
    *,
    target: TargetModel,
    judge: LLMJudge,
    output_dir: Path,
    run_context: BaselineRunContext | None = None,
) -> BaselineRunResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    defense_fn, state = get_defense_fn(baseline_key)
    if state is not None:
        state.reset()

    episodes: list[EvalEpisode] = []
    predictions_path = output_dir / f"{baseline_key}_predictions.jsonl"
    if predictions_path.exists():
        predictions_path.unlink()

    for record in records:
        if baseline_key in ("B3", "B6") and state is not None:
            action, blocked, defended = state.evaluate(
                record.get("prompt", ""),
                record.get("context") or None,
                is_attack=record.get("label") == "attack",
                category=record.get("category", "unknown"),
            )

            def _defense_fn(p, c, _a=action, _b=blocked, _d=defended):
                return _a, _b, _d

            ep = evaluate_episode(
                record,
                defense_fn=_defense_fn,
                target_model=target,
                judge=judge,
            )
        else:
            ep = evaluate_episode(
                record,
                defense_fn=defense_fn,
                target_model=target,
                judge=judge,
            )

        ep.metadata["baseline"] = baseline_key
        ep.metadata["evaluation_mode"] = "real_llm_judge"
        episodes.append(ep)

        if run_context is not None:
            pred_row = build_prediction_row(
                ep,
                baseline=baseline_key,
                model_id=run_context.model_id,
                model_config_key=run_context.model_config_key,
                experiment_id=run_context.experiment_id,
                git_commit=run_context.git_commit,
                seed=run_context.seed,
                dataset_hash=run_context.dataset_hash,
                cache_enabled=run_context.cache_enabled,
                config_version=run_context.config_version,
            )
        else:
            pred_row = {
                "id": ep.id,
                "baseline": baseline_key,
                "label": ep.label,
                "category": ep.category,
                "blocked": ep.blocked,
                "defense_action": ep.defense_action,
                "attack_succeeded": ep.attack_succeeded,
                "utility_success": ep.utility_success,
                "judge_reason": ep.judge_reason,
                "model_response_preview": ep.model_response[:300],
                "target_latency_ms": ep.target_latency_ms,
                "judge_latency_ms": ep.judge_latency_ms,
                "latency_ms": ep.latency_ms,
                "prompt_tokens": ep.prompt_tokens,
                "completion_tokens": ep.completion_tokens,
                "target_cache_hit": ep.metadata.get("target_cache_hit"),
                "judge_parse_error": ep.metadata.get("judge_parse_error"),
            }
        with predictions_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(pred_row, ensure_ascii=False) + "\n")
        print(
            f"  [{baseline_key}] {ep.id} blocked={ep.blocked} "
            f"api={pred_row.get('api_status')} reason={ep.judge_reason}",
            flush=True,
        )

    metrics = compute_real_metrics(episodes)
    attack_flags = [
        1.0 if ep.attack_succeeded else 0.0
        for ep in episodes
        if ep.label == "attack" and not episode_judge_failed(ep)
    ]
    asr_ci = bootstrap_ci(attack_flags, seed=42) if attack_flags else None

    metrics_dict = metrics.to_dict()
    metrics_dict["baseline"] = baseline_key
    metrics_dict["evaluation_mode"] = "real_llm_judge"
    metrics_dict["n_judge_errors"] = metrics.n_judge_errors
    if asr_ci is not None:
        metrics_dict["asr_bootstrap_ci"] = {
            "point": asr_ci[0],
            "lower": asr_ci[1],
            "upper": asr_ci[2],
            "n_bootstrap": 10000,
            "seed": 42,
        }

    if run_context is not None:
        sample_ids = [str(r.get("id", "")) for r in records]
        metrics_dict.update({
            "experiment_id": run_context.experiment_id,
            "model_id": run_context.model_id,
            "model_config_key": run_context.model_config_key,
            "git_commit": run_context.git_commit,
            "seed": run_context.seed,
            "dataset_hash": run_context.dataset_hash,
            "cache_enabled": run_context.cache_enabled,
            "config_version": run_context.config_version,
            "n_samples": len(records),
            "provenance": {
                "experiment_id": run_context.experiment_id,
                "model_id": run_context.model_id,
                "model_config_key": run_context.model_config_key,
                "baseline": baseline_key,
                "n_samples": len(records),
                "seed": run_context.seed,
                "dataset_hash": run_context.dataset_hash,
                "cache_enabled": run_context.cache_enabled,
                "config_version": run_context.config_version,
                "sample_ids": sample_ids,
                "git_commit": run_context.git_commit,
            },
        })

    (output_dir / f"{baseline_key}_metrics.json").write_text(
        json.dumps(metrics_dict, indent=2), encoding="utf-8"
    )

    return BaselineRunResult(
        baseline=baseline_key,
        status="COMPLETED",
        n_samples=len(episodes),
        metrics=metrics_dict,
        episodes_path=str(predictions_path),
        asr_bootstrap_ci=(
            {"point": asr_ci[0], "lower": asr_ci[1], "upper": asr_ci[2]}
            if asr_ci
            else None
        ),
    )


def run_real_llm_pipeline(config: PipelineConfig) -> dict[str, Any]:
    """Execute full real LLM evaluation with provenance."""
    config.output_dir.mkdir(parents=True, exist_ok=True)

    backend, block_reason = resolve_backend(config.backend)
    if block_reason:
        blocked = {
            "status": "BLOCKED",
            "reason": block_reason,
            "experiment_id": config.experiment_id,
            "backend": backend.value,
        }
        (config.output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
        return blocked

    records, dataset_meta = load_records(config)
    if not records:
        blocked = {"status": "BLOCKED", "reason": "no evaluation records"}
        (config.output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
        return blocked

    with ExperimentRunContext.create(
        config.experiment_id,
        config={
            "target": config.target_config_key,
            "judge": config.judge_config_key,
            "backend": backend.value,
            "baselines": config.baselines,
            "n_samples": len(records),
            "seed": config.seed,
            "evaluation_mode": "real_llm_judge",
            "dataset_meta": dataset_meta,
        },
    ) as ctx:
        try:
            target, judge = build_models(config, backend)
        except Exception as exc:
            blocked = {"status": "BLOCKED", "reason": str(exc)}
            ctx.write_metrics(blocked)
            (config.output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
            return blocked

        ctx.write_model_config({
            "target": config.target_config_key,
            "judge": config.judge_config_key,
            "backend": backend.value,
        })
        if config.use_unified_dataset:
            ds_path = Path(config.unified_dataset or UNIFIED_DATASET_DEFAULT)
            if ds_path.exists():
                ctx.write_dataset_manifest({
                    "path": str(ds_path),
                    "sha256": sha256_file(ds_path),
                    "n_samples": len(records),
                    **dataset_meta,
                })
        else:
            bench_path = Path(config.benchmark_dir) / f"{config.split}.jsonl"
            if bench_path.exists():
                ctx.write_dataset_manifest({
                    "path": str(bench_path),
                    "sha256": sha256_file(bench_path),
                    "n_samples": len(records),
                })

        t_start = time.perf_counter()
        baseline_results: list[BaselineRunResult] = []

        for baseline_key in config.baselines:
            ctx.log_stdout(f"Running baseline {baseline_key} ({len(records)} episodes)")
            result = run_baseline_evaluation(
                baseline_key,
                records,
                target=target,
                judge=judge,
                output_dir=config.output_dir / baseline_key,
            )
            baseline_results.append(result)
            ctx.log_stdout(
                f"  {baseline_key}: ASR={result.metrics.get('asr', 'N/A')} "
                f"Utility={result.metrics.get('utility', 'N/A')}"
            )

        # Write aggregate outputs
        all_metrics = {r.baseline: r.metrics for r in baseline_results}
        summary = {
            "status": "COMPLETED",
            "experiment_id": config.experiment_id,
            "backend": backend.value,
            "evaluation_mode": "real_llm_judge",
            "n_samples": len(records),
            "n_baselines": len(baseline_results),
            "elapsed_seconds": round(time.perf_counter() - t_start, 2),
            "baselines": [asdict(r) for r in baseline_results],
            "metrics": all_metrics,
            "run_dir": str(ctx.run_dir),
            "dataset_meta": dataset_meta,
        }

        (config.output_dir / "raw_results.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )

        csv_path = config.output_dir / "metrics.csv"
        fieldnames = [
            "baseline", "asr", "defense_rate", "fpr", "utility",
            "latency_ms_mean", "n_attack", "n_benign", "n_judge_errors",
            "evaluation_mode",
        ]
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in baseline_results:
                row = dict(r.metrics)
                row["evaluation_mode"] = "real_llm_judge"
                writer.writerow(row)

        (config.output_dir / "metrics.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        ctx.write_metrics(summary)
        ctx.write_summary(
            f"# {config.experiment_id}\n\n"
            f"- Backend: {backend.value}\n"
            f"- Samples: {len(records)}\n"
            f"- Mode: real_llm_judge (no simulation ASR)\n"
            f"- Baselines: {', '.join(config.baselines)}\n"
        )

        update_registry_row(
            Path("experiments/registry.csv"),
            {
                "experiment_id": config.experiment_id,
                "run_id": ctx.run_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "COMPLETED",
                "git_commit": ctx.run_dir.joinpath("git_commit.txt").read_text().strip(),
                "dataset": str(config.benchmark_dir),
                "dataset_hash": "",
                "target_model": config.target_config_key,
                "judge_model": config.judge_config_key,
                "n_samples": str(len(records)),
                "seed": str(config.seed),
                "metrics_path": str(config.output_dir / "metrics.json"),
                "run_dir": str(ctx.run_dir),
                "notes": f"backend={backend.value}",
            },
        )
        return summary
