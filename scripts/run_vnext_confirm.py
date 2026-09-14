#!/usr/bin/env python3
"""Official VNEXT confirmation live runner (B0 then VNEXT-ADAPT).

Hash gate and OPENROUTER_API_KEY check run BEFORE any target/judge call.
Episode order is the frozen pack file order (mix seed 61). Pipeline seed 42
is for bootstrap CI only — the pack is not reshuffled.

Usage:
  python3 scripts/run_vnext_confirm.py --require-key
  python3 scripts/run_vnext_confirm.py --preflight-only
  python3 scripts/run_vnext_confirm.py --score-only --output experiments/real_llm_eval/VNEXT_CONFIRM/<ts>
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

from src.adapti_guard.experiments.env_loader import load_project_env

load_project_env()

from src.adapti_guard.evaluation.attack_success import evaluate_episode
from src.adapti_guard.evaluation.experiment_logging import git_commit
from src.adapti_guard.evaluation.prediction_provenance import (
    PROVENANCE_SCHEMA_VERSION,
    build_prediction_row,
)
from src.adapti_guard.experiments.defense_baselines import get_defense_fn
from src.adapti_guard.experiments.real_llm_pipeline import (
    BaselineRunContext,
    EvaluationBackend,
    PipelineConfig,
    build_models,
)
from src.adapti_guard.experiments.vnext_confirm import (
    ADDENDUM_VERSION,
    B0_BASELINE_KEY,
    LOCKED_JUDGE_KEY,
    LOCKED_JUDGE_MODEL,
    LOCKED_PACK_PATH,
    LOCKED_PACK_SHA256,
    LOCKED_SEED,
    LOCKED_TARGET_KEY,
    LOCKED_TARGET_MODEL,
    MSID_ID,
    PACK_ID,
    PROTOCOL_VERSION,
    TREATMENT_BASELINE_KEY,
    TREATMENT_FACTORY,
    VNextGateError,
    load_locked_pack,
    load_predictions,
    require_openrouter_key,
    score_run,
    utc_stamp,
    verify_pack_hash,
)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def preflight(*, require_key: bool) -> dict[str, Any]:
    hash_info = verify_pack_hash()
    if require_key:
        key_info = require_openrouter_key()
    else:
        import os

        present = bool(os.environ.get("OPENROUTER_API_KEY", "").strip())
        key_info = {
            "status": "KEY_OK" if present else "KEY_NOT_CHECKED",
            "openrouter_api_key": "SET" if present else "MISSING",
        }
    records = load_locked_pack()
    from src.adapti_guard.evaluation.target_model import load_model_config

    cfg = load_model_config(ROOT / "configs" / "models.yaml")
    cache_enabled = bool((cfg.get("cache") or {}).get("enabled", True))
    target_model = ((cfg.get("models") or {}).get(LOCKED_TARGET_KEY) or {}).get("model")
    judge_model = ((cfg.get("models") or {}).get(LOCKED_JUDGE_KEY) or {}).get("model")
    if cache_enabled:
        raise VNextGateError("INVALID_CACHE_ENABLED", "cache.enabled must be false")
    if target_model != LOCKED_TARGET_MODEL or judge_model != LOCKED_JUDGE_MODEL:
        raise VNextGateError(
            "INVALID_MODEL_LOCK",
            f"yaml target={target_model} judge={judge_model}; "
            f"locked {LOCKED_TARGET_MODEL} / {LOCKED_JUDGE_MODEL}",
        )
    if target_model == judge_model:
        raise VNextGateError("INVALID_MODEL_LOCK", "target model must differ from judge")
    return {
        "status": "PREFLIGHT_OK",
        "hash": hash_info,
        "key": {k: v for k, v in key_info.items() if k != "key_length"},
        "n_records": len(records),
        "n_attack": sum(1 for r in records if r.get("label") == "attack"),
        "n_benign": sum(1 for r in records if r.get("label") == "benign"),
        "ids": [r["id"] for r in records],
        "cache_enabled": cache_enabled,
        "target_model": target_model,
        "judge_model": judge_model,
        "protocol_version": PROTOCOL_VERSION,
        "addendum_version": ADDENDUM_VERSION,
        "msid_id": MSID_ID,
        "pack_id": PACK_ID,
        "git_commit": git_commit(),
        "seed": LOCKED_SEED,
        "pack_order": "frozen_file_order_mix_seed_61",
        "prior_partial_b0": "NON-OFFICIAL_DISCARDED",
    }


def _prediction_ok(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    reason = str(row.get("judge_reason") or "")
    if reason in {
        "target_api_error",
        "judge_api_error",
        "judge_parse_error",
        "no_judge_configured",
    }:
        return False
    if row.get("api_status") in {"target_error", "judge_error"}:
        return False
    return True


def _enrich_row(ep, pred_row: dict[str, Any]) -> dict[str, Any]:
    pred_row = dict(pred_row)
    pred_row["scientific_arm"] = pred_row.get("baseline")
    pred_row["taxonomy_class"] = ep.taxonomy_class
    pred_row["defense_action"] = ep.defense_action
    pred_row["action"] = ep.defense_action
    pred_row["judge_usage"] = (ep.metadata or {}).get("judge_usage")
    pred_row["tool_turn"] = (ep.metadata or {}).get("tool_turn")
    return pred_row


def run_arm(
    *,
    baseline_key: str,
    records: list[dict[str, Any]],
    target,
    judge,
    output_dir: Path,
    run_context: BaselineRunContext,
) -> dict[str, Any]:
    arm_dir = output_dir / baseline_key
    arm_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = arm_dir / f"{baseline_key}_predictions.jsonl"
    existing = load_predictions(predictions_path)
    defense_fn, state = get_defense_fn(baseline_key)
    if state is not None:
        state.reset()

    n_ok = sum(1 for r in records if _prediction_ok(existing.get(str(r["id"]))))
    n_retry = len(records) - n_ok
    print(
        f"[{baseline_key}] keep_ok={n_ok} retry_or_missing={n_retry}",
        flush=True,
    )

    # Sequential hole-fill: replay controller on scorable rows (no API) so
    # adaptive state stays in frozen pack order; retry only API failures.
    ordered_rows: list[dict[str, Any]] = []
    n_api_calls = 0
    for record in records:
        eid = str(record["id"])
        prev = existing.get(eid)
        if _prediction_ok(prev):
            defense_fn(record.get("prompt", ""), record.get("context") or None)
            ordered_rows.append(prev)
            continue
        t0 = time.perf_counter()
        ep = evaluate_episode(
            record,
            defense_fn=defense_fn,
            target_model=target,
            judge=judge,
        )
        ep.metadata["baseline"] = baseline_key
        ep.metadata["evaluation_mode"] = "real_llm_judge"
        ep.metadata["scientific_arm"] = baseline_key
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
        pred_row = _enrich_row(ep, pred_row)
        ordered_rows.append(pred_row)
        n_api_calls += 1
        elapsed = time.perf_counter() - t0
        print(
            f"  [{baseline_key}] {eid} blocked={ep.blocked} action={ep.defense_action} "
            f"tax={ep.taxonomy_class} asr={ep.attack_succeeded} "
            f"api={pred_row.get('api_status')} {elapsed:.1f}s",
            flush=True,
        )
        predictions_path.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ordered_rows),
            encoding="utf-8",
        )
        _write_json(
            output_dir / "progress.json",
            {
                "arm": baseline_key,
                "last_id": eid,
                "completed": len(ordered_rows),
                "total": len(records),
                "elapsed_s": round(elapsed, 3),
            },
        )

    predictions_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ordered_rows),
        encoding="utf-8",
    )
    preds = load_predictions(predictions_path)
    n = len(preds)
    n_ok_final = sum(1 for r in records if _prediction_ok(preds.get(str(r["id"]))))
    metrics = {
        "baseline": baseline_key,
        "scientific_arm": baseline_key,
        "n_samples": n,
        "n_api_calls_this_pass": n_api_calls,
        "n_scorable": n_ok_final,
        "evaluation_mode": "real_llm_judge",
        "dataset_hash": run_context.dataset_hash,
        "cache_enabled": run_context.cache_enabled,
        "seed": run_context.seed,
        "git_commit": run_context.git_commit,
        "status": "COMPLETED" if n_ok_final >= len(records) else "PARTIAL",
    }
    _write_json(arm_dir / f"{baseline_key}_metrics.json", metrics)
    return metrics


def write_official_audit(output_dir: Path) -> dict[str, Any]:
    scored = score_run(output_dir)
    (output_dir / "AUDIT.md").write_text(scored["audit_markdown"], encoding="utf-8")
    _write_json(output_dir / "comparison.json", scored["comparison"])
    _write_json(
        output_dir / "verdict.json",
        {
            **scored["verdict"],
            "spend": scored["spend"],
            "hash": scored["hash_info"],
        },
    )
    print(scored["audit_markdown"], flush=True)
    print(
        f"STATUS={scored['verdict']['status']} "
        f"qualified_win={scored['verdict']['qualified_win']} "
        f"spend_usd={scored['spend'].get('estimated_usd_total')}",
        flush=True,
    )
    return scored


def main() -> int:
    parser = argparse.ArgumentParser(description="VNEXT official confirmation runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--score-only", action="store_true")
    parser.add_argument("--require-key", action="store_true")
    parser.add_argument(
        "--output",
        default="",
        help="Existing or new run dir under experiments/real_llm_eval/VNEXT_CONFIRM/",
    )
    args = parser.parse_args()

    try:
        live = (not args.score_only) and (not args.preflight_only)
        info = preflight(require_key=live or args.require_key)
    except VNextGateError as exc:
        print(f"STATUS={exc.status}", flush=True)
        print(exc.message, file=sys.stderr, flush=True)
        payload = {"status": exc.status, "reason": exc.message}
        if args.output:
            _write_json(Path(args.output) / "INVALID.json", payload)
        return 2 if exc.status == "INVALID_MISSING_KEYS" else 3

    if args.preflight_only:
        print(json.dumps(info, indent=2))
        print("STATUS=PREFLIGHT_OK", flush=True)
        return 0

    if args.output:
        output_dir = Path(args.output)
        if not output_dir.is_absolute():
            output_dir = ROOT / output_dir
    else:
        output_dir = ROOT / "experiments" / "real_llm_eval" / "VNEXT_CONFIRM" / utc_stamp()
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "preflight.json", info)

    if args.score_only:
        write_official_audit(output_dir)
        return 0

    records = load_locked_pack()
    config = PipelineConfig(
        experiment_id="VNEXT-CONFIRM",
        output_dir=output_dir,
        target_config_key=LOCKED_TARGET_KEY,
        judge_config_key=LOCKED_JUDGE_KEY,
        backend=EvaluationBackend.OPENROUTER,
        baselines=[B0_BASELINE_KEY, TREATMENT_BASELINE_KEY],
        split="confirmation",
        seed=LOCKED_SEED,
        benchmark_dir=str(LOCKED_PACK_PATH.parent),
    )
    target, judge = build_models(
        config, EvaluationBackend.OPENROUTER, cache_enabled=False
    )
    run_context = BaselineRunContext(
        experiment_id="VNEXT-CONFIRM",
        model_id=LOCKED_TARGET_MODEL,
        model_config_key=LOCKED_TARGET_KEY,
        git_commit=git_commit() or "UNKNOWN",
        seed=LOCKED_SEED,
        dataset_hash=LOCKED_PACK_SHA256,
        cache_enabled=False,
        config_version=PROVENANCE_SCHEMA_VERSION,
    )
    _write_json(
        output_dir / "manifest.json",
        {
            "experiment_id": "VNEXT-CONFIRM",
            "protocol_version": PROTOCOL_VERSION,
            "addendum_version": ADDENDUM_VERSION,
            "msid_id": MSID_ID,
            "pack_id": PACK_ID,
            "confirmation_sha256": LOCKED_PACK_SHA256,
            "pack_path": str(LOCKED_PACK_PATH),
            "git_commit": run_context.git_commit,
            "target_config_key": LOCKED_TARGET_KEY,
            "target_model": LOCKED_TARGET_MODEL,
            "judge_config_key": LOCKED_JUDGE_KEY,
            "judge_model": LOCKED_JUDGE_MODEL,
            "temperature": 0.0,
            "seed": LOCKED_SEED,
            "cache_enabled": False,
            "baselines": [B0_BASELINE_KEY, TREATMENT_BASELINE_KEY],
            "treatment_factory": TREATMENT_FACTORY,
            "n_attack": 61,
            "n_benign": 61,
            "n_samples": 122,
            "evaluation_mode": "real_llm_judge",
            "prior_partial_b0": "NON-OFFICIAL_DISCARDED",
            "approval": "LIVE APPROVED by Matin (ادامه بده after PRELIVE_PASS)",
        },
    )
    t_start = time.perf_counter()
    for arm in (B0_BASELINE_KEY, TREATMENT_BASELINE_KEY):
        print(f"Running {arm} n={len(records)} cache=off", flush=True)
        run_arm(
            baseline_key=arm,
            records=records,
            target=target,
            judge=judge,
            output_dir=output_dir,
            run_context=run_context,
        )
    elapsed = round(time.perf_counter() - t_start, 2)
    _write_json(output_dir / "elapsed.json", {"elapsed_seconds": elapsed})
    scored = write_official_audit(output_dir)
    status = scored["verdict"]["status"]
    return 0 if status in {"PASS", "FAIL", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
