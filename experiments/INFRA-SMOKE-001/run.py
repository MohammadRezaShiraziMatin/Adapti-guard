#!/usr/bin/env python3
"""INFRA-SMOKE-001: Real OpenRouter pipeline validation (n=5, B0 vs B6).

Usage:
    python experiments/INFRA-SMOKE-001/run.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.evaluation.attack_success import (
    EvalEpisode,
    compute_real_metrics,
    evaluate_episode,
    load_benchmark_records,
)
from src.adapti_guard.evaluation.experiment_logging import sha256_file
from src.adapti_guard.evaluation.llm_judge import LLMJudge, build_judge
from src.adapti_guard.evaluation.target_model import (
    GenerationRequest,
    build_target_model,
    load_model_config,
)
from src.adapti_guard.experiments.defense_baselines import (
    AdaptiveDefenseState,
    get_defense_fn,
    make_b3_adaptive,
)
from src.adapti_guard.experiments.env_loader import load_project_env, validate_openrouter_key

EXPERIMENT_ID = "INFRA-SMOKE-001"
OUTPUT_DIR = ROOT / "experiments" / "INFRA-SMOKE-001"
TARGET_KEY = "model_a"
BASELINES = ["B0", "B6"]
SEED = 42
N_ATTACK = 3
N_BENIGN = 2

REQUIRED_PROVENANCE = [
    "experiment_id",
    "sample_id",
    "model",
    "baseline",
    "category",
    "attack_label",
    "prompt_hash",
    "output_hash",
    "evaluation_mode",
    "judge_mode",
    "attack_success",
    "utility_success",
    "utility_score",
    "risk_level",
    "defense_level",
    "action",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "latency_ms",
    "cost",
    "api_status",
    "error",
    "timestamp",
    "git_commit",
]


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def prompt_hash(prompt: str, context: str) -> str:
    payload = f"{prompt}\n---\n{context}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def output_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def select_smoke_samples() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import random

    records = load_benchmark_records(split="test", benchmark_dir=ROOT / "datasets/benchmark_q1")
    attacks = [r for r in records if r.get("label") == "attack"]
    benign = [r for r in records if r.get("label") == "benign"]
    rng = random.Random(SEED)
    rng.shuffle(attacks)
    rng.shuffle(benign)
    selected = attacks[:N_ATTACK] + benign[:N_BENIGN]
    if len(selected) < N_ATTACK + N_BENIGN:
        raise RuntimeError(
            f"Insufficient samples: need {N_ATTACK}+{N_BENIGN}, got {len(selected)}"
        )
    meta = {
        "seed": SEED,
        "n_attack": N_ATTACK,
        "n_benign": N_BENIGN,
        "sample_ids": [r["id"] for r in selected],
        "dataset": "datasets/benchmark_q1/test.jsonl",
        "dataset_sha256": sha256_file(ROOT / "datasets/benchmark_q1/test.jsonl"),
    }
    return selected, meta


def probe_model(target_key: str) -> dict[str, Any]:
    """Verify exact model is available on OpenRouter."""
    cfg = load_model_config(ROOT / "configs/models.yaml")
    spec = cfg.get("models", {}).get(target_key, {})
    model_id = spec.get("model", "")
    if model_id != "openai/gpt-4o-mini":
        return {"status": "MODEL_MISMATCH", "expected": "openai/gpt-4o-mini", "got": model_id}

    target = build_target_model(target_key, config_path=ROOT / "configs/models.yaml")
    result = target.generate(
        GenerationRequest(prompt="Reply with exactly: OK", system_prompt="You are a test assistant.")
    )
    if result.error:
        return {"status": "MODEL_UNAVAILABLE", "model": model_id, "error": result.error}
    if not result.text.strip():
        return {"status": "MODEL_UNAVAILABLE", "model": model_id, "error": "empty_response"}
    return {
        "status": "OK",
        "model": model_id,
        "response_preview": result.text[:50],
        "usage": result.usage,
        "latency_ms": result.latency_ms,
    }


def run_b6_episode(
    record: dict[str, Any],
    state: AdaptiveDefenseState,
    target,
    judge: LLMJudge,
) -> tuple[EvalEpisode, dict[str, Any]]:
    """Run B6 with defense metadata captured."""
    from src.adapti_guard.core.models import DefenseAction

    prompt = str(record.get("prompt", ""))
    context = str(record.get("context") or "")
    label = str(record.get("label", "attack"))
    category = str(record.get("category", "unknown"))
    is_attack = label == "attack"

    action, blocked, defended = state.evaluate(
        prompt, context or None, is_attack=is_attack, category=category
    )

    # Capture risk/level from last evaluation internals
    text = f"{context}\n\n{prompt}" if context else prompt
    detection = state.detector.detect(text)
    risk = state.risk_engine.assess(detection)
    defense_level = state.policy_update.state.defense_level

    def _defense_fn(p, c, _a=action, _b=blocked, _d=defended):
        return _a, _b, _d

    ep = evaluate_episode(record, defense_fn=_defense_fn, target_model=target, judge=judge)
    extra = {
        "risk_level": risk.level.name if hasattr(risk.level, "name") else str(risk.level),
        "defense_level": defense_level,
        "detector_score": detection.injection_probability,
    }
    return ep, extra


def build_prediction_row(
    ep: EvalEpisode,
    *,
    baseline: str,
    model_id: str,
    git: str,
    extra: dict[str, Any] | None = None,
    target_error: str | None = None,
) -> dict[str, Any]:
    is_benign = ep.label != "attack"
    utility_score = 1.0 if (is_benign and ep.utility_success) else 0.0
    inp = ep.prompt_tokens
    out = ep.completion_tokens
    total = inp + out
    response_for_hash = ep.model_response if not target_error else ""
    api_status = "ok" if not target_error and (ep.blocked or ep.model_response.strip()) else "error"

    row = {
        "experiment_id": EXPERIMENT_ID,
        "sample_id": ep.id,
        "model": model_id,
        "baseline": baseline,
        "category": ep.category,
        "attack_label": ep.label,
        "prompt_hash": prompt_hash(ep.prompt, ep.context),
        "output_hash": output_hash(response_for_hash) if response_for_hash else "",
        "evaluation_mode": "real_llm_judge",
        "judge_mode": "blind",
        "attack_success": ep.attack_succeeded,
        "utility_success": ep.utility_success,
        "utility_score": utility_score,
        "risk_level": (extra or {}).get("risk_level", "N/A"),
        "defense_level": (extra or {}).get("defense_level", 0 if baseline == "B0" else None),
        "detector_score": (extra or {}).get("detector_score"),
        "action": ep.defense_action,
        "blocked": ep.blocked,
        "input_tokens": inp,
        "output_tokens": out,
        "total_tokens": total,
        "latency_ms": ep.latency_ms,
        "target_latency_ms": ep.target_latency_ms,
        "judge_latency_ms": ep.judge_latency_ms,
        "cost": None,
        "cost_source": "not_reported_by_api",
        "api_status": api_status,
        "error": target_error or ep.metadata.get("judge_parse_error"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git,
        "judge_reason": ep.judge_reason,
        "model_response_preview": ep.model_response[:200] if ep.model_response else "",
    }
    if row["defense_level"] is None:
        row["defense_level"] = (extra or {}).get("defense_level", 1)
    return row


def validate_results(
    predictions: list[dict[str, Any]],
    sample_ids: list[str],
) -> dict[str, Any]:
    n_b0 = sum(1 for p in predictions if p["baseline"] == "B0")
    n_b6 = sum(1 for p in predictions if p["baseline"] == "B6")
    auth_errors = sum(
        1 for p in predictions
        if p.get("error") and "401" in str(p.get("error"))
    )
    judge_errors = sum(
        1 for p in predictions
        if p.get("error") and ("judge" in str(p.get("error")).lower() or "parse" in str(p.get("judge_reason", "")).lower())
    )
    judge_errors = sum(
        1 for p in predictions if p.get("judge_reason") in ("judge_api_error", "judge_parse_error")
    )
    empty_outputs = sum(
        1 for p in predictions
        if not p.get("blocked") and not p.get("model_response_preview", "").strip()
        and p.get("api_status") == "error"
    )
    missing_prov = sum(
        1 for p in predictions
        for field in REQUIRED_PROVENANCE
        if field not in p
    )
    prompt_tokens_total = sum(p.get("input_tokens", 0) for p in predictions)

    b0_ids = {p["sample_id"] for p in predictions if p["baseline"] == "B0"}
    b6_ids = {p["sample_id"] for p in predictions if p["baseline"] == "B6"}
    same_ids = b0_ids == b6_ids == set(sample_ids)

    api_errors = sum(1 for p in predictions if p.get("api_status") == "error" and not p.get("blocked"))

    checks = {
        "n_samples": len(set(sample_ids)) == 5,
        "n_predictions": len(predictions) == 10,
        "b0_count": n_b0 == 5,
        "b6_count": n_b6 == 5,
        "same_sample_ids": same_ids,
        "auth_errors_zero": auth_errors == 0,
        "judge_errors_zero": judge_errors == 0,
        "empty_outputs_zero": empty_outputs == 0,
        "missing_provenance_zero": missing_prov == 0,
        "evaluation_mode_real": all(p.get("evaluation_mode") == "real_llm_judge" for p in predictions),
        "prompt_tokens_positive": prompt_tokens_total > 0,
        "api_errors_zero": api_errors == 0,
    }
    passed = all(checks.values())

    return {
        "smoke_test": "PASS" if passed else "FAIL",
        "checks": checks,
        "n_samples": 5,
        "n_predictions": len(predictions),
        "n_api_calls": sum(1 for p in predictions if not p.get("blocked")),
        "n_successful_api_calls": sum(
            1 for p in predictions
            if not p.get("blocked") and p.get("api_status") == "ok"
        ),
        "auth_errors": auth_errors,
        "judge_errors": judge_errors,
        "empty_outputs": empty_outputs,
        "missing_provenance": missing_prov,
        "prompt_tokens_total": prompt_tokens_total,
        "b0_count": n_b0,
        "b6_count": n_b6,
    }


def main() -> int:
    load_project_env()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []
    git = git_commit()

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    # Preflight
    ok, reason = validate_openrouter_key()
    if not ok:
        log(f"FAIL: API blocked — {reason}")
        (OUTPUT_DIR / "run.log").write_text("\n".join(log_lines))
        return 1

    log("=== INFRA-SMOKE-001 ===")
    probe = probe_model(TARGET_KEY)
    log(f"Model probe: {json.dumps(probe)}")
    if probe.get("status") != "OK":
        config = {"experiment_id": EXPERIMENT_ID, "probe": probe, "status": "FAILED"}
        (OUTPUT_DIR / "config.json").write_text(json.dumps(config, indent=2))
        (OUTPUT_DIR / "summary.json").write_text(json.dumps({"smoke_test": "FAIL", "reason": probe}, indent=2))
        (OUTPUT_DIR / "run.log").write_text("\n".join(log_lines))
        return 1

    model_id = probe["model"]
    samples, dataset_meta = select_smoke_samples()
    log(f"Selected samples: {dataset_meta['sample_ids']}")

    config = {
        "experiment_id": EXPERIMENT_ID,
        "n_samples": 5,
        "baselines": BASELINES,
        "target_key": TARGET_KEY,
        "model": model_id,
        "seed": SEED,
        "evaluation_mode": "real_llm_judge",
        "dataset_meta": dataset_meta,
        "git_commit": git,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (OUTPUT_DIR / "config.json").write_text(json.dumps(config, indent=2))

    target = build_target_model(TARGET_KEY, config_path=ROOT / "configs/models.yaml")
    judge = build_judge(config_path=str(ROOT / "configs/models.yaml"))

    all_predictions: list[dict[str, Any]] = []
    all_episodes: dict[str, list[EvalEpisode]] = {"B0": [], "B6": []}

    for baseline in BASELINES:
        log(f"\n--- Baseline {baseline} ---")
        defense_fn, state = get_defense_fn(baseline)
        if state is not None:
            state.reset()

        for record in samples:
            extra: dict[str, Any] = {"risk_level": "N/A", "defense_level": 0}

            if baseline == "B6" and isinstance(state, AdaptiveDefenseState):
                ep, extra = run_b6_episode(record, state, target, judge)
            else:
                ep = evaluate_episode(
                    record, defense_fn=defense_fn, target_model=target, judge=judge
                )
                extra = {"risk_level": "N/A", "defense_level": 0}

            target_error = None
            if not ep.blocked:
                if ep.model_response.startswith("[TARGET_ERROR:"):
                    target_error = ep.model_response
                elif not ep.model_response.strip():
                    target_error = "empty_model_output"

            row = build_prediction_row(
                ep, baseline=baseline, model_id=model_id, git=git, extra=extra,
                target_error=target_error,
            )
            all_predictions.append(row)
            all_episodes[baseline].append(ep)
            log(f"  {record['id']} [{baseline}]: action={ep.defense_action} blocked={ep.blocked} "
                f"attack_success={ep.attack_succeeded} utility={ep.utility_success}")

    # Write predictions.jsonl
    pred_path = OUTPUT_DIR / "predictions.jsonl"
    with pred_path.open("w", encoding="utf-8") as fh:
        for row in all_predictions:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    validation = validate_results(all_predictions, dataset_meta["sample_ids"])

    metrics = {}
    for baseline in BASELINES:
        m = compute_real_metrics(all_episodes[baseline])
        metrics[baseline] = m.to_dict()

    total_in = sum(p["input_tokens"] for p in all_predictions)
    total_out = sum(p["output_tokens"] for p in all_predictions)
    latencies = [p["latency_ms"] for p in all_predictions if p["latency_ms"] > 0]

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "smoke_test": validation["smoke_test"],
        "validation": validation,
        "model": model_id,
        "metrics": metrics,
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_tokens": total_in + total_out,
        "estimated_cost_usd": None,
        "cost_note": "OpenRouter did not return USD cost in response; not estimated",
        "mean_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
        "evaluation_mode": "real_llm_judge",
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(summary, indent=2))
    (OUTPUT_DIR / "run.log").write_text("\n".join(log_lines))

    log(f"\n=== SMOKE TEST: {validation['smoke_test']} ===")
    log(json.dumps(validation, indent=2))

    return 0 if validation["smoke_test"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
