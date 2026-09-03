"""EXP005: Real-LLM evaluation of ADAPTI-GUARD on Gemini 3.6 Flash.

Canonical conditions: B0, B1, B2_L1 (fixed defense), B3 (adaptive).
Dataset: held-out benchmark_q1 test split (mixed attack + benign).
ASR: independent LLM judge (blind to defense identity).

Judge protocol note:
  Primary OpenRouter judge (Claude Sonnet 4) is currently unavailable (HTTP 401).
  This experiment uses gemini-3.6-flash as a separate judge *call* that is
  blind to baseline/defense metadata. The judge is NOT an independent model
  family. That limitation is recorded in provenance and the final report.

Usage:
    python experiments/EXP005_GEMINI_FLASH/run.py --preflight
    python experiments/EXP005_GEMINI_FLASH/run.py --smoke
    python experiments/EXP005_GEMINI_FLASH/run.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import load_project_env, validate_gemini_key

load_project_env()

from src.adapti_guard.evaluation.attack_success import load_benchmark_records
from src.adapti_guard.evaluation.experiment_logging import git_commit, sha256_file
from src.adapti_guard.evaluation.llm_judge import LLMJudge, JudgeInput
from src.adapti_guard.evaluation.multi_model_statistics import (
    EpisodeOutcome,
    compute_baseline_statistics,
    paired_baseline_comparison,
)
from src.adapti_guard.evaluation.prediction_provenance import build_prediction_row
from src.adapti_guard.evaluation.statistics import cohens_d, holm_correction
from src.adapti_guard.evaluation.target_model import (
    GenerationRequest,
    GeminiTargetModel,
    build_target_model,
)
from src.adapti_guard.experiments.real_llm_pipeline import (
    BaselineRunContext,
    EvaluationBackend,
    PipelineConfig,
    build_models,
    run_baseline_evaluation,
)

EXPERIMENT_ID = "EXP005_GEMINI_FLASH"
DATASET_NAME = "benchmark_q1"
DATASET_VERSION = "q1.0"
TEST_HASH_EXPECTED = "fa35c657dae473e21f6b89d389e3b85b4daa445eccd4aedeb415b344ab3cf74e"
BENCHMARK_DIR = ROOT / "datasets" / "benchmark_q1"
TEST_PATH = BENCHMARK_DIR / "test.jsonl"
# Compact mixed held-out evaluation: 4 conditions × (target + judge).
N_ATTACK = 18
N_BENIGN = 6
SEED = 42
BASELINES = ["B0", "B1", "B2_L1", "B3"]
TARGET_KEY = "gemini_target"
JUDGE_KEY = "gemini_judge"
MODEL_ID = "gemini-3.6-flash"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def select_heldout_records(
    *,
    n_attack: int = N_ATTACK,
    n_benign: int = N_BENIGN,
    seed: int = SEED,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records = load_benchmark_records(split="test", benchmark_dir=BENCHMARK_DIR)
    attacks = [r for r in records if r.get("label") == "attack"]
    benign = [r for r in records if r.get("label") == "benign"]
    rng = random.Random(seed)

    by_cat: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in attacks:
        by_cat[str(rec.get("category", "unknown"))].append(rec)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda r: str(r.get("id", "")))
    cats = sorted(by_cat.keys())
    picked: list[dict[str, Any]] = []
    if cats:
        per = n_attack // len(cats)
        rem = n_attack % len(cats)
        for i, cat in enumerate(cats):
            take = per + (1 if i < rem else 0)
            pool = by_cat[cat]
            take = min(take, len(pool))
            idxs = rng.sample(range(len(pool)), take) if take < len(pool) else list(range(len(pool)))
            picked.extend(pool[j] for j in sorted(idxs))
        if len(picked) < n_attack:
            remaining = [r for r in attacks if r not in picked]
            need = min(n_attack - len(picked), len(remaining))
            extra = rng.sample(remaining, need) if need else []
            picked.extend(extra)

    benign_sorted = sorted(benign, key=lambda r: str(r.get("id", "")))
    b_take = min(n_benign, len(benign_sorted))
    b_idxs = rng.sample(range(len(benign_sorted)), b_take)
    picked_benign = [benign_sorted[j] for j in sorted(b_idxs)]

    selected = picked + picked_benign
    selected.sort(key=lambda r: str(r.get("id", "")))
    meta = {
        "dataset": DATASET_NAME,
        "dataset_version": DATASET_VERSION,
        "split": "test",
        "seed": seed,
        "n_attack_requested": n_attack,
        "n_benign_requested": n_benign,
        "n_selected": len(selected),
        "n_attack_selected": sum(1 for r in selected if r.get("label") == "attack"),
        "n_benign_selected": sum(1 for r in selected if r.get("label") == "benign"),
        "category_counts": dict(Counter(str(r.get("category")) for r in selected)),
        "sample_ids": [str(r.get("id")) for r in selected],
    }
    return selected, meta


def results_dir(run_id: str) -> Path:
    return ROOT / "results" / "real_llm" / "gemini_3_6_flash" / run_id


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def preflight() -> dict[str, Any]:
    ok, reason = validate_gemini_key()
    record: dict[str, Any] = {
        "stage": "preflight",
        "timestamp": _utc(),
        "provider": "google",
        "model": MODEL_ID,
        "api": "interactions",
        "key_valid": ok,
        "key_reason": reason,
        "status": "BLOCKED",
        "http_status": None,
        "error": None,
        "latency_ms": None,
        "request_id": None,
        "response": None,
    }
    if not ok:
        record["error"] = reason
        return record
    try:
        model = GeminiTargetModel(MODEL_ID, cache=None)
        result = model.generate(
            GenerationRequest(prompt="Reply exactly: GEMINI_OK", system_prompt="")
        )
        record["latency_ms"] = result.latency_ms
        record["request_id"] = (result.raw or {}).get("id")
        record["http_status"] = (result.raw or {}).get("http_status")
        record["response"] = (result.text or "")[:200]
        record["usage"] = result.usage
        record["error"] = result.error
        if result.error:
            record["status"] = "BLOCKED"
        elif "GEMINI_OK" in (result.text or "").replace(" ", ""):
            record["status"] = "VALID"
        elif result.text and result.text.strip():
            record["status"] = "VALID"
            record["note"] = "non-exact reply but non-empty successful generation"
        else:
            record["status"] = "BLOCKED"
            record["error"] = "empty_response"
    except Exception as exc:
        record["status"] = "BLOCKED"
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def _smoke_records(pool: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pick one attack + one benign from the protocol sample (≤4 API calls with judge).

    Prefer an injection/jailbreak attack when present so smoke covers a security case
    without exceeding the 5-request smoke budget.
    """
    preferred = (
        "direct_prompt_injection",
        "indirect_prompt_injection",
        "jailbreak",
        "rag_injection",
        "agent_tool_injection",
        "adaptive_attacks",
    )
    attacks = [r for r in pool if r.get("label") == "attack"]
    attack = None
    for cat in preferred:
        attack = next(
            (r for r in attacks if cat in str(r.get("category", "")).lower()),
            None,
        )
        if attack:
            break
    if attack is None and attacks:
        attack = attacks[0]
    benign = next((r for r in pool if r.get("label") == "benign"), None)
    out = []
    if attack:
        out.append(attack)
    if benign:
        out.append(benign)
    return out


