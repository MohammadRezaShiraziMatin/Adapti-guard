# ADAPTI-GUARD — Full Project Status Audit

**Audit date:** 2026-09-03  
**Repository:** `/home/mohammadreza/01_BASE_Q1/adapti_guard`  
**Git HEAD:** `35833a64b35a98d596d729c3fa7687e3228381ca` (`main`, ahead of `origin/main` by 1; working tree has uncommitted Gemini/EXP005 changes)  
**Mode:** AUDIT ONLY — no research-code changes, no API calls, no dataset downloads performed for this audit.

**Legend used throughout**

| Tag | Meaning |
|-----|---------|
| **IMPLEMENTED** | Code/config exists and is wired |
| **EXECUTED** | A run produced artifacts with timestamps/outputs |
| **VERIFIED** | Artifacts inspected; claims match files |
| **PARTIAL** | Some but not all of the intended scope |
| **TODO** | Specified but missing |
| **BLOCKED** | Cannot complete due to external/internal blocker |

---

## Executive summary

ADAPTI-GUARD has a **substantial implemented research codebase** (defense L0–L3, adaptive controller, harmonized runner, metrics/ICS/reward, statistical helpers, real-LLM pipeline with OpenRouter/Ollama/Gemini adapters, frozen benchmarks with hashes).  

It does **not** yet have a **VALID, publication-scale real-LLM evaluation** of fixed vs adaptive policies answering the core research question. Primary empirical tracks are **BLOCKED** (OpenRouter HTTP 401; Gemini free-tier HTTP 429). Documented primary harmonized Phase-8 result bundle (`results/phase8/q1_harmonized_v1/`) is **MISSING on disk**. Simulation/heuristic runs exist and must stay labeled **Simulation / Infrastructure Validation**.

**Honest overall readiness: ~35% (≈ 3.5–4.0 / 10). Not Q1-paper ready.**

---

## 1. Architecture audit

### Pipeline (as implemented)

```text
Dataset (benchmark_q1 / frozen eval_v1 / attack stream)
  → loaders (attack_success.load_*, frozen loaders)
  → defense policy (B0–B3 or PolicyMode fixed/adaptive)
  → [optional] target LLM (OpenRouter / Gemini / Ollama)
  → [optional] blind LLMJudge
  → episode outcomes
  → compute_metrics / multi_model_statistics
  → statistics (bootstrap, McNemar, Holm)
  → artifacts under results/ or experiments/
  → manuscript (docs/MANUSCRIPT_DRAFT.md)  [mostly BLOCKED placeholders]
```

| Stage | STATUS | EVIDENCE | COMMENTS |
|-------|--------|----------|----------|
| Dataset build | **IMPLEMENTED** + **EXECUTED** (builder historically) | `scripts/build_benchmark_q1.py`, `datasets/benchmark_q1/{train,validation,test}.jsonl`, `hashes.json`, `statistics.json` | Frozen artifacts present; raw upstream dirs may live outside repo |
| Preprocessing / splits | **VERIFIED** | `statistics.json`: 70/15/15, seed 42, contamination_check false | Dedup method recorded |
| Benchmark adapter | **IMPLEMENTED** | `src/adapti_guard/evaluation/attack_success.py` (`load_benchmark_records`, `load_frozen_eval_records`) | Multiple loaders coexist |
| Attack stream | **IMPLEMENTED** + **EXECUTED** | `scripts/generate_attack_stream.py`, `results/common_attack_stream.json` (100 episodes; SHA256 `d101f94d…`) | Used by harmonized protocol |
| Model (target LLM) | **IMPLEMENTED**; full eval **BLOCKED** | `target_model.py` (`OpenRouterTargetModel`, `GeminiTargetModel`, `OllamaTargetModel`); `configs/models.yaml` | Smoke/pilot only at scale |
| Defense policy | **IMPLEMENTED** | `defense/action_layer.py`, `policy/policy_engine.py`, `experiments/defense_baselines.py`, `harmonized_runner.py` | L0–L3 + adaptive |
| Agent/runtime | **PARTIAL** | `runtime.py`, AgentDojo n=28 in benchmark | No full AgentDojo tool-loop evaluation |
| Outcome | **IMPLEMENTED** (two modes) | Real: `evaluate_episode` + `LLMJudge`; Sim: `attack_outcome` / harmonized heuristics | Modes must not be mixed in claims |
| Metrics | **IMPLEMENTED** | `evaluation/metrics.py`, `outcome_evaluator.py`, `feedback_engine.py` | ICS/reward weights match design |
| Statistical analysis | **IMPLEMENTED**; primary **NOT EXECUTED** | `evaluation/statistics.py`, `multi_model_statistics.py` | No VALID full-protocol stats artifacts |
| Figures/tables | **TODO** / empty | `figures/README.md` only | No publication figures from VALID real LLM |
| Manuscript | **PARTIAL** | `docs/MANUSCRIPT_DRAFT.md` | Results section **[BLOCKED]** |

