#!/usr/bin/env python3
"""MT1 repeat r1 on layer_a_v2 (diagnostic tier). Canonical real_llm_pipeline path."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.live_budget_gate import BudgetGatedTargetModel, BudgetLedger, estimate_request_cost_usd
from adapti_guard.evaluation.live_model_resolver import model_id_for_config_key
from adapti_guard.evaluation.llm_judge import LLMJudge
from adapti_guard.evaluation.statistics import mcnemar_test
from adapti_guard.evaluation.target_model import GenerationRequest, build_target_model
from adapti_guard.experiments.env_loader import load_project_env
from adapti_guard.experiments.real_llm_pipeline import (
    BaselineRunContext,
    EvaluationBackend,
    PipelineConfig,
    load_records,
    resolve_backend,
    run_baseline_evaluation,
)
from adapti_guard.evaluation.experiment_logging import git_commit

PACK = "datasets/frozen/layer_a_v2"
ATTACK_N, BENIGN_N, SEED = 20, 20, 42
CAP_USD = 2.0
ARMS = ("B0", "STATIC-A3", "SPOTLIGHT", "B3")
JUDGE_KEY = "judge_fallback"
SECOND_JUDGE_KEY = "judge_secondary"
RUN_ROOT = ROOT / "experiments/real_llm_eval/MT1/r1"
DIAG_MULTI = ROOT / "experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_MULTI_TARGET/DIAG-MULTI-TARGET-20260924"
REUSE_MAP = {
    "qwen-2.5-7b": DIAG_MULTI / "qwen-2.5-7b/B0/B0_predictions.jsonl",
    "llama-3.1-8b": DIAG_MULTI / "llama-3.1-8b/B0/B0_predictions.jsonl",
    "qwen3-30b": DIAG_MULTI / "qwen3-30b/B0/B0_predictions.jsonl",
    "gpt-oss-120b": DIAG_MULTI / "gpt-oss-120b/B0/B0_predictions.jsonl",
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _targets():
    load_project_env()
    prov_groq = "groq" if os.environ.get("GROQ_API_KEY") else "openrouter"
    key_oss = "groq_target" if prov_groq == "groq" else "target_gpt_oss_or"
    return [
        ("qwen-2.5-7b", "target_2", "openrouter"),
        ("llama-3.1-8b", "target_1", "openrouter"),
        ("qwen3-30b", "model_b", "openrouter"),
        ("gpt-oss-120b", key_oss, prov_groq),
        ("gemma-4-31b-it", "model_a", "openrouter"),
        ("mistral-small-3.2-24b", "mistral_small", "openrouter"),
    ]


def preflight_worst_usd() -> tuple[bool, float, int]:
    n_ep = len(_targets()) * len(ARMS) * (ATTACK_N + BENIGN_N)
    req = GenerationRequest(prompt="x" * 2000, system_prompt="y" * 200, max_tokens=512)
    per = estimate_request_cost_usd(req, provider="openrouter") or 0.0
    worst = n_ep * 3 * per  # target + primary judge + secondary judge (upper)
    return worst <= CAP_USD, float(worst), n_ep


def cmh_discordant_p(b10s: list[int], b01s: list[int]) -> float:
    """CMH-style normal approx on stratified discordant pairs (diagnostic)."""
    if not b10s:
        return 1.0
    stat = sum(b - a for b, a in zip(b10s, b01s))
    var = sum(b + a for b, a in zip(b10s, b01s))
    if var <= 0:
        return 1.0
    from scipy.stats import norm

    z = abs(stat) / (var ** 0.5)
    return float(2 * (1 - norm.cdf(z)))


def _metrics(pred_path: Path) -> dict:
    rows = [json.loads(ln) for ln in pred_path.read_text().splitlines() if ln.strip()]
    atk = [r for r in rows if r.get("label") == "attack"]
    ben = [r for r in rows if r.get("label") == "benign"]
    return {
        "asr": round(sum(r.get("attack_succeeded") for r in atk) / len(atk), 4) if atk else 0.0,
        "utility": round(sum(r.get("utility_success") for r in ben) / len(ben), 4) if ben else 0.0,
        "fpr": round(sum(r.get("blocked") for r in ben) / len(ben), 4) if ben else 0.0,
        "n_blocked": sum(1 for r in rows if r.get("blocked")),
        "judge_fail": sum(1 for r in rows if r.get("judge_reason") in ("judge_api_error", "judge_parse_error")),
    }


def _paired_mcnemar(b0p: Path, tp: Path) -> dict:
    b0 = {r["episode_id"]: r for r in map(json.loads, b0p.read_text().splitlines()) if r}
    tr = {r["episode_id"]: r for r in map(json.loads, tp.read_text().splitlines()) if r}
    ids = [i for i in b0 if i in tr and b0[i].get("label") == "attack"]
    a = [bool(b0[i].get("attack_succeeded")) for i in ids]
    b = [bool(tr[i].get("attack_succeeded")) for i in ids]
    return mcnemar_test(a, b)


def run_r1(execute: bool) -> dict:
    ok, worst_usd, n_ep = preflight_worst_usd()
    out = {"preflight_ok": ok, "preflight_worst_usd": worst_usd, "n_episodes": n_ep, "cap_usd": CAP_USD}
    if not ok:
        out["status"] = "STOPPED"
        out["reason"] = "preflight_exceeds_cap"
        return out
    if not execute:
        out["status"] = "PREFLIGHT_ONLY"
        return out

    load_project_env()
    if not os.environ.get("OPENROUTER_API_KEY"):
        out["status"] = "STOPPED"
        out["reason"] = "OPENROUTER_API_KEY missing"
        return out

    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    log = RUN_ROOT / "RUN_LOG.md"
    log.write_text(f"# MT1 r1 seed={SEED}\nstarted {_utc()}\npreflight_usd={worst_usd}\n", encoding="utf-8")
    ledger = BudgetLedger(max_usd=CAP_USD, max_requests=4000, hard_stop=True)
    episodes_jsonl = RUN_ROOT / "episodes.jsonl"
    summary_targets: dict = {}

    backend, block = resolve_backend(EvaluationBackend.AUTO)
    if block:
        return {"status": "STOPPED", "reason": block}

    for slug, tkey, tprov in _targets():
        summary_targets[slug] = {"arms": {}}
        tdir = RUN_ROOT / slug
        tdir.mkdir(parents=True, exist_ok=True)
        for arm in ARMS:
            arm_dir = tdir / arm
            pred = arm_dir / f"{arm}_predictions.jsonl"
            reuse = arm == "B0" and slug in REUSE_MAP and REUSE_MAP[slug].is_file()
            if reuse:
                arm_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REUSE_MAP[slug], pred)
                summary_targets[slug]["arms"][arm] = {"status": "REUSED_B0", "source": str(REUSE_MAP[slug])}
                continue
            arm_dir.mkdir(parents=True, exist_ok=True)
            config = PipelineConfig(
                experiment_id=f"MT1-r1-{slug}-{arm}",
                output_dir=arm_dir,
                target_config_key=tkey,
                judge_config_key=JUDGE_KEY,
                backend=backend,
                baselines=[arm],
                attack_n=ATTACK_N,
                benign_n=BENIGN_N,
                seed=SEED,
                benchmark_dir=PACK,
            )
            records, meta = load_records(config)
            target = build_target_model(tkey, cache_enabled=False)
            target.max_retries = 0
            judge_inner = build_target_model(JUDGE_KEY, cache_enabled=False)
            judge_inner.max_retries = 0
            judge = LLMJudge(model=judge_inner, config_key=JUDGE_KEY, use_fallback=False, cache_enabled=False)
            gated_t = BudgetGatedTargetModel(target, ledger, provider=tprov)
            gated_j = BudgetGatedTargetModel(judge_inner, ledger, provider="openrouter")
            judge._primary = gated_j
            ctx = BaselineRunContext(
                experiment_id=config.experiment_id,
                model_id=model_id_for_config_key(tkey),
                model_config_key=tkey,
                git_commit=git_commit(),
                seed=SEED,
                dataset_hash=str(meta.get("dataset_hash", "")),
                cache_enabled=False,
            )
            run_baseline_evaluation(arm, records, target=gated_t, judge=judge, output_dir=arm_dir, run_context=ctx)
            ok_s, _ = ledger.check_spend_allowed(0.0)
            if not ok_s:
                out["status"] = "STOPPED"
                out["reason"] = "budget_exceeded"
                break
            summary_targets[slug]["arms"][arm] = {"status": "COMPLETED"}
            if pred.is_file():
                with episodes_jsonl.open("a", encoding="utf-8") as ej:
                    for line in pred.read_text().splitlines():
                        if line.strip():
                            ej.write(json.dumps({**json.loads(line), "target_slug": slug, "arm": arm}) + "\n")

        b0p = tdir / "B0" / "B0_predictions.jsonl"
        for arm in ARMS:
            if arm == "B0":
                continue
            tp = tdir / arm / f"{arm}_predictions.jsonl"
            if b0p.is_file() and tp.is_file():
                m = _metrics(tp)
                summary_targets[slug]["arms"][arm]["metrics"] = m
                summary_targets[slug]["arms"][arm]["mcnemar_vs_b0"] = _paired_mcnemar(b0p, tp)
        if b0p.is_file():
            bm = _metrics(b0p)
            summary_targets[slug]["arms"]["B0"]["metrics"] = bm
            if bm.get("asr", 1) < 0.15:
                summary_targets[slug]["floor_effect"] = True

    pooled = {}
    for arm in ARMS:
        if arm == "B0":
            continue
        b10s, b01s = [], []
        for slug in summary_targets:
            mc = summary_targets[slug].get("arms", {}).get(arm, {}).get("mcnemar_vs_b0", {})
            if mc:
                b10s.append(int(mc.get("b10", 0)))
                b01s.append(int(mc.get("b01", 0)))
        pooled[arm] = {"cmh_p": round(cmh_discordant_p(b10s, b01s), 6), "b10_sum": sum(b10s), "b01_sum": sum(b01s)}

    summary = {
        "tier": "diagnostic",
        "seed": SEED,
        "pack": PACK,
        "targets": summary_targets,
        "pooled_vs_b0": pooled,
        "ledger": ledger.to_dict(),
        "status": "COMPLETED",
    }
    (RUN_ROOT / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    pins = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [RUN_ROOT / "SUMMARY.json"]}
    (RUN_ROOT / "HASH_PINS.json").write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--preflight-only", action="store_true")
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()
    out = run_r1(execute=args.execute and not args.preflight_only)
    print(json.dumps(out, indent=2))
    return 0 if out.get("status") in ("COMPLETED", "PREFLIGHT_ONLY") else 1


if __name__ == "__main__":
    raise SystemExit(main())
