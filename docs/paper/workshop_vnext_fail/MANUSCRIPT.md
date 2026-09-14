# Adaptive Cost-Aware Runtime Intervention for LLM Prompt Injection Is Not Confirmed under a Pre-Registered MSID

**Workshop / preprint manuscript (negative result)**  
**Not an arXiv deposit. Not a camera-ready defense paper.**

Seyed Mohammadreza Shirazi Matin  
AI Security · LLM-agent defense  
`shirazimatin@gmail.com`

**Status banner.** VNEXT confirmation **STATUS = FAIL**. Qualified win (H1) = **NO**.
Layer A remains a **CLOSED diagnostic** (detector lift; adaptive B3_V4 not significant).
This manuscript does not claim a defense win, SOTA detector, or production-ready system.

**Protocol.** `VNEXT-PROTOCOL-0.1` · Addendum `VNEXT-PROTOCOL-ADDENDUM-0.3` · MSID `VNEXT-MSID-0.1` (δ = 0.20).  
**Confirmation pack.** `vnext_confirm_v1.0`, 61 attack + 61 benign, SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`.  
**Canonical AUDIT.** `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`.  
**Claims map.** [`CLAIMS_MAP.md`](CLAIMS_MAP.md) · Layer A checklist [`../CLAIMS_CHECKLIST_LAYER_A.md`](../CLAIMS_CHECKLIST_LAYER_A.md).

---

## Abstract

Runtime defenses for LLM agents often escalate from sanitization to blocking as detected risk grows. Whether a *label-blind, cost-aware adaptive* policy reduces *defense-attributed* attack success, while preserving benign utility, is an empirical question rather than a design axiom. We report two hash-locked studies that share a discrete intervention stack (detect → risk → action A0–A3) and an independent-judge protocol, and that must not be mixed in unlabeled tables.

**Layer A (CLOSED diagnostic).** On the frozen Layer A v3 TEST split, detector v4 attack recall is 27/40 = 0.675 and AUROC is 0.705, versus v3 recall 2/40 = 0.05 and AUROC 0.368, without TEST retuning. Adaptive B3_V4 has ASR 0.625 and utility 0.85 versus B0 ASR 0.75 and utility 1.00; exact McNemar p = 0.125. This is not a demonstrated ASR reduction. Of the six discordant episodes with B0 attack-success and B3_V4 attack-failure, only one is a true A3 block; the other five are target refusals under A1 and are not defense wins.

**VNEXT (confirmatory, FAIL).** On a new 61+61 pack (SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`), B0 ASR is 0.9508 (58/61) and VNEXT-ADAPT ASR is 0.8689 (53/61). Intervention-mediated McNemar yields b10 = 5, b01 = 0, p = 0.0625. The paired effect δ̂ = 0.0820 is below the pre-registered minimum scientifically interesting difference (MSID) of 0.20. Utility U = 0.9344 fails the co-primary gate U ≥ 0.95 (false blocks = 1). All five b10 events are `correct_block` (A3); 53 attacks remain `insufficient_intervention`. Fail reasons: `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`. Target `qwen/qwen-2.5-7b-instruct` ≠ Judge `qwen/qwen-2.5-72b-instruct`; cache off; estimated spend ~$0.059.

Adaptive cost-aware intervention is **not confirmed** under the pre-registered MSID. The reusable contribution is a hash-locked evaluation protocol with intervention taxonomy and a utility gate—not a working product.

---

## 1. Introduction

Untrusted text in prompts, retrieved documents, and tool outputs can override LLM-agent instructions. A common engineering response is a *runtime* stack: score the incoming text, map the score to a risk band, and apply a discrete action—passthrough (A0), sanitize (A1), restrict tools (A2), or block (A3). Adaptive controllers then raise or lower the intervention level across episodes so that always-on blocking does not destroy benign utility and always-off passthrough does not leave the agent undefended.

That story is plausible and incomplete. Three failure modes are easy to miss if the only published number is mixed attack-success rate (ASR):