---

## 2. Dataset audit

### `benchmark_q1` (canonical mixed benchmark)

| Item | Value | Evidence |
|------|------:|----------|
| Total records | 15,053 | `datasets/benchmark_q1/statistics.json` |
| Train / val / test | 10,537 / 2,257 / 2,259 | same |
| Seed / ratios | 42; [0.7, 0.15, 0.15] | same |
| Attack / benign | 11,859 / 3,194 | same |
| Test SHA-256 | `fa35c657dae473e21f6b89d389e3b85b4daa445eccd4aedeb415b344ab3cf74e` | `hashes.json` |
| Deduplication | 0 duplicates removed (exact normalized prompt hash) | `statistics.json` |
| Train↔test contamination | 0 reported | same |

**Categories (full set):** direct_prompt_injection 263; jailbreak 6104; indirect 1037; rag_injection 1927; agent_tool_injection **28**; benign_tasks 3194; adaptive_attacks 2500.

**Sources attributed as loaded into `benchmark_q1` (via builder stats):** BeaverTails, RAGTruth, JailbreakBench (+ judge), prompt-injections, Do Not Answer, AgentDojo (28), plus adaptive templates derived from those.

**Explicitly UNAVAILABLE at build time (`source_availability`):** NotInject, BIPIA, InjecAgent, TensorTrust, PIArena.

### Frozen attack-only eval (`eval_v1`)

