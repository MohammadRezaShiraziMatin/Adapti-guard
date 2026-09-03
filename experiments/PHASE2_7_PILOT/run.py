#!/usr/bin/env python3
"""Phase 2.7 pilot on frozen eval_v1 — infrastructure validation only.

PILOT ONLY — NOT FINAL SCIENTIFIC EVIDENCE

Usage:
    python experiments/PHASE2_7_PILOT/run.py
"""

from __future__ import annotations

import hashlib
import json
import platform
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
    load_frozen_eval_records,
)
from src.adapti_guard.evaluation.llm_judge import build_judge
from src.adapti_guard.evaluation.target_model import (
    GenerationRequest,
    build_target_model,
    load_model_config,
)
from src.adapti_guard.experiments.defense_baselines import (
    AdaptiveDefenseState,
    get_defense_fn,
)
from src.adapti_guard.experiments.env_loader import load_project_env, validate_openrouter_key

EXPERIMENT_ID = "PHASE2_7_PILOT"
OUTPUT_DIR = ROOT / "experiments" / "PHASE2_7_PILOT"
TARGET_KEY = "model_a"
BASELINES = ["B0", "B6"]
SEED = 42
N_SAMPLES = 15


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def prompt_hash(prompt: str, context: str) -> str:
    return hashlib.sha256(f"{prompt}\n---\n{context}".encode()).hexdigest()


def output_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def run_b6_episode(
    record: dict[str, Any],
    state: AdaptiveDefenseState,
    target,
    judge,
) -> tuple[EvalEpisode, dict[str, Any]]:
    prompt = str(record.get("prompt", ""))
    context = str(record.get("context") or "")
    category = str(record.get("category", "unknown"))
    action, blocked, _ = state.evaluate(
        prompt, context or None, is_attack=True, category=category
    )
    text = f"{context}\n\n{prompt}" if context else prompt
    detection = state.detector.detect(text)
    risk = state.risk_engine.assess(detection)
    defense_level = state.policy_update.state.defense_level

    def _defense_fn(p, c, _a=action, _b=blocked, _d=_):
        return _a, _b, _

    ep = evaluate_episode(record, defense_fn=_defense_fn, target_model=target, judge=judge)
    return ep, {
        "risk_level": risk.level.name if hasattr(risk.level, "name") else str(risk.level),
        "defense_level": defense_level,
        "detector_score": detection.injection_probability,
    }


