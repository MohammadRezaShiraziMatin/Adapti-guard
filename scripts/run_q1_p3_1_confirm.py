#!/usr/bin/env python3
"""Q1-P3-1 supplemental confirmatory runner (STATIC-A3 vs B0 on phase1_confirm_v1).

NOT AUTHORIZED TO RUN live until Matin signs DECISION_LOCK_Q1_P3_1_BASELINE.md + budget.

Offline modes (default safe):
  --preflight-only   hash/lock checks, no API
  --defense-smoke    exercise defense fns on full pack, no Target/Judge calls

When authorized (human only):
  --require-key --output experiments/real_llm_eval/Q1_P3_1/<run_id>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapti_guard.experiments.env_loader import load_project_env

load_project_env()

from adapti_guard.evaluation.experiment_logging import git_commit
from adapti_guard.experiments.defense_baselines import get_defense_fn
from adapti_guard.experiments.real_llm_pipeline import (
    BaselineRunContext,
    EvaluationBackend,
    PipelineConfig,
    build_models,
)
from adapti_guard.experiments.vnext_confirm import load_predictions

import run_phase1_confirm as p1

Q1_P3_1_ARMS: tuple[str, ...] = ("B0", "STATIC-A3")
Q1_P3_1_TREATMENT = "STATIC-A3"
Q1_P3_1_ARTIFACT_ROOT = ROOT / "experiments" / "real_llm_eval" / "Q1_P3_1"
ARM_ID = "Q1-P3-1"


def defense_smoke(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run label-blind defense forward passes only — no LLM/API."""
    stats: dict[str, Any] = {"arm_id": ARM_ID, "arms": {}}
    for arm in Q1_P3_1_ARMS:
        fn, state = get_defense_fn(arm)
        if state is not None and hasattr(state, "reset"):
            state.reset()
        n_ok = 0
        actions: set[str] = set()
        for record in records:
            prompt = record.get("prompt", "")
            context = record.get("context") or None
            tool_call = record.get("tool_call")
            try:
                out = fn(prompt, context, tool_call=tool_call)
            except TypeError:
                try:
                    out = fn(prompt, context, is_attack=record.get("label") == "attack")
                except TypeError:
                    out = fn(prompt, context)
            if isinstance(out, tuple) and len(out) >= 1:
                actions.add(str(out[0]))
            n_ok += 1
        stats["arms"][arm] = {
            "n_records": n_ok,
            "sample_actions": sorted(actions)[:8],
            "factory": "get_defense_fn",
        }
    stats["status"] = "DEFENSE_SMOKE_OK"
    return stats


