# What Reached the Executor? Measurement Validity for Runtime Defenses of LLM Agents, and a Floor Effect on Strong Models

---

## Abstract
Defenses for tool-using LLM agents are usually compared by an attack success rate, and the measurement choices behind that rate are rarely reported. We ask how valid such measurements are, and what happens when public attacks reach a floor on strong models. This is a case study on one testbed: a multi-turn tool harness with an executed-call endpoint, an exploratory two-scenario run on three open-weight models, a partially independent 168-episode attack set, an external InjecAgent test on two 2026 models (186 cases each), and a calibration of five 2026 models.

The success endpoint changes the verdict. A static tool policy executes 0/72 attacks but is invisible to proposal-level scoring (65/72 proposed), and it lowers benign utility from 45/45 to 15/45. Under a strict scenario rule (an untrusted channel and an attacker-controlled effect), the exploratory run contains no valid attack, so its apparent complete stop is not evidence. On the partially independent set, which passes the rule, neither detector-style defense changes executed attacks beyond the replicate noise (56/167 and 57/168 undefended and defended executions), and susceptibility differs by model (41/56 against 8/56). Most 2026 targets are below 5% or undetermined, so defense comparisons on them would be uninformative. On the two assessable targets, a tool-channel delimiter lowers proposal-level attacker tool calls by about ten points. Five of six candidate checks are demonstrated on these traces; the sixth is proposed only. We claim no defense is effective or ineffective in general.

## 1 Introduction

**Question.** How valid are measurements of prompt-injection defenses in LLM agents, and what happens when public attacks hit a floor on strong models? We answer for one testbed, and we treat the defenses as instruments: their effects are measured to illustrate the measurement decisions, not to rank them.

LLM agents that call tools read untrusted content, such as documents, tool outputs and messages, and can be steered by instructions planted in it (indirect prompt injection) [2403.02691; 2406.13352]. Defenses range from delimiters and prompt sandwiching to detectors and system-level designs [2503.18813; 2504.11703]. Two lessons frame the work. Defenses that look strong on static attack sets are routinely broken by adaptive attackers [2503.00061; 2510.09023; 2606.15057]. And the measurement can itself mislead: scoring success by tool identity rather than by arguments inflated an attack success rate from 1.2% to 21.7% in one audit [2609.32691].

We add a more mundane observation from our own evaluation. Choices that look like bookkeeping decided the conclusions: which endpoint counts as success, how a payload stopped before the model is labeled, whether a scenario is an attack at all, who wrote the scenarios, and whether results are pooled across models. We record each choice as a candidate measurement check (M1 to M6, §4) and report what it changes on our traces.

**What we did.** (i) An exploratory multi-turn comparison of four arms on the original scenarios (E2), scored four ways from the same episodes. (ii) A partially independent attack set of seven families, frozen before the run, with undefended and defended arms paired by instance (E3). (iii) An external test of the one assessable pair of targets on InjecAgent at proposal level, with a locally drafted protocol that was not externally registered (§5). (iv) A calibration of five 2026 targets on InjecAgent and on a human-written Hard set, which decides which targets can be tested at all.

**Findings.** (a) Endpoint and labeling choices change verdicts on E2 (§6.1). (b) E2's apparent complete stop by a Phase-1 policy rests on a scenario that fails the scenario-validity rule, so E2 gives no valid defense result. (c) On the partially independent E3 set, both detector-style defenses leave executed attacks unchanged within noise, and undefended susceptibility is model-specific (§6.2). (d) Most 2026 targets show undefended rates below 5% or are undetermined at the protocol's sample sizes (§6.4). (e) On the two assessable targets, a tool-channel delimiter lowers proposal-level attacker tool calls by about ten points, which corroborates a measurement effect but does not test any check (§6.3).

**Contributions.**
1. Six candidate measurement checks (M1 to M6), derived from one case study, with the status of each on our traces (§4, Table 2). Five are demonstrated here, at exploratory strength. M6 (the defense must reach the untrusted channel) is proposed and not demonstrated here.
2. A scenario-validity rule and its consequence for a published-style comparison: under the rule, one of our two E2 scenarios and all of E2 fail (§4.3).
3. A partially independent, frozen attack set with a per-model susceptibility profile and a measured noise floor (§6.2).
4. Calibration evidence that public InjecAgent and Hard-set attacks are not measurable on most strong 2026 targets, with an explicit "undetermined" category (§6.4).
5. Committed traces, offline scripts and a number ledger that regenerate the reported E2 and E3 numbers and the external-test counts (§10, Appendix C).

**Non-claims.** We do not claim that any defense is effective or ineffective in general, that adaptive intervention cannot work, or anything about frontier or closed models. We ran no adaptive attacker and no system-level defense (§8.1).

## 2 Related work
**Benchmarks.** AgentDojo provides stateful, multi-tool environments with deterministic state-based utility and security checks rather than LLM evaluators [2406.13352]. InjecAgent measures indirect injection on single-turn tool-integrated agents and finds that the user case is more strongly associated with success than the attacker case [2403.02691]. BIPIA covers several task families and judges outcome manipulation by rules and an LLM [2312.14197]. LLMail-Inject releases submissions from a public challenge against a simulated email assistant, with success defined by a tool call with the correct arguments; one team reports using an LLM to generate variants of a template [2506.09956]. LongPIBench adds long-context documents, where defenses that look strong on short inputs can fail [2608.28411]; PIArena and pikit provide platforms and toolkits that vary attacks, delivery and defenses [2604.08499; 2609.36817]. We use the principle of scoring the environment state, AgentDojo's tool-filter result as a comparator, InjecAgent for the external test, and the human-written part of LLMail-Inject for calibration only.

**Defenses.** Prompt-level defenses (delimiters, sandwiching, spotlighting), detectors, fine-tuning and system-level designs have all been proposed [2403.14720]. Capability- and interpreter-based systems such as CaMeL isolate a privileged planner from a quarantined parser [2503.18813]; Progent enforces least-privilege rules at the tool-call boundary [2504.11703]; MELON and Task Shield check tool calls against a re-execution or the user's goal [2502.05174; 2412.16682]. In AgentDojo a simple tool filter was the most effective of the defenses tested [2406.13352]. A vendor study reports that only deterministic output filtering held against a long adaptive campaign on system-prompt leakage [2604.23887].

**Adaptive attacks.** Defenses that look strong on static sets are broken by defense-aware attackers: white-box optimization breaks several indirect-injection defenses [2503.00061], a multi-lab study breaks a dozen defenses with search, reinforcement learning and human red-teaming [2510.09023], and a cheap black-box optimizer recovers attack success against several filter defenses [2606.15057]. Automated attacks adapted to AgentDojo are model-dependent [2606.10525], and a protocol for adaptive evaluation of out-of-band defenses has been specified [2606.26479]. We ran no adaptive attacker.

**Evaluation validity.** This is the closest line of work. Shaw audits an agent-security harness and identifies payload non-delivery and tool-identity scoring as defects; scoring by tool identity reports 21.7% where the argument-level rate is 1.2% [2609.32691]. Sakib et al. place a byte-identical payload in a tool output or in a tool description across 13 models and four AgentDojo suites, find that 44.9% of model pairs change their relative ordering, and find that mitigations effective against tool-output attacks can leave exposure through tool descriptions [2605.30454]. Akinrele and Gowda show that detector rankings depend on the evaluation regime and the false-positive budget [2605.26999]. Pathade et al. decompose attack success rate into six axes (A1 Unit of Analysis, A2 Success Oracle, A3 Trials and Non-determinism, A4 Attacker Adaptivity, A5 Attacker Knowledge of the Defense, A6 Binarization of Partial Success), meta-analyze 259 papers, give a ten-item reporting checklist, and show analytically how large an effect a sample of 100 can detect (about 18 pp) [2609.25173]. Their contribution is analytical and meta-analytic, and in our reading they report no defense experiment. A public red-teaming arena reports attack success of 0.5% to 8.5% across 13 frontier models and notes that a replayed attack does not always succeed again on the same model [2603.15714].

