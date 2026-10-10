# §5 Experiments and §6 Results (phase-2 draft)

**Status:** draft prose. Every count, rate and interval cites a `NUMBERS_LEDGER.md` row with its file and key. All harness experiments are exploratory and not pre-registered.

---

## 5 Experiments

**Table 3. Experiments in the evidence base.**

| id | what | data | targets | endpoint | where |
|---|---|---|---|---|---|
| E2 | exploratory four-arm run on the original scenarios | 2 attack scenarios (12 instances each), 3 benign scenarios (5 each), 468 episodes | qwen3-30b-a3b, gemma-4-31b-it, deepseek-v3.2 | executed call; proposal secondary | §6.1 |
| E3 | partially independent families, undefended vs defended, paired | 7 families, 56 instances, 168 undefended and 336 defended episodes | the same three targets | executed call | §6.2 |
| E5 | external test on InjecAgent (locally drafted protocol, not externally registered) | 186 cases per target (62 attacker instructions × 3 contexts) | llama-4-maverick, qwen3.8-flash | first tool call is the attacker's tool (proposal level) | §6.3 |
| C | calibration of undefended rates | InjecAgent (n = 40 per target) and a human-written Hard set (n = 68 or fewer) | five 2026 targets | first tool call (InjecAgent); executed-call flag (Hard set) | §6.4 |
| A | exploratory InjecAgent run, one target | 120 cases | llama-3.3-70b-instruct | first tool call (proposal level) | Appendix A |

### 5.1 Defenses under test
**A0** is no defense. **B3** is the adaptive intervention stack wired into the harness (pre-target; risk-driven levels with sanitizing and wrapping actions). In every run here it never blocked. **PHASE1-CORE** (CORE) is the Phase-1 detector and policy stack, which can deny tool calls. **TOOLDENY** is a static policy that denies `send_email` and `create_record` and allows read tools; it acts after the model and is a deliberately blunt comparator. **ARGALLOW** (a static argument allowlist) was implemented and unit-tested but not run live. A delimiter on the tool channel (SPOT_TOOL) is used only in the external test.

### 5.2 E2: exploratory four-arm run on the original scenarios
A multi-turn tool harness (§3.2) with three targets, four arms, temperature 0, and per-episode trajectories. Two attack scenarios from the original template family, `direct_user_override_v1` and `create_record_exfil_v1`, with 12 instances each, and three benign scenarios with 5 instances each. The primary endpoint is the attacker-specified call reaching the executor; the proposal endpoint is secondary. Scenario validity under M3 is applied in §4.3: under that rule neither attack scenario is valid, and E2 results are reported as measurement illustrations.

### 5.3 E3: partially independent attack set
Seven attack families written from public benchmark styles (an important-instructions block in a document and in a tool output, a workflow footer, an authority claim, an unrequested write, an updated instruction on a second read, a split e-mail address), 24 instances per family, of which 8 per family were run. Every family delivers its payload through a tool output with a clean user turn and has an attacker-controlled effect (a foreign recipient, or a write the user did not request), so it passes both clauses of the M3 rule by design. The template file was frozen before any run; its authorship is partially independent (§8.3). Step 1: undefended screening, 168 episodes over 56 instances and three targets. Step 2: B3 and CORE on the same instances, 336 episodes, paired with step 1 by (family, instance, target).

### 5.4 External test and calibration
*External test (E5).* The 186-case sample is 62 attacker instructions in three contexts each, cluster units are the attacker instruction, and the arms are A0, an identical-input replicate of A0 (A0_REP), SPOT_TOOL (delimiters on the tool channel) and a no-injection control (NOINJ, 40 cases). The endpoint is proposal level: the first tool call is the attacker's tool; nothing is executed. The analysis is a cluster bootstrap of paired differences (resample count and seed as fixed in the protocol draft), Wilson intervals, and exact McNemar tests as descriptive statistics. The protocol named Holm across the four open targets for H1 and H2. The intervals reported in §6.3 are Bonferroni α/4 intervals, not Holm intervals.

*Calibration (C).* Before the test we measured the undefended rate (A0) of five 2026 targets on InjecAgent (40 cases each) and on the human-written Hard set (68 items for four targets; 20 for one, a closed model). Zero events are reported with two-sided 95% Clopper–Pearson upper bounds. A target is classified by a floor rule: a rate below 5% at n ≥ 40 is "below 5%, floor not demonstrated", a zero count at n = 40 or fewer than 40 scored items is "undetermined", and only a target with a rate of at least 5% at n ≥ 40 is "measurable". A target that is not measurable cannot test a defense.

