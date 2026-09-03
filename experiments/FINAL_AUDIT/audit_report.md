# FINAL AUDIT — ADAPTI-GUARD

**Date:** 2026-09-03  
**Scope:** Implementation vs frozen dataset vs experimental protocol vs statistical plan vs paper claims.

This audit does not invent experimental numbers. Phase 5 ASR from Gemini is **not** publication evidence.

## Frozen dataset

| Item | Specified | Role |
|------|-----------|------|
| Path | `datasets/frozen/eval_v1/dataset.jsonl` | Primary eval |
| SHA-256 | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` | Integrity |
| Attack stream SHA-256 | `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` | Integrity |
| Size | 770 attacks, 7×110 categories | Attack-only |

**Do not claim utility, benign success, or FPR from this dataset.**

## Phase 5 constrained experiment (completed Target calls)

- Path: `experiments/PHASE5_CONSTRAINED/raw_results.jsonl`
- Design: 3 × 2 × 50 = **300 Groq Target observations**
- Target: Groq `openai/gpt-oss-120b` (`groq_target`)
- Policies: **B0 vs B6 only**
- Seed: 42
- Gemini judge: **2 valid, 298 failed (429 / circuit)**

Failed Gemini rows must **not** be converted to ASR=0 / Defense=1.

## Policy mapping (implementation)

`get_defense_fn` in `src/adapti_guard/experiments/defense_baselines.py`:

- **B0** = no intervention (A0)
- **B1 / B2** exist; unused in Phase 5
- **B3 and B6** = same factory `make_b3_adaptive()` — **B6 aliases B3**
- **B4 / B5 / B7** not in the real-LLM Phase 5 matrix

## Intervention costs (unchanged)

L0/A0=0.00, L1/A1=0.10, L2/A2=0.25, L3/A3=0.50

Observed in Phase 5 actions: B0 always A0; B6 always A1 (no blocks in the 150 B6 episodes).

## Inconsistencies

1. **BLOCKING (mitigated by rejudge):** Gemini ASR invalid.
2. **HIGH:** Target text truncated to 500 chars.
3. **HIGH:** Prompts missing from raw jsonl (join frozen IDs).
4. **HIGH:** `model_a/b/c` are labels over the **same** Groq model, not three targets.
5. **MEDIUM:** Ablation yaml EXP-006 wants 500 attack + 200 benign real LLM — **not executed**; existing EXP006 metrics are `LEGACY_SIMULATION_ONLY`.
6. **MEDIUM:** Bootstrap default 5000 in code/docs; final analysis will use **10000** and document the change.
7. **MEDIUM:** Reward not computable without utility.

## What this completion protocol will do

1. Reuse 300 Groq responses (no new Target calls).
2. Validate Cerebras `qwen-3.8-27b` judge (≥10 cases).
3. Rejudge all 300 only if validation passes; failures remain `JUDGE_FAILED`.
4. Metrics on **valid** judgments only; ICS from recorded actions.
5. Publication stats: bootstrap B=10000, McNemar paired B0 vs B6, Holm α=0.05 — **not applied to ASR** until valid judgments exist.
6. Ablations: **NOT_EXECUTED** for real-LLM publication claims.

## Completion-pass outcome (2026-09-03)

Cerebras chat completions returned **HTTP 402**. Validation failed (10/10). Mass rejudge was not run. ASR is **NOT COMPUTABLE**. Mean ICS from actions: B0=0.00, B6=0.10.