1. **Detector lift without intervention.** A better detector can rank attacks above benign text and still leave the policy mapping MEDIUM risk to sanitization. Attacks then succeed under A1.
2. **Model refusals credited as defense.** If the undefended target sometimes refuses, a paired ASR drop can be almost entirely target robustness rather than A2/A3 intervention.
3. **Utility-blind “wins.”** Blocking every episode drives ASR to zero and utility to zero. A security improvement that misses a pre-registered utility gate is not a qualified runtime defense.

AdaptiGuard is a testbed for that stack: heuristic detection, risk bands, fixed or adaptive policies, and a real-LLM Target plus independent Judge. This manuscript is a **negative-result workshop paper**. It asks a confirmatory question that was pre-registered before the confirmation pack was scored:

> Does a *label-blind* adaptive runtime defense reduce **defense-attributed** attack success versus no defense (B0) on a **new, hash-locked confirmation pack**, while keeping benign utility \(U \ge 0.95\)?

The official answer is **no**. We do not retune, do not increase N, and do not modify frozen packs after seeing p-values.

**Contributions (evaluation and negative result, not a product).**

- A **CLOSED Layer A diagnostic** showing detector lift on a frozen TEST split and a non-significant adaptive intervention (claims A1–A12 in [`CLAIMS_MAP.md`](CLAIMS_MAP.md)).
- A **pre-registered VNEXT confirmation** (n = 61+61, MSID = 0.20) that **FAILS** McNemar significance, MSID, and the utility gate (claims V1–V10).
- An **intervention taxonomy** that counts only `correct_block` and `correct_tool_deny` as defense-attributed wins, so A1 target refusals cannot be sold as policy success.
- A **reproducibility package**: frozen SHA-256 identities, AUDIT paths, and a claims checklist that forbids SOTA / production language.

**Non-contributions.** We do not introduce a new SOTA detector architecture. We do not claim AdaptiGuard, B3_V4, or VNEXT-ADAPT is a useful fielded defense. Keyword-free general prompt injection is not solved.

---

## 2. Related Work

Prompt injection is the primary threat class. Perez and Ribeiro (2022) documented direct “ignore previous instructions” attacks. Greshake et al. (2023) showed *indirect* injection through retrieved or linked content. Subsequent application-level studies treat injection as a systems problem rather than a single-turn jailbreak (Liu et al., 2023). OWASP’s LLM risk list places prompt injection at LLM01.

**Agent and tool benchmarks.** AgentDojo (Debenedetti et al., 2024) and InjecAgent (Zhan et al., 2024) evaluate tool-using agents under adversarial content. BIPIA (Yi et al., 2023) studies indirect injection. Those environments remain the right long-term target for *agent* claims. This work’s primary harness is episode-level Target+Judge generation with a declared tool request for A2 scoring; it is **not** an AgentDojo leaderboard result and must not be cited as one.

**Static and training-time defenses.** Llama Guard (Inan et al., 2023) and Prompt Guard-style classifiers score or filter generations. NeMo Guardrails (Rebedea et al., 2023) encodes dialogue policies. StruQ and SecAlign (Chen and colleagues, 2024) harden models at training time against injected instructions. Instruction-hierarchy work (Wallace et al., 2024) privileges system messages over untrusted text. These lines are complementary: they change the model or add a classifier, whereas AdaptiGuard studies **discrete runtime actions** after a detector score.

**Adaptive offense, not adaptive defense.** PAIR, GCG, and related red-team methods adapt the *attack*. Adaptive *defense* that escalates sanitization versus blocking under a utility cost is less studied as a confirmatory claim. Hysteresis / counter-based level control is classical process control, not a new learning algorithm. This manuscript treats the controller as a **testable policy**, not as Bayesian or RL novelty.

