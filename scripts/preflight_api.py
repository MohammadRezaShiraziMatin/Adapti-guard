#!/usr/bin/env python3
"""Preflight check for real LLM experiments (OpenRouter and/or Gemini)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import (
    load_project_env,
    validate_gemini_key,
    validate_openrouter_key,
)


def preflight_gemini() -> dict:
    load_project_env()
    ok, reason = validate_gemini_key()
    record = {
        "provider": "google",
        "model": "gemini-3.6-flash",
        "api": "interactions",
        "key_valid": ok,
        "status": "BLOCKED",
        "error": None,
    }
    if not ok:
        record["error"] = reason
        return record
    try:
        from src.adapti_guard.evaluation.target_model import (
            GeminiTargetModel,
            GenerationRequest,
        )

        model = GeminiTargetModel("gemini-3.6-flash", cache=None)
        result = model.generate(
            GenerationRequest(prompt="Reply exactly: GEMINI_OK", system_prompt="")
        )
        record["latency_ms"] = result.latency_ms
        record["http_status"] = (result.raw or {}).get("http_status")
        record["request_id"] = (result.raw or {}).get("id")
        record["error"] = result.error
        if result.error:
            record["status"] = "BLOCKED"
        elif result.text and result.text.strip():
            record["status"] = "VALID"
            record["response_preview"] = result.text[:80]
        else:
            record["status"] = "BLOCKED"
            record["error"] = "empty_response"
    except Exception as exc:
        record["status"] = "BLOCKED"
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="API preflight for real-LLM experiments")
    parser.add_argument(
        "--provider",
        choices=("auto", "openrouter", "gemini", "google"),
        default="auto",
    )
    args = parser.parse_args()
    load_project_env()

    if args.provider in ("gemini", "google"):
        result = preflight_gemini()
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "VALID" else 1

    if args.provider == "openrouter":
        ok, reason = validate_openrouter_key()
        if ok:
            print("PASS: OPENROUTER_API_KEY format valid")
            return 0
        print(f"BLOCKED: {reason}")
        return 1

    # auto: try Gemini live call if key present, else OpenRouter format check
    gemini_ok, _ = validate_gemini_key()
    if gemini_ok:
        result = preflight_gemini()
        print(json.dumps(result, indent=2))
        if result["status"] == "VALID":
            return 0
        # Fall through to OpenRouter format check for diagnostics
        print("Gemini preflight BLOCKED; checking OpenRouter key format...", file=sys.stderr)

    ok, reason = validate_openrouter_key()
    if ok:
        print("PASS: OPENROUTER_API_KEY format valid")
        return 0
    print(f"BLOCKED: {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
