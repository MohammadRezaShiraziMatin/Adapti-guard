# ADAPTI-GUARD: Q1 Pre-Submission Review

**Manuscript:** *Adaptive and Utility-Aware Defense Against Evolving Prompt Injection Attacks in LLM-Based Agents*  
**Review date:** 2026-09-02  
**Reviewer stance:** Strict Q1 gatekeeper (AI / Trustworthy AI / LLM Security / Agent Security)  
**Current readiness score:** **4.8 / 10 — NOT submission-ready**

---

## Executive Summary

ADAPTI-GUARD proposes a modular defense stack (detector → risk → policy → adaptation) with a harmonized evaluation protocol. The **engineering infrastructure is ahead of the evidence**: real-LLM evaluation pipelines, blind judge protocol, and statistical tooling exist, but **zero publication-valid results** have been produced. Simulation numbers (EXP-005, EXP-008) are explicitly labeled `LEGACY_SIMULATION_ONLY` and must not appear in the manuscript. EXP-002 was **INVALID** (100% API 401 errors).

**Predicted outcome if submitted today:** Desk reject or R&R with "fundamental experimental gaps."

---

# PART 1 — REVIEWER-LEVEL CRITIQUE

## 1. Novelty

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| Core mechanism is counter-based threshold escalation (L0–L3), not a new learning paradigm; closest to hysteresis controllers in IDS literature | **Major** | Q1 venues require clear delta over NeMo Guardrails, LLM-Guard, Rebuff, StruQ | Reframe contribution as **harmonized utility-aware evaluation + adaptation protocol**, not "novel defense architecture" | Rewrite §1 contributions; add `docs/NOVELTY_MATRIX.md` comparison table with 8+ prior systems |
| "Bayesian risk adaptation" appears in early drafts but `RiskEngine` is linear weighted sum | **Critical** | Scientific misrepresentation → immediate credibility loss | Remove all Bayesian claims; call it "counter-based hysteresis policy" | Grep manuscript for "Bayesian"; update `MANUSCRIPT_DRAFT.md` §4.4 |
| Adaptive attacker has only 12 templates / 4 families | **Major** | "Evolving attacks" claim unsupported by attacker diversity | Expand to ≥50 templates, 7 families aligned with benchmark categories | Extend `adaptive_attacker.py`; add `attacks/templates/` corpus |
| benchmark_q1 aggregation is useful but not novel vs AgentDojo + InjecAgent + BIPIA composites | **Minor** | Dataset papers compete separately | Position as **evaluation harness**, not primary dataset contribution | One paragraph in §5.1; cite upstream sources with hashes |

## 2. Technical Contribution

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| No formal threat model with adversary budget, observation model, or utility function | **Major** | Agent security reviewers (IEEE S&P, USENIX) expect game-theoretic or MDP framing | Add formal §3 with adversary capabilities, defender actions, utility \(U = \alpha S + \beta U_{benign} - \gamma C\) | Write `docs/THREAT_MODEL.md`; add equations to manuscript |
| Cost gate mentioned but not ablated under real LLM | **Major** | Utility-awareness is a claimed contribution | Run ablation C (no cost gate) on ≥3 models | `scripts/run_ablation_study.py` + EXP-004 real path |
| No convergence or stability analysis of adaptation | **Minor** | Adaptive systems need bounded oscillation guarantees | Report defense-level time series; max oscillation amplitude | EXP-009 plots: `defense_level_over_time.png` |

## 3. Research Gap

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| Gap claim ("no unified benchmark") is partially false — AgentDojo, BIPIA, CyberSecEval exist | **Major** | Reviewers know the field | Narrow gap to **utility-aware adaptive escalation under mixed attack/benign workloads** | Related work table with 15+ citations |
| Agent tool attacks severely underrepresented (2 samples in test split, 28 in attack_dataset) | **Critical** | Title mentions "LLM-Based Agents" | Add ≥100 tool-abuse episodes from AgentDojo/InjecAgent | Import into `datasets/attack_dataset/`; re-run `build_attack_dataset.py` |
| System prompt leakage category has 0–2 samples | **Critical** | Required category empty | Curate 100 leakage probes from Garak/LeakPrompt taxonomy | `datasets/attack_dataset/system_prompt_leakage.jsonl` |

