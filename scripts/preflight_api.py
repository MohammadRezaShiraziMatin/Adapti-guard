#!/usr/bin/env python3
"""Preflight check for real LLM experiments."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import validate_openrouter_key


def main() -> int:
    ok, reason = validate_openrouter_key()
    if ok:
        print("PASS: OPENROUTER_API_KEY format valid")
        return 0
    print(f"BLOCKED: {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