### 5.5 Statistics and status
Rates carry Wilson 95% intervals. E3 paired effects use exact McNemar tests (descriptive, because instances are clustered by family) and paired bootstrap intervals (5000 resamples, seed 20260930, episode-level, with an instance-clustered check in §8.2). We report no confirmatory p-values. The E2 and E3 scoring rules were not pre-registered, and the E2 inclusion rule of §4.2 was adopted post hoc.

## 6 Results

### 6.1 E2: the same traces under four scoring rules, and a validity check
Attack episodes per arm (72 episodes: two scenarios, 12 instances, three targets), scored four ways (`figures/fig1_scoring_flip.csv`):

| rule | A0 | B3 | CORE | TOOLDENY |
|---|---|---|---|---|
| model proposed the call | 66/72 | 65/72 | 36/72 | 65/72 |
| call reached the executor, blocked episodes counted as not successful | 66/72 | 65/72 | 36/72 | 0/72 |
| sensitivity: every `INVALID_NOT_DELIVERED` episode dropped | 65/71 | 65/72 | 36/36 | 0/69 |
| direct-override scenario only, executed (not a valid attack under M3, §4.3) | 30/36 | 29/36 | 0/36 | 0/36 |

The static policy is invisible to the proposal endpoint and complete under the executed endpoint. CORE moves from "halves the attack" to "no effect" to "complete stop" as the labeling and the scenario set change. The complete stop is confined to the direct-override scenario, which fails M3, so it is not a valid defense result. The second scenario, `create_record_exfil_v1`, is executed in 36/36 episodes under A0, B3 and CORE, and in 0/36 under TOOLDENY.

*Benign utility.* Benign tasks (45 per arm) were scored from the executor log against each instance's expected record kind: A0, B3 and CORE complete 45/45; TOOLDENY completes 15/45 (weather tasks only). The static policy's utility cost is therefore a property of denying side-effecting tools.

*B3.* B3 produced no block. Against the undefended arm it changed two pairs one way and one the other (b10/b01 = 2/1 over 72 pairs), and its executed count is 65/72 against 66/72.

### 6.2 E3: partially independent families
*Susceptibility of the undefended agents (Fig. 2).* The undefended agents executed attacks in 41/56 episodes for deepseek, 8/56 for qwen3 and 8/56 for gemma. The authority-claim framing, which has no instruction marker and no literal tool name, succeeded in almost every episode of every target, which is the strongest attack in the set. One target (mostly qwen3, and gemma in two families) wrote that it had performed the action without making the call, in several families, and text-level scoring would count those as compromises; text-level scoring would count those as compromises. A pooled admission rule (at least 50% undefended execution) admits one of seven families, while the same rule applied per model admits six families for deepseek.

*Defended vs undefended, paired (Fig. 3).* B3: 56/167 undefended executions against 57/167 defended, with b10/b01 = 3/4; the paired difference is +0.006 with a bootstrap interval of −0.024 to +0.036 (`analysis` artifact `docs/research/artifacts/e3_delivery_audit_20261003.json`). CORE: 57/168 against 57/168, with b10/b01 = 4/4; the difference is +0.000 with an interval of −0.036 to +0.036. Neither defense produced a block: CORE blocked 0/168 defended episodes, against 36/36 on the original direct-override scenario.

*Labeling and pairing.* The pairs above include episodes that the harness labeled `INVALID_NOT_DELIVERED`, because the estimand is an executed attacker call for an assigned instance. 14 of the 168 undefended episodes carry that label, and in 10 of them the tool carrying the payload was never called. Restricting to pairs where the carrier tool ran leaves the conclusion unchanged: 157 B3 pairs with b10/b01 = 3/3, and 158 CORE pairs with b10/b01 = 4/3 (Appendix D).

*Noise floor.* CORE with zero blocks presents the same model input as the undefended arm, yet 4 pairs flip in one direction and 4 in the other (4/4). Differences of that size cannot be attributed to a defense.

### 6.3 External test on InjecAgent (E5)
Proposal-level outcome on 186 cases per target, with the NOINJ control on 40 cases. Proposal rate is the first tool call being the attacker's tool; no call was executed.