def run_smoke(
    *,
    target,
    judge: LLMJudge,
    records: list[dict[str, Any]],
    git: str,
    dataset_hash: str,
) -> dict[str, Any]:
    """At most 4 API calls: 2 samples × (target + judge). Preflight is separate."""
    rows: list[dict[str, Any]] = []
    api_calls = 0
    failures = 0
    for rec in records[:2]:
        prompt = str(rec.get("prompt", ""))
        context = str(rec.get("context") or "")
        full = f"Context:\n{context}\n\nUser: {prompt}" if context else prompt
        gen = target.generate(
            GenerationRequest(
                prompt=full,
                system_prompt="You are a helpful assistant.",
            )
        )
        api_calls += 1
        if gen.error:
            failures += 1
        verdict = judge.judge(
            JudgeInput(
                user_prompt=prompt,
                model_response=gen.text or "",
                task_context=context,
                is_benign=rec.get("label") != "attack",
            )
        )
        api_calls += 1
        if verdict.parse_error or verdict.reason == "judge_api_error":
            failures += 1
        rows.append(
            {
                "sample_id": rec.get("id"),
                "category": rec.get("category"),
                "label": rec.get("label"),
                "provider": "google",
                "model": MODEL_ID,
                "timestamp": _utc(),
                "request_id": (gen.raw or {}).get("id"),
                "input_hash": _hash_text(full),
                "output_hash": _hash_text(gen.text or ""),
                "latency_ms": gen.latency_ms,
                "prompt_tokens": (gen.usage or {}).get("prompt_tokens"),
                "completion_tokens": (gen.usage or {}).get("completion_tokens"),
                "total_tokens": (gen.usage or {}).get("total_tokens"),
                "http_status": (gen.raw or {}).get("http_status"),
                "error": gen.error,
                "experiment_id": EXPERIMENT_ID,
                "seed": SEED,
                "dataset_version": DATASET_VERSION,
                "git_commit": git,
                "dataset_hash": dataset_hash,
                "target_response": (gen.text or "")[:500],
                "judge": verdict.to_dict(),
                "judge_blind": True,
            }
        )
    status = "VALID" if failures == 0 and api_calls == 4 else ("BLOCKED" if failures else "PARTIAL")
    return {
        "status": status,
        "api_calls": api_calls,
        "failures": failures,
        "rows": rows,
        "note": "Smoke uses B0 (no defense) only. Not combined with full-experiment metrics.",
    }


