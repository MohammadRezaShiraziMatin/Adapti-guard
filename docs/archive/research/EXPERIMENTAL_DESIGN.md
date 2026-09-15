# ADAPTI-GUARD — Experimental Design Blueprint

**Phase 1 Audit | Date:** 2026-09-02  
**Minimum publication-valid suite for Phase 2**

---

## 0. Evidence Status Summary

| Experiment | Mode | n executed | Publication-valid? |
|------------|------|------------|-------------------|
| EXP-000 API smoke | — | 0 | No (BLOCKED) |
| EXP-002 real LLM | real_llm_judge | 5 (all 401) | **INVALID** |
| EXP-003 baselines | — | 0 | NOT_RUN |
| EXP-004 multi-model | real_llm_judge | 0 | BLOCKED |
| EXP-005 adaptation | LEGACY_SIMULATION | 20 × 1 seed | **No** |
| EXP-006 ablation | LEGACY_SIMULATION | 20 episodes | **No** |
| EXP-008 adaptive attack | DETECTOR_SIM | 150 | **No** |
| EXP-016/017/018 detector | NotInject | 1000/1000/144 | Detector-only |
| REAL-LLM-EVAL | — | 0 | BLOCKED |

**Valid real-LLM attack ASR measurements: 0**

---

## 1. Baseline Design (B0–B6)

| ID | Name | Required implementation | Current status |
|----|------|-------------------------|----------------|
| **B0** | No Defense | Passthrough prompt | ✅ `make_b0_no_defense()` |
| **B1** | Static Sanitization | Sanitize always, never block | ❌ Not implemented (B1 currently = threshold block) |
| **B2** | Fixed Blocking | Fixed L2 block policy | ✅ `make_b2_fixed_defense(2)` |
| **B3** | Fixed Tool Restriction | Fixed L2 + tool_sensitive logic | ❌ Not distinct; needs tool eval |
| **B4** | Static Threshold | Detector τ=0.25 → block | ✅ `make_b1_rule_based(0.25)` |
| **B5** | Strong guard baseline | **Real** Llama-Guard-3-8B or Prompt Guard API | ❌ Regex fallback only |
| **B6** | ADAPTI-GUARD | Full adaptive pipeline | ✅ `AdaptiveDefenseState` |

**Critical rule:** Do not publish B5 results until real guard model API is wired. Regex-at-different-threshold is self-comparison.

**Alternative strong B5:** OpenAI Moderation API, Azure Prompt Shields, or Meta Llama-Guard-3 via HuggingFace — must log exact model ID and version date.

---

## 2. Model Generalization Matrix

### API Models (configs/models.yaml)

| Key | Exact model ID | Provider | Temp | max_tokens | Status |
|-----|----------------|----------|------|------------|--------|
| model_a | `openai/gpt-4o-mini` | OpenRouter | 0.0 | 512 | BLOCKED |
| model_b | `qwen/qwen3-30b-a3b` | OpenRouter | 0.0 | 512 | BLOCKED |
| model_c | `deepseek/deepseek-chat-v3-0324` | OpenRouter | 0.0 | 512 | BLOCKED |
| model_d (opt) | `anthropic/claude-sonnet-4` | OpenRouter | 0.0 | 512 | OPTIONAL |

### Local Models (configs/models_local.yaml)

| Key | Exact model ID | Provider | Params | Status |
|-----|----------------|----------|--------|--------|
| local_qwen25_3b | `qwen2.5:3b-instruct` | Ollama | 3B | BLOCKED (Ollama down) |
| local_llama32_3b | `llama3.2:3b-instruct` | Ollama | 3B | BLOCKED |
| local_phi35_mini | `phi3.5:mini-instruct` | Ollama | 3.8B | BLOCKED |
| local_mistral_7b | `mistral:7b-instruct-v0.3` | Ollama | 7B | BLOCKED |

### Judge (independent)

| Role | Model ID | Notes |
|------|----------|-------|
| Primary | `anthropic/claude-sonnet-4` | Same as optional target — conflict if both run |
| Fallback | `openai/gpt-4o` | On primary failure |

**System prompt:** Must be fixed and logged per `docs/JUDGE_PROTOCOL.md`.

---

## 3. Dataset Design

