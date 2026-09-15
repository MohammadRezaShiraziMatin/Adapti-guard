# Final scientific audit

**Date:** 2026-09-14  
**Case:** **B** — detector improves, risk/intervention mapping remains the bottleneck for adaptive defense.  
**Multi-turn footnote:** family recall 3/8 on TEST (CASE E residual, not the headline).

## Answers

1. **Does detection work?** Partially. v4 TEST recall 27/40 = 0.675 vs v3 0.05; AUROC 0.705 vs 0.368. Still 13/40 misses; hard-negative FPR 0.35.
2. **Does risk estimation work?** Partially. HIGH is reachable (v3: 0). On TEST, HIGH is 2/40 attacks and 6/40 benign — inverted HIGH mass.
3. **Does intervention work?** A3 blocks when selected (2 true blocks + 6 false blocks under B3_V4; 34 blocks under B2_L3_V4). A1 still fails on 16 detected attacks. L2 unenforced in the LLM harness; mock loop proves A2 can deny tools.
4. **Does intervention improve outcome?** Adaptive B3_V4 vs B0: ASR 0.625 vs 0.75, McNemar **p=0.125**, utility 0.85 vs 1.00 — **not demonstrated**. Diagnostic B2_L3_V4 vs B0: ASR 0.20 vs 0.75, p=4.8×10⁻⁷, utility 0.825.
5. **Under what families (B3_V4 ASR)?** Direct 11/12, indirect 5/12, multi-turn 6/8, obfuscation 3/8.
6. **At what cost?** B3_V4 mean defense cost 0.131; ~$0.005–0.008/run class. Utility −0.15 from false A3.
7. **Benign traffic?** B3_V4 utility 34/40. Six HIGH false blocks.
8. **Hard negatives?** Detector TEST HN FPR 0.35; those drive false HIGH.
9. **Main bottleneck?** Adaptive mapping: MEDIUM (25/40 attacks) → A1 at `defense_level≤1`. Plus remaining FN and HIGH-on-benign miscalibration.
10. **Security ceiling?** Unconditional L3: ASR 0, utility 0.
11. **Utility floor?** Same L3 utility 0. Oracle utility 1 at ASR 0 (not deployable).
12. **Demonstrated?** v4 detector lift on frozen TEST without TEST tuning; HIGH reachable; A3 enforces; risk-gated level 3 can cut ASR with utility loss.
13. **Not demonstrated?** Adaptive B3 beats B0; production defense; L2; keyword-free general PI solution.
14. **Diagnostic only?** ORACLE_BLOCK, B2_L3_V4, L3, counterfactuals.
15. **Future work?** Calibrate HIGH so attacks—not quoted hard negatives—populate it; cover remaining multi-turn/obfuscation FNs on TRAIN/DEV-style mechanisms without TEST peeking; wire the mock tool loop into `evaluate_episode` before scoring L2.

Manuscript Results were not modified.