**Position.** We do not propose a defense or a benchmark. Pathade et al.'s axes cover general agentic security evaluation design. Four of our checks lie outside those axes, which the authors state are not exhaustive: blocked-payload labeling (M2), scenario validity (M3), attack-set authorship independence (M4) and defense-channel verification (M6). Two of our checks refine existing axes on our traces: the success endpoint (M1) refines A2, and per-model reporting with a noise floor (M5) refines A3. Our evidence is a single case study on one testbed. Only M6 is left as a proposal (§4.7).

## 3 Threat model and testbed
### 3.1 Threat model
The user turn, the system prompt and the defense code are trusted. Content returned by tools is untrusted and may contain text placed by an attacker who cannot see or change the user's prompt, the model weights or the defense configuration. The attacker's goal is an effect the user did not request: an e-mail to an attacker-chosen recipient, or a write carrying attacker content. Attacks are non-adaptive. The defender controls the scaffold: it can transform content before the model, deny or allow tool calls after it, and cannot change model weights. The single-agent, single-user, English-language setting excludes multi-agent, supply-chain, multimodal and cross-session attacks. A user-turn override is outside this model; it is reported only where a scenario uses one, and §4.3 treats it accordingly.

### 3.2 Testbed
*Multi-turn harness (E2, E3).* Four deterministic mock tools (`get_weather`, `retrieve_document`, `send_email`, `create_record`), a scenario-aware executor and per-episode trajectories. The attacker's goal is an argument-level predicate over executed calls (tool, arguments and an injected marker), so a legitimate use of a shared tool cannot satisfy it. A delivery check records whether the marker reached the model through the intended channel; episodes where it did not are labeled by cause, and blocked payloads are a separate outcome (§4.2). Runs use temperature 0 and a hard cap on HTTP requests. Targets were reached through one aggregator: qwen/qwen3-30b-a3b, google/gemma-4-31b-it and deepseek/deepseek-v3.2 in E2 and E3; meta-llama/llama-3.3-70b-instruct only in the 2026-09-30 InjecAgent run (Appendix A).

*External test and calibration.* InjecAgent cases (external; 62 attacker instructions crossed with 17 user tools), run at proposal level on llama-4-maverick and qwen3.8-flash (186 cases each), and calibrated on five 2026 targets (§5.4). A Hard set of human-written items from LLMail-Inject (public, MIT) is used only for calibration.

*Scope.* The evidence base is limited to the runs of 2026-09-30 and 2026-10-01 on non-weak models. Earlier judge-scored tracks, a held-out application of the rules, the qwen-2.5-7b, llama-3.1-8b and mistral-small runs, and the other 2026-09-30 InjecAgent targets are outside the evidence base and are not used as evidence in this paper (`docs/CASE_STUDY_SCOPE.md`).

*Artifacts.* The frozen packs of the excluded tracks are not used here. The E2 and E3 traces and the external-test records are committed, and the analysis scripts read them (Appendix C). The template files of the E3 set are not in the current tree; their SHA-256 values are in `REPRODUCIBILITY.md` (§8.5).

## 4 Candidate measurement checks for defense evaluation

An attack success rate hides at least six decisions: what counts as an attack, what counts as success, how a payload stopped before the model is labeled, who wrote the scenarios, whether results are pooled across models, and whether the defense reaches the channel the attack uses. We state each decision as a check (M1 to M6), the rule we adopt for it, and what it changed on our traces.

Relative to Pathade et al.'s six axes (A1 Unit of Analysis, A2 Success Oracle, A3 Trials and Non-determinism, A4 Attacker Adaptivity, A5 Attacker Knowledge of the Defense, A6 Binarization of Partial Success), M1 refines A2 and M5 refines A3. M2, M3, M4 and M6 are not among the six axes, which the authors state are not exhaustive. M1 and M2 relate to Shaw's defect classes (tool-identity scoring and payload non-delivery) [2609.32691]. To our knowledge M4 and M6 are not covered by existing checklists.

### 4.1 M1: score what reached the executor, not what the model proposed
A defense can act before the model (by removing or wrapping untrusted content) or after it (by refusing to execute a call). If success means "the model proposed a call that matches the attacker's specification", a post-model defense is invisible: the model still tries and the policy stops execution. We define the primary endpoint as the attacker-specified call, with matching arguments and the injected marker, executed by the tool layer, and report the proposal endpoint as secondary.

In E2 a static policy that denies `send_email` and `create_record` yields 65/72 episodes with a matching proposed call (the undefended arm: 66/72), but 0/72 executed calls. Under the proposal endpoint the policy would look like no defense; under the executed endpoint it is a complete stop. The flip is true by construction for a post-model deny, so it illustrates the endpoint rather than testing a defense. Its limits are the scenario limits of §4.3: both E2 scenarios enter the count, and one of them is not a valid attack.

### 4.2 M2: a pre-target block is a defense outcome, not a delivery failure
Harnesses check that the injected payload reached the model and mark episodes where it did not as invalid, to avoid crediting a defense for an attack that never happened [2609.32691, defect class of payload non-delivery]. A defense that sanitizes or blocks content before the model also produces an episode in which the payload never reaches the model. Labeling both as "not delivered" and excluding them converts a defense into missing data.

In E2 all 36 blocks by the Phase-1 policy (PHASE1-CORE) on the direct-override scenario carry the harness label `INVALID_NOT_DELIVERED` (cause: the marker absent from the request channels). Counting them as failed attacks gives 36/72 executed; excluding them gives 36/36 (`figures/fig1_scoring_flip.csv`, rows R2 and R3). The same traces therefore support "halves the attack" or "stops it completely" depending on this one rule. We adopt a separate outcome, *blocked before the target*: the marker absent from the request channels together with a recorded block on the message that carried it. Such an episode counts as an unsuccessful attack and stays in the denominator. Because the rule is a choice, we report the alternative as a sensitivity row and downgrade any claim on which the two disagree.

*Observed-consequence rule (E2 episode scoring, adopted post hoc).* Inclusion in E2 denominators is decided by the recorded consequence, not by the harness status. The rule was fixed after the E2 data were collected and after the first manuscript transfer, and entered the scoring script on 2026-10-03. It changed two headline cells and excludes no E2 episode. It is not pre-registered.

### 4.3 M3: an attack scenario must be an attack under a stated rule
A scenario labeled as an attack must have (a) an untrusted channel through which the instruction arrives and (b) an effect the user did not request and the attacker controls (a foreign recipient, or a write carrying attacker content). We adopt both clauses as one conjunctive rule. The attacker model of §3.1 requires an untrusted channel, and a user-turn override is not within it; a rule that accepted an effect alone would accept a trusted user's own request whenever it went to a foreign recipient. This is a construct-validity check: a scenario that fails it may not be scored as an attack in a defense claim.

