"""Canonical evaluation mode labels for ADAPTI-GUARD scientific reporting."""

from __future__ import annotations

# Primary metric path: independent LLM judge on real target responses.
REAL_LLM_JUDGE = "real_llm_judge"

# Legacy paths — NOT valid for publication ASR/utility claims.
LEGACY_SIMULATION_ONLY = "LEGACY_SIMULATION_ONLY"

# Deprecated aliases (migrate artifacts to LEGACY_SIMULATION_ONLY).
LEGACY_ALIASES = frozenset({
    "HARMONIZED_SIMULATION",
    "DETECTOR_SIMULATION",
    "defense_simulation",
    "LEGACY_SIMULATION_METRIC",
    "heuristic",
})

PUBLICATION_MODES = frozenset({REAL_LLM_JUDGE})


def is_publication_mode(mode: str) -> bool:
    return mode == REAL_LLM_JUDGE


def normalize_legacy_mode(mode: str) -> str:
    if mode in LEGACY_ALIASES or "simulation" in mode.lower():
        return LEGACY_SIMULATION_ONLY
    return mode