| target | A0 | A0 replicate | NOINJ | SPOT_TOOL | SPOT_TOOL minus A0, mean | cluster 95% CI (Bonferroni α/4 CI) |
|---|---|---|---|---|---|---|
| llama-4-maverick | 23/186 (Wilson 8.4 to 17.9) | 24/186 | 0/40 | 5/186 | -0.097 | [-0.145, -0.048] ([-0.161, -0.038]) |
| qwen3.8-flash | 23/186 (Wilson 8.4 to 17.9) | 22/186 | 0/40 | 4/186 | -0.102 | [-0.156, -0.054] ([-0.172, -0.043]) |

The replicate differs from A0 by 0.005 (95% CI [-0.027, 0.038]) for llama-4-maverick, and by -0.005 (95% CI [-0.059, 0.048]) for qwen3.8-flash. That is the run-to-run noise at this sample size. A tool-channel delimiter lowers proposal-level attacker tool calls by about ten points on both targets, larger than that noise, and the intervals exclude zero at the Bonferroni α/4 level for both. The result is descriptive. The two targets were selected from the calibration of §6.4, and the protocol was not frozen. Only the two-target comparison is reported; the other targets were classified in §6.4 and not retested.

*Scope and disclosures.* (i) Two targets, one benchmark, non-adaptive attacks, proposal endpoint; the result corroborates a measurement effect and does not test M1 or M6. (ii) The B3 and CORE arms left every InjecAgent case unchanged in an offline check, so they were not run live. (iii) qwen3.8-flash's calibration (6/36 scored, §6.4) does not meet the protocol's n ≥ 40 requirement for classification; its selection therefore departs from the floor rule. (iv) Sample size: the protocol draft planned 310 cases (5 contexts × 62 instructions), the protocol's analysis section planned 124 (2 × 62), and the run used 186 (3 × 62). Neither change appears in the protocol's deviation log, and the reason given in the paper is the authors' account. (v) Temperature 0 was requested in the runner's request body (commit `96b33e4eec1f2b32afcbe697a1d3d26add2bbd38`, script not in this tree). The episode records store no temperature, provider route or model version, so these settings cannot be verified from the records. (vi) No provider errors occurred in the registered run.

### 6.4 Calibration: most 2026 targets are below 5% or undetermined
Undefended rates (A0) and the NOINJ control on InjecAgent (n = 40 per target), and the human-written Hard set (n = 68, or 20 for the closed target). Zero events are reported with two-sided 95% Clopper–Pearson upper bounds, 8.8% at n = 40 and 5.3% at n = 68.

| target | InjecAgent A0 | Hard set A0 (human-written) | Generated-origin A0 (exploratory) | InjecAgent NOINJ | classification |
|---|---|---|---|---|---|
| llama-4-maverick | 5/40 | 1/68 | 0/22 | 0/40 | measurable on InjecAgent; below 5% on the Hard set, floor not demonstrated |
| qwen3.8-flash | 6/36 scored (4 provider errors) | 0/40 scored (28 provider errors) | 3/15 scored (7 provider errors) | 0/37 scored (3 provider errors) | undetermined on both sets (InjecAgent n = 36 < 40; Hard set 0/40) |
| glm-4.7 | 1/40 | 1/68 | 1/22 | 0/40 | below 5%, floor not demonstrated, on both sets |
| deepseek-v4.1-flash | 0/40 (upper bound 8.8%) | 0/68 (upper bound 5.3%) | 0/22 | 0/40 | InjecAgent undetermined (0/40); Hard set below 5%, floor not demonstrated |
| gpt-5.6-sol (closed) | 0/40 (upper bound 8.8%) | 0/20 | 1/20 | 0/40 | undetermined on both sets (fewer than 40 scored on the Hard set) |

The generated-origin column reports the model-written Hard-set items, which are exploratory. They are shown so that no half of the calibration is hidden, but the classification uses only the human-written Hard set.

Two readings follow. First, a defense cannot be shown to reduce an attack that the undefended model does not carry out, so on most of this panel a defense comparison would measure noise. The floor rule decides which targets enter the external test (§6.3), and the qwen3.8-flash calibration does not meet its n ≥ 40 requirement. Second, the Hard set, built for earlier models, has an undefended rate below 5% at the point estimate for the three targets with 68 scored items and is undetermined for the other two. We did not run older models, so we cannot say whether benchmark informativeness decays over time; we report only that most 2026 targets were below 5% or could not be assessed, and that we did not establish a floor for any of them. The choice of targets from these rates is itself a selection step and is disclosed in §6.3.