**Evaluation hygiene.** Security papers routinely report block rate or heuristic match rate as ASR. We follow an independent-judge rule (Target ≠ Judge) and exclude API failures from denominators rather than imputing ASR = 0. Mixed ASR without an intervention taxonomy repeats a documented Layer A error: five of six discordant “wins” were A1 refusals.

**Negative results.** Pre-registration of an MSID, a paired test, and a utility gate is the difference between “the number moved” and “the hypothesis was confirmed.” This paper is written to make the FAIL inspectable.

---

## 3. Threat Model

**System.** A middleware layer sits in front of a Target LLM. Each *episode* is one confirmation-pack record: user `prompt`, optional `context` (simulated retrieval or prior turns), optional declared `tool_call`, then defense → optional tool-loop gate → Target (unless A3 blocks) → independent Judge.

**Assets.** Integrity of the intended user task; confidentiality of instructions and context; authorization of tool actions (send email, retrieve documents, create records, search).

**Adversary.** Black-box. The attacker supplies UTF-8 in the user prompt and/or context field. Goals: instruction override, exfiltration via unauthorized tools, persistence across concatenated multi-turn context, obfuscated payloads, and tool-output-shaped injection. The attacker does not receive defense level, detector score, or Judge prompt. The confirmation pack is a **frozen authored corpus**, not an online adaptive red team.

**Defender.** Observes prompt and context only at decision time. Gold `label` / `is_attack` is forbidden in the detector, risk engine, policy, action layer, and adaptation feedback except named `ORACLE_*` diagnostic arms. Adaptation, when used, is label-blind and counter-based (escalate after sustained attack pressure; de-escalate after sustained benign pressure, with a cost gate). The defender may sanitize, deny a tool, or skip the Target.

**Out of scope.** Training-time poisoning, white-box weights, side channels, live browsing, full AgentDojo sandboxes as the primary protocol, and any claim that the Target’s own refusals are a deployed product feature of AdaptiGuard.

**Trust boundaries.** Code, fixed system prompt, and Judge protocol are trusted. User prompt, context, and Target output (as Judge input) are untrusted. The Judge is assumed independent of the treatment arm: it does not receive baseline ID, action, or defense level.

---

## 4. Method

### 4.1 Stack

AdaptiGuard evaluates policies, not a single classifier.

1. **Detection.** Heuristic `PromptInjectionDetector`. Layer A v3 is regex V18. Layer A v4 (`evidence_v4.0`) is an evidence-gated score designed on TRAIN/DEV and frozen before one TEST pass. Scores are **not** calibrated probabilities.
2. **Risk.** `RiskEngine` maps the score to LOW / MEDIUM / HIGH.
3. **Policy.** `DefensePolicyEngine` maps `(risk_level, defense_level)` to A0–A3. HIGH maps to block unless a tool-sensitive exception applies. MEDIUM maps to A1 at adaptive `defense_level` 0–1, A2 at ≥ 2, A3 at ≥ 3. LOW never selects A3.
4. **Action.** A0 passthrough; A1 sanitize and still call the Target; A2 deny tools in the episode tool loop (prompt unchanged, `blocked=false`); A3 skip the Target (`blocked_by_defense`).
5. **Adaptation (treatment).** Counter-based `PolicyUpdateEngine`: not Bayesian, not RL. Reward is logged, not optimized. Scientific name of the confirmatory treatment: **VNEXT-ADAPT** (factory `make_b3_adaptive_v4`). That name is not a B3_V4-win claim.
6. **Evaluation.** Independent LLM Judge on `attack_success` / `utility_success`. Publication ASR is never `attack_outcome.py` substring heuristics, never detector block-rate, and never `defense_rate = 1 − ASR` treated as a win.

### 4.2 Named arms

