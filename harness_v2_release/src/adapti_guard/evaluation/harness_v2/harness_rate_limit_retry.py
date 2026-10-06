"""Harness 429 retry parameters (Amendment 8 §2.2)."""
from __future__ import annotations

HARNESS_RATE_LIMIT_MAX_RETRIES = 2
HARNESS_RATE_LIMIT_BACKOFF_S = (10.0, 30.0)
