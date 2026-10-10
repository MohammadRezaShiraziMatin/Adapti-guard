# Case study scope (decided by the author on 2026-10-10)

Status: scope definition only. No result, dataset, script or manuscript file is changed on this branch by this commit.
Base: `ae6675e` (main after PR #107, before the 2026-10-10 `docs/baseline/` commits).

## Evidence base (in scope)

Only experiments run on 2026-09-30 and 2026-10-01 with non-weak models.

| group | date | models | artifacts |
|---|---|---|---|
| E2/E3 multi-turn harness | 2026-09-30 | qwen/qwen3-30b-a3b, google/gemma-4-31b-it, deepseek/deepseek-v3.2 | `experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/`, `HARNESS_V2_EXPLORATORY_SMOKE_20260930/`, `HARNESS_V2_INDEPENDENT_SCREEN_20260930/`, `HARNESS_V2_INDEPENDENT_DEFENDED_20260930/` |
| InjecAgent live | 2026-09-30 | meta-llama/llama-3.3-70b-instruct only | `experiments/external/injecagent_live_20260930_llama-3.3-70b/` |
| Strong-panel calibration | 2026-10-01 | openai/gpt-5.6-sol, deepseek/deepseek-v4.1-flash, meta-llama/llama-4-maverick, qwen/qwen3.8-flash, z-ai/glm-4.7 | `experiments/external/injecagent_panel_calib_20261001/`, `experiments/external/phase2_calibration_20261001/` |
| External InjecAgent test | 2026-10-01 | meta-llama/llama-4-maverick, qwen/qwen3.8-flash (186 cases each) | `experiments/external/injecagent_registered_20261001/` |

## Out of scope (kept in the repository, not used as evidence)

- All experiments before 2026-09-30 and all weak-model work: E1 (Track A, Track B / Phase-1, VNEXT), Layer A v2–v4, MT1, EXP-00x, pilots.
- 2026-09-30 InjecAgent runs on qwen/qwen-2.5-7b-instruct, meta-llama/llama-3.1-8b-instruct, mistralai/mistral-small-3.2-24b-instruct and google/gemma-4-31b-it.
- F3 confirmatory run on llama (branches `claude/project-thread-mbv2c4`, `claude/project-thread-mg7uj9`).
- The 2026-10-10 `docs/baseline/` commits (`f909a2f`, `e5949bc`) on main.
- Configured but unrun panels (e.g. `configs/models_panel_external_v2.yaml`) are not evidence.

## Known open issues for the in-scope evidence (read-only audit, 2026-10-10)

1. Floor claims at n = 40 are not demonstrated (0/40 gives a 95% upper bound of 8.8%, above the 5% threshold).
2. qwen3.8-flash calibration was n = 36 scored (HTTP 429 errors), below the stated n >= 40 rule.
3. External-test sample size: protocol 310 planned, §5.6 says 124, run used 186; only 124 -> 186 is disclosed.
4. InjecAgent runner/analysis scripts and the Hard-set MANIFEST exist only in unreachable commit `96b33e4e`.
5. §6.6 and §6.7 numbers are not in `NUMBERS_LEDGER.md` or `scripts/reproduce_negative_result.sh`.
6. Temperature, provider route and model version are not recorded in the run records.
7. The "Holm 98.75%" interval is a Bonferroni alpha/4 bound; the stated upper bounds are two-sided.
8. No protocol was frozen or externally registered before these runs; all results are exploratory.

## Rules for work on this branch

- New experiments require a frozen protocol, a locked model panel with no weak models, and explicit author approval before any live call; they are reported as a separate confirmatory part.
- Every paper number maps to a file and metric key.
- Merges into main only on the author's explicit instruction.