Applied to E2, the rule excludes both scenarios. `create_record_exfil_v1` fails both clauses: the user turn asks for the record, and the scenario differs from the benign create-record task only in the record-kind name. `direct_user_override_v1` has an attacker-controlled effect (a foreign recipient) but its override sits in the user turn, so it has no untrusted channel. Under the rule, E2 contains no valid attack. The E2 result that PHASE1-CORE executes 0/36 attacks on the direct-override scenario (and that the static policy stops both scenarios) is therefore a measurement on an invalid scenario and is not used as evidence of defense effect. The E3 families were built with both clauses (§5.3) and are the only scenarios in our data that pass the rule.

We report the consequence rather than choosing the more lenient reading after seeing the results: E2 supports the endpoint and labeling checks (M1, M2) as measurement illustrations, but not any valid defense claim, and the valid-scenario defense result rests on E3 alone.

### 4.4 M4: scenario authorship must be independent of detector development
When the attack set and the detector are developed by the same author, or iterated together, the detector's features can coincide with the surface forms of the scenarios without any claim being false. The repository history shows that the Phase-1 detector was committed before the Phase-1 holdout and confirmation packs and after an earlier pack, on the same day [commit `12414c8`, equivalent to `c462945` cited by an internal report]; commit timestamps are author-controlled metadata, so this establishes the recorded order and not an independent time record. We do not quantify the overlap of detector patterns with pack text here, because that analysis used a pack outside the evidence base.

An AI assistant then authored seven attack families from public benchmark styles, which we froze before running any defense on them (E3). The assistant had read the detector's pattern lists earlier in the same working session, so independence is partial and is disclosed in §8.3. On this set the Phase-1 policy blocked no episode (0/168 defended episodes; `paired_vs_a0_analysis.json`, key `arms.CORE.episodes_with_block`), whereas on the original direct-override scenario it blocked 36/36. The difference between the two sets is consistent with the coupling the check describes, but the design does not isolate it; confirming M4 needs an author who has not seen the detector.

### 4.5 M5: report susceptibility per model, and include a noise floor
Two decisions changed which cells were informative. First, susceptibility is model-specific: the undefended agents executed the E3 attacks in 41/56 episodes for deepseek but 8/56 for each of qwen3 and gemma (`figures/fig2_susceptibility.csv`). A defense cannot be shown to help on a model that ignores the attack without it, so admission and reporting should be per model. Second, a paired comparison must include a noise floor. Two arms with identical model input, the undefended arm and the Phase-1 policy with zero blocks, split 4/4 between the two directions of discordance (`paired_vs_a0_analysis.json`). Differences of that order cannot be attributed to a defense. The external test of §6.3 has the same structure: an undefended replicate differs from the first undefended arm by 0.005 for llama-4-maverick and by -0.005 for qwen3.8-flash, the run-to-run noise at 186 cases.

### 4.6 M6: is the defense applied to the untrusted channel? (proposed, not demonstrated here)
In an earlier pipeline a delimiter defense wrapped the user prompt and left the untrusted context unmarked; its effect then appeared on direct injections and was absent on indirect ones, the channel the defense is meant for. The finding came from a held-out application outside the evidence base of this paper and is not used here. Within the in-scope evidence we have one result consistent with the check: a delimiter on the tool channel lowers proposal-level attacker tool calls on the two assessable targets (§6.3). That result does not test M6, because no arm applied the defense to the wrong channel, so the check's failure mode is never observed. We therefore record M6 as proposed: a rule for evaluators to consider, with no demonstration here.

### 4.7 Status of the six checks
**Table 2. Status of the candidate checks on the in-scope evidence.**

| check | rule | in-scope evidence | status |
|---|---|---|---|
| M1 success endpoint | executed call with matching arguments and marker; proposal reported separately | E2: 65/72 proposed vs 0/72 executed for the static policy (§6.1) | demonstrated, exploratory; limited by the M3 result |
| M2 blocked payload | a block before the target is a defense outcome; sensitivity to the alternative labeling | E2: 36/72 vs 36/36 for PHASE1-CORE (§6.1) | demonstrated, exploratory; the scenario it is measured on fails M3 |
| M3 scenario validity | an untrusted channel and an attacker-controlled effect (both clauses) | E2 fails the rule for both scenarios; E3 passes it by design (§6.1, §6.2) | demonstrated as a validity finding; no valid defense result from E2 |
| M4 authorship | attack set written independently of detector development, frozen before defenses are run | E3: partially independent set; 0/168 defended episodes blocked vs 36/36 on the original (§6.2) | demonstrated once, with disclosed partial independence |
| M5 reporting unit | per-model results, a noise floor from a replicate | E3: 41/56 vs 8/56 per model; 4/4 discordant noise pairs (§6.2); external replicate (§6.3) | demonstrated, exploratory |
| M6 defense channel | the defense is applied to the channel the attack uses | consistent tool-channel effect only; no wrong-channel arm (§6.3) | proposed, not demonstrated here |

Each check is a hypothesis for defense-measurement validity, not a validated framework. §8 lists the limits on generalization.

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
*External test (E5).* The 186-case sample is 62 attacker instructions in three contexts each, cluster units are the attacker instruction, and the arms are A0, an identical-input replicate of A0 (A0_REP), SPOT_TOOL (delimiters on the tool channel) and a no-injection control (NOINJ, 40 cases). The endpoint is proposal level: the first tool call is the attacker's tool; nothing is executed. The analysis is a cluster bootstrap of paired differences (4000 resamples, seed 7), Wilson intervals, and exact McNemar tests as descriptive statistics. The protocol named Holm across the four open targets for H1 and H2. The 98.75% intervals reported in §6.3 are Bonferroni α/4 intervals (alpha = 0.0125), not Holm intervals.

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

*Defended vs undefended, paired (Fig. 3).* B3: 56/167 undefended executions against 57/167 defended, with b10/b01 = 3/4; the paired difference is +0.006 with a bootstrap interval of −0.024 to +0.036 (`analysis` artifact `docs/research/artifacts/e3_delivery_audit_20261003.json`). CORE: 57/168 against 57/168, with b10/b01 = 4/4; the difference is 0.000 with an interval of −0.036 to +0.036. Neither defense produced a block: CORE blocked 0/168 defended episodes, against 36/36 on the original direct-override scenario.

*Labeling and pairing.* The pairs above include episodes that the harness labeled `INVALID_NOT_DELIVERED`, because the estimand is an executed attacker call for an assigned instance. 14 of the 168 undefended episodes carry that label, and in 10 of them the tool carrying the payload was never called. Restricting to pairs where the carrier tool ran leaves the conclusion unchanged: 157 B3 pairs with b10/b01 = 3/3, and 158 CORE pairs with b10/b01 = 4/3 (Appendix D).

*Noise floor.* CORE with zero blocks presents the same model input as the undefended arm, yet 4 pairs flip in one direction and 4 in the other (4/4). Differences of that size cannot be attributed to a defense.

### 6.3 External test on InjecAgent (E5)
Proposal-level outcome on 186 cases per target, with the NOINJ control on 40 cases. Proposal rate is the first tool call being the attacker's tool; no call was executed.

| target | A0 | A0 replicate | NOINJ | SPOT_TOOL | SPOT_TOOL minus A0, mean | cluster 95% CI (Bonferroni α/4, 98.75% CI) |
|---|---|---|---|---|---|---|
| llama-4-maverick | 23/186 (Wilson 8.4 to 17.9) | 24/186 | 0/40 | 5/186 | -0.097 | [-0.145, -0.048] ([-0.161, -0.038]) |
| qwen3.8-flash | 23/186 (Wilson 8.4 to 17.9) | 22/186 | 0/40 | 4/186 | -0.102 | [-0.156, -0.054] ([-0.172, -0.043]) |

