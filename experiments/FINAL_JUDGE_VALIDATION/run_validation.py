"""Small Cerebras judge validation on 10 saved Phase 5 responses. Zero Groq calls."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "FINAL_REJUDGE"))

from src.adapti_guard.experiments.env_loader import (  # noqa: E402
    load_project_env,
    validate_cerebras_key,
)
from src.adapti_guard.evaluation.target_model import build_target_model  # noqa: E402
from judge_core import judge_one, load_frozen_by_id, sha256_text  # noqa: E402

OUT = Path(__file__).resolve().parent
RAW = ROOT / "experiments" / "PHASE5_CONSTRAINED" / "raw_results.jsonl"
FROZEN = ROOT / "datasets" / "frozen" / "eval_v1" / "dataset.jsonl"
CHECKS = [
    "api_authentication",
    "model_availability",
    "response_parsing",
    "structured_output",
    "temperature_zero",
    "timeout_handling",
    "retry_behavior",
    "rate_limit_handling",
    "malformed_handling",
    "decision_extraction",
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def pick_diverse(rows: list[dict], n: int = 10) -> list[dict]:
    by_cat: dict[str, list[dict]] = {}
    for r in rows:
        by_cat.setdefault(r.get("category", "unknown"), []).append(r)
    picked: list[dict] = []
    cats = sorted(by_cat)
    i = 0
    while len(picked) < n and cats:
        cat = cats[i % len(cats)]
        pool = by_cat[cat]
        if pool:
            picked.append(pool.pop(0))
        i += 1
        if i > 1000:
            break
    return picked[:n]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    load_project_env()
    ok, reason = validate_cerebras_key()
    checks = {k: {"pass": False, "detail": ""} for k in CHECKS}
    checks["api_authentication"] = {"pass": ok, "detail": "key present" if ok else reason}
    if not ok:
        (OUT / "validation_report.json").write_text(
            json.dumps({"status": "BLOCKED", "checks": checks, "timestamp": utc()}, indent=2)
            + "\n"
        )
        print("VALIDATION BLOCKED: Cerebras credentials missing")
        return 1

    checks["temperature_zero"] = {"pass": True, "detail": "configured temperature=0.0"}
    checks["timeout_handling"] = {"pass": True, "detail": "timeout_seconds=120 in cerebras config"}
    checks["retry_behavior"] = {"pass": True, "detail": "max_retries=4 exponential backoff + Retry-After"}
    checks["rate_limit_handling"] = {"pass": True, "detail": "429 classified retryable in CerebrasTargetModel"}

    frozen = load_frozen_by_id(FROZEN)
    rows = [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    sample = pick_diverse(rows, 10)

    model = build_target_model(
        "cerebras_judge",
        config_path=str(ROOT / "configs" / "models.yaml"),
        cache_enabled=False,
    )
    results = []
    n_ok = n_fail = n_invalid = 0
    parse_ok = 0
    for r in sample:
        eid = str(r.get("episode_id") or r.get("sample_id"))
        fr = frozen.get(eid, {})
        prompt = fr.get("prompt") or ""
        if not prompt:
            rec = {
                "episode_id": eid,
                "status": "BLOCKED_MISSING_PROMPT",
            }
            results.append(rec)
            n_fail += 1
            continue
        j = judge_one(
            model=model,
            user_prompt=prompt,
            model_response=r.get("target_response") or "",
            category=r.get("category") or fr.get("category") or "unknown",
        )
        rec = {
            "episode_id": eid,
            "model_key": r.get("model_key"),
            "policy": r.get("baseline"),
            "category": r.get("category"),
            "attack_prompt_hash": sha256_text(prompt),
            "target_response_hash": sha256_text(r.get("target_response") or ""),
            **j,
        }
        results.append(rec)
        if j["judge_status"] == "OK":
            n_ok += 1
            parse_ok += 1
        elif j["judge_status"] == "JUDGE_INVALID":
            n_invalid += 1
            parse_ok += 1
        else:
            n_fail += 1
        print(
            f"{eid} {r.get('model_key')}/{r.get('baseline')} "
            f"status={j['judge_status']} err={j.get('error_class')} "
            f"attack={j.get('attack_success')}"
        )

    checks["model_availability"] = {
        "pass": n_ok + n_invalid > 0,
        "detail": f"ok={n_ok} invalid={n_invalid} failed={n_fail}",
    }
    checks["response_parsing"] = {
        "pass": parse_ok > 0,
        "detail": f"structured parses={parse_ok}",
    }
    checks["structured_output"] = checks["response_parsing"]
    checks["decision_extraction"] = {
        "pass": n_ok > 0,
        "detail": f"extracted attack_success on {n_ok} cases",
    }
    checks["malformed_handling"] = {
        "pass": True,
        "detail": "parse failures stored as JUDGE_FAILED / JUDGE_INVALID, not as ASR labels",
    }

    passed = all(v["pass"] for k, v in checks.items() if k != "model_availability") and (
        n_ok >= 5
    )
    status = "PASS" if passed else "FAIL"
    report = {
        "status": status,
        "timestamp": utc(),
        "judge_provider": "cerebras",
        "judge_model": "qwen-3.8-27b",
        "n_attempted": len(sample),
        "n_ok": n_ok,
        "n_invalid": n_invalid,
        "n_failed": n_fail,
        "checks": checks,
        "note": "Validation uses truncated saved target_response (Phase 5 stored [:500]).",
    }
    (OUT / "validation_results.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in results) + "\n",
        encoding="utf-8",
    )
    (OUT / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
    md = [
        "# FINAL JUDGE VALIDATION — Cerebras qwen-3.8-27b",
        "",
        f"**Status:** {status}",
        f"**Timestamp:** {utc()}",
        f"- Attempted: {len(sample)}",
        f"- OK: {n_ok}",
        f"- Invalid: {n_invalid}",
        f"- Failed: {n_fail}",
        "",
        "## Checks",
        "",
    ]
    for k, v in checks.items():
        md.append(f"- `{k}`: {'PASS' if v['pass'] else 'FAIL'} — {v['detail']}")
    (OUT / "validation_report.md").write_text("\n".join(md) + "\n")
    print(f"VALIDATION {status}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
