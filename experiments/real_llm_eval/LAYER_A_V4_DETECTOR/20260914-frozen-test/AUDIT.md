# Layer A v4 detector-only evaluation

**Status:** VALID  
**Detector:** `evidence_v4.0`  
**Risk:** `risk_v4.0`  
**include_test:** `True`  
**Git commit:** `46bffe142be334260f767a98c2201ca273c24f71`

## Threshold discipline

- Default threshold `0.25` is the project operating point.
- DEV-selected threshold `0.1` (F1=0.975609756097561, recall=1.0, FPR=0.05).
- TEST was not used for selection.

| Split | n | Attack recall | Benign FPR | F1 | AUROC | HN FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 40 | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 |
| dev | 40 | 1.0 | 0.05 | 0.975609756097561 | 0.99125 | 0.1 |
| test | 80 | 0.675 | 0.175 | 0.7297297297297296 | 0.7053125 | 0.35 |
| test@dev_thr | 80 | 0.675 | 0.175 | 0.7297297297297296 | 0.7053125 | 0.35 |

Manuscript Results were not modified. Historical v2/v3 artifacts were not overwritten.

## Comparison with frozen v3 detector (TEST, threshold=0.25)

| Metric | v3 | v4 | Delta |
| --- | ---: | ---: | ---: |
| Attack recall | 2/40 = 0.05 | 27/40 = 0.675 | +0.625 |
| Benign FPR | 0.325 | 0.175 | -0.150 |
| Hard-negative FPR | 0.65 | 0.35 | -0.30 |
| AUROC | 0.368 | 0.705 | +0.337 |
| AUPRC | 0.448 | 0.615 | +0.167 |
| HIGH on attacks | 0/40 | 2/40 | +2 |
| HIGH on benign | 0/40 | 6/40 | +6 (regression) |

Family recall (v4 TEST): DIRECT 8/12, INDIRECT 12/12, MULTI_TURN 3/8, OBFUSCATED 4/8.

## Risk note (no TEST tuning)

v4 mapping is monotonic in p, so HIGH is reachable. On TEST, HIGH is still rare on attacks (2/40) and appears on 6 benign hard negatives. MEDIUM holds 25/40 attacks. Adaptive B3 at `defense_level≤1` still maps MEDIUM→A1. Do not retune bands on TEST.

