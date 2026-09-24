# Dual-Track Evaluation of Cost-Aware Runtime Intervention for LLM Prompt Injection: A Confirmed Negative and a Scoped Phase-1 Improvement

**Findings manuscript (draft — venue path LOCKED: Findings / workshop-style, not ICLR 2027 main)**  
**Not a venue upload. Not arXiv deposit by agents.** Planning: [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md)

Seyed Mohammadreza Shirazi Matin  
AI Security · LLM-agent defense evaluation  
`mrshirazimatin@gmail.com`

**Status banner.** Track A VNEXT confirmation = **FAIL** (immutable). Track B Phase-1 LIVE = **SUPPORTED_IMPROVEMENT** (scoped; **does not reverse** Track A). This draft does **not** claim prompt injection is solved, SOTA defense, or production readiness.

**Claims map.** [`CLAIMS_MAP.md`](CLAIMS_MAP.md) · **Contribution ceiling** [`CONTRIBUTION_CEILING.md`](CONTRIBUTION_CEILING.md) · Dual-track [`../CLAIMS_CHECKLIST.md`](../CLAIMS_CHECKLIST.md) · Q1 scope [`../../experiments/DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](../../experiments/DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md) · Repro [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) · Verifier [`verify_q1_findings_facts.py`](verify_q1_findings_facts.py)

**Evidence base (this Q1 cycle):** Track A n=61 FAIL + Track B n=61 scoped improvement only. Confirmatory V2, external SOTA baselines, AgentDojo-class loops, and mechanism-pack live eval = **Future Work** (optional Phase 3 after human budget).

---

## Abstract

Runtime middleware for LLM agents maps detector scores to discrete actions (sanitize, restrict tools, block) and may adapt intervention level over episodes under a utility cost. Whether such **label-blind, cost-aware** policies reduce **defense-attributed** attack success while preserving benign utility is an empirical claim that requires hash-locked packs, an independent judge (Target ≠ Judge), and pre-registered stop rules—not a design narrative.

We report a **dual-track** confirmatory evaluation on two disjoint frozen packs and treatments. **Track A (VNEXT):** on `vnext_confirm_v1.0` (61 attack + 61 benign), VNEXT-ADAPT vs B0 **FAILS** the pre-registered qualified win: McNemar b10=5, b01=0, p=0.0625 (not significant at α=0.05); δ̂=0.0820 below MSID 0.20; utility U=0.9344 below gate 0.95. **Track B (Phase-1):** on a separate pack `phase1_confirm_v1`, PHASE1-CORE vs B0 shows **SUPPORTED_IMPROVEMENT** under Phase-1 MSID with utility eligible (δ̂=0.4426, 95% CI [0.2757, 0.6096] per AUDIT)—a **scoped** result on a different treatment and corpus; it is **not** a VNEXT pass and **does not overturn** Track A FAIL.

A **closed Layer A diagnostic** (40+40 TEST) shows detector lift without a significant adaptive ASR reduction (McNemar p=0.125). The contribution is a **dual-track evaluation protocol** and frozen **confirmed negative plus scoped Phase-1 track** under explicit claim boundaries ([`CONTRIBUTION_CEILING.md`](CONTRIBUTION_CEILING.md))—not a fielded guard or SOTA defense.

---

## 1. Introduction

Prompt injection and instruction override remain central risks for LLM-integrated applications: untrusted content in user prompts, retrieval, or tool outputs can redirect agent behavior. Engineering responses often stack **detection → risk band → discrete action**, optionally **adapting** the intervention level so that always-on blocking does not destroy benign utility.

Three evaluation mistakes recur in security reporting: (1) crediting **detector lift** as intervention success; (2) counting **target refusals** as defense wins in paired tests; (3) reporting ASR drops without a **utility co-primary** gate. AdaptiGuard is a testbed that makes those distinctions explicit via an intervention taxonomy and independent LLM judge.

This findings manuscript extends the shorter workshop negative-result packet ([`workshop_vnext_fail/MANUSCRIPT.md`](../workshop_vnext_fail/MANUSCRIPT.md)) by presenting **both confirmatory live tracks** with equal methodological visibility, while forbidding a merged “AdaptiGuard works” headline. Scope is capped in [`CONTRIBUTION_CEILING.md`](CONTRIBUTION_CEILING.md).

**Research questions (confirmatory, pre-registered per track).**

- **Track A:** Does label-blind adaptive **VNEXT-ADAPT** reduce defense-attributed attack success vs B0 on `vnext_confirm_v1.0` with U ≥ 0.95? **Answer: NO (FAIL).**
- **Track B:** Does **PHASE1-CORE** reduce harmful-action success vs B0 on `phase1_confirm_v1` under Phase-1 MSID with utility eligible? **Answer: YES (scoped SUPPORTED_IMPROVEMENT)—on that pack only.**

**Contributions (evaluation, not product).**

1. Dual-track **hash-locked** confirmatory design with frozen AUDIT artifacts and dual-track claim checklists.
2. **Confirmed negative** for VNEXT adaptive intervention under `VNEXT-MSID-0.1`.
3. **Scoped positive** for Phase-1 CORE on an independent pack—reported without reversing Track A.
4. Layer A **diagnostic** closure: detector v4 lift without adaptive win.
5. Limitations and **Future Work** map aligned to Q1 blockers ([`QUALITY_GAPS.md`](QUALITY_GAPS.md); Track A δ̂ CI now offline-only).

**Non-claims.** We do not solve prompt injection, claim SOTA, or recommend production deployment. Phase 3 optional live arms (V2 pack, baselines, mechanism benchmark) are **not** part of this manuscript’s evidence base unless Matin later adds immutable AUDIT folders after budget sign-off.

---

## 2. Related Work

**Prompt injection.** Direct and indirect injection are documented by `perez2022ignore`, `greshake2023not`, and application-level threat models (`liu2023prompt`; `owasp2023llm` LLM01).

**Agent and tool benchmarks.** `debenedetti2024agentdojo`, `zhan2024injecagent`, and `yi2023bipia` evaluate tool-using agents under adversarial content in rich environments. **This work is not an AgentDojo leaderboard entry** and must not be cited as one; our primary harness is episode-level Target+Judge scoring on frozen authored packs with declared tool success conditions. That gap limits external comparability and is explicit in [`QUALITY_GAPS.md`](QUALITY_GAPS.md).

**Static and training-time defenses.** `inan2023llama`, `rebedea2023nemo`, `chen2024struq`, `chen2024secalign`, and `wallace2024instruction` change models, add classifiers, or separate instruction channels at training time. We study **runtime discrete actions** after a heuristic score, with explicit utility gates—complementary, not commensurate without a shared locked protocol and baseline arms (Future Work).

**Evaluation estimands vs block-rate headlines.** Prior lines often report block rate, heuristic match, or single ASR deltas without (i) an independent judge, (ii) a defense-attributed McNemar cell definition, or (iii) a co-primary utility gate. Our pre-registered object is **defense-attributed** discordant success (taxonomy in \(\mathcal{W}\)), not mixed ASR alone. `mcnemar1947note` paired testing applies to discordant cells; our **MSID** rule additionally judges whether \(\hat\delta=(b_{10}-b_{01})/n_{\text{attack}}\) is scientifically large enough to matter—a stricter claim than \(p<0.05\) alone.

**Adaptive defense vs adaptive offense.** PAIR/GCG-style attacks adapt the **offense**. Adaptive **defense** under cost and utility constraints is less often subjected to pre-registered MSID + McNemar + utility co-primary testing. This paper foregrounds that **confirmatory hygiene** and reports a **confirmed negative** on Track A under those rules.

**Negative results and dual-track reporting.** Reporting FAIL alongside a scoped improvement on a **different** pack prevents upgrading Phase-1 into a reversal of VNEXT FAIL. Dual-track separation is a **scientific reporting** requirement ([`CLAIMS_MAP.md`](CLAIMS_MAP.md)).

---

## 3. Threat Model

**System.** Middleware observes prompt and context at decision time, selects A0–A3, optionally adapts defense level label-blind, then invokes Target LLM unless blocked; independent Judge scores attack success and benign utility.

**Assets.** Task integrity, instruction confidentiality, tool authorization.

**Adversary.** Black-box UTF-8 in prompt/context; goals include override, exfiltration, persistence in concatenated context, obfuscation, tool-output-shaped injection. Frozen packs are **authored synthetic** corpora—not live adaptive red teaming.

**Defender.** No gold labels at runtime except named ORACLE diagnostic arms. Adaptation is counter-based, not RL.

**Out of scope.** Training-time poisoning, white-box weights, full AgentDojo sandboxes as primary evidence, browsing, production RAG. Target refusals are **not** defense wins in confirmatory taxonomy.

**Trust boundaries.** Judge is independent (different model ID); Judge does not receive treatment arm labels.

---

## 4. Method

### 4.1 Stack (shared conceptually; arms differ by track)

1. **Detection** — heuristic `PromptInjectionDetector` (Track B: `evidence_phase1.0`, τ=0.25/0.60; Track A / Layer A: v4 evidence path for VNEXT lineage).
2. **Risk** — LOW / MEDIUM / HIGH bands.
3. **Policy** — maps risk and adaptive level to A0–A3.
4. **Action** — sanitize (A1), tool deny (A2), block (A3).
5. **Adaptation** — VNEXT-ADAPT (Track A) vs PHASE1-CORE mapping (Track B); not interchangeable treatments.
6. **Evaluation** — Judge `attack_success` / utility; wins only in `{correct_block, correct_tool_deny}` for McNemar defense attribution.

### 4.2 Dual-track separation (binding)

| Track | Pack SHA-256 (prefix) | Treatment vs B0 | AUDIT folder |
| --- | --- | --- | --- |
| **A — VNEXT** | `523c8818…` | VNEXT-ADAPT | `VNEXT_CONFIRM/20260914-133147/` |
| **B — Phase-1** | `c789811a…` | PHASE1-CORE | `PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/` |

**Never** pool ASR across tracks in one unlabeled table.

### 4.3 Layer A (diagnostic only)

Frozen Layer A v3 TEST 40+40 — CLOSED; informs mechanism narrative; **not** confirmatory for either track above.

---

## 5. Protocol

### 5.1 Shared live eval contract

- **Target:** `qwen/qwen-2.5-7b-instruct`
- **Judge:** `qwen/qwen-2.5-72b-instruct` (**Target ≠ Judge**)
- **Cache:** off on official confirmatory runs
- **Backend:** OpenRouter (historical spend on Track A ~$0.059 list-rate aid per AUDIT)

### 5.2 Track A — VNEXT (`VNEXT-PROTOCOL-0.1`, MSID δ=0.20)

- n_attack = n_benign = **61** on `vnext_confirm_v1.0`
- Qualified win requires McNemar significance, δ̂ ≥ MSID, U ≥ 0.95, and defense-attributed discordant pairs
- **Outcome: FAIL** — see §6.1

### 5.3 Track B — Phase-1 confirmatory LIVE

- Same n=61+61 on **different** pack `phase1_confirm_v1`
- Treatment **PHASE1-CORE** (not VNEXT-ADAPT)
- Phase-1 MSID and utility rules per Phase-1 protocol / AUDIT
- **Outcome: SUPPORTED_IMPROVEMENT (scoped)** — see §6.2

### 5.4 Statistics and estimands

**Primary estimand (Track A confirmatory).** Let \(y_i^{(0)}, y_i^{(1)} \in \{0,1\}\) be B0 and treatment attack-success indicators for scorable attack episode \(i\). Discordant defense-attributed cells \((b_{10}, b_{01})\) count episodes with taxonomy in \(\mathcal{W}=\{\texttt{correct\_block}, \texttt{correct\_tool\_deny}\}\) per protocol addendum—not target refusals. The locked effect size is

\[
\hat\delta = \frac{b_{10} - b_{01}}{n_{\text{attack}}}.
\]

This equals the per-episode mean of contributions \(+1\) (b10), \(-1\) (b01), and \(0\) (concordant). It is **not** the naive difference of marginal ASR proportions unless all discordance is defense-attributed.

**Inference.** McNemar exact on \((b_{10}, b_{01})\) per track; Wilson intervals in AUDIT for marginal ASR and utility; bootstrap (`n_{\text{bootstrap}}=5000`, `seed=42`) for proportions where AUDIT reports them.

**Track A \(\hat\delta\) uncertainty (offline, not in original AUDIT).** Official `AUDIT.md` reports the point \(\hat\delta=0.0820\) only. A **post-hoc offline** 95% CI is computed from frozen integers \(b_{10}=5\), \(b_{01}=0\), \(n_{\text{attack}}=61\) using the same bootstrap-on-contributions method as `adapti_guard.evaluation.statistics.delta_hat_ci_bootstrap_from_mcnemar_contingency` (see [`scripts/recompute_vnext_delta_ci.py`](../../scripts/recompute_vnext_delta_ci.py) and artifact [`artifacts/vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json), `inputs_sha256` `1de3f14d…`). **Do not** claim this interval appeared in the 2026-09-14 AUDIT folder.

