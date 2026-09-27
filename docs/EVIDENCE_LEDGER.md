# Evidence ledger (artifact-backed)

| ID | Tier | Artifact | Manuscript | Metrics (verified) |
|----|------|----------|------------|-------------------|
| Track A VNEXT | confirmatory **FAIL** | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/comparison.json` | workshop VNEXT | **n_attack=61** paired (122 total episodes); B0 ASR≈0.951, VNEXT-ADAPT ASR≈0.869; **δ̂=0.082**; McNemar **b10=5, b01=0**, p=0.0625; MSID 0.20 → **FAIL** (δ̂&lt;MSID, p&gt;α); Wilson/bootstrap ASR CIs in file (**offline CI**, not re-labeled confirmatory) |
| Track B Phase1 | confirmatory scoped | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/verdict.json` | dual-track / Phase1 | **`SUPPORTED_IMPROVEMENT` (scoped)**; effect δ̂≈0.443; McNemar b10=27 b01=0 p≈1.5e-8; B0 harmful success 1.0 → CORE 0.557; utility_core≈0.967; does **not** reverse Track A |
| Layer A v1 (PR18) | historical | `experiments/real_llm_eval/LAYER_A_OPENROUTER/20260913-183742/metrics.json` | Layer A v1 | B0 **ASR=0.05**, utility=0.9, FPR=0.1; B3 **ASR=0.10**, utility=0.9, FPR=0.1; n=40 (20+20) |
| Layer A v2 (PR19) | historical | `experiments/real_llm_eval/LAYER_A_V2_OPENROUTER/20260913-191217/metrics.json` | Layer A v2 | B0 **ASR=0.55**, U=**1.0**, FPR=**0**; B3 **ASR=0.55**, U=**0.95**, FPR=**0.05**; pack `layer_a_v2` |
| DIAG-B0-B1 | diagnostic | `.../DIAGNOSTIC_B0_B1/DIAG-B0-B1-LAYER-A-V2-20260924/` | not Results | target_2, 20+20 seed 42 |
| DIAG-MULTI-TARGET | diagnostic | `.../DIAG-MULTI-TARGET-20260924/SUMMARY.json` | not Results | 4 targets B0/B1; spend≈$0.201 |
| LIVE-PRO-PI pilots | noncanonical | untracked `LIVE-PRO-PI-*` | not citable | — |
| B2 pilot metrics | pilot | `.../LIVE-PRO-PI-B2-EVAL-.../derived/metrics.json` + `PILOT_NOT_EVIDENCE.md` | infra pin | SHA in tests |
| MT1 | diagnostic (protocol) | `docs/PROTOCOL_MT1.md` | future MT1 | r1+ not confirmatory on 20-attack pack |
