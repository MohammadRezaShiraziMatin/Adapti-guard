"""Incomplete OpenRouter response policy (Amendment 8 — documented behavior, not silent)."""
from __future__ import annotations

# Harness retry applies only to rate limits (HTTP 429 or JSON error code 429).
HARNESS_RETRY_PROVIDER_ERROR_CODES: frozenset[int | str] = frozenset({429, "429"})

# Gateway/upstream JSON error codes: one provider_error row, INVALID_PROVIDER_ERROR, no harness retry.
PROVIDER_ERROR_NO_HARNESS_RETRY_CODES: frozenset[int | str] = frozenset(
    {500, 502, 503, 504, "500", "502", "503", "504"}
)

ASSUMPTION_429_UNBILLED_VERBATIM = (
    "Assumption: the provider does not bill rate-limited (429) requests; "
    "this assumption has no independent confirmation from the provider."
)