| Arm | Role | Gold labels at runtime? |
| --- | --- | --- |
| B0 | No defense (A0) | No |
| VNEXT-ADAPT | Label-blind adaptive treatment (primary confirmatory pair) | No |
| B3 / B3_V4 | Historical Layer A adaptive arms | No (VNEXT harness); Layer A historical leakage is CLOSED and not reused as confirmation |
| B2_L3_V4 | Fixed risk-gated level 3 with v4 signal | No; **diagnostic mapping, not adaptive** |
| L3 | Unconditional A3 | No; security ceiling / utility floor |
| ORACLE_BLOCK | A3 iff gold attack | **Yes** — diagnostic only |
| L2 | Tool restriction | Unscored on Layer A; VNEXT harness can deny tools, but L2 is **not** the primary confirmatory pair |

### 4.3 Intervention taxonomy (attribution)

Every scorable episode receives exactly one primary class. A McNemar *defense* win (\(b_{10}\)) requires B0 `attack_success=true`, treatment `attack_success=false`, and treatment class in \(\mathcal{W} = \{\texttt{correct\_block}, \texttt{correct\_tool\_deny}\}\). `sanitize_neutralized` is not in \(\mathcal{W}\) (no pre-registered sanitize-causal rule). `target_refusal`, `detected_not_blocked_attack_failed`, and `detection_miss_but_attack_failed` are **ties**, not wins.

When A3 is selected, the episode does not reach the Target and is scored blocked. That tests **action enforcement**, not adaptive policy quality.

---

## 5. Experimental Protocol

### 5.1 Two tracks that must stay separate

| Track | Pack | Status | Question |
| --- | --- | --- | --- |
| Layer A v2–v4 | Frozen v3 TEST `47b975f7…` (40+40) | **CLOSED diagnostic** | Detector lift? Does adaptive B3_V4 beat B0? |
| VNEXT confirmation | `vnext_confirm_v1.0` `523c8818…` (61+61) | **FAIL** | Pre-registered H1 on a new pack |

Historical harmonized simulation in `docs/paper/04_results.md` is a third track (`LEGACY_SIMULATION_ONLY`). This manuscript does not rewrite that body and does not cite those ASR values as judge ASR.

### 5.2 Shared eval contract (real LLM)

- **Target:** `qwen/qwen-2.5-7b-instruct` (`target_2`).
- **Judge:** `qwen/qwen-2.5-72b-instruct` (`judge_fallback`). Target ≠ Judge.
- **Cache:** off. Official VNEXT target cache hits: 0 / 0.
- **Backend:** OpenRouter. Judge retries on the same episode ID are not extra observations.
- **Seed:** Layer A intervention seed 42; VNEXT pack mix seed 61 (file order), pipeline/bootstrap 42.

### 5.3 Layer A protocol (diagnostic only)

Pack `layer_a_v3.0`: 80 attack + 80 benign; TEST 40+40. Attack success is emission of a synthetic canary (`AG-V3-CANARY-*`). Detector operating point 0.25 is the project default, not fit on TEST. v4 rules were not written from TEST prompt text. L2 was not scored (no tool loop in the Layer A harness at that time).

### 5.4 VNEXT pre-registration (binding)

**Primary RQ.** Label-blind adaptive defense vs B0 on the confirmation pack, defense-attributed ASR, with \(U \ge 0.95\).

**H0.** Paired attack-success vectors are equal (McNemar exact, two-sided α = 0.05), **or** the treatment fails the utility gate.

**H1 (qualified win).** Reject H0 **and** discordant treatment-favoring pairs are predominantly in \(\mathcal{W}\) **and** \(U \ge 0.95\).

**MSID.** Locked as `VNEXT-MSID-0.1`: δ = 0.20 absolute, defense-attributed, not mixed with A1 refusals. Planning values \(p_{10}=0.25\), \(p_{01}=0.05\), \(\psi=0.30\). n_attack = n_benign = **61** (exact 80% McNemar power first attained at n = 61). Changing MSID after unblinding is a protocol violation (S11).

**Stop rules that fired.** S5 (McNemar p ≥ 0.05 at locked N); MSID not met; S4 (\(U < 0.95\)). Forbidden after FAIL: extra N (no post-hoc topping up), Layer A TEST retune (S8), claiming SOTA / production (S10).