def score_p3_1(output_dir: Path, pack_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """McNemar-style cells: B0 vs STATIC-A3 (same as Phase-1 scoring pattern)."""
    b0 = load_predictions(output_dir / "B0" / "B0_predictions.jsonl")
    treat = load_predictions(
        output_dir / Q1_P3_1_TREATMENT / f"{Q1_P3_1_TREATMENT}_predictions.jsonl"
    )
    scorable_attack, scorable_benign, excluded = p1.pair_attack_ids(pack_rows, b0, treat)
    cells = p1.intervention_cells(scorable_attack, b0, treat)
    b0_metrics = p1.arm_metrics(pack_rows, b0)
    treat_metrics = p1.arm_metrics(pack_rows, treat)
    treat_u = p1.arm_metrics(pack_rows, treat, ids=scorable_benign)
    if treat_u.get("n_benign"):
        treat_metrics["utility"] = treat_u["utility"]
    utility = treat_metrics.get("utility")
    classification = p1.classify_result(
        complete=len(scorable_attack) >= p1.N_ATTACK,
        n_paired=len(scorable_attack),
        cells=cells,
        utility=float(utility) if utility is not None else None,
    )
    return {
        "arm_id": ARM_ID,
        "treatment": Q1_P3_1_TREATMENT,
        "classification": classification,
        "intervention_mediated": cells,
        "b0_metrics": b0_metrics,
        "treatment_metrics": treat_metrics,
        "excluded": excluded,
        "n_scorable_attack": len(scorable_attack),
        "n_scorable_benign": len(scorable_benign),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q1-P3-1 STATIC-A3 supplemental runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--defense-smoke", action="store_true")
    parser.add_argument("--require-key", action="store_true")
    parser.add_argument(
        "--output",
        default="",
        help="Run dir under experiments/real_llm_eval/Q1_P3_1/ (live only; NOT AUTHORIZED until signed)",
    )
    args = parser.parse_args()

    live_requested = bool(args.output) and not args.defense_smoke and not args.preflight_only
    if live_requested and not args.require_key:
        print("LIVE BLOCKED: pass --require-key only after Matin authorization", file=sys.stderr)
        return 2

    try:
        info = p1.preflight(require_key=live_requested)
    except p1.GateError as exc:
        print(f"STATUS={exc.status}", flush=True)
        print(exc.message, file=sys.stderr)
        return 2

    live_lock = json.loads(p1.LIVE_LOCK.read_text(encoding="utf-8"))
    refs = live_lock.get("reference_arms") or []
    if Q1_P3_1_TREATMENT not in refs:
        print(
            f"WARNING: {Q1_P3_1_TREATMENT} not in phase1_confirm_live_lock reference_arms",
            file=sys.stderr,
        )

    records = p1.load_confirm_pack()
    payload = {
        **info,
        "q1_p3_1_arms": list(Q1_P3_1_ARMS),
        "treatment_name": Q1_P3_1_TREATMENT,
        "authorized_to_run_live": False,
    }
    print(json.dumps(payload, indent=2))
    print("STATUS=PREFLIGHT_OK", flush=True)

    if args.preflight_only:
        return 0

    if args.defense_smoke:
        smoke = defense_smoke(records)
        print(json.dumps(smoke, indent=2))
        print("STATUS=DEFENSE_SMOKE_OK", flush=True)
        return 0

    if not args.output:
        print("No action: use --defense-smoke or --preflight-only (live requires --output)", file=sys.stderr)
        return 0

    commit = git_commit() or "unknown"
    run_dir = Path(args.output)
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir
    run_dir.mkdir(parents=True, exist_ok=True)
    p1.write_json(run_dir / "preflight.json", payload)
    p1.write_json(
        run_dir / "q1_p3_1_manifest.json",
        {
            "arm_id": ARM_ID,
            "design_lock": "docs/experiments/DECISION_LOCK_Q1_P3_1_BASELINE.md",
            "pack_id": "phase1_confirm_v1.0",
            "benchmark_sha": p1.CONFIRM_SHA,
            "arms": list(Q1_P3_1_ARMS),
            "treatment": Q1_P3_1_TREATMENT,
            "target_model": p1.LOCKED_TARGET,
            "judge_model": p1.LOCKED_JUDGE,
            "git_commit": commit,
        },
    )

    config = PipelineConfig(
        experiment_id=run_dir.name,
        output_dir=run_dir,
        target_config_key=p1.LOCKED_TARGET_KEY,
        judge_config_key=p1.LOCKED_JUDGE_KEY,
        backend=EvaluationBackend.OPENROUTER,
        baselines=list(Q1_P3_1_ARMS),
        split="confirmation",
        seed=42,
        benchmark_dir=str(p1.CONFIRM_PATH.parent),
    )
    target, judge = build_models(config, EvaluationBackend.OPENROUTER, cache_enabled=False)
    run_context = BaselineRunContext(
        experiment_id=run_dir.name,
        model_id=p1.LOCKED_TARGET,
        model_config_key=p1.LOCKED_TARGET_KEY,
        git_commit=commit,
        seed=42,
        dataset_hash=p1.CONFIRM_SHA,
        cache_enabled=False,
        config_version="q1-p3-1",
    )
    t0 = time.perf_counter()
    for arm in Q1_P3_1_ARMS:
        print(f"[Q1-P3-1] Running {arm} n={len(records)}", flush=True)
        p1.run_arm(
            baseline_key=arm,
            records=records,
            target=target,
            judge=judge,
            output_dir=run_dir,
            run_context=run_context,
            allowed_arms=Q1_P3_1_ARMS,
        )
    metrics = score_p3_1(run_dir, records)
    p1.write_json(run_dir / "metrics.json", metrics)
    print(f"CLASSIFICATION={metrics['classification']}", flush=True)
    print(f"elapsed_seconds={time.perf_counter() - t0:.2f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
