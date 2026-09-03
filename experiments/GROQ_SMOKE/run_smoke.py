#!/usr/bin/env python3
"""Exactly ONE real Groq API request — no dataset loop.

Usage:
    .venv/bin/python experiments/GROQ_SMOKE/run_smoke.py

Requires GROQ_API_KEY in .env. Never prints the key.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import load_project_env, validate_groq_key

load_project_env()

from src.adapti_guard.evaluation.experiment_logging import git_commit, redact_env
from src.adapti_guard.evaluation.target_model import GenerationRequest, build_target_model


def main() -> int:
    out_dir = ROOT / "experiments" / "GROQ_SMOKE"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / f"smoke_{stamp}.json"

    ok, reason = validate_groq_key()
    record: dict = {
        "experiment": "GROQ_SMOKE",
        "purpose": "Single real request — NOT publication evidence",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "provider": "groq",
        "model": "openai/gpt-oss-120b",
        "target_config_key": "groq_target",
        "planned_requests": 1,
        "key_valid": ok,
        "key_reason": reason,
        "env_redacted": redact_env(),
        "status": "BLOCKED",
    }
    if not ok:
        record["error"] = reason
        out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "BLOCKED", "reason": reason, "path": str(out_path)}, indent=2))
        return 1

    model = build_target_model("groq_target", cache_enabled=False)
    result = model.generate(
        GenerationRequest(
            prompt="Reply exactly: GROQ_OK",
            system_prompt="You are a concise test assistant.",
        )
    )
    record.update(
        {
            "status": "VALID" if result.error is None and (result.text or "").strip() else "BLOCKED",
            "latency_ms": result.latency_ms,
            "usage": result.usage,
            "cache_hit": result.cache_hit,
            "error": result.error,
            "finish_reason": (result.raw or {}).get("finish_reason"),
            "response_preview": (result.text or "")[:200],
            "raw_meta": {
                k: (result.raw or {}).get(k)
                for k in ("id", "provider", "http_status", "reasoning_effort", "model")
            },
            "success": result.error is None and bool((result.text or "").strip()),
        }
    )
    if "GROQ_OK" in (result.text or "").replace(" ", ""):
        record["status"] = "VALID"
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    (out_dir / "latest_smoke.json").write_text(
        json.dumps({"path": str(out_path), "status": record["status"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": record["status"],
                "latency_ms": record.get("latency_ms"),
                "usage": record.get("usage"),
                "path": str(out_path),
                "error": record.get("error"),
            },
            indent=2,
        )
    )
    return 0 if record["status"] == "VALID" else 1


if __name__ == "__main__":
    raise SystemExit(main())
