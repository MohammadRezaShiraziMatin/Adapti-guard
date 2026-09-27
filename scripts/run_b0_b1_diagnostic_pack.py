#!/usr/bin/env python3
"""Pilot/diagnostic B0 vs B1 on fixed Layer A v2 pack (NOT paper Results)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel, BudgetLedger, estimate_request_cost_usd
from adapti_guard.evaluation.live_model_resolver import model_id_for_config_key
from adapti_guard.evaluation.target_model import GenerationRequest
from adapti_guard.experiments.env_loader import load_project_env
from adapti_guard.evaluation.experiment_logging import git_commit
from adapti_guard.evaluation.llm_judge import LLMJudge
from adapti_guard.evaluation.target_model import build_target_model
from adapti_guard.experiments.real_llm_pipeline import (
    BaselineRunContext,
    EvaluationBackend,
    PipelineConfig,
    load_records,
    resolve_backend,
    run_baseline_evaluation,
)

DIAG_LABEL = "pilot/diagnostic — NOT paper Results / NOT AUDIT=VALID"
PACK = "datasets/frozen/layer_a_v2"
TARGET_KEY = "target_2"
JUDGE_KEY = "judge_fallback"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def preflight_worst_case_usd(n_episodes: int, max_usd: float) -> tuple[bool, float, int]:
    req = GenerationRequest(prompt="x" * 2000, system_prompt="y" * 200, max_tokens=512)
    per = estimate_request_cost_usd(req, provider="openrouter")
    if per is None:
        return False, 0.0, 0
    worst_req = n_episodes * 2
    worst_usd = per * worst_req
    return worst_usd <= max_usd, float(worst_usd), worst_req


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_diagnostic(
    *,
    output_dir: Path,
    run_id: str,
    attack_n: int,
    benign_n: int,
    seed: int,
    max_usd: float,
    target_config_key: str = TARGET_KEY,
    target_provider: str = "openrouter",
    ledger: BudgetLedger | None = None,
    skip_preflight: bool = False,
) -> dict:
    load_project_env()
    if not __import__("os").environ.get("OPENROUTER_API_KEY"):
        return {"status": "STOPPED", "reason": "OPENROUTER_API_KEY missing"}

    n_per_arm = attack_n + benign_n
    n_total = n_per_arm * 2
    ok, worst_usd, worst_req = (True, 0.0, n_total * 2) if skip_preflight else preflight_worst_case_usd(n_total, max_usd)
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log_md = run_dir / "RUN_LOG.md"
    jsonl = run_dir / "episodes.jsonl"
    log_md.write_text(
        f"# {run_id}\n\n"
        f"- label: {DIAG_LABEL}\n"
        f"- created: {_utc()}\n"
        f"- pack: {PACK} attack_n={attack_n} benign_n={benign_n} seed={seed}\n"
        f"- target_config: {target_config_key} judge_config: {JUDGE_KEY} backend: auto\n"
        f"- preflight worst_case_requests: {worst_req} worst_case_usd_est: {worst_usd:.6f} cap: {max_usd}\n"
        f"- preflight: {'PASS' if ok else 'FAIL'}\n"
        f"- order: B0 all episodes then B1 all episodes\n\n",
        encoding="utf-8",
    )
    if not ok:
        return {"status": "STOPPED", "reason": "preflight_exceeds_cap", "worst_usd": worst_usd, "run_dir": str(run_dir)}

    if ledger is None:
        ledger = BudgetLedger(max_usd=max_usd, max_requests=worst_req + 20, hard_stop=True)
    backend, block = resolve_backend(EvaluationBackend.AUTO)
    if block:
        return {"status": "STOPPED", "reason": block, "run_dir": str(run_dir)}

    config = PipelineConfig(
        experiment_id=run_id,
        output_dir=run_dir,
        target_config_key=target_config_key,
        judge_config_key=JUDGE_KEY,
        backend=backend,
        baselines=["B0", "B1"],
        split="test",
        attack_n=attack_n,
        benign_n=benign_n,
        seed=seed,
        benchmark_dir=PACK,
    )
    records, meta = load_records(config)
    target_id = model_id_for_config_key(target_config_key, Path(config.models_config))
    judge_id = model_id_for_config_key(JUDGE_KEY, Path(config.models_config))

    target = build_target_model(target_config_key, config_path=config.models_config, cache_enabled=False)
    target.max_retries = 0
    judge_inner = build_target_model(JUDGE_KEY, config_path=config.models_config, cache_enabled=False)
    judge_inner.max_retries = 0
    judge = LLMJudge(
        model=judge_inner,
        config_key=JUDGE_KEY,
        fallback_config_key=JUDGE_KEY,
        config_path=config.models_config,
        cache_enabled=False,
        use_fallback=False,
    )
    gated_t = BudgetGatedTargetModel(target, ledger, provider=target_provider)
    inner_j = getattr(judge, "_primary", None) or getattr(judge, "model", None)
    if inner_j is not None:
        inner_j.max_retries = 0
        gated_j = BudgetGatedTargetModel(inner_j, ledger, provider="openrouter")
        judge._primary = gated_j
        judge._fallback = gated_j

    ctx = BaselineRunContext(
        experiment_id=run_id,
        model_id=target_id,
        model_config_key=target_config_key,
        git_commit=git_commit(),
        seed=seed,
        dataset_hash=str(meta.get("dataset_hash", "")),
        cache_enabled=False,
    )

    arm_results = {}
    for arm in ("B0", "B1"):
        arm_dir = run_dir / arm
        res = run_baseline_evaluation(
            arm,
            records,
            target=gated_t,
            judge=judge,
            output_dir=arm_dir,
            run_context=ctx,
        )
        pred_path = arm_dir / f"{arm}_predictions.jsonl"
        if pred_path.is_file():
            for line in pred_path.read_text().splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                append_jsonl(
                    jsonl,
                    {
                        "timestamp": _utc(),
                        "arm": arm,
                        "episode_id": row.get("id"),
                        "seed": seed,
                        "target_id": target_id,
                        "judge_id": judge_id,
                        "request_counts": {"ledger_requests_used": ledger.requests_used},
                        "ledger_spent_usd": ledger.spent_usd,
                        "blocked": row.get("blocked"),
                        "attack_success": row.get("attack_succeeded"),
                        "utility": row.get("utility_success"),
                        "errors": None,
                        "label": DIAG_LABEL,
                    },
                )
        arm_results[arm] = res.metrics
        ok_spend, spend_reason = ledger.check_spend_allowed(0.0)
        if not ok_spend:
            return {
                "status": "STOPPED",
                "reason": spend_reason,
                "ledger": ledger.to_dict(),
                "run_dir": str(run_dir),
            }

    comparison = {
        "label": DIAG_LABEL,
        "b0": arm_results.get("B0"),
        "b1": arm_results.get("B1"),
        "ledger": ledger.to_dict(),
        "target_id": target_id,
        "judge_id": judge_id,
    }
    (run_dir / "b0_b1_comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")
    with log_md.open("a", encoding="utf-8") as f:
        f.write(f"\n## completed {_utc()}\n")
        f.write(f"- ledger: {json.dumps(ledger.to_dict())}\n")
        f.write(f"- comparison: b0_b1_comparison.json\n")
    return {"status": "COMPLETED", "run_dir": str(run_dir), "ledger": ledger.to_dict(), "comparison": comparison}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", default="DIAG-B0-B1-LAYER-A-V2-20260924")
    p.add_argument("--output", default="experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_B0_B1")
    p.add_argument("--attack-n", type=int, default=20)
    p.add_argument("--benign-n", type=int, default=20)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-usd", type=float, default=2.0)
    args = p.parse_args()
    out = run_diagnostic(
        output_dir=Path(args.output),
        run_id=args.run_id,
        attack_n=args.attack_n,
        benign_n=args.benign_n,
        seed=args.seed,
        max_usd=args.max_usd,
    )
    print(json.dumps(out, indent=2))
    return 0 if out.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
