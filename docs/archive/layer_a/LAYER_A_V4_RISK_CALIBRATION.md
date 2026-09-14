# Layer A v4 risk calibration (Phase 4)

**Status:** VALID diagnostic. No TEST band tuning.  
**Modules:** `RiskEngine` (historical v3, unmodified) vs `RiskEngineV4` (monotonic p).  
**Detector freeze commit:** `46bffe142be334260f767a98c2201ca273c24f71`

## Mapping

| Engine | Formula | HIGH reachable at p=1.0 PROMPT_INJECTION? |
| --- | --- | --- |
| v3 `RiskEngine` | `0.70 × p × 0.8` (+ unused context/history) | No (cap 0.56) |
| v4 `RiskEngineV4` | `score = p`; HIGH if p≥0.60, MEDIUM if p≥0.25 | Yes |

Boundaries were **not** fit on TEST. 0.25 / 0.60 are the project’s existing policy bands.

## DEV (threshold 0.25)

| Band | Count | Notes |
| --- | ---: | --- |
| LOW | 19/40 | 19/20 benign + 0 attacks |
| MEDIUM | 15/40 | mostly detected attacks |
| HIGH | 6/40 | 6/20 attacks; 0 benign HIGH |

HIGH is reachable for genuine DEV attacks. One DEV FP is MEDIUM (`la_v3_ben_077`).

## TEST (confirmation only, not used to retune)

| Band | Attacks (40) | Benign (40) |
| --- | ---: | ---: |
| LOW | 13 | 33 |
| MEDIUM | 25 | 1 |
| HIGH | 2 | 6 |

HIGH is reachable, but **miscalibrated on TEST hard negatives**: 6 benign HIGH vs 2 attack HIGH. 25/40 attacks sit in MEDIUM, which maps to A1 at adaptive `defense_level` 0–1 and to A3 only at fixed level 3.

## Policy implication

- Adaptive B3_V4 at starting level 1: LOW→A1, MEDIUM→A1, HIGH→A3. Only the 2 HIGH attacks are eligible for A3; 6 HIGH benign are false-block risks.
- Diagnostic B2_L3_V4 (fixed level 3): MEDIUM and HIGH → A3. This tests whether **intervention mapping**, not detection, is the remaining bottleneck.

This is **CASE B pressure**: detector improved, risk/intervention mapping may still dominate outcomes.

Do not move HIGH/MEDIUM thresholds after seeing TEST.
