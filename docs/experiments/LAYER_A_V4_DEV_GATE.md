# Layer A v4 DEV gate (pre-TEST freeze)

**Detector:** `evidence_v4.0`  
**Risk:** `risk_v4.0` (monotonic p; HIGH if p≥0.60)  
**Pack splits used:** TRAIN + DEV only  
**TEST:** not evaluated in this gate. Frozen TEST hash remains `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8`.

## DEV vs legacy v3 (threshold 0.25)

| Split | Detector | Recall | FPR | HN FPR | AUROC | HIGH on attacks |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| train | v3 | 0.10 | 0.30 | 0.60 | 0.389 | 0 |
| train | v4 | **1.00** | **0.00** | **0.00** | **1.00** | 7/20 |
| dev | v3 | 0.10 | 0.20 | 0.40 | 0.44 | 0 |
| dev | v4 | **1.00** | **0.05** | **0.10** | **0.991** | 6/20 |

DEV-selected threshold (max F1 then recall): **0.1**. At 0.25 vs 0.1, DEV recall remains 1.00 (positive scores sit above 0.25). Operating point for comparison with v3 remains **0.25**.

## Gate decision

DEV discrimination improved on recall, FPR, hard-negative FPR, AUROC, and HIGH reachability. **Proceed to one frozen TEST evaluation.** Do not retune after seeing TEST.

One DEV false positive remains (`la_v3_ben_077`, hard negative). Not patched against TEST.

Artifacts: `experiments/real_llm_eval/LAYER_A_V4_DETECTOR/dev_gate/`
