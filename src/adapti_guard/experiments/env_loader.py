"""Load .env before any experiment that needs OPENROUTER_API_KEY."""

from __future__ import annotations

from pathlib import Path


def load_project_env() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    root = Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        return True
    load_dotenv()
    return False


def validate_openrouter_key() -> tuple[bool, str]:
    import os

    load_project_env()
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key:
        return False, "OPENROUTER_API_KEY not set"
    if len(key) < 20:
        return False, "OPENROUTER_API_KEY too short (invalid)"
    if not key.startswith("sk-or-"):
        return False, (
            "OPENROUTER_API_KEY format invalid (expected sk-or-v1-... prefix). "
            "Get a key at https://openrouter.ai/keys"
        )
    return True, "ok"
