"""Load .env before any experiment that needs API credentials."""

from __future__ import annotations

from pathlib import Path


def load_project_env() -> bool:
    try:
        from src.adapti_guard.experiments.dns_workaround import apply_public_dns_fallback

        apply_public_dns_fallback()
    except Exception:
        pass
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    # env_loader.py lives at src/adapti_guard/experiments/ → repo root is parents[3]
    root = Path(__file__).resolve().parents[3]
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        _strip_api_keys()
        return True
    # Fallback: cwd .env (e.g. running from repo root without package-relative path)
    load_dotenv()
    _strip_api_keys()
    return False


def _strip_api_keys() -> None:
    import os

    for name in (
        "CEREBRAS_API_KEY",
        "GROQ_API_KEY",
        "GEMINI_API_KEY",
        "OPENROUTER_API_KEY",
        "GOOGLE_API_KEY",
    ):
        val = os.getenv(name)
        if val is not None:
            os.environ[name] = val.strip()


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


def validate_gemini_key() -> tuple[bool, str]:
    import os

    load_project_env()
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return False, "GEMINI_API_KEY not set"
    if len(key) < 20:
        return False, "GEMINI_API_KEY too short (invalid)"
    return True, "ok"


def validate_groq_key() -> tuple[bool, str]:
    import os

    load_project_env()
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return False, "GROQ_API_KEY not set"
    if len(key) < 20:
        return False, "GROQ_API_KEY too short (invalid)"
    return True, "ok"


def validate_cerebras_key() -> tuple[bool, str]:
    import os

    load_project_env()
    key = os.getenv("CEREBRAS_API_KEY", "").strip()
    if not key:
        return False, "CEREBRAS_API_KEY not set"
    if len(key) < 20:
        return False, "CEREBRAS_API_KEY too short (invalid)"
    return True, "ok"
