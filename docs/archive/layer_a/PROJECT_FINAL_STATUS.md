# Project final status

**CASE B:** Detector v4 improves frozen-TEST discrimination versus the v3 regex detector. Adaptive B3_V4 does **not** demonstrate a statistically meaningful ASR reduction versus B0. Risk/intervention mapping (MEDIUM→A1 at adaptive levels 0–1; HIGH mass on hard negatives) remains the bottleneck.

**CASE E footnote:** MULTI_TURN TEST recall 3/8 remains the weakest family.

**Not CASE A** (no demonstrated adaptive outcome win).  
**Not CASE C** (DEV lift generalized, with a TEST drop: DEV recall 1.00 → TEST 0.675, still far above v3 0.05).  
**Not CASE D** (detector recovery produced a real TEST lift).

## Freeze identities

| Item | Value |
| --- | --- |
| Detector | `evidence_v4.0` freeze commit `46bffe1` |
| TEST pack SHA-256 | `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8` |
| v2 pack SHA-256 | `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33` |
| v3 intervention (B0/L3/oracle) | `LAYER_A_V3_INTERVENTION/20260913-200544` |
| v4 detector TEST | `LAYER_A_V4_DETECTOR/20260914-frozen-test` |
| v4 intervention | `LAYER_A_V4_INTERVENTION/20260914-101700` |

## Strongest justified claim

On the frozen Layer A v3 TEST split, an evidence-gated detector designed on TRAIN/DEV raises attack recall from 2/40 to 27/40 and AUROC from 0.37 to 0.71 relative to regex V18, without TEST tuning. Adaptive runtime intervention using that detector does not significantly beat no-defense. A diagnostic risk-gated level-3 policy can cut ASR with a utility cost; that is a mapping result, not an adaptive-defense result.

## Strongest unsupported claim (must not be made)

“ADAPTI-GUARD is a working / production-ready / state-of-the-art cost-aware defense that solves prompt injection.”

## Remaining limitation

HIGH is rare on TEST attacks and too common on quoted hard negatives; adaptive policy therefore almost never A3s real attacks and sometimes A3s benign text. L2 is still not scored in the LLM harness.

## Recommended next research step

Calibrate the HIGH band and E10 veto on TRAIN/DEV so HIGH tracks primary-control attacks rather than quoted PI, then freeze and run **one** new B3 eval. Do not chase B3–B0 ASR on the current mapping. Do not retune on TEST. Wire the mock tool loop into `evaluate_episode` before any L2 claim.
