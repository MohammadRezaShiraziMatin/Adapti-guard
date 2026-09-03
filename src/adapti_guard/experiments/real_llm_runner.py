"""End-to-end real LLM evaluation pipeline for Q1 experiments."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

from src.adapti_guard.evaluation.attack_success import (
    EvalEpisode,
    compute_real_metrics,
    evaluate_episode,
    load_benchmark_records,
)
from src.adapti_guard.evaluation.experiment_logging import (
    ExperimentRunContext,
    sha256_file,
    update_registry_row,
)
from src.adapti_guard.evaluation.llm_judge import LLMJudge, build_judge
from src.adapti_guard.evaluation.provenance import (
    ExperimentValidity,
    classify_real_llm_validity,
)
from src.adapti_guard.evaluation.statistics import bootstrap_ci
from src.adapti_guard.evaluation.target_model import (
    OllamaTargetModel,
    build_target_model,
    load_model_config,
)
from src.adapti_guard.experiments.env_loader import (
    load_project_env,
    validate_gemini_key,
    validate_groq_key,
    validate_openrouter_key,
)

load_project_env()


def _adapti_guard_defense_fn(defense_level: int = 1):
    from src.adapti_guard.core.models import DefenseAction
    from src.adapti_guard.defense.action_layer import DefenseActionLayer
    from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
    from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
    from src.adapti_guard.risk.risk_engine import RiskEngine

    detector = PromptInjectionDetector()
    risk_engine = RiskEngine()
    policy_engine = DefensePolicyEngine()
    action_layer = DefenseActionLayer()

    def fn(prompt: str, context: str | None = None):
        text = f"{context}\n\n{prompt}" if context else prompt
        detection = detector.detect(text)
        risk = risk_engine.assess(detection)
        decision = policy_engine.decide(
            risk=risk, tool_sensitive=False, defense_level=defense_level
        )
        defense = action_layer.execute(decision.action, prompt)
        blocked = not defense.allowed
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)
        return action, blocked, defense.content if not blocked else ""

    return fn


def _provider_for_config_key(
    target_config_key: str,
    models_config: str,
) -> str:
    try:
        cfg = load_model_config(models_config)
        return str(cfg.get("models", {}).get(target_config_key, {}).get("provider", "openrouter"))
    except Exception:
        return "openrouter"


def _validate_provider_credentials(provider: str) -> tuple[bool, str, str]:
    """Return (ok, reason, key_env_name) for the target provider."""
    if provider == "groq":
        ok, reason = validate_groq_key()
        return ok, reason, "GROQ_API_KEY"
    if provider in ("google", "gemini"):
        ok, reason = validate_gemini_key()
        return ok, reason, "GEMINI_API_KEY"
    if provider == "ollama":
        if OllamaTargetModel.is_available():
            return True, "ok", "OLLAMA"
        return False, "Ollama not available at localhost:11434", "OLLAMA"
    ok, reason = validate_openrouter_key()
    return ok, reason, "OPENROUTER_API_KEY"


def run_real_llm_evaluation(
    *,
    experiment_id: str,
    output_dir: Path,
    target_config_key: str = "target_3",
    defense_fn: Callable | None = None,
    split: str = "test",
    n_samples: int = 500,
    seed: int = 42,
    benchmark_dir: str = "datasets/benchmark_q1",
    models_config: str = "configs/models.yaml",
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    provider = _provider_for_config_key(target_config_key, models_config)
    valid, key_reason, key_env = _validate_provider_credentials(provider)
    api_key_present = (
        True
        if provider == "ollama"
        else bool(os.getenv(key_env, "").strip())
    )
    if not valid:
        blocked = {
            "status": "BLOCKED",
            "reason": key_reason,
            "experiment_id": experiment_id,
            "provider": provider,
            "target_config_key": target_config_key,
            "api_key_env": key_env,
            "api_key_present": api_key_present,
            "n_samples_requested": n_samples,
        }
        (output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
        (output_dir / "logs.json").write_text(json.dumps({"blocked": True}, indent=2))
        return blocked

    records = load_benchmark_records(split=split, limit=n_samples, benchmark_dir=benchmark_dir)
    if not records:
        return {"status": "BLOCKED", "reason": "no benchmark records", "provider": provider}

    defense_fn = defense_fn or _adapti_guard_defense_fn()

    with ExperimentRunContext.create(experiment_id, config={
        "target": target_config_key,
        "provider": provider,
        "split": split,
        "n_samples": len(records),
        "seed": seed,
        "benchmark_dir": benchmark_dir,
        "backend": provider,
    }) as ctx:
        try:
            target = build_target_model(target_config_key, config_path=models_config)
            judge = build_judge(config_path=models_config)
        except Exception as exc:
            blocked = {
                "status": "BLOCKED",
                "reason": str(exc),
                "provider": provider,
                "target_config_key": target_config_key,
            }
            ctx.write_metrics(blocked)
            return blocked

        ctx.write_model_config({
            "target": target_config_key,
            "provider": provider,
            "judge": "judge",
            "api_key_env": key_env,
            "api_key_present": api_key_present,
        })
        bench_path = Path(benchmark_dir) / f"{split}.jsonl"
        if bench_path.exists():
            ctx.write_dataset_manifest({
                "path": str(bench_path),
                "sha256": sha256_file(bench_path),
                "n_samples": len(records),
            })

        episodes: list[EvalEpisode] = []
        predictions_path = output_dir / "predictions.jsonl"
        if predictions_path.exists():
            predictions_path.unlink()
        latency_rows: list[dict[str, Any]] = []
        cost_rows: list[dict[str, Any]] = []
        log_rows: list[dict[str, Any]] = []

        t_start = time.perf_counter()
        for i, record in enumerate(records):
            ep = evaluate_episode(
                record,
                defense_fn=defense_fn,
                target_model=target,
                judge=judge,
            )
            episodes.append(ep)

            pred_row = {
                "id": ep.id,
                "category": ep.category,
                "label": ep.label,
                "blocked": ep.blocked,
                "attack_succeeded": ep.attack_succeeded,
                "utility_success": ep.utility_success,
                "model_response_preview": ep.model_response[:300],
                "judge_reason": ep.judge_reason,
                "provider": provider,
            }
            with predictions_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(pred_row, ensure_ascii=False) + "\n")

            latency_rows.append({
                "id": ep.id,
                "target_ms": ep.target_latency_ms,
                "judge_ms": ep.judge_latency_ms,
                "total_ms": ep.latency_ms,
            })
            cost_rows.append({
                "id": ep.id,
                "prompt_tokens": ep.prompt_tokens,
                "completion_tokens": ep.completion_tokens,
            })
            log_rows.append({
                "id": ep.id,
                "index": i,
                "blocked": ep.blocked,
                "attack_succeeded": ep.attack_succeeded,
            })
            ctx.append_response(pred_row)
            if (i + 1) % 50 == 0:
                ctx.log_stdout(f"Processed {i + 1}/{len(records)}")

        metrics = compute_real_metrics(episodes)
        metrics_dict = metrics.to_dict()

        validity, validity_issues = classify_real_llm_validity(
            {"status": "COMPLETED", "metrics": metrics_dict, "n_samples": len(records)},
            min_samples=1,
        )

        auth_errors = sum(
            1 for ep in episodes
            if "401" in ep.model_response
            or ep.judge_reason in ("judge_api_error", "judge_parse_error")
            or ep.metadata.get("judge_parse_error")
        )
        if validity == ExperimentValidity.INVALID or (
            auth_errors == len(episodes) and len(episodes) > 0
        ):
            blocked = {
                "status": "INVALID",
                "reason": validity_issues[0] if validity_issues else (
                    f"API authentication failed — check {key_env}"
                ),
                "experiment_id": experiment_id,
                "provider": provider,
                "n_samples": len(episodes),
                "auth_errors": auth_errors,
                "n_judge_errors": metrics.n_judge_errors,
                "evaluation_mode": "real_llm_judge",
                "metrics": metrics_dict,
                "validity_issues": validity_issues,
            }
            (output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
            ctx.write_metrics(blocked)
            return blocked

        asr_ci = bootstrap_ci(
            [1.0 if ep.attack_succeeded and ep.label == "attack" else 0.0
             for ep in episodes if ep.label == "attack"],
            seed=seed,
        )

        result = {
            "status": "COMPLETED",
            "experiment_id": experiment_id,
            "target_model": target_config_key,
            "provider": provider,
            "n_samples": len(records),
            "elapsed_seconds": round(time.perf_counter() - t_start, 2),
            "metrics": metrics.to_dict(),
            "asr_bootstrap_ci": {
                "point": asr_ci[0], "lower": asr_ci[1], "upper": asr_ci[2],
            },
            "run_dir": str(ctx.run_dir),
        }

        (output_dir / "metrics.json").write_text(json.dumps(result, indent=2))
        (output_dir / "latency.json").write_text(json.dumps(latency_rows, indent=2))
        (output_dir / "cost.json").write_text(json.dumps({
            "total_prompt_tokens": sum(r["prompt_tokens"] for r in cost_rows),
            "total_completion_tokens": sum(r["completion_tokens"] for r in cost_rows),
            "per_episode": cost_rows,
        }, indent=2))
        (output_dir / "logs.json").write_text(json.dumps(log_rows, indent=2))
        ctx.write_metrics(result)

        update_registry_row(
            Path("experiments/registry.csv"),
            {
                "experiment_id": experiment_id,
                "run_id": ctx.run_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "COMPLETED",
                "git_commit": ctx.run_dir.joinpath("git_commit.txt").read_text().strip(),
                "dataset": benchmark_dir,
                "dataset_hash": sha256_file(bench_path) if bench_path.exists() else "",
                "target_model": target_config_key,
                "judge_model": "judge",
                "n_samples": str(len(records)),
                "seed": str(seed),
                "metrics_path": str(output_dir / "metrics.json"),
                "run_dir": str(ctx.run_dir),
                "notes": f"provider={provider}",
            },
        )
        return result
