#!/usr/bin/env python3
"""Multi-target pilot B0 vs B1 on layer_a_v2 (NOT paper Results)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

_pack_path = ROOT / "scripts/run_b0_b1_diagnostic_pack.py"
_spec = importlib.util.spec_from_file_location("diag_pack", _pack_path)
_diag = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_diag)

DIAG_LABEL = _diag.DIAG_LABEL
JUDGE_KEY = _diag.JUDGE_KEY
PACK = _diag.PACK
append_jsonl = _diag.append_jsonl
preflight_worst_case_usd = _diag.preflight_worst_case_usd
run_diagnostic = _diag.run_diagnostic

from adapti_guard.evaluation.live_budget_gate import (
    BudgetGatedTargetModel,
    BudgetLedger,
    estimate_request_cost_usd,
)
from adapti_guard.evaluation.live_model_resolver import model_id_for_config_key
from adapti_guard.evaluation.llm_judge import JudgeInput, LLMJudge
from adapti_guard.evaluation.statistics import mcnemar_test
from adapti_guard.evaluation.target_model import GenerationRequest, build_target_model
from adapti_guard.experiments.env_loader import load_project_env
from adapti_guard.experiments.real_llm_pipeline import PipelineConfig, load_records

RUN_ROOT = ROOT / "experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_MULTI_TARGET"
REUSE_RUN = (
    ROOT
    / "experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_B0_B1"
    / "DIAG-B0-B1-LAYER-A-V2-20260924"
)
SECOND_JUDGE_KEY = "target_gpt_oss_or"
CAP_USD = 2.0
ATTACK_N, BENIGN_N, SEED = 20, 20, 42


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cohen_kappa(a: list[bool], b: list[bool]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa = sum(a) / n
    pb = sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    if pe >= 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def _prompt_map() -> dict[str, dict]:
    cfg = PipelineConfig(
        benchmark_dir=PACK,
        attack_n=ATTACK_N,
        benign_n=BENIGN_N,
        seed=SEED,
    )
    records, _ = load_records(cfg)
    return {str(r["id"]): r for r in records}


def _resolve_oss_target_key() -> tuple[str, str]:
    load_project_env()
    if os.environ.get("GROQ_API_KEY"):
        return "groq_target", "groq"
    return "target_gpt_oss_or", "openrouter"


def _targets() -> list[tuple[str, str, str, bool]]:
    oss_key, oss_prov = _resolve_oss_target_key()
    return [
        ("qwen-2.5-7b", "target_2", "openrouter", True),
        ("llama-3.1-8b", "target_1", "openrouter", False),
        ("qwen3-30b", "model_b", "openrouter", False),
        ("gpt-oss-120b", oss_key, oss_prov, False),
    ]


def _preflight_all() -> tuple[bool, dict]:
    n_total = (ATTACK_N + BENIGN_N) * 2
    ok_single, worst_usd, worst_req = preflight_worst_case_usd(n_total, CAP_USD)
    new_targets = 3
    second_judge_eps = 2 * (ATTACK_N + BENIGN_N)
    req = GenerationRequest(prompt="x" * 2000, system_prompt="y" * 200, max_tokens=512)
    per_or = estimate_request_cost_usd(req, provider="openrouter") or 0.0
    est_new = worst_usd * new_targets + per_or * second_judge_eps
    detail = {
        "cap_usd": CAP_USD,
        "per_target_worst_usd": worst_usd,
        "per_target_worst_requests": worst_req,
        "new_targets": new_targets,
        "second_judge_episodes": second_judge_eps,
        "net_new_worst_usd_est": round(est_new, 6),
        "single_target_preflight_ok": ok_single,
    }
    return est_new <= CAP_USD and ok_single, detail


def _metrics_from_predictions(path: Path) -> dict:
    rows = [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]
    attacks = [r for r in rows if r.get("label") == "attack"]
    benign = [r for r in rows if r.get("label") == "benign"]
    n_atk = len(attacks)
    n_ben = len(benign)
    asr = sum(1 for r in attacks if r.get("attack_succeeded")) / n_atk if n_atk else 0.0
    util = sum(1 for r in benign if r.get("utility_success")) / n_ben if n_ben else 0.0
    fpr = sum(1 for r in benign if r.get("blocked")) / n_ben if n_ben else 0.0
    jf = sum(1 for r in rows if r.get("judge_reason") in ("judge_api_error", "judge_parse_error"))
    return {
        "n": len(rows),
        "asr": round(asr, 4),
        "utility": round(util, 4),
        "fpr": round(fpr, 4),
        "n_blocked": sum(1 for r in rows if r.get("blocked")),
        "judge_fail_count": jf,
    }


def _mcnemar_b0_b1(b0_path: Path, b1_path: Path) -> dict:
    b0 = {r["episode_id"]: r for r in map(json.loads, b0_path.read_text().splitlines()) if r}
    b1 = {r["episode_id"]: r for r in map(json.loads, b1_path.read_text().splitlines()) if r}
    ids = sorted(set(b0) & set(b1))
    atk_ids = [i for i in ids if b0[i].get("label") == "attack"]
    a_succ = [bool(b0[i].get("attack_succeeded")) for i in atk_ids]
    b_succ = [bool(b1[i].get("attack_succeeded")) for i in atk_ids]
    m = mcnemar_test(a_succ, b_succ)
    return {"n_attack_paired": len(atk_ids), "mcnemar": m}


def _find_b0_predictions(target_dir: Path) -> Path | None:
    direct = target_dir / "B0" / "B0_predictions.jsonl"
    if direct.is_file():
        return direct
    hits = list(target_dir.glob("*/B0/B0_predictions.jsonl"))
    return hits[0] if hits else None


def _second_judge_pass(
    b0_pred: Path,
    ledger: BudgetLedger,
    out_path: Path,
    prompts: dict[str, dict],
) -> dict:
    load_project_env()
    inner = build_target_model(SECOND_JUDGE_KEY, config_path="configs/models.yaml", cache_enabled=False)
    inner.max_retries = 0
    gated = BudgetGatedTargetModel(inner, ledger, provider="openrouter")
    judge = LLMJudge(
        model=gated,
        config_key=SECOND_JUDGE_KEY,
        fallback_config_key=SECOND_JUDGE_KEY,
        config_path="configs/models.yaml",
        cache_enabled=False,
        use_fallback=False,
    )
    primary: list[bool] = []
    secondary: list[bool] = []
    rows_out = []
    for line in b0_pred.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        eid = row.get("episode_id") or row.get("sample_id")
        rec = prompts.get(str(eid), {})
        prompt = rec.get("prompt") or rec.get("user_prompt") or ""
        meta = rec.get("metadata") or {}
        success_condition = str(rec.get("success_condition") or meta.get("success_condition") or "")
        label = row.get("label", "attack")
        response = row.get("target_response") or ""
        is_benign = label == "benign"
        verdict = judge.judge(
            JudgeInput(
                user_prompt=prompt,
                model_response=response,
                is_benign=is_benign,
                success_condition=success_condition,
                attack_category=str(row.get("category") or ""),
            )
        )
        sec = bool(verdict.utility_success) if is_benign else bool(verdict.attack_success)
        pri = bool(row.get("utility_success")) if is_benign else bool(row.get("attack_succeeded"))
        primary.append(pri)
        secondary.append(sec)
        row["second_judge_attack_success"] = verdict.attack_success if not is_benign else None
        row["second_judge_utility_success"] = verdict.utility_success if is_benign else None
        rows_out.append(row)
        ok, reason = ledger.check_spend_allowed(0.0)
        if not ok:
            row["second_judge_stopped"] = reason
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(json.dumps(r) for r in rows_out) + "\n", encoding="utf-8")
    agree = sum(p == s for p, s in zip(primary, secondary)) / len(primary) if primary else 0.0
    return {
        "n": len(primary),
        "agreement_rate": round(agree, 4),
        "cohen_kappa": round(_cohen_kappa(primary, secondary), 4),
        "ledger_spent_usd": ledger.spent_usd,
    }


def main() -> int:
    load_project_env()
    if not os.environ.get("OPENROUTER_API_KEY"):
        print(json.dumps({"status": "STOPPED", "reason": "OPENROUTER_API_KEY missing"}))
        return 1

    ok, pre = _preflight_all()
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = f"DIAG-MULTI-TARGET-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    master = RUN_ROOT / run_id
    master.mkdir(parents=True, exist_ok=True)
    log = master / "RUN_LOG.md"
    log.write_text(
        f"# {run_id}\n\n- label: {DIAG_LABEL}\n- started: {_utc()}\n"
        f"- preflight: {json.dumps(pre)}\n- preflight_pass: {ok}\n\n",
        encoding="utf-8",
    )
    if not ok:
        print(json.dumps({"status": "STOPPED", "reason": "preflight_fail", "preflight": pre}))
        return 1

    prompts = _prompt_map()
    ledger = BudgetLedger(max_usd=CAP_USD, max_requests=700, hard_stop=True)
    episodes_jsonl = master / "episodes.jsonl"
    summary: dict = {"targets": {}, "preflight": pre, "label": DIAG_LABEL, "run_id": run_id}

    for slug, tkey, tprov, reuse in _targets():
        tdir = master / slug
        if reuse and REUSE_RUN.is_dir():
            if tdir.exists():
                shutil.rmtree(tdir)
            shutil.copytree(REUSE_RUN, tdir)
            summary["targets"][slug] = {"status": "REUSED", "path": str(tdir.relative_to(ROOT)), "source": str(REUSE_RUN.relative_to(ROOT))}
            b0p = _find_b0_predictions(tdir) or (tdir / "B0" / "B0_predictions.jsonl")
            b1p = tdir / "B1" / "B1_predictions.jsonl"
            summary["targets"][slug]["b0"] = _metrics_from_predictions(b0p)
            summary["targets"][slug]["b1"] = _metrics_from_predictions(b1p)
            summary["targets"][slug]["mcnemar"] = _mcnemar_b0_b1(b0p, b1p)
            continue

        out = run_diagnostic(
            output_dir=tdir,
            run_id=".",
            attack_n=ATTACK_N,
            benign_n=BENIGN_N,
            seed=SEED,
            max_usd=CAP_USD,
            target_config_key=tkey,
            target_provider=tprov,
            ledger=ledger,
            skip_preflight=True,
        )
        summary["targets"][slug] = out
        if out.get("status") != "COMPLETED":
            summary["status"] = "STOPPED"
            summary["stop_reason"] = out.get("reason")
            break
        run_dir = Path(out["run_dir"])
        b0p = run_dir / "B0" / "B0_predictions.jsonl"
        b1p = run_dir / "B1" / "B1_predictions.jsonl"
        summary["targets"][slug]["b0_metrics"] = _metrics_from_predictions(b0p)
        summary["targets"][slug]["b1_metrics"] = _metrics_from_predictions(b1p)
        summary["targets"][slug]["mcnemar"] = _mcnemar_b0_b1(b0p, b1p)
        for arm in ("B0", "B1"):
            pred = run_dir / arm / f"{arm}_predictions.jsonl"
            if pred.is_file():
                for line in pred.read_text().splitlines():
                    if line.strip():
                        append_jsonl(
                            episodes_jsonl,
                            {**json.loads(line), "target_slug": slug, "label_tag": DIAG_LABEL},
                        )

    second = {}
    for slug in ("llama-3.1-8b", "gpt-oss-120b"):
        b0 = _find_b0_predictions(master / slug)
        if b0 and b0.is_file():
            second[slug] = _second_judge_pass(b0, ledger, master / f"second_judge_{slug}.jsonl", prompts)
    summary["second_judge"] = second
    summary["ledger"] = ledger.to_dict()
    summary["status"] = summary.get("status", "COMPLETED")

    (master / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    pins = {
        str(p.relative_to(ROOT)): _sha256(p)
        for p in [master / "SUMMARY.json", episodes_jsonl, log]
        if p.is_file()
    }
    (master / "HASH_PINS.json").write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## finished {_utc()}\n\n```json\n{json.dumps(summary, indent=2)}\n```\n")

    print(json.dumps(summary, indent=2))
    return 0 if summary.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
