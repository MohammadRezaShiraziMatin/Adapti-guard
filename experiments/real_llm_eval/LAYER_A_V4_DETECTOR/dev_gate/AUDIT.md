# Layer A v4 detector-only evaluation

**Status:** VALID  
**Detector:** `evidence_v4.0`  
**Risk:** `risk_v4.0`  
**include_test:** `False`  
**Git commit:** `ac66652255beb8e377f260fe654ef35ce9d87185`

## Threshold discipline

- Default threshold `0.25` is the project operating point.
- DEV-selected threshold `0.1` (F1=0.975609756097561, recall=1.0, FPR=0.05).
- TEST was not used for selection.

| Split | n | Attack recall | Benign FPR | F1 | AUROC | HN FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 40 | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 |
| dev | 40 | 1.0 | 0.05 | 0.975609756097561 | 0.99125 | 0.1 |

Manuscript Results were not modified. Historical v2/v3 artifacts were not overwritten.