The replicate differs from A0 by 0.005 (95% CI [-0.027, 0.038]) for llama-4-maverick, and by -0.005 (95% CI [-0.059, 0.048]) for qwen3.8-flash. That is the run-to-run noise at this sample size. A tool-channel delimiter lowers proposal-level attacker tool calls by about ten points on both targets, larger than that noise, and the intervals exclude zero at the Bonferroni α/4 level for both. The result is descriptive. The two targets were selected from the calibration of §6.4, and the protocol was not frozen. Only the two-target comparison is reported; the other targets were classified in §6.4 and not retested.

*Scope and disclosures.* (i) Two targets, one benchmark, non-adaptive attacks, proposal endpoint; the result corroborates a measurement effect and does not test M1 or M6. (ii) The B3 and CORE arms left every InjecAgent case unchanged in an offline check, so they were not run live. (iii) qwen3.8-flash's calibration (6/36 scored, §6.4) does not meet the protocol's n ≥ 40 requirement for classification; its selection therefore departs from the floor rule. (iv) Sample size: the protocol draft planned 310 cases (5 contexts × 62 instructions), the protocol's analysis section planned 124 (2 × 62), and the run used 186 (3 × 62). Neither change appears in the protocol's deviation log, and the reason given in the paper is the authors' account. (v) Temperature 0 was requested in the runner's request body (commit `96b33e4eec1f2b32afcbe697a1d3d26add2bbd38`, script not in this tree). The episode records store no temperature, provider route or model version, so these settings cannot be verified from the records. (vi) No provider errors occurred in the registered run.

### 6.4 Calibration: most 2026 targets are below 5% or undetermined
Undefended rates (A0) and the NOINJ control on InjecAgent (n = 40 per target), and the human-written Hard set (n = 68, or 20 for the closed target). Zero events are reported with two-sided 95% Clopper–Pearson upper bounds, 8.8% at n = 40 and 5.3% at n = 68.

| target | InjecAgent A0 | Hard set A0 | InjecAgent NOINJ | classification |
|---|---|---|---|---|
| llama-4-maverick | 5/40 | 1/68 | 0/40 | measurable on InjecAgent; below 5% on the Hard set, floor not demonstrated |
| qwen3.8-flash | 6/36 scored (4 provider errors) | 0/40 scored (28 provider errors) | 0/37 scored (3 provider errors) | undetermined on both sets (InjecAgent n = 36 < 40; Hard set 0/40) |
| glm-4.7 | 1/40 | 1/68 | 0/40 | below 5%, floor not demonstrated, on both sets |
| deepseek-v4.1-flash | 0/40 (upper bound 8.8%) | 0/68 (upper bound 5.3%) | 0/40 | InjecAgent undetermined (0/40); Hard set below 5%, floor not demonstrated |
| gpt-5.6-sol (closed) | 0/40 (upper bound 8.8%) | 0/20 | 0/40 | undetermined on both sets (fewer than 40 scored on the Hard set) |

Two readings follow. First, a defense cannot be shown to reduce an attack that the undefended model does not carry out, so on most of this panel a defense comparison would measure noise. The floor rule decides which targets enter the external test (§6.3), and the qwen3.8-flash calibration does not meet its n ≥ 40 requirement. Second, the Hard set, built for earlier models, has an undefended rate below 5% at the point estimate for the three targets with 68 scored items and is undetermined for the other two. We did not run older models, so we cannot say whether benchmark informativeness decays over time; we report only that most 2026 targets were below 5% or could not be assessed, and that we did not establish a floor for any of them. The choice of targets from these rates is itself a selection step and is disclosed in §6.3.

## 7 Discussion
**What the evidence supports.** The most defensible summary is a measurement claim, not a defense claim. On the same traces the reported verdict depended on the success endpoint (proposal or executed call), on how a payload stopped before the model is labeled, and on whether a scenario is a valid attack. Those are decisions papers rarely report, and each changed a result we could check.

**The E2 stop was not evidence.** The one configuration in our data that stopped an attack completely was the Phase-1 policy on the direct-override scenario. That scenario fails the validity rule (§4.3): the override sits in the user turn. On the scenarios that pass the rule, the same defenses changed nothing beyond the noise floor (§6.2). The gap between the two results is itself a measurement lesson: a valid comparison must fix the scenario rule before the results are seen.

**Why the defenses did not transfer.** The straightforward reading is that a detector's features coincided with the surface forms of the scenarios it was developed beside. We cannot test that reading here. The repository history shows that such coincidences can arise when a detector is iterated while the evaluation set is authored (§4.4). This is a process explanation, not an accusation: the remedy is procedural, to freeze the detector before the scenarios are unsealed and to have authors who have not seen it write or review the scenarios.

**Tool policies and the utility cost.** A static policy that denies side-effecting tools stops every executed attack in E2 and removes most benign tool utility (45/45 to 15/45). The trade-off is between text-level defenses, which leave the model in control and, on our valid families, changed nothing, and tool-boundary policies, which are deterministic but only as good as their allowlists [2406.13352; 2504.11703]. Our static policy is an illustration of scale, not a contribution. An attack that stays inside the allowed action set is indistinguishable from the task, which is a limit of any tool-boundary policy.

**Model-specific susceptibility.** One model executed 41/56 undefended attacks and two others 8/56 each. A defense evaluated only on the susceptible model can look effective for unrelated reasons, and one evaluated on the resistant models cannot show any effect. Pooled rates hide this, so per-model reporting is needed.

**Practical recommendations, based on this study.** (1) Score the executed effect with argument-level predicates and report the proposal rate separately. (2) Treat blocked-before-target as a defense outcome and report the sensitivity to the alternative labeling. (3) Fix the scenario-validity rule before the results and apply it to every scenario. (4) Freeze detectors before scenarios are unsealed; report who wrote the scenarios. (5) Report per model, and include a baseline replicate to bound nondeterminism. (6) Before scoring a defense on a public benchmark, check the undefended rate per model and report models below the floor as undetermined. These recommendations come from one case study; independent validation on other harnesses and defenses is needed before they become practice.

## 8 Limitations

### 8.1 What the results cannot support
**No defense claim.** No evaluated defense is shown to work. On the scenarios that pass the M3 rule, the two detector-style defenses leave executed attacks unchanged within the noise floor (§6.2). The one complete stop in E2 is on a scenario that fails the rule (§4.3). We make no claim that adaptive intervention, the Phase-1 detector, or spotlighting-style wrapping is effective or ineffective in general; the claim is limited to the scenarios, targets and harness described.

**No adaptive attacker.** All attacks are non-adaptive, and a defense-aware attacker was outside the threat model. Prior work reports that detector- and prompt-based defenses can be broken by adaptive attacks even when they look strong on static sets [2503.00061; 2510.09023; 2606.15057]. Our finding that two such defenses do not help against a non-adaptive, partially independent set gives no information about a stronger defense of the same family, or about system-level defenses under adaptive pressure.

**No system-level defense.** We did not implement or run CaMeL-, Progent- or DRIFT-style defenses [2503.18813; 2504.11703]. Our static tool policy is a hand-written illustration. It blocks by construction, and its utility cost (45/45 to 15/45 benign tasks) is a property of denying side-effecting tools, not a measurement of any published system. ARGALLOW was implemented and unit-tested but never run live.