| Item | Value | Evidence |
|------|------:|----------|
| n | 770 (110×7 categories) | `datasets/frozen/eval_v1/manifest.json` |
| SHA-256 | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` | same |
| Labels | attack-only (no benign) | category counts; PHASE2_7 note |

### Harmonized attack stream

| Item | Value | Evidence |
|------|------:|----------|
| Episodes | 100 | `results/common_attack_stream.json` |
| SHA256 | `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` | `sha256sum` + `REPRODUCIBILITY.md` |

### Named sources checklist (loaded into unified benchmark?)

| Source | In `benchmark_q1`? | Evidence |
|--------|--------------------|----------|
| BeaverTails | **YES** | `statistics.json` source_attribution |
| RAGTruth | **YES** | same |
| JailbreakBench | **YES** | same |
| AgentDojo | **YES (n=28 only)** | same; `configs/datasets.yaml` |
| Open-Prompt-Injection / prompt-injections | **YES** (as `prompt_injection`) | same |
| Do Not Answer | **YES** | same |
| NotInject | **NO** | `source_availability: UNAVAILABLE`; local `dataset/raw/NotInject` **absent** |
| BIPIA | **NO** | same; `BIPIA/` **absent** |
| AdvBench | **NO** | not in `build_benchmark_q1.py` / `configs/datasets.yaml` |
| llm-attacks | **NO** | not referenced as loaded |
| HarmBench | **NO** | not loaded |
| AgentHarm | **NO** | config inventory only; raw path absent |
| PromptBench | **NO** | not loaded |
| InjecAgent / TensorTrust / PIArena | **NO** | marked unavailable |

**Important:** Presence of adapter stubs or gitignored paths ≠ integration. Builder marks NotInject/BIPIA unavailable; this workspace has **no** local `dataset/raw/NotInject` or `BIPIA`.

---

## 3. Defense implementation audit

| Question | Answer | Evidence |
|----------|--------|----------|
| L0 = NO_INTERVENTION | **YES** | `DefenseAction.NO_INTERVENTION = "A0"` in `core/models.py`; `DefenseActionLayer.execute` |
| L1 = SANITIZE | **YES** | A1 + regex sanitize in `action_layer.py` |
| L2 = TOOL_RESTRICTION | **YES** | A2 sets `tool_access=False` |
| L3 = BLOCK | **YES** | A3 `allowed=False` |
| All four executed in code paths | **YES (unit + sim)** | `tests/test_action_layer.py`, harmonized runner, B2_L1/L2/L3 factories |
| Transitions | **YES** | `PolicyUpdateEngine` level ±1 |
| Escalation | **YES** | `attack_pressure >= attack_threshold` (default 2) |
| De-escalation | **YES (implemented)** | `legitimate_pressure` + feedback `REDUCE_DEFENSE`; README notes often **not activated** under default harmonized workload |
| Cost gate | **YES** | `FeedbackEngine`: de-escalation paths require `cost_penalty >= 0.50` (or `< 0.50` for keep); `NoCostGateFeedbackEngine` ablation |
| Thresholds configurable | **YES** | `attack_threshold`, `legitimate_threshold` ctor args |
| Deterministic policies | **PARTIAL** | Fixed levels deterministic; adaptive deterministic given stream + thresholds; LLM path non-deterministic unless API seed |
| Decisions logged | **PARTIAL** | Harmonized episodes + prediction provenance rows; depends on runner |
| Intervention cost measurable | **YES (table costs)** | A0=0, A1=0.10, A2=0.25, A3=0.50 in `outcome_evaluator.py` / `defense_baselines.py`; **measured API $** only when provider returns cost |

---

## 4. Policy audit

| Policy | Implementation | Execution (evidence) | Config | Result files |
|--------|----------------|----------------------|--------|--------------|
| Fixed L0 | **IMPLEMENTED** `PolicyMode.FIXED_L0` / B0 | Sim: EXP-005/006; Real smoke/pilot partial | `harmonized_runner.py`, `defense_baselines.py` | EXP005/006 metrics; REAL-LLM-EVAL n=5; Gemini smoke B0 |
| Fixed L1 | **IMPLEMENTED** `FIXED_L1` / B2_L1 | Sim + small real | same | REAL-LLM-EVAL baselines; EXP005 `A_no_adaptation` as fixed_l1 |
| Fixed L2 | **IMPLEMENTED** `FIXED_L2` / B2_L2 | Small real n=5; sim via harmonized | same | REAL-LLM-EVAL |
| Fixed L3 | **IMPLEMENTED** `FIXED_L3` / B2_L3 | Small real n=5 | same | REAL-LLM-EVAL |
| Full adaptive | **IMPLEMENTED** `FULL_ADAPTIVE` / B3/B6 | Sim EXP-005/006; pilot B6 n=15; infra smoke B6 n=5 | `PolicyUpdateEngine` | PHASE2_7; INFRA-SMOKE; EXP005/006 |
| Escalation-only | **IMPLEMENTED** | Sim EXP-005 (`B_rule_based`→escalation_only) | `allow_deescalation=False` | `EXP005_ADAPTATION/metrics.json` |
| De-escalation-only | **IMPLEMENTED** | Sim EXP-005 | `allow_escalation=False` | same |
| No-cost-gate | **IMPLEMENTED** | Sim EXP-006 `C_no_cost_gate` | `NoCostGateFeedbackEngine` | `EXP006_ABLATION/summary.json` |

**Execution status for publication primary comparison (Full Adaptive vs Fixed L1 on held-out real LLM):** **NOT EXECUTED / BLOCKED**.

---

## 5. Evaluation audit

| Element | Status | Evidence |
|---------|--------|----------|
| Frozen test population | **VERIFIED** | `eval_v1` 770; `benchmark_q1` test hash |
| Shared population across policies | **IMPLEMENTED** in runners | REAL-LLM-EVAL / EXP005 select once, loop baselines |
| Attack/benign distribution | Mixed in `benchmark_q1`; attack-only in `eval_v1` | stats + pilot note |
| Deterministic seeds | Protocol seed **42** common | configs / runners |
| Model / version | GPT-4o-mini (pilot/smoke); Gemini 3.6 Flash (EXP005 smoke) | PHASE2_7, INFRA-SMOKE, Gemini smoke |
| Inference backend | OpenRouter / Gemini Interactions | adapters |
| Temperature / max tokens / system prompt | Documented in configs; Gemini temp/top_p **unsupported** | `configs/models.yaml`, EXP005 config |
| Tool environment | **PARTIAL** (flag only, no rich AgentDojo loop) | action_layer `tool_access` |
| Primary experiment run? | **NO (BLOCKED)** | `docs/FINAL_REAL_LLM_EVALUATION_REPORT.md`; EXP-004 BLOCKED; Gemini full BLOCKED |
| Phase-8 harmonized bundle | **MISSING** | `REPRODUCIBILITY.md` points to `results/phase8/...` — directory **does not exist** |

Do **not** treat `docs/EXPERIMENT_STATUS.md` (dated 2026-09-01) as current; newer COMPLETED REAL-LLM-EVAL runs exist under `results/experiment_runs/` but are **n=5 infrastructure**, not the primary study.

---

## 6. Metrics audit

| Metric | Implemented? | Definition match? | In result files? |
|--------|--------------|-------------------|------------------|
| ASR | **YES** `metrics.py` | successful_attacks / N_a | Yes in sim + pilots |
| Defense Rate | **YES** | 1 − ASR | Yes |
| Utility | **YES** | legitimate_successes / N_l; **None** if N_l=0 | Pilots attack-only → N/A |
| ICS / defense_cost | **YES** | L0=0, L1=0.10, L2=0.25, L3=0.50 | Episode fields; means often null in EXP005 summary |
| Reward | **YES** | `0.5*sec + 0.4*util − 0.1*cost` in `FeedbackEngine` | Computed in sim path; often 0/null in abbreviated JSON |
| Latency | **YES** (real path) | episode/target/judge ms | INFRA-SMOKE, Gemini smoke |

**Not verified:** publication tables of ICS/Reward for a VALID real-LLM full protocol — **NOT EXECUTED**.

---

## 7. Statistical analysis audit

| Item | Implemented | Executed on VALID primary real-LLM results |
|------|-------------|--------------------------------------------|
| Bootstrap 95% CI | **YES** `bootstrap_ci` | **NOT EXECUTED** (no full VALID matrix) |
| McNemar paired | **YES** `mcnemar_test` | **NOT EXECUTED** for Adaptive vs Fixed L1 primary |
| Holm correction | **YES** `holm_correction` | **NOT EXECUTED** |
| Bonferroni α=0.0167 | **NOT found** as coded constant | Docs mention Holm more than Bonferroni; **NOT EXECUTED** |
| Effect size Cohen’s d | **YES** `cohens_d` | **NOT EXECUTED** on primary |
| Multi-seed analysis | Helpers/scripts partial | Seeds **137** and **2025** **not** used in primary executed bundles |

**Full Adaptive vs Fixed L1 McNemar:** **NOT EXECUTED** (no valid paired real-LLM artifact).

---

## 8. Ablation study audit

| Ablation | Implemented | Executed | Mode | Publication-valid? |
|----------|-------------|----------|------|--------------------|
| A Full adaptive | YES | YES (sim) | `LEGACY_SIMULATION_ONLY` | **NO** |
| B Escalation-only | YES | YES (sim EXP-005) | same | **NO** |
| C De-escalation-only | YES | YES (sim EXP-005) | same | **NO** |
| D No-cost-gate | YES | YES (sim EXP-006) | same | **NO** |

Effects of escalation / de-escalation / cost gate are **only heuristically suggested** by simulation numbers in `EXP005_ADAPTATION/metrics.json` and `EXP006_ABLATION/summary.json` (explicit warning: not valid for publication ASR).

---

## 9. Multi-seed / robustness audit

| Seed | Primary real-LLM | Harmonized sim primary |
|------|------------------|------------------------|
| 42 | Used in protocols / smoke / pilots | Used |
| 137 | **NOT EXECUTED** | **NOT FOUND** in result artifacts |
| 2025 | **NOT EXECUTED** | **NOT FOUND** |

Aggregation / variance across seeds for the paper claim: **NOT DONE**.  
Known issue (docs): simulation multi-seed can be identical — see `docs/research/METRICS_AND_STATISTICS.md`.

---

## 10. Category-level analysis

| Category family | In dataset | Per-category real-LLM results |
|-----------------|------------|-------------------------------|
| Prompt injection | YES | **MISSING** (full protocol) |
| RAG security | YES (`rag_injection`) | **MISSING** |
| Safety / jailbreak | YES (jailbreak heavily BeaverTails-mapped) | **MISSING** |
| Benign | YES in benchmark_q1 | Pilots often attack-only |
| Jailbreak | YES | **MISSING** |
| Agent security | YES but n=28 | **MISSING**; insufficient for agent claims |

Subtype analysis for publication: **TODO** after VALID runs (`EXP005` runner has hooks for per-category ASR but no VALID full output).

---

## 11. Current empirical results

### A. VERIFIED EXECUTED RESULTS (proven artifacts)

| Experiment | Model | Dataset | Episodes | Policy | Result | Evidence |
|------------|-------|---------|---------:|--------|--------|----------|
| Gemini preflight | gemini-3.6-flash | probe | 1 | — | VALID | `results/real_llm/.../EXP005-20260903-081324/preflight.json` |
| Gemini smoke | gemini-3.6-flash | benchmark_q1 subsample | 2 prompts × (target+judge)=4 calls | B0 only | VALID | `.../EXP005-20260903-081350/smoke.json` |
| Gemini full EXP005 | gemini-3.6-flash | planned 24×4 | 0 success | B0–B3 planned | **BLOCKED** 429 | `.../EXP005-20260903-083258/metrics.json` |
| PHASE2_7_PILOT | gpt-4o-mini | frozen eval_v1 | 15 | B0, B6 | ASR **2/15 both** | `experiments/PHASE2_7_PILOT/{REPORT.md,metrics.json,predictions.jsonl}` — **pilot only** |
| INFRA-SMOKE-001 | gpt-4o-mini | benchmark_q1 test n=5 | 5×2 | B0, B6 | ASR 0.0 both; util 1.0 | `experiments/INFRA-SMOKE-001/summary.json` — infra |
| REAL-LLM-EVAL runs | openrouter | test n=5 | 5×6 baselines | B0–B3 | COMPLETED n=5 (ASR 0.0 reported) | `results/experiment_runs/REAL-LLM-EVAL/RUN-20260902-*/metrics.json` — **not primary N** |
| OPENROUTER_SMOKE (earlier) | gpt-4o-mini + Claude | smoke | 2 calls | — | HTTP 200 at that time | `experiments/OPENROUTER_SMOKE_TEST/results.json` |
| EXP-004 current | openrouter | frozen 150 planned | — | B0 vs B6 | **BLOCKED** 401 | `experiments/EXP-004/BLOCKED_REPORT.md` |
| EXP-005 adaptation | simulation | stream/sim n=20 | 20 | fixed_l1 / esc / deesc / full | COMPLETED sim | `experiments/EXP005_ADAPTATION/metrics.json` |
| EXP-006 ablation | simulation | 20 | 20 | A–F variants | COMPLETED sim | `experiments/EXP006_ABLATION/summary.json` |
| EXP-008 adaptive attack | detector sim | 3×50 | 150 | detector | block_rate 0.0 | `experiments/EXP008_ADAPTIVE_ATTACK/metrics.json` |
| EXP-017 detector | regex detector | NotInject smoke 1000 | 1000 | detector | F1≈0.802 | `experiments/runs/EXP-017_V17/metrics.json` |
| EXP-017 held-out (recorded) | same | NotInject valid 144 | 144 | detector | F1≈0.41 | same file `held_out_validation` |
| Harmonized Phase-8 primary | — | 100 stream | 100 | all PolicyModes | **ARTIFACTS MISSING** | `results/phase8/` absent despite `REPRODUCIBILITY.md` |

### B. IMPLEMENTED BUT NOT EXECUTED (publication-scale)

- Full EXP005 Gemini B0–B3 on held-out mixed test (planned 24 samples × 4)
- EXP-004 multi-model frozen eval_v1 n=150
- Real-LLM ablations (escalation-only / de-escalation-only / no-cost-gate)
- Multi-seed 42/137/2025 real-LLM
- Category/subtype real-LLM tables
- McNemar Adaptive vs Fixed L1 with Holm/Bonferroni on real data

### C. PLANNED

- See `docs/research/PHASE2_EXPERIMENT_MANIFEST.md`, `docs/MANUSCRIPT_EVIDENCE_MAP.md` (many TBD / NOT_RUN)

---

## 12. Reproducibility audit

| Element | Status |
|---------|--------|
| `requirements.txt` / `requirements-core.txt` | Present |
| Python | Documented 3.12; local venv used historically |
| Model config | `configs/models.yaml` |
| Dataset hashes | **YES** for benchmark_q1 + eval_v1 + attack stream |
| Seeds | Documented (esp. 42) |
| CLI runners | Extensive under `scripts/` and `experiments/*/run.py` |
| Output dirs | Convention exists; `results/` partially gitignored |
| Phase-8 frozen bundle | **MISSING on this disk** |
| API credentials | External; currently OpenRouter **401**, Gemini **429** |

**Reproducibility score: 5.5 / 10**  
Strong hashing and scripts; weak because primary result directories are missing/blocked and API state prevents re-execution without new credentials/quota.

---

## 13. Paper readiness audit

Source of truth: `docs/MANUSCRIPT_DRAFT.md` (no `paper/` or `manuscript/` directory).

| Section | Status |
|---------|--------|
| Introduction | **PARTIAL** |
| Related Work | **PARTIAL** |
| Methodology | **PARTIAL** (implementation described) |
| Benchmark | **PARTIAL** (q1 described; gaps honest in limitations) |
| Experimental Setup | **PARTIAL** / **BLOCKED** models |
| Results | **MISSING** genuine primary results (placeholders **[BLOCKED]**) |
| Ablation | **PARTIAL** simulation only |
| Statistical Analysis | **MISSING** executed primary stats |
| Discussion | **MISSING** |
| Limitations | **PARTIAL** (updated with API/quota blockers) |
| Conclusion | **BLOCKED** |

Results section does **not** contain genuine full-protocol experimental results suitable for Q1 claims.

---

## 14. Q1 readiness scores (0–10)

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| A. Research idea | 7 | Clear security–utility–cost tradeoff question |
| B. Novelty | 5 | Incremental vs AgentDojo/guards; agent evaluation thin |
| C. Implementation | 7.5 | Solid modular defense + eval stack |
| D. Dataset/benchmark | 6 | Large q1 + hashes; missing BIPIA/NotInject; agent n=28 |
| E. Experimental evaluation | 2.5 | Only pilots/smoke real LLM; primary BLOCKED |
| F. Statistical rigor | 4 | Code ready; primary analysis not run |
| G. Reproducibility | 5.5 | Hashes/scripts good; phase8 missing; APIs blocked |
| H. Paper completeness | 3 | Draft gated; no real Results |

**Overall readiness: 4.0 / 10 (~35%).** Submission-ready: **NO**.

---

## 15. Critical blockers (priority)

### P0

1. **No VALID full real-LLM policy comparison**  
   - Missing: B0/B1/B2/B3 (or Fixed L0–L3 + Full Adaptive) on held-out mixed set with blind judge  
   - Files: `experiments/EXP005_GEMINI_FLASH/run.py`, `experiments/EXP-004/run.py`  
   - Why: Core RQ unanswered for publication  
   - Action: Restore paid Gemini quota **or** working OpenRouter key; re-run full protocol; refuse fabrication  

2. **OpenRouter HTTP 401**  
   - Evidence: `experiments/EXP-004/BLOCKED_REPORT.md`  
   - Action: Replace/re-auth key  

3. **Gemini free-tier HTTP 429 (limit 20)**  
   - Evidence: `docs/FINAL_REAL_LLM_EVALUATION_REPORT.md`, `.../EXP005-20260903-083258/metrics.json`  
   - Action: Billing upgrade or alternate provider  

### P1

4. **Phase-8 harmonized result tree missing** despite `REPRODUCIBILITY.md`  
   - Path: `results/phase8/q1_harmonized_v1/`  
   - Action: Re-run `scripts/run_q1_harmonized_v1.py` and freeze artifacts **as simulation-labeled** if kept  

5. **Independent judge model family unavailable**  
   - Claude Sonnet via OpenRouter blocked; Gemini same-family judge documented as limitation  

6. **Agent evaluation underpowered** (28 tool samples)  
   - Action: Expand AgentDojo/InjecAgent before agent-title claims  

7. **NotInject/BIPIA not in unified benchmark; NotInject raw absent**  

### P2

8. Multi-seed 137/2025  
9. Publication figures generation  
10. Human judge subset  
11. True SOTA baselines without regex fallback  

---

## 16. Completion plan (shortest reliable path)

### PHASE 1 — Fix/verify infrastructure
- Task: Valid API (OpenRouter **or** paid Gemini); `pytest -q`; preflight+smoke VALID  
- Command: `experiments/EXP005_GEMINI_FLASH/run.py --preflight-only` / `--smoke-only` or EXP-004 preflight  
- Artifact: VALID smoke JSON  
- Criterion: smoke VALID, no auth/quota errors  

### PHASE 2 — Freeze benchmark
- Task: Confirm test hash `fa35c657…` (mixed) or eval_v1 `27b1733c…` (attack-only); document choice  
- Artifact: config+provenance with hash  
- Criterion: hash match; split = test  

### PHASE 3 — Run baseline experiments
- Task: B0, B1, B2_L1 (and L2/L3 if required) on **same** held-out IDs  
- Command: EXP005 or REAL-LLM pipeline with fixed N≥ sufficient power  
- Artifact: per-baseline predictions.jsonl + metrics  
- Criterion: status VALID; judge_failures=0  

### PHASE 4 — Run adaptive-policy experiments
- Task: B3 / full_adaptive on identical IDs  
- Artifact: paired rows vs B0/Fixed L1  
- Criterion: VALID  

### PHASE 5 — Run ablations
- Task: escalation-only, de-escalation-only, no-cost-gate on **real LLM** (not only sim)  
- Artifact: ablation metrics + raw  
- Criterion: VALID or explicitly scoped sim  

### PHASE 6 — Multi-seed robustness
- Task: seeds 42, 137, 2025 (or protocol seeds)  
- Artifact: aggregated mean±CI  
- Criterion: non-identical variance documented  

### PHASE 7 — Statistical analysis
- Task: McNemar Full Adaptive vs Fixed L1; Holm (or Bonferroni α=0.0167 if required by protocol); bootstrap; effect sizes  
- Command: EXP-004 `analyze.py` / EXP005 stats in runner  
- Artifact: `statistics.json` with p, adj-p, CI, effect  
- Criterion: numbers trace to raw JSONL  

### PHASE 8 — Category/subtype analysis
- Task: ASR/FPR/utility by category  
- Artifact: per-category tables  
- Criterion: all categories with n≥ protocol minimum  

### PHASE 9 — Generate final tables/figures
- Task: Build from machine-readable metrics only  
- Artifact: `figures/` + manuscript tables  
- Criterion: every number has provenance path  

### PHASE 10 — Update manuscript
- Task: Promote Results only from VALID real-LLM; keep sim labeled  
- Artifact: updated `docs/MANUSCRIPT_DRAFT.md` / camera-ready  
- Criterion: claim–evidence audit PASS  

**Shortest path:** Fix API (P0) → EXP005 full VALID on mixed held-out (B0/B1/B2_L1/B3) → stats → manuscript. Parallel: regenerate phase8 sim bundle for infrastructure paper section only.

---

## 17. Final answer

## CURRENT STATUS

Research implementation: **72%**

Experimental execution: **18%**

Dataset readiness: **65%**

Statistical analysis: **35%** (code high; executed primary **~5%**)

Paper readiness: **28%**

Overall project readiness: **35%**

## DONE

- Modular L0–L3 defense + adaptive controller + cost-aware feedback (code + tests)
- Harmonized runner + eight policy modes (implemented)
- Metrics ASR / Defense Rate / Utility / ICS table / Reward weights (implemented)
- Statistics helpers: bootstrap, McNemar, Holm, Cohen’s d (implemented)
- `benchmark_q1` built with hashes; frozen `eval_v1`; frozen attack stream SHA recorded
- Real-LLM pipeline + Gemini Interactions adapter + provenance
- Offline tests largely green historically (`pytest` suite present)
- VALID Gemini smoke; PHASE2_7 real pilot (n=15); INFRA-SMOKE (n=5)
- Honest BLOCKED reports for EXP-004 and Gemini full run

## PARTIALLY DONE

- Manuscript draft (methods/limitations; Results blocked)
- Dataset coverage (strong on some sources; weak agent; missing BIPIA/NotInject)
- Simulation ablations executed (not publication-valid)
- Small real-LLM runs (n=5–15) — infrastructure only
- De-escalation pathway coded but weakly evidenced under default workloads
- Reproducibility docs vs missing `results/phase8/`

## NOT DONE

- VALID full real-LLM fixed vs adaptive comparison
- Executed McNemar/Holm/CI/effect sizes on that comparison
- Multi-seed 137/2025 primary runs
- Category/subtype real-LLM tables
- Publication figures from VALID data
- Independent-model judge at scale
- Agent-scale evaluation
- Integration of NotInject/BIPIA/AdvBench/HarmBench/AgentHarm/PromptBench into unified benchmark

## BLOCKED

- OpenRouter authentication (HTTP 401) for EXP-004 / Claude judge
- Gemini free-tier quota (HTTP 429, limit 20) for full EXP005
- Primary Phase-8 result artifacts missing on disk
- Q1 Results claims until VALID matrix exists

## NEXT 5 ACTIONS

1. **Restore usable LLM API quota/auth** (paid Gemini and/or valid OpenRouter).  
2. **Re-run EXP005 full protocol** (or EXP-004) to **VALID** with raw+judge+metrics+stats.  
3. **Compute Adaptive vs Fixed L1 McNemar + CI + effect size + multiple-comparison correction** from those artifacts only.  
4. **Regenerate or relocate Phase-8 harmonized sim bundle** and label it Simulation / Infrastructure Validation.  
5. **Update manuscript Results solely from VALID real-LLM traces**; keep pilots/sim out of primary claims.

## DEFINITION OF "PROJECT COMPLETE"

We may honestly say *"ADAPTI-GUARD is experimentally complete and paper-ready"* only when **all** of the following exist:

1. Held-out dataset hash recorded; shared sample IDs across policies.  
2. Real target LLM + blind judge evaluation for **Fixed L0–L3 (or B0/B1/B2) and Full Adaptive** with status **VALID**.  
3. Raw model outputs + judge JSONL preserved; no simulation ASR in primary tables.  
4. Metrics: ASR, Defense Rate, Utility, FPR (if benign present), ICS/cost, latency.  
5. Statistics: bootstrap 95% CIs; McNemar Full Adaptive vs Fixed L1; multiple-comparison correction; effect size.  
6. Ablations (escalation / de-escalation / cost gate) either real-LLM VALID or explicitly non-primary.  
7. Every manuscript quantitative claim traces: raw → judge → metric → stats → table.  
8. Reproducibility pack: commands, configs, hashes, git commit, environment.  
9. Independent scientific audit status **PASS** (not FAIL/WARN on primary claims).

Until then, maximum honest statement: **infrastructure and protocol are largely ready; primary empirical evaluation remains incomplete and blocked.**

---

## Appendix — Key evidence paths

- `datasets/benchmark_q1/statistics.json`, `hashes.json`
- `datasets/frozen/eval_v1/manifest.json`
- `results/common_attack_stream.json`
- `src/adapti_guard/experiments/harmonized_runner.py`
- `src/adapti_guard/defense/action_layer.py`
- `src/adapti_guard/adaptation/feedback_engine.py`
- `src/adapti_guard/evaluation/{metrics,statistics,target_model,llm_judge}.py`
- `docs/FINAL_REAL_LLM_EVALUATION_REPORT.md`, `docs/FINAL_Q1_SCIENTIFIC_AUDIT.md`
- `experiments/EXP-004/BLOCKED_REPORT.md`
- `experiments/PHASE2_7_PILOT/REPORT.md`
- `REPRODUCIBILITY.md` (note missing `results/phase8/`)
- `docs/MANUSCRIPT_DRAFT.md`