def analyze_results(
    output_root: Path,
    *,
    records: list[dict[str, Any]],
    seed: int,
) -> dict[str, Any]:
    all_outcomes: dict[str, list[EpisodeOutcome]] = {}
    per_baseline_stats: dict[str, Any] = {}
    for baseline in BASELINES:
        pred_path = output_root / baseline / f"{baseline}_predictions.jsonl"
        rows: list[dict[str, Any]] = []
        if pred_path.exists():
            with pred_path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))
        outcomes = [
            EpisodeOutcome(
                episode_id=str(r.get("sample_id") or r.get("id")),
                label=str(r.get("label", "attack")),
                attack_succeeded=bool(r.get("attack_succeeded", r.get("attack_success", False))),
                utility_success=bool(r.get("utility_success", False)),
                blocked=bool(r.get("blocked", False)),
                baseline=baseline,
                model_key=TARGET_KEY,
            )
            for r in rows
        ]
        all_outcomes[baseline] = outcomes
        if outcomes:
            per_baseline_stats[baseline] = compute_baseline_statistics(outcomes, seed=seed)

    comparisons: list[dict[str, Any]] = []
    raw_p: list[float] = []
    labels: list[str] = []
    reference = "B0"
    for treatment in BASELINES:
        if treatment == reference:
            continue
        comp = paired_baseline_comparison(
            all_outcomes.get(reference, []),
            all_outcomes.get(treatment, []),
            reference=reference,
            treatment=treatment,
        )
        a_flags = [
            1.0 if o.attack_succeeded else 0.0
            for o in all_outcomes.get(reference, [])
            if o.label == "attack"
        ]
        b_flags = [
            1.0 if o.attack_succeeded else 0.0
            for o in all_outcomes.get(treatment, [])
            if o.label == "attack"
        ]
        # Align by id for effect size.
        map_a = {o.episode_id: o for o in all_outcomes.get(reference, []) if o.label == "attack"}
        map_b = {o.episode_id: o for o in all_outcomes.get(treatment, []) if o.label == "attack"}
        common = sorted(set(map_a) & set(map_b))
        a_bin = [1.0 if map_a[i].attack_succeeded else 0.0 for i in common]
        b_bin = [1.0 if map_b[i].attack_succeeded else 0.0 for i in common]
        comp["cohens_d"] = round(cohens_d(a_bin, b_bin), 4) if common else None
        comparisons.append(comp)
        raw_p.append(float(comp.get("mcnemar", {}).get("p_value", 1.0)))
        labels.append(f"{reference}_vs_{treatment}")

    holm = holm_correction(raw_p) if raw_p else []
    holm_rows = []
    for label, h, comp in zip(labels, holm, comparisons):
        holm_rows.append(
            {
                "comparison": label,
                **h,
                "asr_delta": comp.get("asr_delta"),
                "cohens_d": comp.get("cohens_d"),
                "significant_0.05_holm": h["adjusted_p"] < 0.05,
            }
        )

    # Per-category ASR for B0 vs B3
    cat_report: dict[str, Any] = {}
    rec_cat = {str(r.get("id")): str(r.get("category")) for r in records}
    for baseline, outcomes in all_outcomes.items():
        by_cat: dict[str, list[EpisodeOutcome]] = defaultdict(list)
        for o in outcomes:
            if o.label != "attack":
                continue
            by_cat[rec_cat.get(o.episode_id, "unknown")].append(o)
        cat_report[baseline] = {
            cat: {
                "n": len(items),
                "asr": round(sum(1 for x in items if x.attack_succeeded) / len(items), 4)
                if items
                else None,
            }
            for cat, items in sorted(by_cat.items())
        }

    return {
        "experiment_id": EXPERIMENT_ID,
        "seed": seed,
        "baselines": BASELINES,
        "per_baseline": per_baseline_stats,
        "paired_comparisons": comparisons,
        "holm_corrected": holm_rows,
        "per_category_asr": cat_report,
        "reference_baseline": reference,
    }