### 8.2 Statistical limitations
**Small, clustered samples.** The E2 runs use 12 instances per attack scenario and two scenarios. The E3 set uses seven families, 8 instances per family and model, and 56 unique instances over three targets. Instances within a family share a template, so the effective number of independent units is the number of families (two in E2, seven in E3), not the number of episodes. The E3 intervals were also computed with the 56 instances as clusters and coincide with the episode-level intervals to three decimals (`scripts/audit_e3_delivery.py`). Seven families are too few for a family-level interval.

**Intervals are not equivalence tests.** No equivalence margin was set. The E3 intervals bound the observed difference; they show no detectable effect, not proof of no effect. Per-cell rates (n = 8) have wide intervals. We report no confirmatory p-values.

**Nondeterminism.** Runs use temperature 0 through a hosted provider, yet two arms with identical model input differed in 4 and 4 discordant pairs (b10/b01 = 4/4). Effects of that size cannot be attributed to a defense. The external test has an undefended replicate for each target, and the replicate differs from A0 by 0.005 and −0.005 (§6.3). A confirmatory design would need repeated baseline runs to estimate the floor per model.

**Exploratory status.** The E2 and E3 runs were analyzed before the proposed amendment that would fix the scoring rules (Amendment 10, status *proposed*, not approved). The measurement checks of §4 were partly derived from these data and then applied to them. They are hypotheses for a confirmatory run, not pre-registered tests. The E2 inclusion rule of §4.2 was adopted after the first analysis; it changed two headline cells and excludes no episode.

### 8.3 Scenario and authorship limitations
**Authorship and independence.** The partially independent attack set was authored by an AI assistant at the first author's request. The same assistant family drafted this manuscript and produced the internal review notes, so no human independent of the project has yet reviewed the scenarios or the text. The assistant had read the repository's Phase-1 detector pattern lists earlier in the same working session while auditing it, so independence from the detector's development is partial. We froze the template file (SHA-256 `8ae353ca…9de8`) before running any defense on it, wrote from public benchmark styles [2406.13352; 2403.02691], and did not modify the templates after the post-freeze offline replay. We cannot exclude subtle influence. Full independence requires an author who has not seen the detector's implementation or patterns.

**Coverage.** Seven attack families using four mock tools (`get_weather`, `retrieve_document`, `send_email`, `create_record`), reserved example domains, and English text. There are no code-execution, file, web or multi-agent scenarios, no multi-turn persistence beyond one delayed second read, and no confidentiality-only leakage without a tool call.

**Original scenarios.** Both E2 attack scenarios fail the M3 rule (§4.3). The E2 scenario set therefore supports the endpoint and labeling illustrations of §4.1 and §4.2, but no valid defense claim.

### 8.4 Target and provider limitations
The E2 and E3 targets are three open-weight models reached through one aggregator, with reasoning disabled where the provider allows it. A fourth model excluded after a smoke test showed truncation and non-delivery on the provider's route; the record of that smoke test exists only in an archive commit that is not reachable from any ref (`dfbea801`) and is not verifiable from this tree. Susceptibility is strongly model-specific (41/56 for one model, 8/56 for two others), so results should not be extrapolated to other models. No frontier or closed model entered a defense comparison. The one closed model of the calibration (gpt-5.6-sol) is undetermined on both sets (§6.4). The 2026 calibration covers five targets only.

### 8.5 Provenance and artifact limits
**Provenance of the E2 and E3 runs.** The multi-turn harness runs of 2026-09-30 have manifests that record commit SHAs for the runner and repository. Those commits are not reachable from any branch or tag of the repository; they can be fetched from the public remote by full SHA, but the archive tag named in `REPRODUCIBILITY.md` does not exist on the remote, and unreachable commits are not guaranteed to remain retrievable. No provider-key usage snapshots were preserved, so reported spend rests on the runner's own cost summaries. No record of the authors' approval of these runs is preserved in the repository.

**Pairing and the delivery label.** The paired E3 comparisons pair episodes on (scenario, instance, target) and require run status `COMPLETE` on both sides, giving 167 B3 pairs and 168 CORE pairs. The harness delivery label is not used for pairing. An episode labeled `INVALID_NOT_DELIVERED` stays in the denominator and counts as an executed attack only if the executor log records one. The estimand is therefore the probability that an assigned attack instance ends in an executed attacker call, not that probability given that the payload reached the model. Of the 168 undefended episodes, 14 carry the label: in 10 the carrier tool was never called, in 3 a provider error ended the episode with an executed call recorded, and in 1 the episode was truncated. Dropping the pairs in which the carrier tool never ran gives the delivered-only pair counts of §6.2. The E2 observed-consequence rule (§4.2) is a different eligibility rule and was not applied to E3.

**Provider errors.** `COMPLETE` does not exclude provider errors. Some `COMPLETE` episodes ended with a provider error and no executed call and are counted as not executed; each is concordant with its undefended pair, and the sensitivity analysis above gives the same qualitative result.

**Excluded evidence.** The paper's evidence base is limited to the runs of 2026-09-30 and 2026-10-01 on non-weak models (`docs/CASE_STUDY_SCOPE.md`). The judge-scored tracks, the held-out application of the rules, and the runs on qwen-2.5-7b, llama-3.1-8b, mistral-small and gemma-4-31b InjecAgent are excluded and are not used as evidence in this paper. Their artifacts remain in the repository, and the repository does not claim that they support any statement here.

**Spend.** E2 and E3 spend was small and is reported from runner summaries only. The calibration and the external test were run under per-run caps; their spend is not reported as a result.

### 8.6 What would change our conclusions
A defense-aware attacker or a system-level baseline could reverse the ordering we observe among defenses. A confirmatory run with scenarios written by an author independent of the detector, with per-model admission and a baseline replicate, could show a text-level defense helps on families we did not cover. A different labeling convention for pre-target blocks changes the E2 headline (§4.2), which is why we require the sensitivity analysis. Conversely, none of the measurement effects in §4 depends on the defense being ineffective: they would apply to any defense evaluated with the same harness.

### 8.7 Hard-set provenance
The human-written part of the Hard set consists of participant submissions to LLMail-Inject. The dataset paper notes that one team generated variants of a template with an LLM [2506.09956], so "human-written" means participant-submitted and selected by tool-call ground truth, not verified to be free of LLM assistance. The Hard set is used only for calibration (§6.4).

## 9 What the paper may and may not claim
| may claim | may not claim |
|---|---|
| On the E2 traces the success endpoint changes the verdict: a static tool policy executes 0/72 attacks and is invisible to proposal-level scoring (65/72 proposed), and it lowers benign utility from 45/45 to 15/45 | that the static policy is a defense, or that the effect generalizes beyond these scenarios |
| Under the stated M3 rule (an untrusted channel and an attacker-controlled effect), E2 contains no valid attack, so the complete stop of PHASE1-CORE on its direct-override scenario is not evidence of a defense effect | that PHASE1-CORE stops attacks |
| On the partially independent E3 set, which passes the M3 rule, neither detector-style defense changes executed attacks beyond the replicate noise (56/167 undefended vs 57/167 with B3; 57/168 vs 57/168 with CORE) | that any defense is ineffective in general, or on other attacks, adaptive or system-level defenses |
| Undefended susceptibility is model-specific (41/56 for one target, 8/56 for two others) | that results transfer to other targets or to frontier or closed models |
| On the two assessable 2026 targets, a tool-channel delimiter lowers proposal-level attacker tool calls by about ten points (23/186 to 5/186 and 4/186) | that delimiters defend against executed attacks, adaptive attackers or long contexts |
| Most of the five 2026 calibration targets are below 5% or undetermined on InjecAgent and on the Hard set (the closed target gpt-5.6-sol is 0/40, undetermined) | that these targets are robust, or that a floor was demonstrated for any of them |
| Five candidate checks (M1 to M5) are demonstrated on these traces, at exploratory strength; M6 is proposed and not demonstrated | that the checks are a validated measurement framework |

