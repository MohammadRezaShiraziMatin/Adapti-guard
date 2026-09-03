# ADAPTI-GUARD — Final Completion Status

**Date:** 2026-09-02  
**Git commit (workspace):** `35833a64b35a98d596d729c3fa7687e3228381ca`

---

## Executive summary

| Milestone | Status |
|-----------|--------|
| Frozen dataset (eval_v1) | **COMPLETE** |
| Infrastructure (EXP-004 pipeline) | **COMPLETE** |
| Phase 2.7 pilot (n=15, model_a) | **COMPLETE** (infrastructure only) |
| OpenRouter smoke test (3 calls) | **PASSED** (earlier session; key since invalid) |
| **EXP-004 final evaluation (n=150 × 3 models)** | **BLOCKED — HTTP 401** |
| Statistical analysis (final) | **NOT RUN** |
| Final tables/figures (final) | **NOT GENERATED** |
| Manuscript with final claims | **BLOCKED** |

**Project completion for PhD evidence:** **~75% infrastructure / 0% final empirical claims**

---

## Preflight checklist (2026-09-02)

| Check | Result |
|-------|--------|
| Dataset exists | PASS — 770 records, 7×110 categories |
| SHA-256 | PASS — `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` |
| Unique IDs | PASS — 770/770 |
| Attack-only | PASS — 0 benign in frozen loader |
| seed=42 deterministic n=150 | PASS |
| `publication_mode` / `cache_enabled=false` | PASS (code path) |
| OPENROUTER_API_KEY format | PASS |
| **OpenRouter API authentication** | **FAIL — HTTP 401 User not found** |
| **Target model callable** | **FAIL** |
| **Judge callable** | **FAIL** |
| Sufficient credits | NOT VERIFIED (blocked at auth) |

**EXP-004 was not started** after this preflight (prior partial run is invalid).

---

## Evidence inventory (honest labels)

### A. PILOT ONLY — NOT FINAL EVIDENCE

**Path:** `experiments/PHASE2_7_PILOT/`

- n=15, `openai/gpt-4o-mini`, B0 vs B6
- B0 ASR = 2/15 = 0.1333
- B6 ASR = 2/15 = 0.1333
- 0 judge failures in successful pilot rerun
- **Cannot support hypothesis test** (underpowered; no multi-model)

Pilot `metrics.json` reports `utility=0`, `fpr=0`, `balanced_accuracy=0.433` — **misleading on attack-only set**; treat ASR/defense_rate only.

### B. INVALID PARTIAL — DO NOT CITE

**Path:** `experiments/EXP-004/model_a/B0/B0_predictions.jsonl` (4 rows)

- All judge failures
- No metrics file
- Resume validation: FAIL

### C. FINAL EXP-004 — MISSING

Required for manuscript claims:

- 150 paired samples × 3 models × 2 baselines
- McNemar + Holm across models
- Category breakdowns

---

## Statistical design (ready, not executed)

- Paired B0/B6 on identical sample IDs per model
- Exact McNemar (`paired_baseline_comparison`)
- Bootstrap 95% CI on ASR
- Holm correction across 3 model comparisons
- Attack-only: FPR/utility/balanced accuracy → N/A in analysis code

---

## Cost estimate (for planning)

See `experiments/EXP-004/COST_ANALYSIS.md`

- n=150: ~$5–11 USD at OpenRouter list prices (judge-dominated)
- Requires working API key + credits

---

## Manuscript status

`docs/MANUSCRIPT_DRAFT.md` remains **evidence-gated**.

Sections requiring EXP-004:

- Abstract results
- Multi-model ASR table
- McNemar significance
- B6 vs B0 claims

Permitted now:

- Method description
- Threat model
- Dataset description (benchmark_q1 + frozen eval_v1)
- Pilot labeled **PILOT ONLY**

---

## Reproducibility audit

| Item | Status |
|------|--------|
| Frozen dataset hash pinned in loader | PASS |
| Canonical entrypoint | `experiments/EXP-004/run.py` |
| Config persisted | `config.json` on run start |
| Provenance schema | v1.2 with pilot aliases |
| Resume validation | PASS (code); partial artifacts FAIL validation |
| Offline tests | 101 passed, 2 skipped |

---

## Unblock procedure

1. Fix `OPENROUTER_API_KEY` (new key from OpenRouter dashboard).
2. Confirm probe: target + judge return HTTP 200.
3. Delete `experiments/EXP-004/model_a/` (invalid partial).
4. Run `python experiments/EXP-004/run.py`.
5. Run `python experiments/EXP-004/analyze.py`.
6. Regenerate manuscript tables from `statistical_analysis.json` only.

---

## Scientific rules compliance

- No fabricated EXP-004 results
- No invented p-values
- Pilot not presented as final
- Attack-only limitations documented
- No SOTA claims