### Current counts

| Set | Samples | Purpose |
|-----|---------|---------|
| benchmark_q1 train | 10,537 | Detector training (if used) |
| benchmark_q1 validation | 2,257 | Dev tuning |
| benchmark_q1 test | 2,259 | **Primary held-out eval** |
| attack_dataset.json | 528 attacks | Q1 eval subset (incomplete) |

### Critical distinction

**528 prompts ≠ 528 valid LLM experiments.**  
Each prompt × model × baseline × (target + judge) calls = budget multiplier.

Example: 500 episodes × 7 baselines × 3 models × 2 LLM calls ≈ **21,000 API calls** (estimate).

### Split policy

| Set | Use | Leakage prevention |
|-----|-----|-------------------|
| **Development** | Tune τ, thresholds, schedule | Never report as test |
| **Validation** | Select fixed L* for RQ2 | Single pass only |
| **Test** | All manuscript numbers | Frozen before EXP-004 |
| **attack_dataset** | Rebuild from benchmark_q1 with hash lock | No adaptive template overlap with test IDs |

**Current leak risk:** Adaptive templates derived from same news/RAG corpus as test — lexical overlap audit required.

---

## 4. Experiment Suite (Phase 2 Minimum)

### EXP-004 — Main multi-model (PRIMARY)

- **Design:** B0, B6 on all models; optional B2_L2, B4
- **n:** ≥500 episodes (stratified by category)
- **Schedule:** W1 (75% attack / 25% benign)
- **Output:** `predictions.jsonl`, `metrics.json`, statistical report
- **Gate:** `evaluation_mode=real_llm_judge`, auth_errors=0

### EXP-003 — Full baseline comparison

- **Design:** B0–B6 on model_a
- **n:** ≥500
- **Output:** `comparison_table.csv` (filled)

### EXP-006 — Ablation (real LLM)

- **Design:** Variants A, C, E, F minimum
- **n:** ≥300 per variant
- **Wire:** B_no_risk_engine hook (currently identical in sim)

### EXP-009 — Long-term adaptation

- **Design:** 1000 episodes, 5 phases (config exists)
- **n:** 1000 on model_a + 1 local model
- **Output:** time-series figures

### HUMAN-EVAL — Judge calibration

- **n:** 200 episodes, 2 annotators
- **Metric:** Cohen's κ vs LLM judge

### EXP-AGENT (NEW — required for agent claims)

- **Design:** AgentDojo subset with tool sandbox
- **n:** ≥100 security test cases
- **Baselines:** B0, B2_L2, B6

---

## 5. Ablation Design (Verified Components)

| Variant | Real component? | Implementation path |
|---------|-----------------|---------------------|
| A Full | Yes | `PolicyMode.FULL_ADAPTIVE` |
| B −Risk Engine | Partial | **Needs bypass** — currently no effect in sim |
| C −Cost Gate | Yes | `PolicyMode.NO_COST_GATE` |
| D Fixed L2 | Yes | `PolicyMode.FIXED_L2` |
| E −Feedback | Partial | Proxy as fixed — needs feedback disable |
| F −Escalation | Yes | `PolicyMode.DE_ESCALATION_ONLY` |

---

## 6. Failure Analysis (Pre-registered)

See `docs/failure_analysis_protocol.md`:
- 10+ successful attacks (ASR despite defense)
- 10+ false positives (benign blocked)
- Module attribution: detector / risk / policy / action / adaptation / judge

---

## 7. Reproducibility Checklist (Per Run)

- [ ] Git commit hash logged
- [ ] `OPENROUTER_API_KEY` fingerprint (not secret)
- [ ] Exact model ID strings
- [ ] Dataset file SHA-256 (`hashes.json`)
- [ ] Seed, n_samples, baseline list
- [ ] Judge primary/fallback model
- [ ] `evaluation_mode` in every metrics.json
- [ ] Raw `predictions.jsonl` retained

---

## 8. What NOT to Run for Publication

- `harmonized_runner` ASR for manuscript claims
- EXP-005/006 simulation numbers
- EXP-008 block_rate
- EXP-002 stale run dir (`results/experiment_runs/EXP-002/...` still shows ASR=0 fraud risk)
- Any baseline labeled Llama Guard without model load
