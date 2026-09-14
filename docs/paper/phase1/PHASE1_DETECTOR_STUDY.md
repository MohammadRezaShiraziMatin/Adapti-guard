# Phase 1 Detector Study (Independent of Defense)

**ID:** `PHASE1-DET-STUDY-0.1`  
**Date (UTC):** 2026-09-14  
**Lock:** `configs/phase1_detector_lock.json` (`evidence_phase1.0`)  
**Live LLM/API:** 0

Detector metrics ≠ defense effectiveness. Primary defense endpoint remains harmful-action success.

---

## Splits

| Role | Pack | Use |
| --- | --- | --- |
| DEV | Layer A train | Reference only |
| VAL | Layer A dev | Reference only |
| PILOT | `phase1_holdout_v1` | Already measured; not confirmatory N |
| **CONFIRM TEST** | `phase1_confirm_v1` | Locked; **no tuning** |

---

## Metrics (pre-registered)

Precision, recall, F1, FPR; Wilson intervals; per-family on attacks; hard-negative FP count; failure tags (obfuscation / social / indirect / delayed).

Script: `scripts/run_phase1_independent_offline_eval.py` (extended to confirm pack).

---

## Locked offline metrics on CONFIRM TEST (no tuning)

Source: `docs/experiments/artifacts/phase1_confirm_detector_metrics.json`  
Pack SHA: `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01`

| Metric | Value |
| --- | ---: |
| Precision | 0.809 |
| Recall | 0.902 |
| F1 | 0.853 |
| FPR | 0.213 |
| TP/FP/TN/FN | 55 / 13 / 48 / 6 |

These are **detector** metrics only. They are **not** defense ASR and **must not** trigger rule edits.

## Lock rule

No detector/threshold/policy edits justified by `phase1_confirm_v1` or Layer A TEST outcomes.  
VNEXT `56/61` remains diagnostic-only.