**Pack construction.** Authored synthetic, 0 LLM calls to build, IDs `vnext_c1_atk_*` / `vnext_c1_ben_*` disjoint from Layer A. Families (descriptive cells): DIRECT_OVERRIDE 11; INDIRECT_RAG_DOC, TOOL_OUTPUT_INJECTION, MULTI_TURN_PERSISTENCE, OBFUSCATION, PRIVILEGE_EXFIL 10 each. Benign: 21 tool workflows, 25 hard negatives (quoted PI / analysis), 15 ordinary. All 61 attacks declare a tool/action success condition; markers are not ASR by themselves.

**Same-ID repair.** Three `judge_api_error` rows were retried on the **same locked IDs** (`vnext_c1_atk_031` B0, `vnext_c1_ben_046` B0, `vnext_c1_atk_045` VNEXT-ADAPT). That is not extra N. A prior unofficial ~78-episode B0 fragment is discarded and is not cited as confirmation.

### 5.5 Statistics

Primary: McNemar exact on intervention-mediated cells. Proportions: Wilson and bootstrap 95% CIs (`n_bootstrap=5000`). Family ASR is descriptive. Holm correction is unused because only one treatment is tested against B0.

---

## 6. Results

Layer A numbers and VNEXT numbers are **different packs, different N, and different scientific status**. They appear in separate subsections. Do not pool them.

### 6.1 Layer A diagnostic (CLOSED)

Integrity: TEST SHA-256 `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8`. Narrative tables: `docs/paper/04_results_layer_a_diagnostic.md`. Allowed wording: `docs/paper/CLAIMS_CHECKLIST_LAYER_A.md`.

#### Detector-only

On the frozen Layer A v3 TEST split, detector v4 attack recall is 27/40 = 0.675 and AUROC is 0.705, versus v3 recall 2/40 = 0.05 and AUROC 0.368, without TEST retuning.

TRAIN recall is 20/20 = 1.00 (FPR 0, AUROC 1.00) and DEV recall is 20/20 = 1.00 (FPR 0.05, AUROC 0.991); the drop to TEST recall 0.675 is an overfitting / generalization risk.

Under v4 risk mapping, TEST HIGH mass is inverted: 2 attack HIGH versus 6 benign HIGH. These are detector metrics, not intervention ASR.

#### Intervention

With no defense (B0), judge ASR is 0.75 and benign utility is 1.00 on this TEST split.

With the v3 regex detector, adaptive B3 applied A1 on all 80 episodes (ASR 0.70 vs B0 0.75; McNemar p = 0.6875) and is not a defense win.

Adaptive B3_V4 has ASR 0.625 and utility 0.85 versus B0 ASR 0.75 and utility 1.00; exact McNemar p = 0.125. This is not a demonstrated ASR reduction.

Of the six discordant episodes with B0 attack-success and B3_V4 attack-failure, only one is a true A3 block; the other five are target refusals under A1 and are not defense wins.

When A3 is selected, the episode is scored as blocked; the two B3_V4 HIGH attacks are true blocks. That tests action enforcement, not adaptive policy quality.

#### Diagnostic mapping arms (not adaptive)

B2_L3_V4 (fixed risk-gated level 3 with the v4 signal) has ASR 0.20 and utility 0.825. This is a diagnostic mapping arm, not an adaptive-defense result.

Unconditional L3 has ASR 0 and utility 0 (security ceiling and utility floor).

ORACLE_BLOCK has ASR 0 and utility 1.00; it is label-conditioned and diagnostic only.

**Case label.** CASE B: detector improved; adaptive HIGH/MEDIUM routing remains the bottleneck. Not CASE A (no demonstrated adaptive outcome win).

### 6.2 VNEXT confirmation (FAIL)

