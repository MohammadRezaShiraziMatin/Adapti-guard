# Phase 1 independent holdout v1.0

**Role:** LOCKED INDEPENDENT TEST for Phase-1 final hardening.

**SHA-256 (`dataset.jsonl`):** `c42e979724cdb29d353366d0a77f5bccb28ad2cb337e775592a72b516da7b1bd`

**N:** 40 (20 attack / 20 benign; 7 hard negatives). Tool-bearing + text-only.

**DEV/VAL (reuse, unchanged):** Layer A train/dev (`6a6d0423…` / `659ad5cf…`).

**Must not influence:** detector rules, thresholds, policy, attack selection after freeze.

**Not:** VNEXT confirmation pack. Not Layer A TEST. Official VNEXT FAIL unchanged.

**Generation:** human-authored synthetic, no LLM, contamination-screened against VNEXT and Layer A prompt/context strings.
