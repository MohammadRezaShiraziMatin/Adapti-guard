#!/usr/bin/env python3
"""Controlled OpenRouter smoke test — max 4 API calls, no retries.

NOT publication evidence. Does NOT run EXP-004.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import load_project_env, validate_openrouter_key

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TARGET_MODEL = "openai/gpt-4o-mini"
JUDGE_MODEL = "anthropic/claude-sonnet-4"
FROZEN_HASH = "27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24"


def _git_commit() -> str:
    import subprocess

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def _classify_http(status: int | None, error_type: str | None) -> str:
    if status == 401:
        return "authentication"
    if status == 402:
        return "insufficient credit / payment"
    if status == 403:
        return "access / permission"
    if status == 404:
        return "model / endpoint issue"
    if status == 408:
        return "timeout"
    if status == 429:
        return "rate limit"
    if status is not None and status >= 500:
        return "provider/server error"
    if error_type and "timeout" in error_type.lower():
        return "timeout"
    if error_type and "connect" in error_type.lower():
        return "network"
    return ""


def _extract_cost(data: dict[str, Any], headers: httpx.Headers) -> float | None:
    usage = data.get("usage") or {}
    for key in ("cost", "total_cost", "cost_usd"):
        if key in usage and usage[key] is not None:
            return float(usage[key])
        if key in data and data[key] is not None:
            return float(data[key])
    for header in (
        "x-openrouter-cost-usd",
        "x-openrouter-cost",
        "openrouter-cost",
    ):
        if header in headers:
            try:
                return float(headers[header])
            except (TypeError, ValueError):
                pass
    return None


def one_call(
    call_id: str,
    model: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 64,
) -> dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/adapti-guard/smoke-test",
        "X-Title": "ADAPTI-GUARD OpenRouter Smoke Test",
    }
    record: dict[str, Any] = {
        "call_id": call_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "http_status": None,
        "success": False,
        "response": None,
        "latency_ms": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "cost_usd": None,
        "cost_source": None,
        "request_id": None,
        "error_type": None,
        "error_message": None,
        "error_class": None,
    }

    start = time.perf_counter()
    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(OPENROUTER_URL, json=payload, headers=headers)
        record["latency_ms"] = round((time.perf_counter() - start) * 1000.0, 2)
        record["http_status"] = resp.status_code

        if resp.status_code >= 400:
            record["error_type"] = _classify_http(resp.status_code, None)
            try:
                err_body = resp.json()
                record["error_message"] = json.dumps(err_body)[:2000]
            except Exception:
                record["error_message"] = resp.text[:2000]
            return record

        data = resp.json()
        record["success"] = True
        record["request_id"] = data.get("id")
        choice = (data.get("choices") or [{}])[0]
        record["response"] = (choice.get("message") or {}).get("content", "")[:2000]

        usage = data.get("usage") or {}
        record["prompt_tokens"] = usage.get("prompt_tokens")
        record["completion_tokens"] = usage.get("completion_tokens")
        record["total_tokens"] = usage.get("total_tokens")
        cost = _extract_cost(data, resp.headers)
        if cost is not None:
            record["cost_usd"] = cost
            record["cost_source"] = "response"
        else:
            record["cost_source"] = "cost_unavailable_from_response"
        return record

    except httpx.TimeoutException as exc:
        record["latency_ms"] = round((time.perf_counter() - start) * 1000.0, 2)
        record["error_type"] = "timeout"
        record["error_class"] = type(exc).__name__
        record["error_message"] = str(exc)
        return record
    except httpx.RequestError as exc:
        record["latency_ms"] = round((time.perf_counter() - start) * 1000.0, 2)
        record["error_type"] = "network"
        record["error_class"] = type(exc).__name__
        record["error_message"] = str(exc)
        return record


def _aggregate(calls: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [c["latency_ms"] for c in calls if c.get("latency_ms") is not None]
    latencies_sorted = sorted(latencies)
    p95 = latencies_sorted[int(0.95 * (len(latencies_sorted) - 1))] if latencies_sorted else None

    def _sum(field: str) -> int | None:
        vals = [c.get(field) for c in calls if c.get(field) is not None]
        return sum(vals) if vals else None

    costs = [c["cost_usd"] for c in calls if c.get("cost_usd") is not None]
    per_model: dict[str, Any] = {}
    for c in calls:
        m = c["model"]
        bucket = per_model.setdefault(
            m,
            {
                "model": m,
                "requests": 0,
                "successful": 0,
                "tokens": 0,
                "cost_usd": 0.0,
                "cost_available": True,
                "latencies_ms": [],
                "statuses": [],
            },
        )
        bucket["requests"] += 1
        if c.get("success"):
            bucket["successful"] += 1
        if c.get("total_tokens") is not None:
            bucket["tokens"] += int(c["total_tokens"])
        if c.get("cost_usd") is not None:
            bucket["cost_usd"] += float(c["cost_usd"])
        elif c.get("cost_source") == "cost_unavailable_from_response":
            bucket["cost_available"] = False
        if c.get("latency_ms") is not None:
            bucket["latencies_ms"].append(c["latency_ms"])
        bucket["statuses"].append(c.get("http_status"))

    for bucket in per_model.values():
        lats = bucket.pop("latencies_ms")
        bucket["mean_latency_ms"] = round(sum(lats) / len(lats), 2) if lats else None
        bucket["cost_usd"] = round(bucket["cost_usd"], 8) if bucket["cost_available"] else None
        if not bucket["cost_available"] and bucket["cost_usd"] == 0.0:
            bucket["cost_note"] = "cost_unavailable_from_response"

    return {
        "total_requests": len(calls),
        "successful_requests": sum(1 for c in calls if c.get("success")),
        "failed_requests": sum(1 for c in calls if not c.get("success")),
        "total_prompt_tokens": _sum("prompt_tokens"),
        "total_completion_tokens": _sum("completion_tokens"),
        "total_tokens": _sum("total_tokens"),
        "total_cost_usd": round(sum(costs), 8) if costs else None,
        "cost_note": None if costs else "cost_unavailable_from_response",
        "mean_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
        "p95_latency_ms": p95,
        "per_model": list(per_model.values()),
    }


def _verdict(calls: list[dict[str, Any]], key_valid: bool) -> tuple[str, str, list[str]]:
    errors: list[str] = []
    if not key_valid:
        return "BLOCKED", "BLOCKED — OPENROUTER_API_KEY invalid", errors

    for c in calls:
        if c.get("http_status") == 402:
            return (
                "BLOCKED",
                "BLOCKED — HTTP 402 Payment Required",
                [c.get("error_message") or "insufficient credit"],
            )
        if c.get("http_status") == 401:
            return (
                "BLOCKED",
                "BLOCKED — OPENROUTER_API_KEY invalid",
                [c.get("error_message") or "authentication failed"],
            )

    call_map = {c["call_id"]: c for c in calls}
    target1 = call_map.get("call_1_target_smoke")
    judge = call_map.get("call_2_judge_smoke")
    target2 = call_map.get("call_3_target_compat")

    if not target1 or not target1.get("success"):
        errors.append("Call 1 target failed")
    if not judge or not judge.get("success"):
        errors.append("Call 2 primary judge failed")
        if judge and not judge.get("success"):
            return (
                "BLOCKED",
                "BLOCKED — Primary Judge unavailable",
                errors,
            )
    if not target2 or not target2.get("success"):
        errors.append("Call 3 target compatibility failed")

    if errors:
        detail = errors[0]
        if "402" in detail:
            return "BLOCKED", "BLOCKED — HTTP 402 Payment Required", errors
        return "BLOCKED", f"BLOCKED — {detail}", errors

    return "READY_FOR_PILOT", "READY_FOR_PILOT", []


def main() -> int:
    load_project_env()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    key_ok, key_reason = validate_openrouter_key()
    log(f"Phase 1: key validation = {key_ok} ({key_reason})")

    import hashlib

    frozen_path = ROOT / "datasets/frozen/eval_v1/dataset.jsonl"
    frozen_hash = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    log(f"Frozen dataset hash: {frozen_hash}")

    calls: list[dict[str, Any]] = []
    if not key_ok:
        results = {
            "environment": {"python": sys.version, "cwd": str(ROOT)},
            "git_commit": _git_commit(),
            "key_validation": {"valid": False, "reason": key_reason},
            "calls": [],
            "aggregate": _aggregate([]),
            "frozen_dataset_sha256": frozen_hash,
            "exp004_executed": False,
        }
    else:
        log("Call 1: target openai/gpt-4o-mini")
        c1 = one_call(
            "call_1_target_smoke",
            TARGET_MODEL,
            [{"role": "user", "content": "Return exactly: SMOKE_TEST_OK"}],
            max_tokens=16,
        )
        calls.append(c1)
        log(json.dumps(c1, indent=2))
        if c1.get("http_status") == 402:
            log("STOP: HTTP 402 on call 1")
        else:
            log("Call 2: judge anthropic/claude-sonnet-4")
            c2 = one_call(
                "call_2_judge_smoke",
                JUDGE_MODEL,
                [
                    {
                        "role": "user",
                        "content": (
                            "Classify this response as PASS or FAIL.\n\n"
                            "Response:\nSMOKE_TEST_OK\n\n"
                            "Return exactly one label: PASS or FAIL."
                        ),
                    }
                ],
                max_tokens=16,
            )
            calls.append(c2)
            log(json.dumps(c2, indent=2))
            if c2.get("http_status") == 402:
                log("STOP: HTTP 402 on call 2")
            else:
                log("Call 3: target compatibility")
                c3 = one_call(
                    "call_3_target_compat",
                    TARGET_MODEL,
                    [
                        {
                            "role": "system",
                            "content": "You are an evaluation target.",
                        },
                        {
                            "role": "user",
                            "content": (
                                "Respond briefly to the following test input:\n\n"
                                "TEST_INPUT: Explain what 2+2 equals."
                            ),
                        },
                    ],
                    max_tokens=64,
                )
                calls.append(c3)
                log(json.dumps(c3, indent=2))
                if c3.get("http_status") == 402:
                    log("STOP: HTTP 402 on call 3")

        # Call 4 only if prior calls lack sufficient info
        need_call4 = False
        if calls and any(not c.get("success") for c in calls):
            successes = [c for c in calls if c.get("success")]
            if not successes:
                need_call4 = True
        if need_call4 and len(calls) < 4 and all(c.get("http_status") != 402 for c in calls):
            log("Call 4: skipped — failures are auth/credit blocking, not missing metadata")

    aggregate = _aggregate(calls)
    verdict, verdict_detail, verdict_errors = _verdict(calls, key_ok)

    credit_status = "unknown"
    if any(c.get("http_status") == 402 for c in calls):
        credit_status = "insufficient (HTTP 402 observed)"
    elif calls and all(c.get("success") for c in calls):
        credit_status = "sufficient for smoke test (402 not observed; full EXP-004 budget NOT verified)"
    elif not key_ok:
        credit_status = "not tested (invalid key)"

    results = {
        "experiment": "OPENROUTER_SMOKE_TEST",
        "purpose": "API access and cost validation only — NOT publication evidence",
        "exp004_executed": False,
        "environment": {
            "python": sys.version,
            "cwd": str(ROOT),
            "openrouter_url": OPENROUTER_URL,
        },
        "git_commit": _git_commit(),
        "models_tested": sorted({c["model"] for c in calls}) if calls else [TARGET_MODEL, JUDGE_MODEL],
        "key_validation": {"valid": key_ok, "reason": key_reason},
        "frozen_dataset_sha256": frozen_hash,
        "frozen_dataset_unchanged": frozen_hash == FROZEN_HASH,
        "calls": calls,
        "aggregate": aggregate,
        "authentication_status": "pass" if key_ok and not any(c.get("http_status") == 401 for c in calls) else "fail",
        "credit_status": credit_status,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "verdict_errors": verdict_errors,
        "exp004_readiness": (
            "READY (repository preflight passed; proceed Smoke→Pilot→Review before EXP-004)"
            if verdict == "READY_FOR_PILOT"
            else "BLOCKED until API access/credit issues resolved"
        ),
    }

    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (OUT_DIR / "run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    report = _build_report(results)
    (OUT_DIR / "REPORT.md").write_text(report, encoding="utf-8")
    log(f"\nVERDICT: {verdict_detail}")
    return 0 if verdict == "READY_FOR_PILOT" else 1


def _build_report(r: dict[str, Any]) -> str:
    agg = r["aggregate"]
    lines = [
        "# OpenRouter Controlled API Smoke Test",
        "",
        "**NOT publication evidence.** EXP-004 was NOT executed.",
        "",
        f"**Verdict:** `{r['verdict_detail']}`",
        "",
        "## 1. Environment",
        f"- Python: `{r['environment']['python']}`",
        f"- CWD: `{r['environment']['cwd']}`",
        "",
        "## 2. Git commit",
        f"- `{r['git_commit']}`",
        "",
        "## 3. Models tested",
    ]
    for m in r.get("models_tested", []):
        lines.append(f"- `{m}`")
    lines += [
        "",
        "## 4. Number of API calls",
        f"- **{agg['total_requests']}** (max allowed: 4)",
        "",
        "## 5. HTTP results",
    ]
    for c in r.get("calls", []):
        lines.append(
            f"- `{c['call_id']}` → HTTP **{c.get('http_status')}** "
            f"success={c.get('success')} model=`{c.get('model')}`"
        )
    lines += [
        "",
        "## 6. Token usage",
        f"- prompt: {agg.get('total_prompt_tokens')}",
        f"- completion: {agg.get('total_completion_tokens')}",
        f"- total: {agg.get('total_tokens')}",
        "",
        "## 7. Cost",
        f"- total_cost_usd: {agg.get('total_cost_usd')}",
        f"- note: {agg.get('cost_note') or 'from response where available'}",
        "",
        "## 8. Latency",
        f"- mean_latency_ms: {agg.get('mean_latency_ms')}",
        f"- p95_latency_ms: {agg.get('p95_latency_ms')}",
        "",
        "## 9. Authentication status",
        f"- {r.get('authentication_status')}",
        "",
        "## 10. Credit status",
        f"- {r.get('credit_status')}",
        "",
        "## 11. Model availability",
    ]
    for c in r.get("calls", []):
        if "target" in c["call_id"]:
            lines.append(
                f"- Target `{c['model']}`: "
                f"{'OK' if c.get('success') else 'FAIL'} (HTTP {c.get('http_status')})"
            )
    lines += ["", "## 12. Judge availability"]
    for c in r.get("calls", []):
        if "judge" in c["call_id"]:
            lines.append(
                f"- Judge `{c['model']}`: "
                f"{'OK' if c.get('success') else 'FAIL'} (HTTP {c.get('http_status')})"
            )
    lines += ["", "## 13. Errors"]
    errs = [c for c in r.get("calls", []) if not c.get("success")]
    if errs:
        for c in errs:
            lines.append(f"- `{c['call_id']}`: {c.get('error_type')} — {c.get('error_message')}")
    else:
        lines.append("- none")
    lines += [
        "",
        "## 14. EXP-004 readiness",
        f"- {r.get('exp004_readiness')}",
        "",
        "## Per-call detail",
        "",
        "```json",
        json.dumps(r.get("calls", []), indent=2),
        "```",
        "",
        f"Frozen dataset SHA-256: `{r.get('frozen_dataset_sha256')}` "
        f"(unchanged={r.get('frozen_dataset_unchanged')})",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
