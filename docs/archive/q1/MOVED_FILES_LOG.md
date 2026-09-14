# Moved Files Log

Date: 2026-09-03

| From | To | Reason |
|------|----|--------|
| `experiments/REAL_LLM_EVAL` | `experiments/real_llm_eval/REAL_LLM_EVAL` | categorize + keep legacy path symlink |
| `experiments/REAL_LLM_EVAL_MIXED` | `experiments/real_llm_eval/REAL_LLM_EVAL_MIXED` | categorize + keep legacy path symlink |
| `experiments/PHASE5_CONSTRAINED` | `experiments/real_llm_eval/PHASE5_CONSTRAINED` | categorize + keep legacy path symlink |
| `experiments/PHASE4_PILOT` | `experiments/real_llm_eval/PHASE4_PILOT` | categorize + keep legacy path symlink |
| `experiments/GROQ_SMOKE` | `experiments/real_llm_eval/GROQ_SMOKE` | categorize + keep legacy path symlink |
| `experiments/OPENROUTER_SMOKE_TEST` | `experiments/real_llm_eval/OPENROUTER_SMOKE_TEST` | categorize + keep legacy path symlink |
| `experiments/INFRA-SMOKE-001` | `experiments/real_llm_eval/INFRA-SMOKE-001` | categorize + keep legacy path symlink |
| `experiments/EXP002_REAL_LLM` | `experiments/real_llm_eval/EXP002_REAL_LLM` | categorize + keep legacy path symlink |
| `experiments/EXP004_MULTI_MODEL` | `experiments/real_llm_eval/EXP004_MULTI_MODEL` | categorize + keep legacy path symlink |
| `experiments/EXP005_GEMINI_FLASH` | `experiments/real_llm_eval/EXP005_GEMINI_FLASH` | categorize + keep legacy path symlink |
| `experiments/PHASE2_7_PILOT` | `experiments/real_llm_eval/PHASE2_7_PILOT` | categorize + keep legacy path symlink |
| `experiments/EXP003_BASELINES` | `experiments/simulation/EXP003_BASELINES` | categorize + keep legacy path symlink |
| `experiments/EXP005_ADAPTATION` | `experiments/simulation/EXP005_ADAPTATION` | categorize + keep legacy path symlink |
| `experiments/EXP008_ADAPTIVE_ATTACK` | `experiments/simulation/EXP008_ADAPTIVE_ATTACK` | categorize + keep legacy path symlink |
| `experiments/EXP009_LONG_TERM` | `experiments/simulation/EXP009_LONG_TERM` | categorize + keep legacy path symlink |
| `experiments/FINAL_COMPLETION` | `experiments/simulation/FINAL_COMPLETION` | categorize + keep legacy path symlink |
| `experiments/EXP006_ABLATION` | `experiments/ablations/EXP006_ABLATION` | categorize + keep legacy path symlink |
| `experiments/FINAL_AUDIT` | `experiments/statistics/FINAL_AUDIT` | categorize + keep legacy path symlink |
| `experiments/FINAL_QC` | `experiments/statistics/FINAL_QC` | categorize + keep legacy path symlink |
| `experiments/FINAL_REJUDGE` | `experiments/statistics/FINAL_REJUDGE` | categorize + keep legacy path symlink |
| `experiments/FINAL_JUDGE_VALIDATION` | `experiments/statistics/FINAL_JUDGE_VALIDATION` | categorize + keep legacy path symlink |
| `experiments/FINAL_PROVIDER_TEST` | `experiments/statistics/FINAL_PROVIDER_TEST` | categorize + keep legacy path symlink |
| `experiments/FINAL_FIGURES` | `experiments/reports/FINAL_FIGURES` | categorize + keep legacy path symlink |
| `experiments/EXP-004` | `experiments/archive/EXP-004` | categorize + keep legacy path symlink |
| `experiments/FINAL_REPORT.md` | `experiments/reports/FINAL_REPORT.md` | paper/report artifact |
| `experiments/FINAL_RESEARCH_MANIFEST.json` | `experiments/reports/FINAL_RESEARCH_MANIFEST.json` | paper/report artifact |
| `experiments/PAPER_LIMITATIONS.md` | `experiments/reports/PAPER_LIMITATIONS.md` | paper/report artifact |
| `experiments/PAPER_METHODS_SECTION.md` | `experiments/reports/PAPER_METHODS_SECTION.md` | paper/report artifact |
| `experiments/PAPER_RESULTS_SECTION.md` | `experiments/reports/PAPER_RESULTS_SECTION.md` | paper/report artifact |
| `experiments/PAPER_TABLES.md` | `experiments/reports/PAPER_TABLES.md` | paper/report artifact |
| `experiments/REAL_LLM_EVAL_MIXED_STATUS.json` | `experiments/reports/REAL_LLM_EVAL_MIXED_STATUS.json` | paper/report artifact |
| `experiments/experiment_history.md` | `experiments/reports/experiment_history.md` | paper/report artifact |
| `experiments/REAL_LLM_EVAL_MIXED_run.log` | `results/archive/logs/` | preserve aborted-run log |
| `AUDIT_BEFORE_GROQ.md` | `docs/archive/AUDIT_BEFORE_GROQ.md` | root clutter → docs archive |
| `AUDIT_REPORT.md` | `docs/archive/AUDIT_REPORT.md` | root clutter → docs archive |
| `MULTI_MODEL_EVAL_REPORT.md` | `docs/archive/MULTI_MODEL_EVAL_REPORT.md` | root clutter → docs archive |
| `PHASE1_SCIENTIFIC_AUDIT.md` | `docs/archive/PHASE1_SCIENTIFIC_AUDIT.md` | root clutter → docs archive |
| `Q1_IMPROVEMENT_ROADMAP.md` | `docs/archive/Q1_IMPROVEMENT_ROADMAP.md` | root clutter → docs archive |
| `Q1_SCIENTIFIC_COMPLETION_PART1.md` | `docs/archive/Q1_SCIENTIFIC_COMPLETION_PART1.md` | root clutter → docs archive |
| `REAL_LLM_UPGRADE_REPORT.md` | `docs/archive/REAL_LLM_UPGRADE_REPORT.md` | root clutter → docs archive |
| `CHANGELOG_Q1.md` | `docs/archive/CHANGELOG_Q1.md` | root clutter → docs archive |
| `test_core.py` | `tests/test_core.py` | consolidate tests |
| `test_pipeline.py` | `tests/test_pipeline.py` | consolidate tests |
| `configs/models.yaml` | `configs/models/models.yaml` (symlink) | standard layout pointer |

## Packaging follow-up (2026-09-04)

| From | To | Reason |
|------|----|--------|
| `attacks/`, `defenses/`, `evaluation/`, `figures/`, `models/` (root stubs) | `results/archive/legacy_root_stubs/` | Empty README-only placeholders; real code lives under `src/adapti_guard/` |
| `paper_notes/` | `docs/archive/paper_notes_dup/paper_notes` | Duplicate of `docs/paper/` content |
| `REPRODUCIBILITY.md` | `docs/archive/REPRODUCIBILITY_ROOT.md` | Superseded by `docs/reproducibility.md` |