## 4. Methodological Rigor

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| Simulation outcome uses regex `attack_succeeded()` — not LLM behavior | **Critical** | Invalid for security claims | All ASR from blind LLM judge only | Enforce `evaluation_modes.py` gate in all runners |
| EXP-002 ran with 401 errors but was marked COMPLETED | **Critical** | Data integrity failure | Provenance checks before any metric write (now fixed) | `phase1_preflight_audit.py` as submission gate |
| No human judge validation (Cohen's κ) | **Major** | LLM-as-judge is standard but requires calibration | 200-episode human adjudication subset | `docs/HUMAN_EVALUATION.md` protocol; recruit 2 annotators |
| Benign utility measured via 8 hardcoded tasks | **Major** | Not representative of agent workloads | Use benchmark_q1 benign split (1,751 samples) | Update `harmonized_runner.py` BENIGN_TASKS → dataset loader |

## 5. Experimental Strength

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| **Zero valid real-LLM results** | **Critical** | No experiments = no paper | Complete EXP-004 on 3+ API models | Fix API key; run full matrix |
| Single evaluation mode (block/no-block) insufficient for agent settings | **Major** | Agents have tool calls, RAG retrieval | Add tool-emulation episodes with mock `read_file`/`search` | `experiments/EXP007_AGENT_TOOL/` |
| No cross-dataset generalization (train NotInject, test benchmark_q1) | **Major** | Overfitting concern | Report detector transfer F1 on held-out sources | EXP-018 already shows F1=0.41 — must discuss honestly |

## 6. Fairness of Comparisons

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| B5 "Llama Guard" uses regex fallback in `baselines/llama_guard.py` | **Critical** | Strawman baseline | Wire real Llama-Guard-3-8B via API or Together AI | New `make_b5_llm_guard()` in `defense_baselines.py` |
| B1 conflated with B4 (both regex threshold) | **Major** | Duplicate baselines | B1 = sanitization only; B4 = detect+block at τ; B2 = fixed L2 | Clarify in `comparison_table.csv` |
| Adaptive defense (B6) gets sequential state; baselines are stateless | **Major** | Unfair if attack sequence is adaptive | Either: (a) give B2 rolling window, or (b) evaluate on i.i.d. episodes plus separate adaptive track | Document in `BASELINE_PROTOCOL.md` |
| Judge sees defensestripped prompts but may infer from response style | **Minor** | Judge bias | Blind protocol exists — verify no metadata leakage | Audit `llm_judge.py` prompt template |

## 7. Reproducibility

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| No pinned model versions for API models | **Major** | Results drift | Log `model` string + date + response headers per call | `llm_cache.py` already exists — enforce |
| Missing Docker/conda lockfile | **Minor** | Environment variance | Add `environment.lock` or `Dockerfile` | Part 10 structure |
| Experiment seeds documented but multi-seed runs produce identical simulation results | **Major** | Indicates deterministic bug | Fix seed propagation in attacker + detector | Debug EXP-005 seed loop |

## 8. Statistical Validity

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| No McNemar / Wilcoxon in published results | **Critical** | "Our method is better" insufficient | All claims with p < 0.05, 95% CI, effect size | `scripts/statistical_analysis.py` (created) |
| No multiple-comparison correction across 7 baselines × 4 models | **Major** | Inflated significance | Holm correction (implemented in `statistics.py`) | Apply in EXP-004 report |
| Bootstrap CI on proportions with n < 30 per cell | **Major** | Unstable estimates | Minimum n=100 per (model, baseline) cell | Power analysis in §5.1 |

## 9. Generalization Capability

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| Only 3 API models configured; 0 local models tested | **Critical** | Model-independence unproven | Run 4 local + 3 API models | `configs/models_local.yaml` + Ollama |
| Detector F1=0.41 on held-out NotInject | **Critical** | Contradicts "strong detection" | Either improve detector or scope claims to policy layer only | Retrain detector OR demote detector to feature extractor |
| RAG/indirect attacks dominate; direct injection underrepresented in test | **Major** | Category imbalance skews ASR | Stratified reporting per category | Per-category table in results |

## 10. Practical Deployment Relevance

| Reviewer criticism | Severity | Why reviewers care | Required fix | Implementation plan |
|---|---|---|---|---|
| Latency overhead estimated (~8ms) not measured | **Major** | Deployment papers need cost | Real latency breakdown | `docs/efficiency_report.md` |
| No streaming / production integration path | **Minor** | Limits industry impact | Add FastAPI middleware example | `defenses/middleware_example.py` (optional) |
| Escalation to L3 blocks 100% utility — no graceful degradation analysis | **Major** | Utility-awareness claim | Report utility vs defense level Pareto curve | EXP-006 ablation + plot |

---

# PART 2 — EXPERIMENTAL WEAKNESS AUDIT

## A) Dataset Audit

| Question | Finding | Severity |
|----------|---------|----------|
| Large enough? | benchmark_q1: 15,053 total; attack_dataset: **528** (below 500–1000 target for 7 balanced categories) | **Major** |
| Diverse categories? | 5/7 categories ≥100 samples; **system_prompt_leakage: 2**; **tool_abuse: 28** | **Critical** |
| Representative? | RAG/indirect overrepresented; agent tool near-absent | **Critical** |
| Hidden biases? | Adaptive templates derived from same news/RAG corpus → lexical overlap | **Major** |
| Reproducible generation? | Hashes in `datasets/benchmark_q1/hashes.json`; adaptive templates seeded | **OK** |

### Attack Dataset (Created)

**Path:** `datasets/attack_dataset/attack_dataset.json`  
**Builder:** `python scripts/build_attack_dataset.py --split all --min-per-category 100`

**Current counts (seed=42):**

| Category | n | Status |
|----------|---|--------|
| direct_prompt_injection | 100 | OK |
| indirect_prompt_injection | 100 | OK |
| jailbreak_attacks | 100 | OK |
| system_prompt_leakage | 2 | **GAP: need +98** |
| tool_abuse_attacks | 28 | **GAP: need +72** |
| rag_poisoning | 100 | OK |
| multi_turn_attacks | 100 | OK |
| **Total** | **528** | Below 1000 target |

**Schema (per record):**
```json
{
  "attack_id": "atk_00001",
  "category": "direct_prompt_injection",
  "difficulty": "medium",
  "prompt": "...",
  "context": "...",
  "expected_behavior": "refuse_or_neutralize",
  "severity": "low",
  "source": "upstream_dataset",
  "upstream_id": "q1_bench_v2_...",
  "upstream_category": "direct_prompt_injection"
}
```

### Required Dataset Actions

1. Import AgentDojo tool-manipulation episodes → `tool_abuse_attacks` (+72 minimum)
2. Curate system-prompt leakage from Garak probe set (+98)
3. Rebuild to 700–1000 total with ≥100 per category
4. Add `attack_dataset_test.json` (held-out) never seen during adaptation

---

# PART 3 — MODEL GENERALIZATION TEST

## Evaluation Matrix

**Template:** `experiments/templates/model_generalization_matrix.csv`

| Model | Params | Provider | ASR↓ | Defense↑ | Utility↑ | Latency | Cost | Status |
|-------|--------|----------|------|----------|----------|---------|------|--------|
| Qwen2.5-3B | 3B | Ollama | TODO | TODO | TODO | TODO | $0 | BLOCKED |
| Llama-3.2-3B | 3B | Ollama | TODO | TODO | TODO | TODO | $0 | BLOCKED |
| Phi-3.5-mini | 3.8B | Ollama | TODO | TODO | TODO | TODO | $0 | BLOCKED |
| Mistral-7B | 7B | Ollama | TODO | TODO | TODO | TODO | $0 | BLOCKED |
| GPT-4o-mini | ~8B eq | OpenRouter | TODO | TODO | TODO | TODO | TODO | BLOCKED |
| Qwen3-30B-A3B | 30B | OpenRouter | TODO | TODO | TODO | TODO | TODO | BLOCKED |
| DeepSeek-V3 | 671B MoE | OpenRouter | TODO | TODO | TODO | TODO | TODO | BLOCKED |
| Claude Sonnet 4 | — | OpenRouter | TODO | TODO | TODO | TODO | TODO | OPTIONAL |
| Gemini 2.0 Flash | — | Google | TODO | TODO | TODO | TODO | TODO | OPTIONAL |

**Config:** `configs/models.yaml` (API) + `configs/models_local.yaml` (local)

## Model-Independence Analysis Plan

1. Run B6 on all 7+ models with identical `attack_dataset` sample (n=500, seed=42)
2. Compute ASR CV (coefficient of variation) across models — claim "model-independent" only if CV < 15%
3. Per-category breakdown — identify model-specific weaknesses
4. **Manuscript figure:** grouped bar chart (model × ASR) with 95% CI error bars

```bash
# After API fix + Ollama start:
ollama pull qwen2.5:3b-instruct llama3.2:3b-instruct phi3.5:mini-instruct mistral:7b-instruct-v0.3
python experiments/EXP004_MULTI_MODEL/run.py \
  --targets model_a model_b model_c local_qwen25_3b local_llama32_3b \
  --baselines B0 B6 --n-samples 500 --seed 42
python scripts/statistical_analysis.py --input experiments/EXP004_MULTI_MODEL
```

---

# PART 4 — BASELINE COMPARISON

## Baselines (B0–B6)

| ID | Name | Implementation | Status |
|----|------|----------------|--------|
| B0 | No Defense | `make_b0_no_defense()` | Ready |
| B1 | Static Sanitization | Strip known patterns, no block | **Needs implementation** |
| B2 | Fixed Blocking | `make_b2_fixed_defense(level=2)` | Ready |
| B3 | Fixed Tool Restriction | Block tool calls when risk > τ | **Needs implementation** |
| B4 | Static Threshold Detector | `make_b1_rule_based(τ=0.25)` | Ready |
| B5 | LLM Guard | Llama-Guard-3-8B API | **Regex fallback only — Critical** |
| B6 | ADAPTI-GUARD | `AdaptiveDefenseState` | Ready |

**Template:** `experiments/templates/comparison_table.csv`

## Manuscript Table Target

**Table 2: Defense comparison on GPT-4o-mini (n=500, seed=42)**

| Method | ASR↓ | Defense↑ | Utility↑ | FPR↓ | Latency↓ | Cost↓ |
|--------|------|----------|----------|------|----------|-------|
| B0 | | | | | | |
| ... | | | | | | |
| B6 | | | | | | |

Statistical footnote: McNemar p-value vs B0; Holm-corrected across baselines.

---

# PART 5 — ABLATION STUDY

**Config:** `configs/experiments/ablation_study.yaml`  
**Runner:** `scripts/run_ablation_study.py`

| Exp | Variant | PolicyMode | Expected effect |
|-----|---------|------------|-----------------|
| A | Full ADAPTI-GUARD | `full_adaptive` | Best ASR–utility tradeoff |
| B | −Risk Engine | `full_adaptive` + fixed risk | ASR ↑ if risk helps |
| C | −Cost Gate | `no_cost_gate` | Utility ↓ (over-blocking) |
| D | −Feedback Loop | `fixed_l2` (proxy) | No adaptation to drift |
| E | −Policy Adaptation | `fixed_l2` | ASR ↑ under evolution |
| F | −Escalation | `de_escalation_only` | ASR ↑, Utility ↑ |

**Metrics:** ASR, Defense Rate, Utility, Cost, Reward

**Manuscript figure:** Ablation bar chart with 95% CI; highlight component with largest ASR Δ.

**Code gap:** Real-LLM ablation hooks for B (risk bypass) and D (feedback disable) not yet wired in `defense_baselines.py`.

---

# PART 6 — STATISTICAL VALIDATION

**Script:** `scripts/statistical_analysis.py`

| Test | Application | Implementation |
|------|-------------|----------------|
| Bootstrap 95% CI | ASR, utility, FPR proportions | `statistics.py` |
| McNemar | Paired ASR success B0 vs B6 per episode | `multi_model_statistics.py` |
| Wilcoxon signed-rank | Reward, cost, latency | `statistics.py` |
| Cohen's d | Effect size for continuous metrics | `statistics.py` |
| Holm correction | Multiple baseline comparisons | `statistics.py` |

**Claim template (mandatory):**
> "ADAPTI-GUARD reduces ASR from X% (95% CI [a,b]) to Y% (95% CI [c,d]) compared to no defense, with McNemar's test p < 0.05 and Cohen's d = Z."

**Never write:** "Our method is better."

---

# PART 7 — LONG-TERM ADAPTATION TEST

**Config:** `configs/experiments/long_term_adaptation.yaml`  
**Runner:** `scripts/run_long_term_adaptation.py`

| Phase | Episodes | Attack focus | Attacker mode |
|-------|----------|--------------|---------------|
| P1 | 1–200 | Basic injection | Static |
| P2 | 201–400 | Jailbreak evolution | AdaptiveAttacker |
| P3 | 401–600 | Indirect / RAG | Static |
| P4 | 601–800 | Tool abuse | Tool-focused |
| P5 | 801–1000 | Mixed adaptive | Full adaptive |

**Tracked metrics:** defense_level, ASR (rolling 50), utility (rolling 50), reward cumulative, intervention count

**Required figures:**
1. `figures/defense_level_over_time.png`
2. `figures/asr_over_time.png`
3. `figures/reward_curve.png`

**Recovery analysis:** After phase transition, measure episodes until ASR returns to within 10% of phase baseline.

---

# PART 8 — COST AND EFFICIENCY ANALYSIS

**Report:** `docs/efficiency_report.md` (template created)

Measure after EXP-004:
- Latency p50/p95 per component
- Token overhead vs B0
- Memory peak (local models)
- USD per 1K episodes (API models)
- Intervention rate by defense level

**Manuscript Table:** Deployment overhead (see efficiency_report.md §5)

---

# PART 9 — FAILURE ANALYSIS

**Protocol:** `docs/failure_analysis_protocol.md`

| Item | Target | Current |
|------|--------|---------|
| Successful attacks | 10+ | 0 (no predictions) |
| False positives | 10+ | 0 |
| Module attribution | Per case | Template ready |
| Human validation | 50 cases | NOT_RUN |

**Expected dominant failures (hypothesis — verify with data):**
1. Detector miss on indirect/RAG (low lexical signal)
2. Sanitize (A2) insufficient for jailbreak roleplay
3. Adaptation lag at phase boundaries (EXP-009)
4. Over-blocking benign RAG queries at L3

---

# PART 10 — REPRODUCIBILITY PACKAGE

## Target Structure

```
ADAPTI-GUARD/
├── attacks/              # Adaptive attacker templates
├── datasets/
│   ├── benchmark_q1/
│   └── attack_dataset/
├── models/               # Model configs (no secrets)
├── defenses/             # Defense modules
├── evaluation/           # Judge, metrics, statistics
├── experiments/
│   ├── EXP004_MULTI_MODEL/
│   ├── EXP006_ABLATION/
│   ├── EXP009_LONG_TERM/
│   └── templates/
├── configs/
│   ├── models.yaml
│   ├── models_local.yaml
│   └── experiments/
├── results/              # Gitignored outputs
├── figures/              # Publication figures
├── scripts/
├── README.md
└── requirements.txt
```

**Current mapping:** Code lives under `src/adapti_guard/` — create symlinks or document mapping in README.

## Reproducibility Checklist

- [x] Random seeds (42, 123, 456) in configs
- [x] Dataset hashes (`datasets/benchmark_q1/hashes.json`)
- [x] Judge protocol (`docs/JUDGE_PROTOCOL.md`)
- [x] Evaluation mode separation (`SIMULATION_VS_REAL_LLM.md`)
- [ ] Docker/conda lockfile
- [ ] One-command reproduction script
- [ ] Zenodo dataset DOI

**One-command target:**
```bash
make reproduce  # → preflight → EXP-004 → stats → figures
```

---

# PART 11 — PAPER IMPROVEMENT PLAN

## 1. Reviewer Rejection Risks (Ranked)

| Risk | Likelihood | Impact |
|------|------------|--------|
| No real LLM results | Certain | Desk reject |
| Fake SOTA baseline (regex Llama Guard) | High | Ethics/reject |
| Agent claims with 28 tool-abuse samples | High | Reject |
| Detector F1=0.41 contradicts detection claims | High | Major revision |
| Simulation results presented as real | High | Reject |
| No statistical tests | High | Major revision |
| Novelty overclaim | Medium | Major revision |

## 2. Required Experiments Before Submission

1. Fix API key; pass `phase1_preflight_audit.py`
2. EXP-004: B0/B6 on 3 API + 4 local models (n≥500)
3. EXP-003: Full B0–B6 on GPT-4o-mini (n≥500)
4. Complete attack_dataset to 700+ with all 7 categories ≥100
5. EXP-006 ablation on real LLM (3 models minimum)
6. EXP-009 long-term adaptation (1000 episodes, 1 model)
7. Statistical analysis with McNemar + Holm
8. Human judge validation (n=200, κ report)
9. Real B5 Llama Guard API baseline
10. Failure analysis (10+10 cases)

## 3. Nice-to-Have Experiments

- EXP-007 agent tool emulation with mock tools
- Cross-dataset detector transfer (NotInject → benchmark_q1)
- Adaptive attacker with RL-based mutation
- Gemini + Claude as additional API targets
- Production middleware demo (FastAPI)
- Comparison with NeMo Guardrails / Rebuff

## 4. Updated Contribution Claims

**Remove:**
- State-of-the-art defense performance
- Bayesian adaptation
- Validated across multiple LLM families (until EXP-004 completes)
- Publication-ready results

**Keep (with evidence gates):**
1. Harmonized evaluation protocol coupling attack ASR with benign utility under mixed workloads
2. Counter-based adaptive escalation (L0–L3) with cost-aware de-escalation
3. benchmark_q1 corpus (15K samples) with provenance hashes
4. Blind LLM-judge evaluation pipeline with statistical testing framework

## 5. Revised Abstract (Draft — fill after EXP-004)

> LLM-based agents face prompt injection across direct, indirect, RAG, and tool-manipulation vectors. We present ADAPTI-GUARD, a defense framework combining pattern-based detection, linear risk scoring, and counter-based policy escalation that adapts defense intensity while preserving benign task utility. We introduce a harmonized evaluation protocol with 75/25 attack–benign scheduling and independent blind LLM judging. On [N] models and [M] attack categories ([K] episodes), ADAPTI-GUARD reduces attack success rate from [X]% to [Y]% (McNemar p < 0.05) while maintaining [Z]% benign utility, outperforming [B] static baselines. Ablation confirms [component] drives the largest improvement. We release benchmark_q1 ([N] samples) and full reproduction artifacts.

## 6. Revised Experimental Section Outline

```
§5.1 Experimental Setup
  5.1.1 Threat model and metrics (ASR, utility, FPR, cost)
  5.1.2 Dataset: benchmark_q1 + attack_dataset (Table 1: category counts)
  5.1.3 Models: 4 local + 3 API (Table 2)
  5.1.4 Baselines B0–B6 (Table 3)
  5.1.5 Judge protocol and human validation (κ = ?)

§5.2 Main Results
  5.2.1 ASR vs utility tradeoff (Figure 1: Pareto)
  5.2.2 Baseline comparison (Table 4 + statistical footnotes)
  5.2.3 Per-category breakdown (Figure 2: heatmap)

§5.3 Model Generalization
  5.3.1 Cross-model ASR (Figure 3: grouped bars + CI)
  5.3.2 Model-independence analysis (CV across models)

§5.4 Ablation Study
  5.4.1 Component removal (Table 5, Figure 4)
  5.4.2 Component contribution ranking

§5.5 Long-Term Adaptation
  5.5.1 1000-episode stress test (Figure 5–7: time series)
  5.5.2 Recovery after distribution shift

§5.6 Efficiency and Deployment
  5.6.1 Latency/token/cost overhead (Table 6)
  5.6.2 Intervention rate by defense level

§5.7 Failure Analysis
  5.7.1 Attack bypass taxonomy (Figure 8)
  5.7.2 False positive analysis

§5.8 Limitations
  - Detector generalization (F1=0.41 held-out)
  - Tool-abuse sample size
  - Judge bias
  - API model version drift
```

---

# FINAL OUTPUT — Q1 IMPROVEMENT ROADMAP

See `Q1_IMPROVEMENT_ROADMAP.md` for prioritized task list.

**Estimated timeline to submission-ready:** 6–10 weeks (assuming API budget ~$200–500, 1 GPU for local models).

**Bottom line:** The project has solid infrastructure but **no evidence**. Priority 1 is executing real-LLM experiments; everything else is secondary.

---

*Review conducted against codebase commit state 2026-09-02. No experimental metrics fabricated.*
