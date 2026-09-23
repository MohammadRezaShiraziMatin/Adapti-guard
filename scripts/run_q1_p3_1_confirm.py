#!/usr/bin/env python3
"""Q1-P3-1 supplemental confirmatory runner (STATIC-A3 vs B0 on a locked confirmatory pack).

NOT AUTHORIZED TO RUN live until Matin signs DECISION_LOCK_Q1_P3_1_BASELINE.md + budget.

Offline modes (default safe):
  --preflight-only   hash/lock checks, no API
  --defense-smoke    exercise defense fns on full pack, no Target/Judge calls

Pack (design default phase1; Matin may choose vnext before live):
  --pack phase1_confirm_v1   Track B corpus (default)
  --pack vnext_confirm_v1    Track A corpus (VNEXT hash gate; supplemental P3-1 only)

When authorized (human only):
  --require-key --output experiments/real_llm_eval/Q1_P3_1/<run_id>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

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
from adapti_guard.experiments.vnext_confirm import (
    LOCKED_JUDGE_KEY as VN_JUDGE_KEY,
    LOCKED_JUDGE_MODEL as VN_JUDGE,
    LOCKED_PACK_PATH as VN_PACK_PATH,
    LOCKED_PACK_SHA256 as VN_PACK_SHA,
    LOCKED_SEED as VN_SEED,
    LOCKED_TARGET_KEY as VN_TARGET_KEY,
    LOCKED_TARGET_MODEL as VN_TARGET,
    PACK_ID as VN_PACK_ID,
    VNextGateError,
    arm_metrics as vn_arm_metrics,
    intervention_cells as vn_intervention_cells,
    load_locked_pack,
    load_predictions,
    pair_attack_ids as vn_pair_attack_ids,
    verify_pack_hash,
)

import run_phase1_confirm as p1

Q1_P3_1_ARMS: tuple[str, ...] = ("B0", "STATIC-A3")
Q1_P3_1_TREATMENT = "STATIC-A3"
Q1_P3_1_ARTIFACT_ROOT = ROOT / "experiments" / "real_llm_eval" / "Q1_P3_1"
ARM_ID = "Q1-P3-1"

PACK_PHASE1 = "phase1_confirm_v1"
PACK_VNEXT = "vnext_confirm_v1"


@dataclass(frozen=True)
class PackProfile:
    pack_key: str
    pack_id: str
    pack_path: Path
    pack_sha: str
    benchmark_dir: Path
    split: str
    seed: int
    target_key: str
    target_model: str
    judge_key: str
    judge_model: str
    n_attack: int
    preflight: Callable[..., dict[str, Any]]
    load_records: Callable[[], list[dict[str, Any]]]
    score: Callable[[Path, list[dict[str, Any]]], dict[str, Any]]


def _preflight_vnext(*, require_key: bool) -> dict[str, Any]:
    hash_info = verify_pack_hash()
    if require_key:
        import os

        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not key:
            raise VNextGateError(
                "INVALID_MISSING_KEYS",
                "OPENROUTER_API_KEY missing — live eval must not start.",
            )
        key_info = {"status": "KEY_OK", "openrouter_api_key": "SET"}
    else:
        import os

        present = bool(os.environ.get("OPENROUTER_API_KEY", "").strip())
        key_info = {
            "status": "KEY_OK" if present else "KEY_NOT_CHECKED",
            "openrouter_api_key": "SET" if present else "MISSING",
        }
    from adapti_guard.evaluation.target_model import load_model_config

    cfg = load_model_config(ROOT / "configs" / "models.yaml")
    cache_enabled = bool((cfg.get("cache") or {}).get("enabled", True))
    if cache_enabled:
        raise VNextGateError("INVALID_CACHE_ENABLED", "cache.enabled must be false")
    yaml_target = ((cfg.get("models") or {}).get(VN_TARGET_KEY) or {}).get("model")
    yaml_judge = ((cfg.get("models") or {}).get(VN_JUDGE_KEY) or {}).get("model")
    if yaml_target != VN_TARGET or yaml_judge != VN_JUDGE:
        raise VNextGateError(
            "INVALID_MODEL_LOCK",
            f"yaml target={yaml_target} judge={yaml_judge}; locked {VN_TARGET}/{VN_JUDGE}",
        )
    rows = load_locked_pack()
    return {
        "status": "PREFLIGHT_OK",
        "pack_key": PACK_VNEXT,
        "pack_id": VN_PACK_ID,
        "benchmark_sha": hash_info["sha256"],
        "n_attack": sum(1 for r in rows if r.get("label") == "attack"),
        "n_benign": sum(1 for r in rows if r.get("label") == "benign"),
        "n_total": len(rows),
        "target_model": VN_TARGET,
        "judge_model": VN_JUDGE,
        "target_ne_judge": VN_TARGET != VN_JUDGE,
        "cache_enabled": False,
        "key": key_info,
        "git_commit": git_commit(),
        "vnext_pack_gate": hash_info,
    }


def _score_phase1(output_dir: Path, pack_rows: list[dict[str, Any]]) -> dict[str, Any]:
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
        "scoring_protocol": "phase1_confirm",
    }


def _score_vnext(output_dir: Path, pack_rows: list[dict[str, Any]]) -> dict[str, Any]:
    b0 = load_predictions(output_dir / "B0" / "B0_predictions.jsonl")
    treat = load_predictions(
        output_dir / Q1_P3_1_TREATMENT / f"{Q1_P3_1_TREATMENT}_predictions.jsonl"
    )
    scorable_attack, scorable_benign, excluded = vn_pair_attack_ids(pack_rows, b0, treat)
    cells = vn_intervention_cells(scorable_attack, b0, treat)
    b0_metrics = vn_arm_metrics(pack_rows, b0)
    treat_metrics = vn_arm_metrics(pack_rows, treat)
    treat_u = vn_arm_metrics(pack_rows, treat, ids=scorable_benign)
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
        "scoring_protocol": "vnext_confirm",
    }


def _profile_for(pack_key: str) -> PackProfile:
    if pack_key == PACK_PHASE1:
        return PackProfile(
            pack_key=PACK_PHASE1,
            pack_id="phase1_confirm_v1.0",
            pack_path=p1.CONFIRM_PATH,
            pack_sha=p1.CONFIRM_SHA,
            benchmark_dir=p1.CONFIRM_PATH.parent,
            split="confirmation",
            seed=42,
            target_key=p1.LOCKED_TARGET_KEY,
            target_model=p1.LOCKED_TARGET,
            judge_key=p1.LOCKED_JUDGE_KEY,
            judge_model=p1.LOCKED_JUDGE,
            n_attack=p1.N_ATTACK,
            preflight=p1.preflight,
            load_records=p1.load_confirm_pack,
            score=_score_phase1,
        )
    if pack_key == PACK_VNEXT:
        return PackProfile(
            pack_key=PACK_VNEXT,
            pack_id=VN_PACK_ID,
            pack_path=ROOT / VN_PACK_PATH,
            pack_sha=VN_PACK_SHA,
            benchmark_dir=(ROOT / VN_PACK_PATH).parent,
            split="confirmation",
            seed=VN_SEED,
            target_key=VN_TARGET_KEY,
            target_model=VN_TARGET,
            judge_key=VN_JUDGE_KEY,
            judge_model=VN_JUDGE,
            n_attack=p1.N_ATTACK,
            preflight=_preflight_vnext,
            load_records=load_locked_pack,
            score=_score_vnext,
        )
    raise SystemExit(f"Unknown pack: {pack_key}")


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Q1-P3-1 STATIC-A3 supplemental runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--defense-smoke", action="store_true")
    parser.add_argument("--require-key", action="store_true")
    parser.add_argument(
        "--pack",
        choices=(PACK_PHASE1, PACK_VNEXT),
        default=PACK_PHASE1,
        help="Frozen confirmatory pack (default phase1_confirm_v1 / Track B)",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Run dir under experiments/real_llm_eval/Q1_P3_1/ (live only; NOT AUTHORIZED until signed)",
    )
    args = parser.parse_args()

    profile = _profile_for(args.pack)

    live_requested = bool(args.output) and not args.defense_smoke and not args.preflight_only
    if live_requested and not args.require_key:
        print("LIVE BLOCKED: pass --require-key only after Matin authorization", file=sys.stderr)
        return 2

    try:
        info = profile.preflight(require_key=live_requested)
    except (p1.GateError, VNextGateError) as exc:
        status = getattr(exc, "status", "GATE_ERROR")
        print(f"STATUS={status}", flush=True)
        print(exc.message, file=sys.stderr)
        return 2

    if profile.pack_key == PACK_PHASE1:
        live_lock = json.loads(p1.LIVE_LOCK.read_text(encoding="utf-8"))
        refs = live_lock.get("reference_arms") or []
        if Q1_P3_1_TREATMENT not in refs:
            print(
                f"WARNING: {Q1_P3_1_TREATMENT} not in phase1_confirm_live_lock reference_arms",
                file=sys.stderr,
            )

    records = profile.load_records()
    payload = {
        **info,
        "q1_p3_1_arms": list(Q1_P3_1_ARMS),
        "treatment_name": Q1_P3_1_TREATMENT,
        "pack_key": profile.pack_key,
        "pack_id": profile.pack_id,
        "authorized_to_run_live": False,
    }
    print(json.dumps(payload, indent=2))
    print("STATUS=PREFLIGHT_OK", flush=True)

    if args.preflight_only:
        return 0

    if args.defense_smoke:
        smoke = defense_smoke(records)
        smoke["pack_key"] = profile.pack_key
        smoke["n_records"] = len(records)
        print(json.dumps(smoke, indent=2))
        print("STATUS=DEFENSE_SMOKE_OK", flush=True)
        return 0

    if not args.output:
        print(
            "No action: use --defense-smoke or --preflight-only (live requires --output)",
            file=sys.stderr,
        )
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
            "pack_key": profile.pack_key,
            "pack_id": profile.pack_id,
            "pack_path": str(profile.pack_path),
            "benchmark_sha": profile.pack_sha,
            "arms": list(Q1_P3_1_ARMS),
            "treatment": Q1_P3_1_TREATMENT,
            "target_model": profile.target_model,
            "judge_model": profile.judge_model,
            "git_commit": commit,
        },
    )

    config = PipelineConfig(
        experiment_id=run_dir.name,
        output_dir=run_dir,
        target_config_key=profile.target_key,
        judge_config_key=profile.judge_key,
        backend=EvaluationBackend.OPENROUTER,
        baselines=list(Q1_P3_1_ARMS),
        split=profile.split,
        seed=profile.seed,
        benchmark_dir=str(profile.benchmark_dir),
    )
    target, judge = build_models(config, EvaluationBackend.OPENROUTER, cache_enabled=False)
    run_context = BaselineRunContext(
        experiment_id=run_dir.name,
        model_id=profile.target_model,
        model_config_key=profile.target_key,
        git_commit=commit,
        seed=profile.seed,
        dataset_hash=profile.pack_sha,
        cache_enabled=False,
        config_version="q1-p3-1",
    )
    t0 = time.perf_counter()
    for arm in Q1_P3_1_ARMS:
        print(f"[Q1-P3-1] Running {arm} n={len(records)} pack={profile.pack_key}", flush=True)
        p1.run_arm(
            baseline_key=arm,
            records=records,
            target=target,
            judge=judge,
            output_dir=run_dir,
            run_context=run_context,
            allowed_arms=Q1_P3_1_ARMS,
        )
    metrics = profile.score(run_dir, records)
    metrics["pack_key"] = profile.pack_key
    p1.write_json(run_dir / "metrics.json", metrics)
    print(f"CLASSIFICATION={metrics['classification']}", flush=True)
    print(f"elapsed_seconds={time.perf_counter() - t0:.2f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