def build_row(
    ep: EvalEpisode,
    *,
    baseline: str,
    model_id: str,
    git: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "sample_id": ep.id,
        "model": model_id,
        "baseline": baseline,
        "category": ep.category,
        "attack_label": ep.label,
        "prompt_hash": prompt_hash(ep.prompt, ep.context),
        "output_hash": output_hash(ep.model_response) if ep.model_response else "",
        "evaluation_mode": "real_llm_judge",
        "judge_mode": "blind",
        "attack_success": ep.attack_succeeded,
        "utility_success": ep.utility_success,
        "utility_score": None,
        "utility_note": "attack-only frozen eval — benign utility N/A",
        "risk_level": (extra or {}).get("risk_level", "N/A"),
        "defense_level": (extra or {}).get("defense_level", 0),
        "action": ep.defense_action,
        "blocked": ep.blocked,
        "input_tokens": ep.prompt_tokens,
        "output_tokens": ep.completion_tokens,
        "total_tokens": ep.prompt_tokens + ep.completion_tokens,
        "latency_ms": ep.latency_ms,
        "target_latency_ms": ep.target_latency_ms,
        "judge_latency_ms": ep.judge_latency_ms,
        "api_status": "ok" if not ep.metadata.get("judge_parse_error") else "judge_error",
        "judge_reason": ep.judge_reason,
        "judge_raw": ep.metadata.get("judge_raw") or None,
        "judge_model": ep.metadata.get("judge_model") or None,
        "cache_hit": ep.metadata.get("cache_hit"),
        "judge_failure": ep.judge_reason in ("judge_api_error", "judge_parse_error"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git,
        "model_response_preview": ep.model_response[:200] if ep.model_response else "",
        "target_prompt": ep.prompt,
        "target_response": ep.model_response,
    }


def main() -> int:
    load_project_env()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_commit()
    log: list[str] = []

    ok, reason = validate_openrouter_key()
    if not ok:
        (OUTPUT_DIR / "BLOCKED_REPORT.md").write_text(
            f"# Phase 2.7 Pilot BLOCKED\n\nAPI: {reason}\n", encoding="utf-8"
        )
        return 1

    records, dataset_meta = load_frozen_eval_records(n_samples=N_SAMPLES, seed=SEED)
    cfg = load_model_config(ROOT / "configs/models.yaml")
    model_id = cfg["models"][TARGET_KEY]["model"]

    target = build_target_model(TARGET_KEY, config_path=ROOT / "configs/models.yaml")
    probe = target.generate(
        GenerationRequest(prompt="Reply with exactly: OK", system_prompt="You are a test assistant.")
    )
    if probe.error or not probe.text.strip():
        (OUTPUT_DIR / "BLOCKED_REPORT.md").write_text(
            f"# Phase 2.7 Pilot BLOCKED\n\nModel probe failed: {probe.error}\n",
            encoding="utf-8",
        )
        return 1

    config = {
        "experiment_id": EXPERIMENT_ID,
        "pilot_only": True,
        "n_samples": len(records),
        "baselines": BASELINES,
        "target_key": TARGET_KEY,
        "model": model_id,
        "seed": SEED,
        "dataset_meta": dataset_meta,
        "git_commit": git,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (OUTPUT_DIR / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "environment.json").write_text(
        json.dumps({
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git_commit": git,
        }, indent=2),
        encoding="utf-8",
    )

    judge = build_judge(config_path=str(ROOT / "configs/models.yaml"))
    predictions: list[dict[str, Any]] = []
    episodes: dict[str, list[EvalEpisode]] = {b: [] for b in BASELINES}

    for baseline in BASELINES:
        defense_fn, state = get_defense_fn(baseline)
        if state is not None:
            state.reset()
        for record in records:
            extra = {"risk_level": "N/A", "defense_level": 0}
            if baseline == "B6" and isinstance(state, AdaptiveDefenseState):
                ep, extra = run_b6_episode(record, state, target, judge)
            else:
                ep = evaluate_episode(
                    record, defense_fn=defense_fn, target_model=target, judge=judge
                )
            episodes[baseline].append(ep)
            predictions.append(
                build_row(ep, baseline=baseline, model_id=model_id, git=git, extra=extra)
            )
            log.append(
                f"{record['id']} [{baseline}] blocked={ep.blocked} "
                f"attack_success={ep.attack_succeeded} judge={ep.judge_reason}"
            )
            time.sleep(0.1)

    with (OUTPUT_DIR / "predictions.jsonl").open("w", encoding="utf-8") as fh:
        for row in predictions:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    metrics = {b: compute_real_metrics(episodes[b]).to_dict() for b in BASELINES}
    judge_failures = sum(1 for p in predictions if p.get("judge_failure"))
    api_errors = sum(1 for p in predictions if p.get("api_status") != "ok")

    summary = {
        "pilot_status": "PASS" if judge_failures == 0 and api_errors == 0 else "FAIL",
        "metrics": metrics,
        "n_predictions": len(predictions),
        "judge_failures": judge_failures,
        "api_errors": api_errors,
        "note": "PILOT ONLY — NOT FINAL SCIENTIFIC EVIDENCE",
    }
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "run.log").write_text("\n".join(log), encoding="utf-8")

    report = f"""# Phase 2.7 Pilot Report

**PILOT ONLY — NOT FINAL SCIENTIFIC EVIDENCE**

## Status: {summary['pilot_status']}

- Samples: {len(records)}
- Model: `{model_id}`
- Baselines: B0, B6
- Dataset SHA-256: `{dataset_meta['frozen_sha256']}`
- Judge failures: {judge_failures}
- API errors: {api_errors}

## B0 ASR: {metrics['B0'].get('asr', 'N/A')}
## B6 ASR: {metrics['B6'].get('asr', 'N/A')}

Utility: N/A (attack-only frozen eval set; no benign holdout)

See `predictions.jsonl` for raw target/judge outputs.
"""
    (OUTPUT_DIR / "REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["pilot_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
