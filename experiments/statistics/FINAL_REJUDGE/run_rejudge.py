"""Rejudge 300 saved Phase 5 Groq target responses with Cerebras. No Groq calls."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "FINAL_REJUDGE"))

from src.adapti_guard.experiments.env_loader import load_project_env  # noqa: E402
from src.adapti_guard.evaluation.target_model import build_target_model  # noqa: E402
from judge_core import (  # noqa: E402
    ACTION_COST,
    LEVEL_FROM_ACTION,
    judge_one,
    load_frozen_by_id,
    sha256_text,
)

OUT = Path(__file__).resolve().parent
RAW = ROOT / "experiments" / "PHASE5_CONSTRAINED" / "raw_results.jsonl"
FROZEN = ROOT / "datasets" / "frozen" / "eval_v1" / "dataset.jsonl"
CKPT = OUT / "checkpoint.jsonl"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_done() -> dict[str, dict]:
    done = {}
    if CKPT.exists():
        for line in CKPT.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            key = f"{r.get('model_key')}|{r.get('policy')}|{r.get('sample_id')}"
            done[key] = r
    return done


def persist(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    load_project_env()
    frozen = load_frozen_by_id(FROZEN)
    targets = [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    if len(targets) != 300:
        print(f"ERROR: expected 300 rows, got {len(targets)}")
        return 1
    done = load_done()
    model = build_target_model(
        "cerebras_judge",
        config_path=str(ROOT / "configs" / "models.yaml"),
        cache_enabled=False,
    )
    all_rows: list[dict] = []
    errors: list[dict] = []
    n_ok = n_fail = n_invalid = 0
    calls = 0
    retries_logged = 0

    def retry_hook():
        nonlocal retries_logged
        retries_logged += 1

    model._budget_retry_callback = retry_hook

    for src in targets:
        eid = str(src.get("episode_id") or src.get("sample_id"))
        mk = src.get("model_key")
        pol = src.get("baseline")
        key = f"{mk}|{pol}|{eid}"
        if key in done and done[key].get("judge_status") in {"OK", "JUDGE_INVALID", "JUDGE_FAILED"}:
            rec = done[key]
            all_rows.append(rec)
            st = rec.get("judge_status")
            if st == "OK":
                n_ok += 1
            elif st == "JUDGE_INVALID":
                n_invalid += 1
            else:
                n_fail += 1
                errors.append(rec)
            continue
        fr = frozen.get(eid, {})
        prompt = fr.get("prompt") or ""
        response = src.get("target_response") or ""
        action = src.get("action") or "A0"
        base = {
            "experiment_id": "FINAL_REJUDGE",
            "source_experiment_id": src.get("experiment_id"),
            "run_id": "FINAL_REJUDGE-cerebras-qwen-3.8-27b",
            "timestamp": utc(),
            "seed": src.get("seed", 42),
            "model": mk,
            "policy": pol,
            "sample_id": eid,
            "attack_category": src.get("category") or fr.get("category"),
            "attack_prompt_hash": sha256_text(prompt),
            "target_response_hash": sha256_text(response),
            "target_response_truncated": True,
            "target_response_stored_chars": len(response),
            "judge_model": "qwen-3.8-27b",
            "judge_provider": "cerebras",
            "intervention_level": LEVEL_FROM_ACTION.get(action, "UNKNOWN"),
            "intervention_cost": ACTION_COST.get(action),
            "target_latency_ms": src.get("target_latency_ms"),
            "token_usage_target": {
                "prompt_tokens": src.get("prompt_tokens"),
                "completion_tokens": src.get("completion_tokens"),
                "total_tokens": src.get("total_tokens"),
            },
            "dataset_hash": src.get("dataset_hash"),
            "git_commit_source": src.get("git_commit"),
            "blocked": src.get("blocked"),
            "action": action,
        }
        if not prompt:
            rec = {
                **base,
                "judge_status": "JUDGE_FAILED",
                "error_status": "missing_frozen_prompt",
                "attack_success": None,
                "defense_success": None,
            }
            n_fail += 1
            errors.append(rec)
        else:
            calls += 1
            j = judge_one(
                model=model,
                user_prompt=prompt,
                model_response=response,
                category=base["attack_category"] or "unknown",
            )
            rec = {
                **base,
                **j,
                "error_status": None if j["judge_status"] == "OK" else j.get("error_class"),
            }
            if j["judge_status"] == "OK":
                n_ok += 1
            elif j["judge_status"] == "JUDGE_INVALID":
                n_invalid += 1
            else:
                n_fail += 1
                errors.append(rec)
        all_rows.append(rec)
        persist(CKPT, all_rows)
        print(
            f"{len(all_rows)}/300 {mk}/{pol} {eid} {rec.get('judge_status')} "
            f"calls={calls} retries={retries_logged}"
        )

    persist(OUT / "raw_judgments.jsonl", all_rows)
    persist(OUT / "errors.jsonl", errors)
    summary = {
        "timestamp": utc(),
        "n_source": len(targets),
        "n_written": len(all_rows),
        "n_ok": n_ok,
        "n_invalid": n_invalid,
        "n_failed": n_fail,
        "judge_calls": calls,
        "retries": retries_logged,
        "judge_provider": "cerebras",
        "judge_model": "qwen-3.8-27b",
        "target_calls": 0,
    }
    (OUT / "rejudge_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
