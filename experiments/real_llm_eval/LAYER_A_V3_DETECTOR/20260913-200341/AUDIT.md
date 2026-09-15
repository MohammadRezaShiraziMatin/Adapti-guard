# Layer A v3 detector-only evaluation

**Status:** VALID  
**Pack:** `/workspace/datasets/frozen/layer_a_v3`  
**test_split SHA-256:** `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8`  
**Git commit:** `1b3b6827e2fe7b0c29970dfe082ac5f2f2eb4b0c`

## Headline (TEST, threshold=0.25 project default)

Attack recall=0.050 (2/40), benign FPR=0.325, F1=0.07272727272727272, AUROC=0.3678125, hard-negative FPR=0.65.

This is a **detector** result, not an intervention ASR result.

## Threshold discipline

- Project default threshold: `0.25` (not tuned on TEST).
- DEV-selected threshold (max F1 then recall): `0.1` (dev F1=0.15384615384615383, recall=0.1, FPR=0.2).
- TEST metrics at the DEV-selected threshold are reported in `test_at_dev_selected_threshold/` and were not used for selection.

## Split summary (default threshold)

| Split | n | Attack recall | Benign FPR | F1 | AUROC | HN FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 40 | 0.1 | 0.3 | 0.14285714285714288 | 0.38875 | 0.6 |
| dev | 40 | 0.1 | 0.2 | 0.15384615384615383 | 0.44 | 0.4 |
| test | 80 | 0.05 | 0.325 | 0.07272727272727272 | 0.3678125 | 0.65 |
| test@dev_thr | 80 | 0.05 | 0.325 | 0.07272727272727272 | 0.3678125 | 0.65 |

## TEST attack-family recall (threshold=0.25)

| Family | n | Recall |
| --- | ---: | ---: |
| DIRECT_INJECTION | 12 | 0.08333333333333333 |
| INDIRECT_INJECTION | 12 | 0.0 |
| MULTI_TURN_INJECTION | 8 | 0.0 |
| OBFUSCATED_INJECTION | 8 | 0.125 |

## TEST difficulty recall (threshold=0.25)

| Difficulty | n | Recall |
| --- | ---: | ---: |
| D1 | 5 | 0.20 |
| D2 | 16 | 0.00 |
| D3 | 12 | 0.083 |
| D4 | 7 | 0.00 |

## Scientific reading

Under the current regex detector, Layer A v3 TEST attack recall is near floor while hard-negative FPR is high. Adaptive escalation that depends on this detector cannot be expected to outperform weak sanitization on missed attacks.

Manuscript Results were not modified.
