# Harness v2 — preregistered deviations and amendments (append-only log)

Citable audit trail for paper Methods. **Do not edit** historical run directories; corrections are new files + rows here.

| # | Date (UTC) | Commit | Title | What changed | Why | Affected runs / artifacts |
|---|------------|--------|-------|--------------|-----|---------------------------|
| — | 2026-09-27 | `fb1e515` | Step 1 prereg + tools session | Native OpenRouter tools harness, provider probe, `PREREG_HARNESS_V2.md` | Replace ad-hoc smoke with logged trajectories | `PROVIDER_PROBE.json` |
| 1 | 2026-09-27 | `72e78e2` | Amendment 1 | HTTP completion budget formula, `finish_reason` capture, C1/C2 smoke criteria | Cap overrun on smoke2 gemma multi-round | `run_harness_v2_smoke2.py` behavior |
| — | 2026-09-27 | `d10a983` | Smoke2 artifacts (valid) | gemma+deepseek, 4 HTTP, 1 round/scenario | Post–Amendment 1 verification | `HARNESS_V2_SMOKE2_20260927-125200` |
| — | 2026-09-27 | `6d5e56c` / `fb1e515` | Smoke1 live | 6 HTTP, llama+qwen3 indirect | Initial tools path | `HARNESS_V2_SMOKE_20260927-124451` |
| 2 | 2026-09-27 | `ee5ad9b` | Amendment 2 | `HttpCompletionBudget`, four-state C2 enum, smoke3 runner | Multi-model indirect with shared HTTP cap | `run_harness_v2_smoke3.py` |
| — | 2026-09-27 | `015446d` | Smoke3 live | 7/9 HTTP, 3 models, $0.001395 | Amendment 2 execution | `HARNESS_V2_SMOKE3_20260927-131707` |
| 3 | 2026-09-27 | `57b7746` | Amendment 3 | Full-trajectory C2 precedence; orthogonal `text_claim_candidate`, `explicit_refusal`; offline relabel JSON | Per-request C2 mislabeled llama smoke1 | `C2_RELABEL_AMENDMENT3.json` per smoke dir; `QWEN3_USAGE_AUDIT_AMENDMENT3.md` |
| 4 | 2026-09-27 | `05fa35d` | Amendment 4 (code) | Persist full `request` in trajectories; reasoning-off default (`include_reasoning:false` + `reasoning.effort:none` when supported); metadata + pricing reconcile | Qwen3 reasoning tokens without request logging; cost clarity | All **future** harness v2 runs; `AMENDMENT4_*` |
| — | 2026-09-27 | `dd885d1` | Reasoning-off smoke | qwen3 only, 2 HTTP, \$0.000129; PASS (`reasoning_tokens=0`, no `message.reasoning`) | Verify Amendment 4 default | `HARNESS_V2_REASONING_SMOKE_20260927-133103` |
| 4b | 2026-09-27 | *`d18cc6cbf593c8e319658f9e10e97fbd0f5b0fa7`* | Analysis exclusion | `EXCLUDED_FROM_ANALYSIS.json` for plan-invalid smoke2 | Prevent 125041 from efficacy aggregates | `HARNESS_V2_SMOKE2_20260927-125041` |
| 5 | 2026-09-27 | `a59fba1` | Amendment 5 | Scenario-aware delivery in stored requests; `BENIGN_NA`; templates rewrite; pilot2 criteria; offline pilot1 relabel | Poisoned-benign false INVALID; P4/P5 delivery evidence | `SCENARIO_INSTANCE_TEMPLATES.json` SHA `dd445b19…`; `PILOT2_CRITERIA_LOCKED.md` SHA `e2ce8ce9…`; `C2_RELABEL_AMENDMENT5.json` |

## Smoke2 125041 exclusion (Amendment 4 registry)

- **Path:** `experiments/harness_v2/HARNESS_V2_SMOKE2_20260927-125041/EXCLUDED_FROM_ANALYSIS.json`
- **`excluded_from_analysis`:** `true`
- **Reason:** plan-invalid (pre–Amendment 1 `max_rounds=4`); data retained, not deleted.

## Full eval prereg draft

- **Path:** `experiments/harness_v2/PREREG_HARNESS_V2_FULL.md` — commit `6ac04f6` (DRAFT, awaiting Matin).

## Related non-harness deviations (context only)

| Date | Commit | Note |
|------|--------|------|
| 2026-09-27 | `6df5d40` | Step 0 usage token capture errata |
| 2026-09-27 | `eb8094b` | P1 RQ1 run marked INVALID (J1 parse), not harness v2 |

*Update the “step 2 commit” SHA in the row above after `git commit` for reasoning smoke.*