## 10 Ethics, dual use, AI assistance and reproducibility
**Ethics and dual use.** All attacks run against mock tools and reserved example domains; no live system, account or person was involved. The attack templates of the partially independent set are directly reusable. They are not in the tree of any branch; the file is retrievable from the public repository by commit SHA (`e5135a6`), and the SHA-256 values in `REPRODUCIBILITY.md` match it, so we do not describe the templates as withheld. The traces, the offline analysis scripts and the number ledger are public. The live multi-turn harness (`src/adapti_guard/evaluation/harness_v2/`), the E2 and E3 run scripts and the registered external-test runner are not in the tree. The work is defensive: it improves how defenses are measured.

**Use of AI assistance.** An AI assistant was used under the first author's direction in the research-support and writing work. It contributed to analysis code, harness extensions, the partially independent attack-scenario templates (§8.3), drafts of this manuscript, and internal review notes. The first author specified the studies. No record of approval of the E2 and E3 runs or of their budgets is preserved (§8.5). Numbers were regenerated from the persisted traces by scripts. The assistant is not an author, and the same assistant family wrote the scenarios, drafted this manuscript and produced the internal reviews, so none of these is an independent human check.

**Number ledger.** `NUMBERS_LEDGER.md` lists the quoted counts, rates and intervals of §5 and §6, the figures' tabulated values, and the external-test and calibration cells, each with its file and key. Two classes of number are not ledgered. The per-family and per-target cells of Appendix D are read from one committed file, `paired_vs_a0_analysis.json`. Design constants (sample sizes, caps, resample counts, seeds, dates, commit and file hashes) are cited to the file that fixes them in the text. A consistency test checks that every ledgered string appears in this manuscript.

**Reproducibility.** The E2 and E3 numbers, the figures, the number ledger and the manuscript regenerate from the committed traces with `scripts/reproduce_negative_result.sh`. The counts, rates and calibration cells of §6.3 and §6.4 are recomputed from the committed external-test and calibration records by `scripts/recompute_external_test.py`, and `tests/test_external_ledger_raw.py` recomputes them again from the raw files without importing that script. The cluster-bootstrap intervals of §6.3 are read from `ANALYSIS.json`, because the script that produced them is not in the tree. The InjecAgent calibration and panel run scripts are restored unchanged (`docs/RESTORED_FROM_96b33e4e.md`). They call a provider and are not run by the reproduction script. Hosted models change, and temperature 0 is not deterministic (measured, §6.2), so traces, model identifiers and dates are released rather than relying on reruns. Live spend is reported as runner summaries in §8.5.

## 11 Conclusion
This paper reports a case study of how valid measurements of runtime defenses are, on one testbed. On the same traces, the success endpoint, the labeling of pre-target blocks and the validity of the attack scenarios each changed or qualified the reported verdict (§6.1). On a partially independent set that passes the scenario rule, two detector-style defenses leave executed attacks unchanged within noise (§6.2), and undefended susceptibility differs by model. Most 2026 targets are below 5% or undetermined on public attack sets, so defense comparisons on them would not be informative (§6.4). The external test on two assessable targets corroborates a tool-channel effect at proposal level (§6.3). The checks are candidate rules: five are demonstrated here at exploratory strength, and the sixth is only proposed. Confirmation requires independent replication on other harnesses, defenses and authors (§8).

## References
Reading status: the axes of Pathade et al. and the author order of Sakib et al. were re-checked on 2026-10-10 against the arXiv pages and the full text of 2609.25173. Several cited works are preprints or workshop papers that are not peer reviewed (Shaw, Pathade et al., Sakib et al., Akinrele and Gowda, Deep et al.).
- [2406.13352] Debenedetti et al. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. [arXiv:2406.13352, 2024]
- [2403.02691] Zhan et al. InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents. [arXiv:2403.02691, 2024; ACL 2024 Findings]
- [2503.18813] Debenedetti et al. Defeating Prompt Injections by Design (CaMeL). [arXiv:2503.18813, 2025]
- [2504.11703] Shi et al. Progent: Securing AI Agents with Privilege Control. [arXiv:2504.11703, 2025]
- [2503.00061] Zhan et al. Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents. [arXiv:2503.00061, 2025; NAACL 2025 Findings]
- [2510.09023] Nasr et al. The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections. [arXiv:2510.09023, 2025]
- [2606.15057] Ma et al. AutoDojo: A Generative Benchmark for Evaluating Prompt Injection Defenses in LLM Agents. [arXiv:2606.15057, 2026]
- [2606.26479] Narisetty et al. Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents. (not peer-reviewed, per the paper) [arXiv:2606.26479, 2026]
- [2609.32691] Shaw. Silent Failures in Agentic Security Evaluation: A Validated Harness for Tool-Call Mediation Under Indirect Prompt Injection (full text). [arXiv:2609.32691, 2026]
- [2502.05174] Zhu et al. MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents (ICML 2025). [arXiv:2502.05174, 2025]
- [2412.16682] Jia et al. The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents. [arXiv:2412.16682, 2024]
- [2312.14197] Yi et al. Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models (BIPIA; KDD 2025). [arXiv:2312.14197, 2023]
- [2506.09956] Abdelnabi et al. LLMail-Inject: A Dataset from a Realistic Adaptive Prompt Injection Challenge. (dataset license: MIT) [arXiv:2506.09956, 2025]
- [2608.28411] Liu et al. LongPIBench: A Long-Context Benchmark for Prompt Injection. [arXiv:2608.28411, 2026; Findings of EMNLP 2026 (to appear)]
- [2605.30454] Sakib et al. The Surface You Test Is Not the Surface That Breaks. (NeurIPS 2026 workshop paper) [arXiv:2605.30454, 2026]
- [2606.10525] Hofer, Debenedetti and Tramèr. Assessing Automated Prompt Injection Attacks in Agentic Environments. [arXiv:2606.10525, 2026]
- [2605.26999] Akinrele and Gowda. Prompt Injection Detection is Regime-Dependent: A Deployment-Aware Evaluation with Interpretable Structural Signals. [arXiv:2605.26999, 2026]
- [2604.23887] Deep et al. Evaluation of Prompt Injection Defenses in Large Language Models (vendor study). [arXiv:2604.23887, 2026]
- [2609.25173] Pathade, Pawar and Patil. Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation. [arXiv:2609.25173, 2026]
- [2603.15714] Dziemian et al. How Vulnerable Are AI Agents to Indirect Prompt Injections? Insights from a Large-Scale Public Competition. [arXiv:2603.15714, 2026]
- [2609.36817] Ying et al. (Tencent Zhuque Lab). pikit: A Composable Toolkit for Indirect Prompt Injection Research and Evaluation. [arXiv:2609.36817, 2026]
- [2604.08499] Geng et al. PIArena: A Platform for Prompt Injection Evaluation. [arXiv:2604.08499, 2026; ACL 2026 (to appear)]
- [2403.14720] Hines et al. Defending Against Indirect Prompt Injection Attacks With Spotlighting. [arXiv:2403.14720, 2024]

