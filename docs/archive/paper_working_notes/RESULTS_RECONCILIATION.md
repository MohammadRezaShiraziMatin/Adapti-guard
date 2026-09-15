# Results reconciliation (Phase 11)

**This file does not rewrite `docs/paper/04_results.md`.** It maps claims to current evidence.

| Historical / working claim | Supporting experiment | Current evidence | Limitation | Status |
| --- | --- | --- | --- | --- |
| B3 reduces ASR vs B0 on Layer A v2 | `LAYER_A_V2_OPENROUTER/20260913-191217` | Both ASR 0.55 | n=20 | **UNSUPPORTED** as a defense win |
| Stronger fixed L3 drives ASR to 0 | `LAYER_A_V2_FIXED_ABLATION` + v3 L3 | ASR 0, utility 0 | scoring rule `blocked⇒fail` | **SUPPORTED** as security ceiling / utility floor; **UNSUPPORTED** as practical defense |
| L2 is a usable Layer A baseline | ablation attempt | no tool loop in `evaluate_episode` | A2 cannot deny tools in LLM eval | **UNSUPPORTED** (harness). Mock loop now exists, not wired |
| Detector/risk is the v3 bottleneck | v3 detector + intervention | recall 0.05, HIGH 0, B3=A1×80 | regex V18 gate | **SUPPORTED** |
| v4 detector improves discrimination on frozen TEST | `LAYER_A_V4_DETECTOR/20260914-frozen-test` | recall 0.675 vs 0.05; AUROC 0.705 vs 0.368; HN FPR 0.35 vs 0.65 | 13 FN; HIGH-on-benign | **SUPPORTED** (detector-only) |
| Adaptive B3_V4 is a useful runtime defense | `LAYER_A_V4_INTERVENTION` | ASR 0.625 vs B0 0.75, p=0.125; utility 0.85 | MEDIUM→A1; 6 false A3 | **UNSUPPORTED** |
| Risk-gated level 3 with v4 signal can cut ASR | B2_L3_V4 | ASR 0.20 vs 0.75, p=4.8e-7; utility 0.825 | not adaptive; FPR 0.175 | **PARTIALLY SUPPORTED** (diagnostic mapping) |
| ORACLE_BLOCK is deployable performance | v3 oracle | ASR 0, utility 1 | uses labels | **DIAGNOSTIC ONLY** |
| Cost-aware Pareto dominance of adaptive policy | frontier.json | B3_V4 does not Pareto-dominate B0 | utility drop | **UNSUPPORTED** |

Do not copy these rows into manuscript Results without a separate explicit review.
