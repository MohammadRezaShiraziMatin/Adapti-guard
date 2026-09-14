# Scientific Audit Report (Auto-Generated)

**Generated:** 2026-09-01T22:06:58.457073+00:00
**Git commit:** `612f577118a19949b4862a3b27b801db8c7eef65`
**Overall readiness:** 5.0/10 (Q1 threshold: 8.0)
**Submission ready:** NO

## API Status

- OpenRouter: BLOCKED — OPENROUTER_API_KEY format invalid (expected sk-or-v1-... prefix). Get a key at https://openrouter.ai/keys

## Experiment Inventory

| ID | Status | Validity | Mode | N | Publication-ready | Issues |
|---|---|---|---|---:|---|---|
| EXP-000 | NOT_RUN | NOT_RUN | unknown | 0 | ❌ | No metrics.json found |
| EXP-002 | BLOCKED | BLOCKED | real_llm_judge | 0 | ❌ | Experiment blocked before execution |
| EXP-002-target_3 | INVALID | INVALID | real_llm_judge | 5 | ❌ | All 5 episodes had judge errors |
| EXP-003 | NOT_RUN | NOT_RUN | unknown | 0 | ❌ | No metrics.json found |
| EXP-005 | COMPLETED | SIMULATION | HARMONIZED_SIMULATIO | 0 | ❌ | — |
| EXP-008 | COMPLETED | SIMULATION | DETECTOR_SIMULATION | 0 | ❌ | — |
| EXP-004 | BLOCKED | BLOCKED | real_llm_judge | 0 | ❌ | Experiment blocked before execution |
| REAL-LLM-EVAL | BLOCKED | BLOCKED | real_llm_judge | 0 | ❌ | Experiment blocked before execution |
| EXP-017 | VALIDATED_BUT_POOR_GENERALIZATION | PARTIAL | legacy | 0 | ❌ | — |

## Datasets

| Dataset | Records | SHA256 (prefix) |
|---|---:|---|
| benchmark_q1/train | 10537 | `d408ddfd0ebe5e41...` |
| benchmark_q1/validation | 2257 | `b62e9a3622af34b1...` |
| benchmark_q1/test | 2259 | `fa35c657dae473e2...` |
| unified_security_dataset | 12799 | `3d3ae9e4863c0288...` |

## Component Scores

- **infrastructure:** 6/10
- **real_llm_results:** 0/10
- **simulation_separated:** 9/10
- **provenance:** 7/10
- **statistical_validation:** 4/10
- **human_validation:** 1/10
- **dataset_coverage:** 8/10

## Critical Gaps

1. No VALID real-LLM experiment with publication sample size (≥50)
2. EXP-002 artifacts marked COMPLETED but contain 100% API/judge errors
3. All adaptation/ablation results are simulation-only
4. Human judge validation not executed
5. SOTA baselines (Llama Guard) use regex fallback

---
*Regenerate: `python scripts/scientific_audit.py`*