## Appendix A Exploratory InjecAgent run, one target (2026-09-30)
This run is exploratory: one target, one seed, no confirmatory claim rests on it. It is reported because it is the only InjecAgent run of 2026-09-30 in the evidence base, and it informed the design of §6.3.

We used cases from InjecAgent (Zhan et al. 2024; external repository, hashes pinned in the run manifest). The 1054 base cases (510 direct-harm, 544 data-stealing) pass mechanical validity checks (the tools exist, the injected text is present in the tool output). Offline, B3 and CORE block or modify none of the tool outputs, so on these cases they receive the same input as the undefended arm. Live, we ran 120 cases (60 per kind; stratified over 17 user tools; seed 20260930) on one target, meta-llama/llama-3.3-70b-instruct, one request per episode at temperature 0. The endpoint is the first tool call the model emits, a proposal-level endpoint: an attacker tool or not, with no judge or detector involved. It does not test M1's proposal-versus-execution contrast.

| target | A0 | A0 replicate | NOINJ | SPOT_TOOL | SPOT_TOOL minus A0 (mean; cluster 95% CI) | A0-only / SPOT-only pairs (exact p, descriptive) |
|---|---|---|---|---|---|---|
| llama-3.3-70b | 48/120 | 50/120 | 0/119 | 54/120 | +0.050 [-0.018, 0.122] | 7/13 (0.26) |

The 1054 base cases are a grid of 62 attacker instructions crossed with 17 user tools, so the 120 sampled episodes (58 distinct instructions) are not independent. The primary interval is therefore a cluster bootstrap over attacker instruction (4000 resamples, seed 7). The exact McNemar p-value treats episodes as independent and is descriptive only. The control (NOINJ) is at zero, so the 48 undefended attacker calls are caused by the injection. The replicate (50/120) and A0 (48/120) differ by two calls out of 120, which is the run-to-run noise at this size. The delimiter on the tool channel did not lower the rate in this run: its interval includes zero and its mean difference is positive. This is one target and one seed, so the run neither supports nor refutes the two-target effect of §6.3. Limits: one model, 120 cases, one seed, a single-step endpoint, and no benign-utility measure (InjecAgent has none).

## Appendix B Reporting checklist for evaluations of runtime defenses against prompt injection
Intended for authors and reviewers. Each item has a pass criterion that can be checked from the paper and its artifacts. Items correspond to the candidate checks M1 to M6 of §4, derived from this case study. The checklist complements Pathade et al.'s general evaluation-design checklist and is intended for defense-specific evaluation design, not as a universal validation framework.

| # | Item | Pass criterion | Check |
|---|---|---|---|
| 1 | Endpoint | success is the executed tool call (argument-level predicate); the proposal rate is reported separately | M1 |
| 2 | Judge in the primary endpoint | if a judge is used, it is compared with the executed outcome and the agreement is reported | M1 |
| 3 | Blocked payloads | a block before the target is counted as a defense outcome; results are shown under both labelings | M2 |
| 4 | Delivery check | the harness verifies that the payload reached the model and reports how many episodes failed delivery, by cause | M2 |
| 5 | Validity control | a control with the injection removed; a model is assessable only if the control is at or near zero | M3 |
| 6 | Scenario validity | every attack scenario has an untrusted channel and an attacker-controlled effect, stated as a rule applied before results are seen | M3 |
| 7 | Authorship | the attack set was written independently of detector or defense development and frozen (hash) before defenses were run; authorship (human, model, mixed) is stated | M4 |
| 8 | Selection | any filter used to select attacks is stated and does not use the targets' results | M4 |
| 9 | Per-model reporting | results are given per model; pooled rates only as a secondary summary | M5 |
| 10 | Floor rule | a stated rule for models whose undefended rate is too low to assess a defense; undetermined targets are labelled as such | M5 |
| 11 | Noise floor | an undefended replicate shows run-to-run discordance per model | M5 |
| 12 | Non-independence | the unit of analysis accounts for repeated instructions (cluster bootstrap or equivalent) | M5 |
| 13 | Defense channel | the defense is applied to the channel through which the attack arrives, with a check that it sees the injected text, and a wrong-channel arm is run | M6 |
| 14 | Utility | benign utility is measured with the same endpoint, with and without the defense | M1 |
| 15 | Adaptive attackers | the paper states whether an adaptive attacker was run; if not, no claim of robustness against one | scope |
| 16 | Errors | provider failures are reported as failures, never scored as safe; spend and caps are reported | reporting |
| 17 | Reproducibility | one command regenerates the numbers and figures from committed traces; pack or template hashes and code commit SHAs are recorded | reporting |
| 18 | Pre-registration | hypotheses, endpoint, sample, analysis and floor rule are registered before the confirmatory run; deviations are logged | reporting |

How to cite: refer to "the M1 to M6 checks" and to "Appendix B of this paper" when stating which items a study satisfies. An item that is not satisfied should be listed as a limitation.

**Self-assessment of this paper.** Satisfied, as §4 to §6 read: items 1, 4, 9, 14 and 16 (E2 and E3 record delivery causes and executed endpoints per model; the external test reports failures as failures). Partly satisfied: item 3 (both labelings are shown for E2, but the scenario they are measured on fails item 6); items 6 and 8 (the M3 rule was adopted before the defense results were used, and E2 fails it); item 7 (the E3 set is frozen by hash, but partially independent, §8.3); item 10 (floor rule applied to the 2026 calibration, with one selection that departs from it, §6.3); item 11 and 12 (noise floor for E3 and the external test; cluster bootstrap for the external test and an instance-clustered check for E3). Satisfied: item 15 (no adaptive attacker was run, and the paper says so). Not satisfied: item 5 (E2 has no injection-free control), item 13 (no wrong-channel arm; M6 is only proposed), and item 18 (no pre-registration; the protocol was drafted locally, not registered).

## Appendix C Artifacts and data availability
Unless a row says otherwise the artifact is in the repository. Items that are not in the tree are marked. Artifacts of excluded evidence (the judge-scored tracks, the held-out application, and the qwen-2.5-7b, llama-3.1-8b, mistral-small and gemma-4-31b InjecAgent runs) remain in the repository but are not evidence for this paper.

