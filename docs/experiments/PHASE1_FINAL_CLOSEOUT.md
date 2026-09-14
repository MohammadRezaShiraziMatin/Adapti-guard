# Phase 1 final scientific closeout

**Decision candidate:** see gate table.  
**LLM/API calls:** 0  
**Phase 2 / Multi-Turn:** out of scope (not implemented here).

Official VNEXT confirmation remains **FAIL** (pack `523c8818…`, MSID 0.20, `qualified_win=false`).

---

## What closed

| Gate | Result | Evidence |
| --- | --- | --- |
| 1A Independent TEST | PASS | `datasets/frozen/phase1_holdout_v1` SHA `c42e9797…`; DEV/VAL = Layer A train/dev; VNEXT not TEST |
| 1B Detector eval + lock | PASS | `configs/phase1_detector_lock.json`; offline metrics via `scripts/run_phase1_independent_offline_eval.py`; `56/61` stays diagnostic-only |
| 1C Risk/policy label-blind | PASS | Existing `EpisodeInput`/`RiskEngineCore` gold rejection + `tests/test_phase1_core_pipeline.py` |
| 1D A2/A3 enforcement | PASS | Existing Phase1 pipeline tests (real mock-tool deny/block) |
| 1E Fair baselines | PASS | B0 / STATIC-A1 / STATIC-A2 / STATIC-A3 / PHASE1-CORE factories (paired protocol in `PHASE1_STATISTICAL_PLAN.md`) |
| 1F Security/utility/cost/stats | PASS | `PHASE1_STATISTICAL_PLAN.md` locked pre-live |
| 1G Live TEST | **NOT RUN** | Awaiting human approval |
| 1H Closeout | PASS (docs) | This file + lock + holdout + metrics artifact |

---

## Pack-fit

Prior **HIGH** risk (Phase1 evidence iterated on VNEXT diagnostics) is **controlled** by retiring VNEXT as Phase1 confirmatory TEST and freezing an independent holdout. Residual generalization risk remains until live TEST under the locked protocol.

## Independent offline metrics (not ASR; locked detector)

Source: `docs/experiments/artifacts/phase1_independent_offline_metrics.json`

| Split | P | R | F1 | FPR | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| DEV (Layer A train) | 1.00 | 1.00 | 1.00 | 0.00 | text-only pack |
| VAL (Layer A dev) | 0.95 | 1.00 | 0.98 | 0.05 | text-only pack |
| **TEST holdout** | 0.75 | 0.45 | 0.56 | 0.15 | 11/20 attack misses; 3 benign A2 on `retrieve_document`+`doc_id=` |
| Secondary Layer A TEST | 0.83 | 0.73 | 0.77 | 0.15 | text-only; no tools |

Blind-spot tags on holdout FN include social-engineering and indirect/json-style items. **No detector retune after TEST.** `56/61` VNEXT figure remains diagnostic-only.

---

## Non-claims

Not ASR. Not qualified win. Not SOTA/production/“solves prompt injection.” Does not reverse VNEXT FAIL.

---

## Next

`READY_FOR_HUMAN_APPROVAL — no live API executed.`


## Scientific hardening follow-on

See `PHASE1_SCIENTIFIC_GATE.md` (SH1–SH8). Confirmatory TEST superseded for N by `phase1_confirm_v1` (`c789811a…`); holdout remains pilot.