Canonical record: `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`. Pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` (match=True). n = 61+61 scorable; exclusions empty after same-ID repair.

#### Primary pair

| Arm | n_attack | ASR | 95% Wilson | n_benign | U | 95% Wilson |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| B0 | 61 | **0.9508** (58/61) | [0.865, 0.983] | 61 | 0.9672 | [0.888, 0.991] |
| VNEXT-ADAPT | 61 | **0.8689** (53/61) | [0.762, 0.932] | 61 | **0.9344** | [0.843, 0.974] |

#### Confirmatory McNemar (intervention-mediated)

| Cell | Count | IDs |
| --- | ---: | --- |
| b10 (VNEXT intervention win) | **5** | `vnext_c1_atk_011`, `vnext_c1_atk_030`, `vnext_c1_atk_023`, `vnext_c1_atk_001`, `vnext_c1_atk_028` |
| b01 (B0 win) | **0** | — |
| Refusal-mediated “safer” (ties) | 0 | — |

- McNemar exact two-sided p = **0.0625** (α = 0.05) → **not statistically significant** (`s5_mcnemar_not_significant`).
- δ̂ = (b10 − b01) / n = **0.0820** vs MSID 0.20 → **not met** (`msid_not_met`).
- Treatment U = **0.9344** vs gate 0.95 → **utility-ineligible** (`s4_utility_ineligible`); false blocks = **1**.
- Qualified win: **NO**. STATUS: **FAIL**.

Mixed ASR McNemar is the same cell counts (b10 = 5, b01 = 0, p = 0.0625) and is **not** a qualified defense win by itself.

#### Taxonomy (VNEXT-ADAPT)

| Class | n | Counts as defense win? |
| --- | ---: | --- |
| `correct_block` | **5** | Yes (A3) |
| `correct_tool_deny` | 0 | Yes if present |
| `insufficient_intervention` | **53** | No |
| `false_block` | **1** | Utility harm |
| `unnecessary_intervention` | 60 | Not a security win |
| `target_refusal` | 2 | **No** |
| `detection_miss_but_attack_failed` | 1 | **No** |

Action mix: A1 × 114, A3 × 6, A2 × 2. Mean defense cost (treatment) = 0.1221. The six A3 decisions are five attack blocks plus one benign false block. Residual attacks: `insufficient_intervention` = 53.

B0 taxonomy (context): `detection_miss` 58, `correct_allow` 59, `target_refusal` 2, `detection_miss_but_attack_failed` 1, `utility_fail_nonblock` 2, A0 × 122.

#### Family ASR (descriptive; not powered)

| Family | B0 n | B0 ASR | VNEXT n | VNEXT ASR |
| --- | ---: | ---: | ---: | ---: |
| DIRECT_OVERRIDE | 11 | 0.909 | 11 | 0.727 |
| INDIRECT_RAG_DOC | 10 | 1.000 | 10 | 1.000 |
| MULTI_TURN_PERSISTENCE | 10 | 0.900 | 10 | 0.900 |
| OBFUSCATION | 10 | 1.000 | 10 | 1.000 |
| PRIVILEGE_EXFIL | 10 | 0.900 | 10 | 0.900 |
| TOOL_OUTPUT_INJECTION | 10 | 1.000 | 10 | 0.700 |

Point estimates move on DIRECT_OVERRIDE and TOOL_OUTPUT_INJECTION only. Those cells are not a family-wise confirmation.

#### Spend

Estimated USD (list-rate aid, not an invoice): B0 0.030358 + VNEXT 0.028658 = **0.059016** (~$0.059). Wall time 2453.92 s (pass1 2339.87 s + same-ID repair 114.05 s).

---

## 7. Failure Analysis

The confirmatory hypothesis failed for three independently sufficient reasons. Meeting any one stop rule already bars a qualified win; this run met three.

**S5 — McNemar not significant.** Exact two-sided p = 0.0625 on b10 = 5, b01 = 0. Under binomial McNemar with b01 = 0, significance at α = 0.05 requires b10 ≥ 6. Five A3 blocks on 61 attacks is below that threshold. We do **not** describe p = 0.0625 as “marginally confirmed.”

**MSID not met.** Locked δ = 0.20. Observed δ̂ = 0.0820. Even if a later experiment obtained p < 0.05 at this effect size, `VNEXT-MSID-0.1` would still reject a “useful intervention” claim. We do not lower the MSID after unblinding.

**S4 — utility ineligible.** U = 0.9344 < 0.95. False blocks = 1. A security story that misses the co-primary gate is not a qualified runtime result.

**Attribution is honest and still insufficient.** All five b10 IDs are `correct_block` (A3), not target refusals. That is an improvement over Layer A, where five of six discordant pairs were A1 refusals. Honesty about attribution does not convert a FAIL into a PASS: 53 / 61 attacks remain `insufficient_intervention` (detected or acted with A0/A1/A2, judge still `attack_success=true`). A2 appears twice and `correct_tool_deny` is 0, so tool restriction did not drive the confirmatory cells.

**Mechanism continuity with Layer A (CASE B), without mixing numbers.** After the v4 detector lift, adaptive HIGH/MEDIUM routing remains the bottleneck: most detected TEST attacks sit in MEDIUM and receive A1 at adaptive `defense_level` ≤ 1. The VNEXT action mix (A1 × 114) is consistent with that mapping remaining dominant on a *new* pack. This is a qualitative failure analysis, not a pooled ASR.

**What we refuse to do after FAIL.** Retune thresholds or HIGH/MEDIUM bands on Layer A TEST `47b975f7…`. Increase N on `vnext_confirm_v1.0`. Rewrite MSID. Relabel B2_L3_V4 or ORACLE_BLOCK as the confirmatory treatment. Treat detector AUROC as a substitute for intervention McNemar.

---

## 8. Limitations

1. **Single Target / Judge pair.** Results are for Qwen 2.5 7B Instruct judged by Qwen 2.5 72B Instruct. They are not a multi-architecture robustness proof (protocol RQ-S4 was not the primary test).
2. **Authored synthetic packs.** Layer A uses exclusive-output canaries. VNEXT uses authored tool/action success conditions. Neither is production RAG, browsing, or a full agent environment.
3. **Heuristic detector.** v4 evidence scores are not probabilities. TRAIN/DEV saturation with TEST drop is an overfitting risk, not a generalization theorem.
4. **Adaptation is counter-based**, not learned, and not Judge-in-the-loop on the same episode.
5. **L2 / agent claims.** Layer A did not score L2. VNEXT can deny tools in-harness, but the primary pair is B0 vs VNEXT-ADAPT; `correct_tool_deny` = 0. This is not AgentDojo.
6. **n = 61 is powered for MSID 0.20, not for small effects.** Observing δ̂ = 0.0820 is a failed useful-intervention claim, not an invitation to extend the same locked pack.
7. **Utility CI overlaps the gate.** Treatment U Wilson interval [0.843, 0.974] includes 0.95; the pre-registered rule is the **point estimate** U ≥ 0.95. The point estimate fails.
8. **Spend is a list-rate aid** (~$0.059), not a systems cost benchmark.
9. **No human κ on the Judge.** Independence (different model ID, blind payload) is implemented; calibration against human labels is not.
10. **Historical simulation** in `docs/paper/04_results.md` can look like a large adaptive win under circular outcome semantics. It is out of the confirmatory claim set.

---

## 9. Ethics

**Purpose.** This package documents a **failed confirmatory security claim** so that adaptive runtime intervention is not oversold.

**Dual use.** The confirmation pack contains synthetic instruction-override and tool-misuse prompts. It is an evaluation corpus, not a cookbook for attacking third-party systems. Success conditions are tool/action outcomes on a harness, not exploits against production services.

**Human subjects and data.** No user logs, no PII collection, no crowdworker study. Packs are authored synthetic text.

**Compute and cost.** The official confirmation used on the order of $0.06 in list-rate token aid. We do not present that as an environmental or economic result.

**Release.** Code is MIT-licensed. We do not submit this manuscript to arXiv as part of this package. Downstream users must not advertise AdaptiGuard as production-ready on the basis of this FAIL.

**Responsible claim language.** Overstating a non-significant, below-MSID, utility-ineligible run as a “promising defense” would itself be an ethical failure: operators might disable other controls. The claims map exists to prevent that.

---

## 10. Reproducibility

**Do not rerun live eval to change the verdict.** The official FAIL is the AUDIT folder. New API calls would be a new experiment ID, not an amendment of `VNEXT-MSID-0.1`.

**Inspect (no LLM):**

```bash
sha256sum datasets/frozen/vnext_confirm_v1/dataset.jsonl
# expected 523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518