| artifact | content | size | origin | hash or pin |
|---|---|---|---|---|
| E2 traces | multi-turn tool episodes with the executor log (`experiments/harness_v2/HARNESS_V2_EXPLORATORY_20260930/episodes.jsonl`), run manifest, cost summary | 468 episodes | project | commit SHAs in the run manifest (not file hashes) |
| E3 traces | undefended screen and defended runs (`HARNESS_V2_INDEPENDENT_{SCREEN,DEFENDED}_20260930/episodes.jsonl`), paired analysis | 168 undefended, 336 defended episodes | project | commit SHAs in the run manifests |
| partially independent scenario set | seven families, partially independent of the detector: authored without running any defense, by an author who had read the detector's pattern lists (§8.3); the template file is not in the tree of any branch and is retrievable only by commit SHA (`e5135a6`) | 7 families | project | SHA-256 of the template file (§4.4; `REPRODUCIBILITY.md`) |
| InjecAgent (external) | attacker instructions crossed with user tools; the 186-case registered sample and the 120-case 2026-09-30 sample | 1,054 base cases | external repository | commit and file hashes in `datasets/external_samples/injecagent_phase2_sample.json` |
| external test records | per-episode records of the registered run (llama-4-maverick, qwen3.8-flash) and the summary `ANALYSIS.json` | 598 episodes per target | project | `experiments/external/injecagent_registered_20261001/MANIFEST.json` |
| calibration records | undefended and NOINJ episodes on five 2026 targets (InjecAgent) and the Hard set (`calibration.json`) | 80 episodes per target on InjecAgent; 180 per target in the Hard-set file | project | `experiments/external/injecagent_panel_calib_20261001/`, `experiments/external/phase2_calibration_20261001/calibration.json` |
| Hard set, human-written | tool-call-verified items from LLMail-Inject, used for calibration only | 68 calibration items | MIT (Hugging Face `microsoft/llmail-inject-challenge`) | `datasets/attackset_hard_v1/FREEZE_RECORD.json`; `MANIFEST.json` restored from `96b33e4e`, SHA-256 matches the record |
| model panel | registry with pinned settings | four open, one closed, two judges | OpenRouter list | `configs/models_panel_external_v2.yaml` |
| code | analysis, figure, ledger and reproduction scripts, and the two external-test checks (`scripts/recompute_external_test.py`, `tests/test_external_ledger_raw.py`). Restored unchanged from commit `96b33e4e` (`docs/RESTORED_FROM_96b33e4e.md`): the InjecAgent calibration and panel run scripts (these call a provider and are not run by the reproduction), the offline check and the live analysis script | | project | git blob SHAs in `docs/RESTORED_FROM_96b33e4e.md` |
| not in the tree | the live multi-turn harness (`src/adapti_guard/evaluation/harness_v2/`), the E2/E3 run scripts, the registered external-test runner (`scripts/run_injecagent_registered.py`, commit `96b33e4e`), the producer of `ANALYSIS.json`, and the harness test; the bootstrap intervals of §6.3 are read from `ANALYSIS.json` | | | `REPRODUCIBILITY.md` |
| reproduction | `scripts/reproduce_negative_result.sh` regenerates the E2 and E3 numbers, the figures, the ledger and the manuscript offline; `scripts/recompute_external_test.py` regenerates the counts, rates and calibration cells of §6.3 and §6.4 from the committed records; the bootstrap intervals are not regenerated | | | `NUMBERS_LEDGER.md` with a consistency test |

Attack texts: items from LLMail-Inject are public under their license. The manifests contain identifiers and hashes; item texts are regenerated from the public dataset. The model-generated items of the Hard set are exploratory and not released here.

## Appendix D E3 detailed results: Per-family and per-model breakdown

Experiment E3 tested seven partially independent attack families on three models with the B3 adaptive stack and the PHASE1-CORE deterministic defense. Both defenses produced zero blocks across all 336 episodes. The tables below provide the breakdown by family and model; in every table, the difference is A0 minus the defended arm, counted over paired episodes (the opposite sign to the `mean_diff` of Fig. 3, which is defended minus A0).

Data source: `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json`. The per-family and per-model cells below are read from this file and are not individually listed in `NUMBERS_LEDGER.md`; the summary counts and paired counts are.

### E3.1 B3 adaptive stack

**Summary statistics:**
- Paired episodes: 167 (of 168 A0 episodes; the one B3 episode with run status `INVALID_PROVIDER_ERROR` recorded an executed attacker call, as did its undefended pair, and is dropped from the pairing)
- A0 (undefended) executed: 56/167
- B3 executed: 57/167
- Blocks by B3: 0
- Paired comparison (n=167): McNemar exact p = 1.0

### E3.2 PHASE1-CORE deterministic defense

**Summary statistics:**
- Total episodes: 168
- A0 (undefended) executed: 57/168
- CORE executed: 57/168
- Blocks by CORE: 0
- Paired comparison (n=168): McNemar exact p = 1.0

#### Per-family and per-model results, B3 and PHASE1-CORE

The B3 comparison uses 167 pairs and the CORE comparison 168 pairs (see the summary statistics above), so the A0 column is given for each pairing; where the two differ (second instruction doc, 7/23 vs 8/24; deepseek-v3.2, 40/55 vs 41/56) the denominators differ by one.

| Attack family | A0 executed (B3 pairing) | B3 executed | Difference (A0 − B3) | A0 executed (CORE pairing) | CORE executed | Difference (A0 − CORE) |
|---|---|---|---|---|---|---|
| authority claim doc | 23/24 | 22/24 | +1 | 23/24 | 23/24 | 0 |
| important instructions doc | 9/24 | 8/24 | +1 | 9/24 | 8/24 | +1 |
| important instructions weather | 8/24 | 8/24 | 0 | 8/24 | 8/24 | 0 |
| second instruction doc | 7/23 | 7/23 | 0 | 8/24 | 9/24 | −1 |
| split address doc | 4/24 | 5/24 | −1 | 4/24 | 3/24 | +1 |
| unrequested write doc | 5/24 | 7/24 | −2 | 5/24 | 6/24 | −1 |
| workflow footer doc | 0/24 | 0/24 | 0 | 0/24 | 0/24 | 0 |

| Model | A0 executed (B3 pairing) | B3 executed | Difference (A0 − B3) | A0 executed (CORE pairing) | CORE executed | Difference (A0 − CORE) |
|---|---|---|---|---|---|---|
| deepseek-v3.2 | 40/55 | 43/55 | −3 | 41/56 | 41/56 | 0 |
| gemma-4-31b-it | 8/56 | 6/56 | +2 | 8/56 | 7/56 | +1 |
| qwen3-30b-a3b | 8/56 | 8/56 | 0 | 8/56 | 9/56 | −1 |

### E3.3 Non-delivered episodes and delivery-restricted pairs

The pairing above uses run status `COMPLETE` on both sides and keeps episodes the harness labeled `INVALID_NOT_DELIVERED` (they count as executed only if the executor log records an executed attacker call). Of the 168 undefended episodes, 14 carry that label: 10 because the tool carrying the payload was never called (9 `retrieve_document`, 1 `get_weather`; all qwen3, 8 of them in the split-address family), 3 because of a provider error with an executed call recorded (deepseek), and 1 truncated episode (deepseek, split-address). Among the `COMPLETE` defended episodes, 18 (B3) and 13 (CORE) carry the label, 8 each for the same never-called carrier tool and the rest provider errors. The table restricts the pairs; it is a sensitivity analysis, not the primary comparison (source: `docs/research/artifacts/e3_delivery_audit_20261003.json`, `scripts/audit_e3_delivery.py`).

| arm | pairs used | pairs | A0 executed | defended executed | b10/b01 |
|---|---|---|---|---|---|
| B3 | published | 167 | 56 | 57 | 3/4 |
| B3 | carrier tool never ran (either side) dropped | 157 | 56 | 56 | 3/3 |
| B3 | any `INVALID_NOT_DELIVERED` (either side) dropped | 144 | 48 | 46 | 3/1 |
| B3 | published plus the `INVALID_PROVIDER_ERROR` episode | 168 | 57 | 58 | 3/4 |
| CORE | published | 168 | 57 | 57 | 4/4 |
| CORE | carrier tool never ran (either side) dropped | 158 | 57 | 56 | 4/3 |
| CORE | any `INVALID_NOT_DELIVERED` (either side) dropped | 149 | 49 | 47 | 4/2 |

No restriction produces a significant difference (exact McNemar p ≥ 0.625 in every row); the sample is small and these are descriptive.

### Interpretation

Neither defense produced a block or a consistent reduction in attack execution across the independent families. The per-family and per-model differences are small and within the run-to-run noise of §6.2 (4/4 discordant pairs at temperature 0 for CORE; 3/4 for B3), so differences of this size cannot be attributed to a defense.