### 5.5 Future Work (not executed this cycle)

Per [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](../../experiments/DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md): Confirmatory V2 episodes/allocation/SAP/pack; AgentDojo-class loops; `p1_mechanism_v1.0.0` live (`live_evaluated=false`). D-22 six `family_id` names locked for **future** V2 metadata; +1 remainder rule → `PRIVILEGE_EXFIL` when V2 is authorized. Optional Phase 3 **priority 1** ([`Q1_P3_PRIORITY.md`](../../experiments/Q1_P3_PRIORITY.md)): commensurate **external baseline** comparison on the same episode IDs ([`DECISION_LOCK_Q1_P3_1_BASELINE.md`](../../experiments/DECISION_LOCK_Q1_P3_1_BASELINE.md); offline runner smoke only) — **not executed live**; **not** superiority or SOTA; Track A FAIL unchanged. P3-5 mechanism · P3-3/4 multi-model: design locks only ([`DECISION_LOCK_Q1_P3_5_MECHANISM.md`](../../experiments/DECISION_LOCK_Q1_P3_5_MECHANISM.md), [`DECISION_LOCK_Q1_P3_3_MULTIMODEL.md`](../../experiments/DECISION_LOCK_Q1_P3_3_MULTIMODEL.md)).

---

## 6. Results