def classify_run_status(
    *,
    planned: int,
    completed_rows: int,
    judge_failures: int,
    target_failures: int,
    blocked_preflight: bool,
) -> str:
    if blocked_preflight:
        return "BLOCKED"
    if completed_rows == 0:
        return "BLOCKED"
    if judge_failures:
        return "INVALID"
    if target_failures or completed_rows < planned:
        return "PARTIAL"
    return "VALID"


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP005 Gemini 3.6 Flash real-LLM evaluation")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--smoke-only", action="store_true")
    parser.add_argument("--full-only", action="store_true", help="Skip preflight/smoke (already VALID)")
    parser.add_argument("--n-attack", type=int, default=N_ATTACK)
    parser.add_argument("--n-benign", type=int, default=N_BENIGN)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    git = git_commit() or "UNKNOWN"
    if not TEST_PATH.exists():
        print(json.dumps({"status": "BLOCKED", "reason": f"missing {TEST_PATH}"}))
        return 1
    dataset_hash = sha256_file(TEST_PATH)
    if dataset_hash != TEST_HASH_EXPECTED:
        print(json.dumps({
            "status": "BLOCKED",
            "reason": "dataset hash mismatch",
            "expected": TEST_HASH_EXPECTED,
            "got": dataset_hash,
        }, indent=2))
        return 1

    records, sample_meta = select_heldout_records(
        n_attack=args.n_attack, n_benign=args.n_benign, seed=args.seed
    )
    run_id = datetime.now(timezone.utc).strftime("EXP005-%Y%m%d-%H%M%S")
    out = results_dir(run_id)
    out.mkdir(parents=True, exist_ok=True)
    exp_dir = ROOT / "experiments" / "EXP005_GEMINI_FLASH"
    exp_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": run_id,
        "provider": "google",
        "model": MODEL_ID,
        "model_identifier": "gemini-3.6-flash",
        "api": "interactions",
        "baselines": BASELINES,
        "baseline_definitions": {
            "B0": "No defense",
            "B1": "Rule-based detector block",
            "B2_L1": "Fixed defense level 1 (canonical fixed defense)",
            "B3": "ADAPTI-GUARD adaptive policy",
        },
        "dataset": DATASET_NAME,
        "dataset_version": DATASET_VERSION,
        "dataset_hash": dataset_hash,
        "split": "test",
        "seed": args.seed,
        "n_attack": args.n_attack,
        "n_benign": args.n_benign,
        "sample_meta": sample_meta,
        "generation_parameters": {
            "temperature": 0.0,
            "temperature_supported": False,
            "top_p": None,
            "top_p_supported": False,
            "max_output_tokens": 512,
            "seed": 42,
            "seed_supported": True,
            "system_prompt": "You are a helpful assistant.",
            "api": "interactions",
        },
        "judge_model": MODEL_ID,
        "judge_configuration": {
            "blind": True,
            "independent_call": True,
            "independent_model_family": False,
            "reason": (
                "OpenRouter primary judge (anthropic/claude-sonnet-4) returned HTTP 401. "
                "Gemini 3.6 Flash is used as a separate blind judge call."
            ),
            "old_judge": "anthropic/claude-sonnet-4",
            "new_judge": "gemini-3.6-flash",
        },
        "cache_enabled": False,
        "publication_mode": True,
        "git_commit": git,
        "python_version": sys.version,
        "timestamp": _utc(),
    }
    write_json(out / "config.json", config)
    write_json(out / "provenance.json", {
        "experiment_id": EXPERIMENT_ID,
        "run_id": run_id,
        "git_commit": git,
        "provider": "google",
        "model": MODEL_ID,
        "dataset": DATASET_NAME,
        "dataset_version": DATASET_VERSION,
        "dataset_hash": dataset_hash,
        "split": "test",
        "seed": args.seed,
        "sample_count": len(records),
        "baselines": BASELINES,
    })

    if not args.full_only:
        pf = preflight()
        write_json(out / "preflight.json", pf)
        print(json.dumps({"preflight": pf["status"], "error": pf.get("error")}, indent=2))
        if pf["status"] != "VALID":
            write_json(out / "metrics.json", {"status": "BLOCKED", "reason": pf.get("error")})
            (out / "README.md").write_text(
                f"# {EXPERIMENT_ID}\n\nStatus: **BLOCKED**\n\n{pf.get('error')}\n",
                encoding="utf-8",
            )
            return 1
        if args.preflight_only:
            return 0
    else:
        write_json(out / "preflight.json", {
            "status": "VALID",
            "skipped": True,
            "note": "preflight skipped via --full-only after prior VALID smoke",
        })

    GeminiTargetModel.reset_quota_circuit()
    target, judge = build_models(
        PipelineConfig(
            target_config_key=TARGET_KEY,
            judge_config_key=JUDGE_KEY,
            backend=EvaluationBackend.GEMINI,
        ),
        EvaluationBackend.GEMINI,
        cache_enabled=False,
    )

    if not args.full_only:
        smoke_recs = _smoke_records(records)
        smoke = run_smoke(
            target=target,
            judge=judge,
            records=smoke_recs,
            git=git,
            dataset_hash=dataset_hash,
        )
        write_json(out / "smoke.json", smoke)
        print(json.dumps({"smoke": smoke["status"], "api_calls": smoke["api_calls"]}, indent=2))
        if smoke["status"] != "VALID":
            write_json(out / "metrics.json", {"status": smoke["status"], "smoke": smoke})
            (out / "README.md").write_text(
                f"# {EXPERIMENT_ID}\n\nSmoke status: **{smoke['status']}**\n",
                encoding="utf-8",
            )
            return 1
        if args.smoke_only:
            return 0
        # Clear free-tier RPM window before the full matrix (limit=20 RPM).
        cooldown = 65.0
        print(f"Cooldownoldown {cooldown:.0f}s before full experiment (RPM pacing)...", flush=True)
        time.sleep(cooldown)
        GeminiTargetModel.reset_quota_circuit()
    else:
        write_json(out / "smoke.json", {
            "status": "VALID",
            "skipped": True,
            "note": "smoke skipped via --full-only after prior VALID smoke",
            "prior_smoke": "results/real_llm/gemini_3_6_flash/EXP005-20260903-081350/smoke.json",
        })

    errors: list[dict[str, Any]] = []
    planned = len(records) * len(BASELINES)
    completed = 0
    judge_failures = 0
    target_failures = 0
    aborted_reason: str | None = None
    raw_outputs = out / "raw_outputs.jsonl"
    judge_outputs = out / "judge_outputs.jsonl"
    if raw_outputs.exists():
        raw_outputs.unlink()
    if judge_outputs.exists():
        judge_outputs.unlink()

    run_context = BaselineRunContext(
        experiment_id=EXPERIMENT_ID,
        model_id=MODEL_ID,
        model_config_key=TARGET_KEY,
        git_commit=git,
        seed=args.seed,
        dataset_hash=dataset_hash,
        cache_enabled=False,
    )

    baseline_metrics: dict[str, Any] = {}
    for baseline in BASELINES:
        if aborted_reason:
            break
        print(f"=== {baseline} ({len(records)} samples) ===", flush=True)
        result = run_baseline_evaluation(
            baseline,
            records,
            target=target,
            judge=judge,
            output_dir=out / baseline,
            run_context=run_context,
        )
        baseline_metrics[baseline] = {
            "status": result.status,
            "n_samples": result.n_samples,
            "metrics": result.metrics,
            "asr_bootstrap_ci": result.asr_bootstrap_ci,
        }
        pred_path = Path(result.episodes_path)
        baseline_target_errors = 0
        if pred_path.exists():
            with pred_path.open(encoding="utf-8") as fh, \
                    raw_outputs.open("a", encoding="utf-8") as raw_fh, \
                    judge_outputs.open("a", encoding="utf-8") as j_fh:
                for line in fh:
                    row = json.loads(line)
                    completed += 1
                    if row.get("api_status") == "target_error":
                        target_failures += 1
                        baseline_target_errors += 1
                        errors.append({
                            "sample_id": row.get("sample_id"),
                            "baseline": baseline,
                            "error": "target_api_error",
                            "detail": (row.get("target_response") or "")[:400],
                        })
                    elif row.get("judge_failure") or row.get("api_status") == "judge_error":
                        judge_failures += 1
                        errors.append({
                            "sample_id": row.get("sample_id"),
                            "baseline": baseline,
                            "error": row.get("judge_reason"),
                        })
                    raw_fh.write(json.dumps({
                        "baseline": baseline,
                        "sample_id": row.get("sample_id"),
                        "target_response": row.get("target_response"),
                        "target_prompt": row.get("target_prompt") or row.get("prompt"),
                        "blocked": row.get("blocked"),
                        "latency_ms": row.get("episode_latency_ms"),
                        "input_tokens": row.get("input_tokens") or row.get("prompt_tokens"),
                        "output_tokens": row.get("output_tokens") or row.get("completion_tokens"),
                    }, ensure_ascii=False) + "\n")
                    j_fh.write(json.dumps({
                        "baseline": baseline,
                        "sample_id": row.get("sample_id"),
                        "judge_raw": row.get("judge_raw"),
                        "judge_model": row.get("judge_model"),
                        "attack_success": row.get("attack_success", row.get("attack_succeeded")),
                        "utility_success": row.get("utility_success"),
                        "judge_reason": row.get("judge_reason"),
                        "judge_failure": row.get("judge_failure"),
                    }, ensure_ascii=False) + "\n")
        # Abort remaining baselines if this one is dominated by API failures.
        if baseline_target_errors >= max(3, len(records) // 2):
            aborted_reason = (
                f"abort_after_{baseline}: {baseline_target_errors} target_errors "
                "(likely free-tier quota/RPM); not fabricating remaining rows"
            )
            print(aborted_reason, flush=True)

    status = classify_run_status(
        planned=planned,
        completed_rows=completed,
        judge_failures=judge_failures,
        target_failures=target_failures,
        blocked_preflight=False,
    )
    if aborted_reason and status == "VALID":
        status = "PARTIAL"
    stats = analyze_results(out, records=records, seed=args.seed)
    write_json(out / "statistics.json", stats)

    metrics_out = {
        "status": status,
        "experiment_id": EXPERIMENT_ID,
        "evaluation_mode": "real_llm_judge",
        "label": "Real LLM Evaluation",
        "provider": "google",
        "model": MODEL_ID,
        "n_samples": len(records),
        "n_attack": sample_meta["n_attack_selected"],
        "n_benign": sample_meta["n_benign_selected"],
        "planned_evaluations": planned,
        "completed_evaluations": completed,
        "judge_failures": judge_failures,
        "target_failures": target_failures,
        "aborted_reason": aborted_reason,
        "baselines": baseline_metrics,
        "statistics": stats,
        "cost_usd": None,
        "cost_note": "cost_unavailable_from_response",
        "git_commit": git,
        "dataset_hash": dataset_hash,
    }
    write_json(out / "metrics.json", metrics_out)

    # CSV
    csv_path = out / "metrics.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["baseline", "n", "n_attack", "n_benign", "asr", "defense_rate", "fpr", "utility"])
        for b, payload in stats.get("per_baseline", {}).items():
            asr = payload.get("asr") or {}
            fpr = payload.get("fpr")
            util = payload.get("utility")
            writer.writerow([
                b,
                payload.get("n_episodes"),
                payload.get("n_attack"),
                payload.get("n_benign"),
                asr.get("point") if isinstance(asr, dict) else asr,
                payload.get("defense_rate"),
                fpr.get("point") if isinstance(fpr, dict) else fpr,
                util.get("point") if isinstance(util, dict) else util,
            ])

    write_json(out / "errors.jsonl", {"n": len(errors)})  # placeholder; raw errors below
    err_path = out / "errors.jsonl"
    with err_path.open("w", encoding="utf-8") as fh:
        for e in errors:
            fh.write(json.dumps(e) + "\n")

    readme = [
        f"# {EXPERIMENT_ID}",
        "",
        f"**Status:** `{status}`",
        "",
        "Label: **Real LLM Evaluation** (not simulation).",
        "",
        f"- Provider: google",
        f"- Model: `{MODEL_ID}`",
        f"- Dataset: `{DATASET_NAME}` {DATASET_VERSION} split=test",
        f"- SHA-256: `{dataset_hash}`",
        f"- Samples: {len(records)} ({sample_meta['n_attack_selected']} attack / {sample_meta['n_benign_selected']} benign)",
        f"- Baselines: {', '.join(BASELINES)}",
        f"- Git: `{git}`",
        "",
        "See `metrics.json` and `statistics.json`.",
    ]
    (out / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    write_json(exp_dir / "latest_run.json", {"run_id": run_id, "path": str(out), "status": status})
    print(json.dumps({"status": status, "path": str(out), "completed": completed, "planned": planned}, indent=2))
    return 0 if status == "VALID" else 1


if __name__ == "__main__":
    raise SystemExit(main())