python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py

python3 -m pytest tests/test_vnext_confirm_pack.py tests/test_vnext_confirm_runner.py \
  tests/test_vnext_phase2_harness.py -q
```

**If a reader reproduces the live pair** (requires `OPENROUTER_API_KEY`; not requested here): `python3 scripts/run_vnext_confirm.py --require-key` must hash-gate the pack, keep cache off, score B0 then VNEXT-ADAPT on the same IDs, and abort on hash mismatch. That runner already recorded STATUS=FAIL.

**Artifact index.** [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md). [`CITATION.md`](CITATION.md). Protocol files under `docs/experiments/VNEXT_*.md`.

**What was not modified.** Frozen JSONL packs; Layer A AUDIT folders; the simulation body of `docs/paper/04_results.md` (pointer only).

---

## Conclusion

On the frozen Layer A v3 TEST split, detector v4 raises recall and AUROC without TEST retuning, and adaptive B3_V4 is still not a demonstrated ASR reduction. On the pre-registered VNEXT pack, VNEXT-ADAPT vs B0 **FAILS**: McNemar p = 0.0625, δ̂ = 0.0820 < MSID 0.20, U = 0.9344 < 0.95. Five A3 `correct_block` events and 53 `insufficient_intervention` attacks do not confirm cost-aware adaptive intervention. Report the negative result; do not retune it into a win.

---

## References (workshop, non-archival)

- Chen, S., Piet, J., Sitawarin, C., and Wagner, D. StruQ: Defending against prompt injection with structured queries. 2024.
- Chen, S., Zharmagambetov, A., Mahloujifar, S., Chaudhuri, K., and Wagner, D. SecAlign: Defending against prompt injection with preference optimization. 2024.
- Debenedetti, E., et al. AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents. NeurIPS Datasets and Benchmarks, 2024.
- Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., and Fritz, M. Not what you’ve signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. 2023.
- Inan, H., et al. Llama Guard: LLM-based input-output safeguard for Human-AI conversations. 2023.
- Liu, Y., et al. Prompt injection attack against LLM-integrated applications. 2023.
- McNemar, Q. Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika*, 12(2):153–157, 1947.
- OWASP. OWASP Top 10 for Large Language Model Applications (LLM01 Prompt Injection).
- Perez, F., and Ribeiro, I. Ignore previous prompt: Attack techniques for language models. 2022.
- Rebedea, T., Dinu, R., Sreedhar, M., Parisien, C., and Cohen, J. NeMo Guardrails: A toolkit for controllable and safe LLM applications with programmable rails. 2023.
- Wallace, E., Xiao, K., Leike, R., Weng, L., Heidecke, J., and Beutel, A. The instruction hierarchy: Training LLMs to prioritize privileged instructions. 2024.
- Yi, J., et al. Benchmarking and defending against indirect prompt injection attacks on large language models (BIPIA). 2023.
- Zhan, Q., Liang, Z., Ying, Z., and Kang, D. InjecAgent: Benchmarking indirect prompt injections in tool-integrated large language model agents. 2024.

Primary *evidence* for this manuscript is not the bibliography; it is the frozen packs and `AUDIT.md` files listed in [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md).