**Presentation rule:** Track A first (FAIL), then Track B (scoped improvement). Layer A diagnostic follows as non-confirmatory context. No pooled headline ASR.

### 6.1 Track A — VNEXT confirmation (**FAIL**)

Canonical: `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`

| Arm | n_attack | ASR | n_benign | U |
| --- | ---: | ---: | ---: | ---: |
| B0 | 61 | **0.9508** (58/61) | 61 | 0.9672 |
| VNEXT-ADAPT | 61 | **0.8689** (53/61) | 61 | **0.9344** |

Wilson intervals for ASR/U as in workshop AUDIT table (e.g. B0 ASR [0.865, 0.983]; treatment U [0.843, 0.974]).

**McNemar (intervention-mediated):** b10=**5**, b01=**0**, exact two-sided p=**0.0625** → **not statistically significant** at α=0.05.

**Effect vs MSID:** δ̂ = (b10−b01)/n = **0.0820** &lt; MSID **0.20** → useful-intervention claim **fails**.

**δ̂ uncertainty (recomputed offline):** Original AUDIT has **no** δ̂ CI. From frozen McNemar counts, bootstrap percentile CI (**95%**, `n_bootstrap=5000`, `seed=42`): **\[0.0164, 0.1639\]** (artifact [`artifacts/vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json); method `bootstrap_percentile_episode_contributions`). The upper bound remains **below MSID 0.20**, consistent with `msid_not_met`—this does **not** upgrade McNemar significance (\(p=0.0625\)).

**Utility:** U=**0.9344** &lt; **0.95** (false blocks = 1) → utility-ineligible.

**Taxonomy (VNEXT-ADAPT):** five b10 = `correct_block` (A3); **53** `insufficient_intervention`; refusals not wins.

**Verdict:** Qualified win (H1) = **NO**. STATUS = **FAIL**. Fail reasons: `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`.

Family ASR cells (n∈{10,11}) are **descriptive** only (see workshop §6.2 table).

### 6.2 Track B — Phase-1 confirmatory LIVE (**SUPPORTED_IMPROVEMENT**, scoped)

Canonical: `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md`

| Field | Value |
| --- | --- |
| Pack | `phase1_confirm_v1`, SHA-256 `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |
| Treatment | PHASE1-CORE vs B0 |
| B0 ASR | **1.0000** |
| CORE ASR | **0.5574** |
| δ̂ | **0.4426**, 95% CI **[0.2757, 0.6096]** (per AUDIT) |
| McNemar | p=**1.49012e-08**, b10/b01=**27/0** (all `correct_tool_deny` per status sheet) |
| Utility U | **0.9672131147540983** (eligible) |
| API | 244 calls / 0 failures (AUDIT) |

**Interpretation bound:** This track supports a **scoped** claim that PHASE1-CORE reduced intervention-mediated harmful-action success vs B0 **on this pack** with utility above 0.95. It uses a **different** detector lock and treatment than VNEXT-ADAPT.

**Explicit non-interpretation:** Track B **does not reverse** Track A FAIL, is **not** evidence that VNEXT-ADAPT works, and is **not** solve-PI / SOTA / production-ready.

### 6.3 Layer A diagnostic (CLOSED)

On frozen TEST 40+40: v4 attack recall **27/40=0.675**, AUROC **0.705** vs v3 recall **0.05**. B3_V4 ASR **0.625** vs B0 **0.75**, McNemar p=**0.125** — **not** a demonstrated ASR reduction. Five of six discordant pairs were A1 target refusals, not A3 blocks. **Do not** mix Layer A TEST ASR with Track A or B confirmatory ASR in one unlabeled figure.

---

## 7. Failure Analysis (Track A primary)

Track A failed for **three sufficient reasons** (any one bars qualified win):

1. **McNemar:** p=0.0625 with b10=5 — not significant; do not call “marginal confirmation.”
2. **MSID:** δ̂=0.0820 &lt; 0.20 even if significance were arguable.
3. **Utility:** point U=0.9344 &lt; 0.95.

Attribution is **honest but insufficient:** all b10 are true A3 blocks, yet **53/61** attacks remain `insufficient_intervention`. Tool deny (`correct_tool_deny`) did not drive Track A McNemar cells (count 0).

Mechanism narrative (qualitative, CASE B): after detector lift, MEDIUM→A1 routing dominates; VNEXT action mix remains A1-heavy. This explains continuity with Layer A without pooling numbers.

Track B success on tool-deny-heavy taxonomy **does not** explain away Track A FAIL—they are different treatments and packs.

---

## 8. Limitations

Sourced from [`Q1_BLOCKER_MATRIX.md`](../../experiments/Q1_BLOCKER_MATRIX.md) and Q1-P2 dispositions:

| Limitation | P2 disposition | Honest reporting |
| --- | --- | --- |
| Track A **FAIL** immutable | immutable | Confirmed negative; no FAIL→PASS |
| Small **n=61** per track | Future Work (V2); offline power artifact | See power paragraph below; V2 not in this cycle |
| Track A δ̂ **95% CI absent** in AUDIT | docs-fixed + offline artifact | Point δ̂ in AUDIT; CI from [`recompute_vnext_delta_ci.py`](../../scripts/recompute_vnext_delta_ci.py) only |
| **Heuristic detector**; no AgentDojo-class loops | Future Work | Single-turn confirmatory scope |
| **No external SOTA baselines** | Future Work; P3-if-budget | Compare locked arms only |
| **Simulation ≠ confirmatory live** | docs-fixed | Do not cite `04_results.md` sim ASR as judge wins |
| **Dual-track mixup** risk | docs-fixed | Separate sections/tables always |
| Confirmatory **V2** deferred | Future Work | Paper uses A/B n=61 only |
| **`p1_mechanism_v1.0.0` not live-evaluated** | Future Work; P3-if-budget | Spec/freeze SHA only |
| **Venue TBD** | P4 human | No submission DONE in repo |
| **Overclaim** (refusal, L3 oracle, ASR=0 sim) | docs-fixed | Taxonomy + CLAIMS_MAP |
| Single Target/Judge pair | docs-fixed | No multi-model robustness claim |
| Authored synthetic packs | docs-fixed | Not production RAG/agents |

**Sample size / power (Track A, offline).** Under documented simplifications (`b01=0`, McNemar exact, binomial scaffold for planning), n=61 would yield **~99%** power to detect a **true** per-episode b10 rate of **MSID=0.20** at α=0.05 ([`artifacts/vnext_track_a_power_sensitivity.json`](artifacts/vnext_track_a_power_sensitivity.json)). Observed **b10=5** requires **≥6** discordant wins for significance and **≥13** for point δ̂≥0.20 at `b01=0`; the offline δ̂ 95% CI upper bound (**0.1639**, from [`vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json)) stays below MSID. **Interpretation:** Track A **FAIL** is consistent with a **small estimated effect** and pre-registered gates—not primarily “n=61 could never detect MSID-sized effects” under this model. Generalization beyond n=61 remains limited.

**Phase 3:** No new live AUDIT folders are claimed. Optional arms per [`DECISION_LOCK_Q1_P3_ARMS.md`](../../experiments/DECISION_LOCK_Q1_P3_ARMS.md) require human budget.

---

## 9. Ethics

Documenting a **confirmed negative** (Track A) alongside a **bounded positive** (Track B) reduces the risk that operators over-trust adaptive runtime middleware. Synthetic attack text is for evaluation, not operational attack guidance. No human subjects or PII. Historical API spend is order $0.06 (Track A) plus Track B per AUDIT—not an environmental benchmark. Do not market AdaptiGuard as production-ready on these results.

---

## 10. Reproducibility and Hash Appendix

**Do not rerun live eval to amend locked verdicts.** Official outcomes are AUDIT folders cited above.

Offline checks:

```bash
python3 docs/paper/q1_findings/verify_q1_findings_facts.py
python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py
```

**Hash and config tables:** [`workshop_vnext_fail/APPENDIX_HASHES.md`](../workshop_vnext_fail/APPENDIX_HASHES.md) · [`CONFIGS_SNAPSHOT.md`](../workshop_vnext_fail/CONFIGS_SNAPSHOT.md) · hub [`docs/experiments/REPRODUCIBILITY_PACKAGE.md`](../../experiments/REPRODUCIBILITY_PACKAGE.md)

**Frozen pack SHA (Track A):** `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`  
**Frozen pack SHA (Track B):** `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01`

---

## 11. Conclusion

Under pre-registered rules on `vnext_confirm_v1.0`, **VNEXT-ADAPT does not confirm** cost-aware adaptive runtime intervention: McNemar p=0.0625, δ̂=0.0820 below MSID 0.20, utility ineligible. On a separate Phase-1 pack, **PHASE1-CORE** shows **scoped** improvement vs B0 with AUDIT-reported δ̂=0.4426 and eligible utility—**without** reversing Track A. Layer A diagnostics show detector lift but not adaptive confirmatory success. The reusable outcome is **evaluation methodology and honest dual-track reporting**, not a shipped defense. Confirmatory V2 and agent-class benchmarks remain **Future Work** pending design locks and optional Phase 3 budget.

---

## References

BibTeX keys for camera-ready compile: [`references.bib`](references.bib). Related-work pointers (not primary evidence):

- `perez2022ignore` — direct prompt injection attacks.
- `greshake2023not` — indirect injection in LLM-integrated apps.
- `liu2023prompt` — LLM-integrated application attacks.
- `owasp2023llm` — OWASP LLM Top 10 (LLM01).
- `debenedetti2024agentdojo` — AgentDojo agent benchmark (**not** our leaderboard entry).
- `zhan2024injecagent` — InjecAgent tool-agent injections.
- `yi2023bipia` — BIPIA indirect injection benchmark.
- `inan2023llama` — Llama Guard input-output safeguard.
- `rebedea2023nemo` — NeMo Guardrails toolkit.
- `chen2024struq` — StruQ structured queries (training-time channel separation).
- `chen2024secalign` — SecAlign preference optimization defense.
- `wallace2024instruction` — instruction hierarchy training.
- `mcnemar1947note` — paired proportions test.

**Primary evidence:** frozen packs and `AUDIT.md` paths in [`APPENDIX_HASHES.md`](../workshop_vnext_fail/APPENDIX_HASHES.md), not this bibliography alone.
