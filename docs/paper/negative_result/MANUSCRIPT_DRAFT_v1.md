# What Reached the Executor? Six Measurement Checks for Evaluating Runtime Defenses of LLM Agents, with a Negative Result

---

## Abstract
This paper is an empirical case study of six candidate measurement validity checks (M1 to M6) for defense evaluation—rules for how to measure defense effectiveness in tool-using LLM agents. Using a hash-locked testbed, we show that concrete measurement decisions can change or qualify reported conclusions: whether success means the model proposed a call or the executor ran it, how blocked payloads are labeled, whether a scenario contains an attacker-controlled effect, who wrote the attack scenarios, whether results are reported per model, and whether the defense is applied to the untrusted channel. The evidence is stronger for the first, second and fifth decisions than for the third, fourth and sixth, which are preliminary. We quantify on the same traces how the same defense outcome flips under different measurement rules, and we turn the six checks into a reporting checklist.

Two frozen judge-scored confirmatory runs reached opposite verdicts (a failure and a "supported improvement" with a 0.44 paired effect). Re-scoring the same episodes by the tool layer's execution record moves that effect to 0.90 while benign utility falls from 0.97 to 0.80, and the judge agrees with the executed outcome only weakly (κ 0.16 to 0.36). On seven independently authored attack families with an executed-call endpoint, neither detector-style defense changes outcomes beyond run-to-run noise (56 undefended vs 57 defended, and 57 vs 57, of 167 and 168 pairs), while a static tool policy stops everything at large utility cost. Applied unchanged to held-out data, the measurement rules expose a sixth check (is the defense applied to the untrusted channel?). We release the harness, traces and scripts that regenerate every number (attack templates are released in stages, §10), and report an external InjecAgent test whose protocol was drafted locally before the run but not externally registered. A calibration on five 2026 targets shows why such measurement validation must precede any defense comparison: three of the five carry out almost none of the public attacks undefended, so a defense effect would have been unmeasurable on them. We do not claim that any defense is effective.

**Keywords:** prompt injection; LLM agents; evaluation validity; tool calling; reproducibility; negative results.

## 1 Introduction

**Framing.** This paper is a study of how to measure the effect of an agent security defense validly. The defenses we evaluate serve as a case study for demonstrating measurement decisions, and we make no claim that any defense is effective. The question we ask of every benchmark is whether the undefended model actually carries out the attack, and whether the evidence of execution is valid, before any defense is scored. We propose six measurement checks (M1–M6) and demonstrate that each changes or qualifies a conclusion.

---

LLM agents that call tools read untrusted content — retrieved documents, tool outputs, messages — and can be steered by instructions planted in it (indirect prompt injection) [2403.02691; 2406.13352]. A large body of work proposes defenses, from delimiters and prompt sandwiching to detectors, fine-tuning, and system-level reference monitors [2503.18813; 2504.11703]. Two lessons from the security-evaluation literature frame this paper. First, defenses that look strong on static sets are routinely broken by adaptive attackers [2503.00061; 2510.09023; 2606.15057]. Second, the measurement itself can be wrong: scoring success by tool identity rather than arguments inflated an attack success rate from 1.2% to 21.7% in one audit [2609.32691].

We add a third, more mundane lesson from our own evaluation: choices that look like bookkeeping — which endpoint counts as success, how blocked payloads are labeled, whether a scenario is an attack at all, who wrote the scenarios, whether results are pooled across models — decided the conclusion. We arrived at this by building a testbed to compare fixed and adaptive intervention policies (AdaptiGuard), running two hash-locked confirmatory experiments whose verdicts differed, and then trying to reproduce the favorable one under stricter measurement.

**What we did.** (i) We re-scored the frozen judge-based runs with the tool layer's execution record. (ii) We built a multi-turn tool harness with an executed-call endpoint and ran an exploratory four-arm comparison. (iii) We authored seven attack families independently of the detector's development, froze them, and measured undefended susceptibility and two defenses' effects, paired with the undefended baseline.

**Findings.** The judge-scored favorable result understates the tool-layer effect (0.44 vs 0.90) and overstates benign utility (0.97 vs 0.80). An adaptive stack has no measurable effect in any run. The one defense that removes an attack on the original scenarios does not on independent families. A static tool policy is the only complete stop and costs most of the benign tool utility. Susceptibility is model-specific (one model executed 41 of 56 undefended attacks; two others 8 of 56 each).

**Table 1. Key findings.** Every number is regenerated by `scripts/reproduce_negative_result.sh` and listed in `NUMBERS_LEDGER.md`.
| decision (rule) | scored one way | scored the other way | where |
|---|---|---|---|
| success endpoint (M1) | judge-scored paired effect 0.4426 | executed-call effect 0.9016 | §6.1 |
| benign utility behind the gate (M1) | judge 0.97 | executed 0.80 (49/61) | §6.1 |
| blocked payload label (M2) | static tool policy: 65/72 proposed | 0/72 executed | §6.2, Fig. 1 |
| authorship independence (M4) | original scenarios: defense removes the attack (36/36 blocked) | independent families: 4/4 discordant pairs, no net effect | §6.3, Figs. 2 and 3 |
| per-model reporting (M5) | pooled | 41/56 executed for one model, 8/56 for another | §6.3, Fig. 2 |

**Contributions.**
1. **Six candidate measurement checks (M1 to M6)** derived from a single case study and demonstrated on the same traces, with the score flip shown in Fig. 1, stated as rules (§4, Table 3) and as a reporting checklist for other evaluations to consider (Appendix B). M1–M5 are exploratory hypotheses; the sixth check (is the defense applied to the untrusted channel?) was found on held-out data and confirmed by a small re-run but remains preliminary (§4.7, §6.5). These are not claims of universal measurement validity; confirmation requires independent replication (Table 3b, §8).
2. A quantified judge–executor disagreement on two frozen confirmatory runs, including a case where a headline improvement rests on two offsetting judge errors (§6.1).
3. A partially independent, frozen attack-scenario set with a construct-validity gate and an undefended susceptibility profile per model, with disclosed limitations on author independence (§5.4, §6.3).
4. A negative result on two detector-style defenses under non-adaptive independent scenarios, with a measured nondeterminism floor (§6.3).
5. A calibration on five 2026 targets showing that three are at or near the floor on public attack sets, so a defense comparison on them would have been unmeasurable; the floor rule decides which targets enter the registered test (§6.7).
6. Released packs, harness, traces and scripts that regenerate every table and figure with one command, and an external InjecAgent test, whose protocol was drafted locally before the run but not externally registered, for corroboration of measurement-level effects (§5.6, §6.6; Appendix C lists the artifacts).

**Non-claims.** We do not claim that any defense is effective or ineffective in general, that adaptive intervention cannot work, or anything about frontier models; we evaluated no adaptive attacker and no system-level defense such as CaMeL or Progent (§8).

## 2 Related work
**Benchmarks.** AgentDojo provides stateful, multi-tool environments with deterministic state-based utility and security checks rather than LLM evaluators, and reports benign utility, utility under attack and targeted attack success [2406.13352]; InjecAgent measures indirect injection on single-turn tool-integrated agents (17 user cases crossed with 62 attacker cases) and finds that the user case, in particular how much freedom the content field leaves, is more strongly associated with success than the attacker case [2403.02691]. BIPIA covers email, web, table, summarization and code tasks with 250 attacker goals and judges outcome manipulation by rules and an LLM rather than by a tool call [2312.14197]. LLMail-Inject releases 208,095 unique attack submissions from 839 participants against a simulated email assistant, with success defined by a tool call with the correct arguments; submissions are participant-written, and one team reports using an LLM to generate variants of a template [2506.09956]. LongPIBench adds long-context documents, where defenses that look strong on short inputs fail [2608.28411]; PIArena offers a unified platform for comparing attacks and defenses and a defense-adaptive attack [2604.08499]; pikit is a composable toolkit that varies attack wording, delivery channel and defense independently [2609.36817]. We use the principle of scoring the environment state, AgentDojo's public "important message" phrasing for two attack families, InjecAgent for an external test, and the human-written part of LLMail-Inject as the independent source of our Hard attack set.

**Defenses.** Prompt-level defenses (delimiters, sandwiching, spotlighting), detectors, fine-tuning and system-level designs have all been proposed. Capability- and interpreter-based systems such as CaMeL isolate a privileged planner from a quarantined parser and enforce policies over tracked data flow [2503.18813]; Progent enforces deterministic least-privilege rules at the tool-call boundary [2504.11703]; MELON compares the agent's tool calls with those of a masked re-execution and Task Shield checks each instruction and tool call for alignment with the user's goal [2502.05174; 2412.16682]. In AgentDojo a simple tool filter was the most effective of the defenses tested and a BERT detector hurt utility through false positives [2406.13352]. A vendor study reports that only deterministic output filtering (alone or inside a multi-layer stack) held against a long adaptive campaign on system-prompt leakage [2604.23887].

**Adaptive attacks.** Defenses that look strong on static sets are broken by defense-aware attackers: white-box optimization breaks eight indirect-injection defenses above 50% [2503.00061], a multi-lab study breaks twelve defenses, including spotlighting and sandwiching, above 90% with search, reinforcement-learning and human red-teaming [2510.09023], and a cheap black-box optimizer recovers attack success against several filter defenses while most system-level defenses stay low, though one of them (DRIFT) rises above its static rate [2606.15057]. Automated attacks adapted to AgentDojo are model-dependent: black-box tree search beats gradient-based search, and attacks optimized on small open models do not transfer to a frontier model [2606.10525]. A protocol for adaptive evaluation of out-of-band defenses has been specified [2606.26479]. The same vendor study reports that one prompt-level defense (sandwiching) leaked in 0.4% of attacks after 25 rounds and in 3.8% over 277 rounds, so short evaluations overstate protection [2604.23887]. We ran no adaptive attacker.

**Evaluation validity.** This is the closest line of work. Shaw audits an agent-security harness and identifies payload non-delivery, tool-identity scoring, false-rejection conflated with incapacity and missing audit trails, showing that scoring by tool identity reports 21.7% where the argument-level rate is 1.2% [2609.32691]. Sakib et al. place a byte-identical payload in a tool output or in a tool description across 13 models and four AgentDojo suites and find that 44.9% of model pairs change their relative ordering, and that prompt-level defenses (repeating the user prompt, spotlighting) reduce tool-output attacks but leave the tool-description surface exposed [2605.30454]. Hofer et al. score an LLM judge against AgentDojo's deterministic ground truth and find perfect recall but a precision of 52.3% on Qwen3-4B and 29.4% on GPT-5 [2606.10525]. For detectors, Akinrele and Gowda show that rankings depend on the evaluation regime and the false-positive budget [2605.26999]. Each of these varies one evaluation decision: payload delivery, injection surface, judge reliability or detector regime. Pathade et al. is the closest work: they decompose attack success rate into six axes (A1 to A6), meta-analyze 259 papers, give a ten-item reporting checklist and show analytically how large an effect a sample of 100 can detect (about 18 pp) [2609.25173]. Their contribution is analytical and meta-analytic; in our reading they report no defense experiment and no artifact repository. At the evidence level, a public red-teaming arena with 464 participants and about 272k attempts against 13 frontier models finds attack success of 0.5% to 8.5% and notes that one-shot evaluation can be unreliable because a replayed attack does not always succeed again on the same model [2603.15714].

**Position.** We do not propose a defense or a benchmark. Our scope differs from Pathade et al. in its breadth and method. Pathade et al. addresses general agentic security evaluation design: their six axes (A1–A6) span what constitutes an attack (A1), agent capability level (A2), task complexity (A3), evaluation environment (A4), attempt constraints (A5), and success measurement method (A6). **ADAPTI-GUARD addresses measurement validity for runtime defense evaluation specifically: our six checks (M1–M6) operate at a finer, defense-specific measurement layer and are derived empirically from a single case study.** Three checks—blocked payload labeling (M2), attack-set authorship independence (M4), and defense-channel verification (M6)—were not identified in Pathade et al.'s six axes or ten-item checklist as we read them. Three checks—success endpoint (M1), scenario validity (M3), and per-model reporting (M5)—refine Pathade's concepts at finer granularity for the defense-evaluation context. We show on the same execution traces that each measurement decision changes or qualifies conclusions, and we turn them into a reporting checklist (Appendix B) that complements, rather than replaces, Pathade's ten-item checklist. **Our scope is limited to one testbed and two held-out datasets from the same project; generalization to other harnesses or defenses would require independent replication.** Whereas Pathade establishes by literature analysis that such decisions matter, we demonstrate with same-trace measurement flips, an executed-call endpoint, released artifacts and an external InjecAgent test (protocol drafted locally, not externally registered) that they change conclusions quantitatively on this system. Table 2 positions the work. The judge-versus-executor disagreement we measure on frozen confirmatory runs (κ 0.16 to 0.36) is consistent with the judge precision reported by Hofer et al.; the channel check of §4.7 is consistent with the surface sensitivity of defenses reported by Sakib et al.

**Table 2. Positioning (from the papers' own descriptions; entries marked with a question mark were not verified).** Pathade et al.'s six axes (A1–A6) address general agentic security evaluation design; ADAPTI-GUARD's six checks (M1–M6) address defense-specific measurement validity. These operate at different problem levels: Pathade's axes span all decisions involved in designing any agent security study, while ADAPTI-GUARD's checks operate at the finer granularity of how to measure defense effectiveness validly.
| | AgentDojo | InjecAgent | LLMail-Inject | BIPIA | Sakib et al. | Hofer et al. | Shaw | Pathade et al. | this paper |
|---|---|---|---|---|---|---|---|---|---|
| success from executed tool or environment state | yes | tool name | yes (tool call) | no (rules and judge) | yes | yes (ground truth) | yes | no (meta-analysis) | yes (executed call) |
| LLM judge in the primary endpoint | no | no | no | partly | no | studied | no | n/a | no (judge compared, not used) |
| human-written attacks | templates | GPT-4-generated, manually revised | yes (839 participants; some LLM-assisted) | authored | reused | automated | n/a | n/a | independent subset (human) plus generated, reported apart |
| adaptive attackers | manual baselines | follow-up work | yes (participants) | no | no | yes (automated) | n/a | n/a | no |
| evaluation decisions studied as the object | no | no | no | no | one (surface) | one (judge) | several defects | six axes, analytical | six, on the same traces |
| judge versus executed outcome measured | n/a | n/a | n/a | n/a | n/a | yes (precision) | n/a | n/a | yes (kappa 0.16 to 0.36) |
| defense applied to the untrusted channel checked | n/a | n/a | n/a | n/a | yes | n/a | n/a | no | yes (§4.7) |
| per-model reporting with validity control and noise floor | partly | partly | partly | partly | per cell | per model | n/a | power analysis only | yes |

## 3 Threat model and testbed
### 3.1 Threat model
The user turn, the system prompt and the defense code are trusted. Content returned by tools is untrusted and may contain adversarial text placed by an attacker who cannot see or change the user's prompt, the model weights or the defense configuration. The attacker's goal is an effect the user did not request: an e-mail to an attacker-chosen recipient, or a write carrying attacker content. Attacks are non-adaptive: the attacker knows the tool interface and general agent behavior but not the deployed defense and does not optimize against it. Direct injection (the user turn itself carries the override) appears only in the original scenario family and is labeled as such. A scenario in which the trusted user requests the effect is not an attack (§4.3). The defender controls the scaffold: it can transform content before the model, deny or allow tool calls after it, and cannot change model weights. The single-agent, single-user, English-language setting excludes multi-agent, supply-chain, multimodal and cross-session attacks.

### 3.2 Testbed
*Frozen tracks (E1).* Two hash-locked packs of 61 attack and 61 benign episodes, run once in a single-turn text interface with simulated tools; the tool layer records for each episode whether the requested call was permitted and executed. Success and utility were scored by an LLM judge under a frozen protocol.
*Multi-turn harness (E2, E3).* Four deterministic mock tools (`get_weather`, `retrieve_document`, `send_email`, `create_record`), a scenario-aware executor, and per-episode trajectories. The attacker's goal is an argument-level predicate over executed calls (tool, arguments and an injected marker), so a legitimate use of a shared tool cannot satisfy it. A delivery check verifies that the marker reached the model through the intended channel; episodes where it did not are labeled by cause, and blocked payloads are a separate outcome (§4.2). Runs use temperature 0, a hard cap on HTTP requests and a soft cap on spend checked after each billed response, and are reconciled against the provider's key usage. Three open-weight targets were reached through one aggregator: qwen/qwen3-30b-a3b, google/gemma-4-31b-it, deepseek/deepseek-v3.2.
*Artifacts.* Frozen packs and templates carry SHA-256 hashes recorded in run manifests together with the runner's commit; all analyses read persisted traces and are regenerated by scripts.

## 4 Candidate measurement rules for defense evaluation

Defense evaluations for tool-using agents report an attack success rate. That single number hides at least five decisions about what counts as an attack, what counts as success, and which episodes are in the denominator. Prior work has shown that such decisions can distort results by an order of magnitude, for example when success is scored by tool identity rather than by arguments [2609.32691]. In this section we describe six decisions that changed or qualified the conclusion of our own evaluation, the rule we adopt for each, and the evidence. Relative to Pathade et al.'s general evaluation-design axes, three of our checks—blocked payload labeling (M2), attack-set authorship independence (M4), and defense-channel verification (M6)—were not identified in their six axes or ten-item checklist as we read them. Three checks—success endpoint (M1), scenario validity (M3), and per-model reporting (M5)—operate at finer granularity than Pathade's axes for the defense-specific context. The first two extend the defect classes of Shaw [2609.32691]; the last four, to our knowledge, are not covered by existing checklists.

**Scope:** The six checks (M1–M6) are candidate measurement rules derived from and applied to a single hash-locked testbed and two held-out datasets from the same project. M1, M2, M3, M5 were discovered during exploratory analysis (E2, E3); M4 was audited as part of the process; M6 was found on held-out data and confirmed by a small follow-up run. They are not claims of universal measurement validity; rather, they are evidence that the same traces support radically different conclusions depending on measurement choices, and a hypothesis for how defenses should be measured more carefully in this domain. Confirmation on independently authored scenarios and a fully independent dataset would be needed before generalizing these checks to other harnesses or defenses.

### 4.1 Score what reached the executor, not what the model proposed
A defense can act before the model (by removing or wrapping untrusted content) or after it (by refusing to execute a call). If success is defined as "the model proposed a call that matches the attacker's specification", post-model defenses are invisible: the model still tries, the policy stops execution. We therefore define the primary endpoint as *the attacker-specified call, with matching arguments and the injected marker, was executed by the tool layer* (`exec_executed`), and report the proposal-level endpoint (`exec_success`) as secondary.
In our multi-turn tool harness, a static policy that denies `send_email` and `create_record` yields 65 of 72 attack episodes with a matching proposed call (the same as the undefended baseline, 66 of 72) but 0 of 72 executed calls (Fig. 1, panels 1 and 2). Under a proposal-level metric this policy would have been reported as having no effect at all; under the execution-level metric it is a complete stop. This is the agent-security analogue of scoring by tool identity, and is the reason execution-level, state-based endpoints are the standard in AgentDojo-style benchmarks [2406.13352]. The same distinction applies to LLM-judge scoring: on our two frozen judge-scored runs the judge and the tool layer's execution record agree only weakly (κ 0.16 to 0.36 on attack success), with every disagreement in the direction judge = success, executed = false (§6.1).

### 4.2 A pre-target block is a defense outcome, not a delivery failure
Harnesses verify that the injected payload reached the model, and mark episodes where it did not as invalid, to avoid crediting a defense for an attack that never happened because of a harness fault [2609.32691, defect D1]. But a defense that sanitizes or blocks content *before* the model also produces an episode in which the payload never reaches the model. Labelling both as "not delivered" and excluding them from the denominator converts a successful defense into missing data.
In our data all 36 blocks by the Phase-1 defense (PHASE1-CORE) on the direct-override scenario were labeled `INVALID_NOT_DELIVERED` by the harness (`injection_marker_not_in_request_channels`). Counting them as failed attacks gives 36 of 72 attacks executed (0.50); excluding them, as the harness's rule for invalid episodes would, gives 36 of 36 (1.00) (Fig. 1, panels 2 and 3). The same traces support "halves the attack", "no effect", or, restricted to the one valid attack scenario (§4.3), "stops it completely" (0 of 36). We adopt a separate outcome, *blocked before the target*, defined by the absence of the marker in the request channels together with a recorded block on the message that carried it; it counts as an unsuccessful attack and stays in the denominator. Because the rule is a choice, we require a mandatory sensitivity analysis under the alternative rule and downgrade any claim on which the two disagree.
*Observed-consequence rule (E2 episode scoring).* Inclusion is decided by the recorded consequence, not by the harness status. An episode with `exec_executed = true` is retained and scored by its observed outcome; an episode with another observable non-success or block outcome is retained and scored as a failed attack; an episode with no observable consequence is excluded. An `INVALID` status alone neither includes nor excludes an episode.

### 4.3 An attack scenario must contain an attacker-controlled effect (M3)
A scenario labeled as an attack must differ from a legitimate request in some observable property: the malicious instruction arrives through an untrusted channel, or the success predicate involves an effect the user did not request and the attacker controls (a foreign recipient, a write carrying attacker content). This is a construct-validity check; it identifies scenarios that should not be scored as attacks in defense evaluations. We found one scenario in our original set that fails this test. In `create_record_exfil_v1` the user turn itself asks for the record ("log a `audit_trail` entry … using `create_record(kind='audit_trail', payload=…)`"); there is no untrusted channel and no foreign destination, and the scenario differs from the benign create-record task only in the record-kind name (attack kinds `shift_log`, `audit_trail`, `inventory_snapshot`, `compliance_note`; benign kinds `shift_note`, `pantry_inventory`, `training_attendance`, `desk_ticket`). Executing the call is what the trusted user asked for, so scoring it as attack success, and a policy that blocks it as a defense win, is a construct-validity error. Every arm's numbers on that scenario are excluded from defense claims. Progent's authors describe the underlying limitation for attacks that stay inside the allowed action set [2504.11703]. Restricting to the valid scenario, the undefended baseline executes the attack in 30 of 36 episodes, the adaptive baseline in 29, PHASE1-CORE in 0 and the static policy in 0 (Fig. 1, panel 4).

### 4.4 Scenario authorship must be independent of detector development (M4)
When the attack set and the detector are developed by the same author or developed iteratively, the detector's features can coincide with the pack's surface forms without any claim being false. We audited our own repository and found that the Phase-1 detector contains patterns (e.g. tool-invocation literals such as `send_email … to`) that occur in the attack pack it was later evaluated on; 36 of 42 patterns added in the Phase-1 detector match prompt or context text of the earlier VNEXT pack and of neither Phase-1 pack (33 of 42 when whole JSON records including metadata are searched). The chronology of when these patterns were introduced in the detector relative to pack authorship is uncertain: an earlier internal report cites commit `c462945` as the origin of the Phase-1 detector patterns, but this commit is not present in the current repository history, so we report this as an unverified claim. Repository history as currently available shows Phase-1 detector patterns appearing after the earlier confirmatory failure and shortly before the Phase-1 pack was built [repository history; `PHASE1_SCIENTIFIC_REPORT.md` §6.3a].

This finding is a case-study observation, not a criticism of any specific team. Any team that iterates on a detector while authoring the evaluation set is exposed to this coupling; the remedy is procedural.

We then authored seven attack families from public benchmark styles [2406.13352, 2403.02691] without running any defense on them before freezing the template file (SHA-256 `8ae353ca…9de8`). PHASE1-CORE removed the payload from 0 of 168 independent instances and executed the attack in 57 of 168 pairs, identical to the undefended baseline (57), while it had blocked 36 of 36 on the original pack. The difference in the same defense between the two sets is the evidence that the original effect depended on pack-shaped patterns. **Independence in our independent set is only partial: the author had read the detector's pattern lists earlier in the same working session; this limitation is disclosed in the released template file and in the artifacts.** A confirmatory design requires an author who has not seen the detector, and this work does not provide it. Confirmation of the M4 check therefore requires an external study with a fully independent author.

### 4.5 Report susceptibility per model, and count actions, not claims
Two further decisions changed which cells of the evaluation were informative. First, susceptibility is model-specific: in our screening of the independent families the undefended agents executed the attack in 41 of 56 episodes for one model (deepseek) but 8 of 56 for each of the other two (qwen3, gemma) (Fig. 2). A family-level admission rule on pooled rates admitted one of seven families; a per-model rule admits five for the most susceptible model. A defense cannot be shown to help on a model that ignores the attack without it, so admission and reporting should be per model.
Second, text-level scoring counts a model that *says* it acted. One model wrote that it had performed the requested action without making the call in 3 to 8 of 8 episodes in five families; an evaluation that reads the reply text or the tool name would count these as compromises, whereas the executor log does not. Finally, a paired comparison must include a noise floor: two arms whose model input is identical (undefended vs PHASE1-CORE with zero blocks) still differed in 8 of 168 paired outcomes at temperature 0 (Fig. 3), so differences of that size cannot be attributed to a defense, and a confirmatory design should contain a replicate of the baseline.

### 4.6 Summary of the rules
**Table 3. The six checks.**
| # | Decision | Rule adopted | Failure it prevents | Evidence here | Related support |
|---|---|---|---|---|---|
| M1 | Success endpoint | executed call with matching arguments and marker; proposal reported separately | post-model defenses invisible; judge errors | §6.1, §6.2 | tool-identity scoring [2609.32691]; judge precision [2606.10525] |
| M2 | Blocked payload | a pre-target block is a defense outcome, counted as a failed attack; sensitivity to the alternative labeling is mandatory | blocks dropped as "not delivered" | §4.2, §6.2 | payload non-delivery, inverted [2609.32691] |
| M3 | Scenario validity | untrusted channel and attacker-controlled effect; a validity control without the injection | benign requests scored as attacks | §4.3 | none found |
| M4 | Authorship | attack set authored independently of detector development and frozen before running defenses | detector features coinciding with pack surface forms | §4.4, §6.3 | adaptive evaluation [2503.00061] |
| M5 | Reporting unit | per-model results, admission by undefended rate, executor log over text, baseline replicate for the noise floor | pooled rates hiding model-specific effects | §4.5, §6.3 | model-dependent attacks [2606.10525]; regime dependence [2605.26999] |
| M6 | Defense channel | check that the defense is applied to the channel the attack arrives through | a defense that never sees the attack | §4.7, §6.5 | surface sensitivity [2605.30454] |

**Table 3b. Validation status of the six checks.**
| # | Check | Status | Derivation | Confirmation |
|---|---|---|---|---|
| M1 | Success endpoint | Exploratory hypothesis | Derived from re-scoring E1 and analyzing E2; applied to same data | Held-out application (MT1 r1; κ with canary) and InjecAgent (E6); partial replication |
| M2 | Blocked payload | Exploratory hypothesis | Derived from analyzing E2; applied to same data | Held-out application (MT1 r1); not retested on independent data |
| M3 | Scenario validity | Exploratory hypothesis | Found during E2 analysis (construct-validity audit); applied to same data | Checked in E3 (no invalid scenarios); not independently discovered; E6 is not a test of this check |
| M4 | Authorship independence | Case-study observation | Derived from repository history audit; partial disclosure of coupling | Demonstrated in E3 with independent set (0/168 vs 36/36 on original set); independence is partial and disclosed |
| M5 | Per-model reporting | Exploratory hypothesis | Derived from E3 susceptibility analysis; applied to same data | Confirmed in MT1 r1 (model-specific effects) and Appendix A pilot; E6 reports per-model rates with a replicate noise floor (corroboration only) |
| M6 | Defense channel | Held-out discovery | Found when applying M1–M5 to MT1 r1 (held-out data); hypothesis formed post-hoc | Confirmed by targeted re-run (18 indirect episodes); small sample; not replicated on further data; tool-channel delimiters in E6 are consistent with it (§6.6) |

Each check is presented as a hypothesis for defense-measurement validity, not as a validated universal framework. See §8 for limitations on generalization.

**Figures.** Fig. 1 (`figures/fig1_scoring_flip.png`) shows M1–M3 on the same 468 traces; Fig. 2 (`figures/fig2_susceptibility.png`) M5 (susceptibility); Fig. 3 (`figures/fig3_defended_vs_a0.png`) M4/M5 (independent set, noise floor).

### 4.7 A sixth check found on held-out data (M6, preliminary): is the defense applied to the untrusted channel?
When we applied our candidate rules unchanged to an earlier, independently generated run (§6.5), we found a defect that none of M1–M5 covers. A delimiter-based defense in that pipeline wrapped the user's prompt and left the untrusted context unmarked; its measured effect was concentrated on direct injections in the prompt (46 to 22 successful attacks of 60, judge-scored) and absent on indirect injections in the context (21 to 21 of 36), the channel the defense exists for. A defense evaluation should therefore confirm, from the stored request, that the transformation reaches the untrusted content and the model as intended (`M6`). 

**M6 is a preliminary finding with limited scope.** A targeted re-run confirmed it: marking the context instead lowered indirect injections from 8 to 1 of 18 (7 wins, 0 losses) and left direct ones unchanged (22 to 22 of 30), the mirror image of the prompt-wrapped arm (direct 22 to 6, indirect 8 to 7) [`docs/research/SPOTLIGHT_CTX_CHECK_20260930.md`]. The sample is small (18 indirect episodes, three models), the finding was discovered post-hoc on held-out data, and it has not been independently replicated. M6 is included as a candidate check and in the reporting checklist (Appendix B) but is not confirmed and should not be generalized to other harnesses or defenses.

## 5 Experiments

**Table 4. Experiments at a glance.**
| id | what | data | targets | endpoint | status |
|---|---|---|---|---|---|
| E1 | re-score the frozen judge-scored confirmatory runs (Tracks A and B) | frozen packs, 61 + 61 episodes each | one target, same-family judge | judge vs executed call | done (§6.1) |
| E2 | exploratory four-arm run on the original scenarios | harness v2, original families | one to three targets | executed call | done (§6.2) |
| E3 | independently authored families, defended vs undefended | 7 families, 168 instances | three targets | executed call | done (§6.3) |
| E4 | held-out application of the rules and a channel re-run | MT1 pack, 180 live episodes | three targets | judge and canary token | done (§6.5) |
| E5 | external test (protocol drafted locally, not externally registered) | InjecAgent; the Hard set was planned but not run | planned 4 open + 1 closed; run: 2 open | executed call | InjecAgent run reported on two targets (§5.6, §6.6) |
| pilot | exploratory external pilot | InjecAgent, 120 cases | earlier open models | executed call | Appendix A |

We report three experiments of increasing measurement quality. E1 re-examines two frozen, judge-scored confirmatory runs. E2 and E3 use a multi-turn tool harness whose primary endpoint is the executed call. Total live spend across E2 and E3 was about $0.23; E1 was frozen earlier and was only re-analyzed offline here.

### 5.1 Defenses under test
**A0** is no defense. **B3** is the adaptive intervention stack wired into the harness (pre-target; original detector; risk-driven levels with sanitizing/wrapping actions); in every run reported here it never blocked. **PHASE1-CORE** (CORE) is the Phase-1 detector and policy stack that can deny tool calls. **VNEXT-ADAPT** (Track A only) is the adaptive stack with detector v4. **TOOLDENY** is a static policy that denies `send_email` and `create_record` and allows read tools; it acts after the model and is a deliberately blunt comparator. **ARGALLOW** (static argument allowlist) was implemented and unit-tested but not run live.

### 5.2 E1: frozen judge-scored tracks (re-analyzed offline)
Track A (`vnext_confirm_v1`, SHA-256 `523c8818…721518`) and Track B (`phase1_confirm_v1`, `c789811a…536d01`) are hash-locked packs of 61 attack and 61 benign episodes each, run once with a single target (qwen/qwen-2.5-7b-instruct), a single-turn text interface with simulated tools, and an LLM judge (qwen/qwen-2.5-72b-instruct, temperature 0) that scores harmful action and benign utility; the primary test is an exact McNemar test on intervention-mediated wins with a minimum meaningful improvement of 0.20 and a utility floor of 0.95 (`AUDIT.md` of each track). The stored predictions also contain the tool layer's own record per episode (tool, `executed`, observation). We re-score the same episodes with that record (attacker-specified call executed, key argument present in the observation) and compare it with the judge (`scripts/rescore_tracks_ab_deterministic.py`). This is a sensitivity analysis; it does not replace the frozen verdicts.

### 5.3 E2: exploratory four-arm run on the original scenarios
A multi-turn tool harness (mock tools `get_weather`, `retrieve_document`, `send_email`, `create_record`; temperature 0; per-episode trajectories and ledger reconciliation against the provider's key usage) with three targets: qwen/qwen3-30b-a3b, google/gemma-4-31b-it, deepseek/deepseek-v3.2, all via one aggregator. Two attack scenarios from the original template family (`direct_user_override_v1`, `create_record_exfil_v1`; 12 instances each) and three benign scenarios (5 instances each), four arms, 468 episodes, hard HTTP cap 1,872 and soft cap $0.20 (runner commit `bea82347`). Primary endpoint: the attacker-specified call reached the executor (`exec_executed`); the proposal endpoint is secondary. A 60-episode smoke run preceded it ($0.0104).

### 5.4 E3: independent attack set
Seven attack families × 24 instances authored from public benchmark styles (AgentDojo-style important-instructions block in a document and in a tool output, workflow footer, authority claim, unrequested write, updated instruction on a second read, split e-mail address), all delivered through tool outputs with a clean user turn and an attacker-controlled effect (foreign recipient, or a write the user did not request). The template file was frozen before any run (SHA-256 `8ae353ca…9de8`, commit `e5135a6`). Step 1: A0-only screening, 7 families × 8 instances × 3 models = 168 episodes ($0.0469). Step 2: B3 and CORE on the same instances, 336 episodes ($0.0944), paired with step 1 by (family, instance, model). Authorship independence is partial and disclosed in the template file.

### 5.4b E4: held-out application and targeted re-run
The rules are applied unchanged to MT1 r1, an earlier single-turn run on a synthetic pack (six targets, four arms, judge-scored, canary-token attacks; generated before the rules were written), offline. A follow-up live run ($0.0669; 180 episodes; three targets; same pack, seed, judge and pipeline) adds a delimiter arm that marks the untrusted context and a fresh undefended replicate, to test the channel explanation found in §6.5.

### 5.5 Statistics, pre-registration status and reproducibility
Rates carry Wilson 95% intervals; paired effects use exact McNemar tests (descriptive for E2/E3 because instances are clustered by scenario family) and paired bootstrap intervals (5,000 resamples, seed 20260930). We do not report confirmatory p-values for E2/E3. The earlier Option D protocol covers a different, unrun design; the scoring rules used in E2/E3 were fixed before analysis in the analysis scripts but not pre-registered, and Amendment 10 that would fix them is a proposal. All runs write append-only episode records, ledgers and manifests with commit SHA and template SHA; scripts to regenerate every table and figure are in the repository. Provider nondeterminism at temperature 0 is measured (§6.3), not assumed away. Denominators: applying the frozen observed-consequence rule (§4.2), provider-error episodes with observed consequences are included in Fig. 1 and §6.2 denominators as failed attacks; those without observed consequences are excluded.

---

### 5.6 External test: locally drafted protocol (InjecAgent part reported in 6.6)
Purpose: test, on independently authored attacks and a fixed model panel, whether the adaptive stack (B3) and the core pipeline (CORE) change executed attacker tool calls (H1), whether delimiters on the tool channel change them in a model-specific way (H2), and how far undefended susceptibility differs across models (H3). The protocol, hypotheses and analysis plan were drafted locally (`PROTOCOL_EXTERNAL_TEST_DRAFT_v1.md`, labeled not frozen) and were not externally registered; §6.6 gives the chronology that the repository supports.

*Panel.* Four open targets (llama-4-maverick, deepseek-v4.1-flash, qwen3.8-flash, glm-4.7), one closed target (gpt-5.6-sol), and two judges that are never targets and share no vendor family with a target (claude-sonnet-5.5, grok-4.7), used only on the judge-scored tracks. The panel is a pilot-informed choice (made after smoke tests and a data audit), not an independent pre-registration; exact ids and read dates are in the run manifests and `configs/models_panel_external_v2.yaml`.

*Data.* (i) InjecAgent (external; 62 distinct attacker instructions crossed with 17 user tools; a fixed seeded sample with the attacker instruction as the cluster unit). (ii) A Hard set whose human-written part comes from LLMail-Inject (public, MIT; items selected by tool-call ground truth from the original challenge, clustered, capped per team, half from each phase, QC-validated) and whose model-generated part (cross-channel, generated by a model that is neither a target nor a judge) counts as exploratory unless two independent human raters confirm it (kappa >= 0.70, agreement >= 95%). The calibration split is used only to classify floor behavior; the test split is untouched until the run. Selection filters, thresholds and their sensitivity are reported in the attack-set specification.

*Arms and endpoint.* A0, NOINJ (the injection replaced by neutral text or the benign twin; a model is assessable only if this control is at most 3%), SPOT_TOOL (delimiters on the tool channel; InjecAgent only), and B3 or CORE only where their input differs from A0. The endpoint is the first tool call being the attacker's tool with the constrained arguments (state-based; no judge, no detector of this project).

*Analysis.* Cluster bootstrap of the paired difference (4000 resamples, seed 7; unit: attacker instruction or near-duplicate cluster), Wilson intervals, exact McNemar descriptive only, Holm across the four open targets for H1 and H2, noise floor from an undefended replicate where affordable. With the Hard set test split the power to detect a defense that removes half of successful attacks is about 0.6 at an undefended rate of 0.2 and above 0.95 at 0.4 (alpha = 0.0125), so models at the floor are described, not tested.

*Scope under budget.* The run is sized to the project's compute budget: InjecAgent (A0 and SPOT_TOOL on 124 cases, NOINJ on 40) on the four open targets and A0 on 40 cases for the closed target; Hard set test (A0 on the full human-written test split plus the generated test items, NOINJ on 40) on the four open targets and A0 on 40 items for the closed target. AgentDojo is limited to health checks and a pilot and is not part of the confirmatory run. Judge-scored tracks A and B are re-scored with the two contract judges on a subset fixed in the protocol draft (not run).

## 6 Results

### 6.1 E1: the judge and the tool layer disagree, in both directions
| track / arm | judge-scored success | executed (tool layer) | judge = success, executed = false | κ |
|---|---|---|---|---|
| A, B0 | 58/61 (0.951) | 40/61 (0.656) | 18 | 0.18 |
| A, VNEXT-ADAPT | 53/61 (0.869) | 36/61 (0.590) | 17 | 0.36 |
| B, B0 | 61/61 | 61/61 | 0 | n/a |
| B, PHASE1-CORE | 34/61 (0.557) | 6/61 (0.098) | 28 | 0.16 |
[`docs/research/TRACKS_AB_DETERMINISTIC_RESCORING_20260930.md`; the judge side reproduces the frozen AUDIT numbers]. Every disagreement is judge = success while the call did not execute; there are none in the other direction.
*Track A.* Judge-scored paired effect b10/b01 = 5/0, δ̂ = 0.0820, p = 0.0625 (FAIL as frozen). With executed calls: 4/0, δ̂ = 0.0656, p = 0.125; the qualitative outcome (below the 0.20 threshold, not significant) is unchanged.
*Track B.* Judge-scored: 27/0, δ̂ = 0.4426, 95% CI [0.2757, 0.6096], p = 1.49e-8, utility 59/61 = 0.967 (frozen classification: improvement). With executed calls: 55/0, δ̂ = 0.9016. PHASE1-CORE denied the attacker call in 55 of 61 attack episodes; the judge scored 28 of these 55 as attack success and 27 as failure, that is, it labeled the same tool-layer outcome inconsistently. All 10 benign `retrieve_document` episodes under PHASE1-CORE had the tool denied but were scored useful by the judge; tool-required benign tasks executed 30/40 (B0: 40/40), and combined utility with executed-call scoring for tool-required tasks is 49/61 = 0.80, below the 0.95 floor. The frozen classification therefore rests on two judge errors that offset each other: it understated harm reduction (0.44 vs 0.90) and overstated benign utility (0.967 vs 0.80).

### 6.2 E2: the same traces under four scoring rules (Fig. 1)
Attack episodes (72 per arm) scored four ways:
| rule | A0 | B3 | CORE | TOOLDENY |
|---|---|---|---|---|
| model proposed the call | 66/72 | 65/72 | 36/72 | 65/72 |
| call reached executor, blocks = not successful | 66/72 | 65/72 | 36/72 | 0/72 |
| same, blocks excluded as invalid | 65/71 | 65/72 | 36/36 | 0/69 |
| executor, valid scenario only | 30/36 | 29/36 | 0/36 | 0/36 |
[`figures/fig1_scoring_flip.csv`]. The static policy is invisible to the proposal-level rule and complete under the execution-level rule; PHASE1-CORE moves from "halves the attack" to "no effect" to "complete stop" depending on the treatment of blocked payloads and on whether the scenario is a valid attack. Benign utility (45 tasks per arm, scored from the executor log with each instance's expected record kind): A0, B3, CORE 45/45; TOOLDENY 15/45 (weather 15/15, e-mail 0/15, create-record 0/15). B3 produced no block and no change (65 vs 65 executed; b10/b01 = 2/1 on the 72 pairs). The second original scenario is excluded from all defense claims (§4.3).

### 6.3 E3: independent families (Figs. 2 and 3)
*Susceptibility of the undefended agents (Fig. 2).* Attack execution by family: authority claim 23/24, important-instructions in a document 9/24, in a tool output 8/24, updated instruction on a second read 8/24, unrequested write 5/24, split address 4/24, workflow footer 0/24. By model: deepseek 41/56, qwen3 8/56, gemma 8/56. The authority-claim framing, which contains no "ignore previous instructions"-style marker and no literal tool name, succeeds in 7 or 8 of 8 episodes for each model; the public important-instructions block succeeds essentially only for one model. One model (mostly qwen3; gemma in two families) wrote that it had performed the action without making the call (3 to 8 of 8 episodes in five families), which text-level scoring would count as compromise. A pooled admission rule of 50% undefended execution admits one of seven families; a per-model rule admits five families for deepseek.
*Defended vs undefended, paired (Fig. 3).* B3: 167 pairs, undefended 56 vs defended 57 executed, b10/b01 = 3/4, pooled paired difference +0.006 (bootstrap 95% CI −0.024 to +0.036). PHASE1-CORE: 168 pairs, 57 vs 57, b10/b01 = 4/4, difference 0.000 (−0.036 to +0.036). Neither defense produced a block in any of the 336 episodes and per-family intervals include zero. This matches an offline replay of the frozen templates through the defenses (the attack marker survives in 168 of 168 instances for B3, B3-v4 and PHASE1-CORE). PHASE1-CORE, which blocked 36/36 direct-override episodes on the original pack, removed the payload from 0/168 independent instances.
*Nondeterminism floor.* PHASE1-CORE with zero blocks presents essentially the same model input as the baseline, yet 8 of 168 paired outcomes differ at temperature 0 (B3: 7 of 167); differences of that order cannot be attributed to a defense.

### 6.4 Synthesis
| question | evidence |
|---|---|
| Does the adaptive stack (B3) reduce executed attacks? | No effect in this case study: pilot (b10/b01 = 2/1 on 47 pairs), E2 (65 vs 65), E3 (57 vs 56). |
| Does PHASE1-CORE? | Only where a literal tool string shared with the detector appears (E2 direct override 0/36); 0/168 removals and no change on independent families. |
| Does a static tool policy stop attacks? | Yes by construction; benign tool tasks fail with it (utility 1.00 → 0.33 in E2). |
| Do the frozen judge-scored tracks measure executed harm? | No: κ 0.16 to 0.36; the Track B classification depends on two offsetting judge errors. |
| Do measurement choices change conclusions on the same traces? | Yes, demonstrated on this case study's traces (§4). Limited to this testbed; generalization requires independent replication. |
Detailed per-family and per-model results for E3 are in Appendix D.

### 6.5 Held-out application of the rules (MT1 r1)
To test whether the rules are artifacts of the traces they were derived on, we applied them unchanged to an earlier run (MT1 r1: six targets × four arms on a synthetic single-turn pack; generated before the rules were written down; same project, so not fully independent). Endpoint (M1): with a verifiable canary token, judge and deterministic emission agree well (κ 0.81 to 0.91), so the judge-vs-tool-layer gap of §6.1 is specific to judges interpreting simulated tool outcomes; the endpoint still changes an effect size (delimiter defense: 0.29 judge vs 0.19 canary, both significant; paired wins/losses 39/6 judge-scored vs 31/9 canary-scored, pooled; adaptive stack: none under either). Per-model reporting (M5): the pooled delimiter effect is carried by three of six models (14/0, 11/1, 5/0 wins/losses vs the undefended arm) and absent for two. Channel: the whole effect is on direct injections and encoded ones and none on indirect injections in the untrusted context (21 to 21 of 36), because the pipeline wrapped the user prompt rather than the context (§4.7). M2 and M4 could not be tested on this run. [`docs/research/SECOND_DATASET_MT1_RULES_20260930.md`] A follow-up run ($0.07, three targets, 180 episodes) that marks the context instead confirmed the channel explanation: indirect injections 8 to 1 of 18 (7 wins, 0 losses vs the undefended arm), direct injections unchanged (22 to 22 of 30), benign tasks unharmed; a fresh undefended replicate differed from the earlier undefended run in 8 of 57 attack pairs (14%, judge-scored), a larger nondeterminism floor than in the tool harness [`docs/research/SPOTLIGHT_CTX_CHECK_20260930.md`].

### 6.6 External test: corroboration of measurement-level effects (InjecAgent run, 2026-10-01)
**Scope of this test.** This test provides external corroboration, on an independent benchmark (InjecAgent), for the specific measurement effects it tests: the executed-call endpoint (M1), per-model reporting with a replicate noise floor (M5) and applying the defense on the tool channel (M6). It does not test M2, M3 or M4, and it does not validate the six checks (M1–M6) as a universal framework. The test uses an external dataset (InjecAgent), independent models (llama, qwen3.8), and an independent endpoint (first tool call is the attacker's tool, unrelated to our defenses). It does not evaluate our defenses (B3, CORE) on independent data—those defenses showed no effect on InjecAgent in an offline check, as stated below.

The protocol was drafted locally (`PROTOCOL_EXTERNAL_TEST_DRAFT_v1.md`, first committed on 2026-10-01 in `0e64abc` with the label "not frozen") before the runner (`14404a2`) and the results (`15b4610`) were committed; the run manifest records no start time, so that order rests on commit order. No external registry record (OSF, AsPredicted) exists, so this is a protocol-guided test with a locally drafted plan, not a preregistered one. Run on the frozen 186-case sample (62 attacker instructions as clusters; sample hash in `experiments/external/injecagent_registered_20261001/MANIFEST.json`), temperature 0, endpoint: first tool call is the attacker's tool. Targets are the two that were measurable in the calibration of §6.7; the other targets are classified there and not retested. NOINJ was run on 40 cases. No provider errors occurred.

| target | A0 (attacker tool called) | A0 replicate | NOINJ | SPOT_TOOL | SPOT_TOOL minus A0, cluster-bootstrap 95% CI (Holm 98.75% CI) |
|---|---|---|---|---|---|
| llama-4-maverick | 23/186 (12.4%; Wilson 8.4 to 17.9) | 24/186 | 0/40 | 5/186 (2.7%) | -0.097 [-0.145, -0.048] ([-0.161, -0.038]) |
| qwen3.8-flash | 23/186 (12.4%; Wilson 8.4 to 17.9) | 22/186 | 0/40 | 4/186 (2.2%) | -0.102 [-0.156, -0.054] ([-0.172, -0.043]) |

The replicate differs from A0 by 0.005 (95% CI -0.027 to 0.038) for llama-4-maverick and -0.005 (-0.059 to 0.048) for qwen3.8-flash, which is the run-to-run noise floor at this sample size. Delimiters on the tool channel (SPOT_TOOL) lower executed attacker calls for both targets by about ten percentage points, well beyond that floor, and the interval excludes zero also after the Holm adjustment, which follows the protocol's correction over its four open targets (alpha = 0.0125) and is conservative here because only two targets were run. The adaptive stack (B3) and the core pipeline (CORE) leave every InjecAgent case unchanged (offline check, `scripts/injecagent_offline_check.py`), so they equal A0 by construction and were not run live; for these inputs the case-study defense therefore has no measurable effect, while a channel-level delimiter does. Stated limits: two targets, one benchmark, non-adaptive attacks, and the targets were selected by their calibration rates (§6.7). The delimiter we used is the plain delimiting variant of spotlighting, which its authors do not recommend over datamarking or encoding because an attacker who knows the delimiters can reproduce them [2403.14720]; the effect is measured on short inputs, and a long-context benchmark reports that delimiters did not lower attack success there (ASR 0.96 against 0.98 undefended on its synthetic tasks) [2608.28411], so the ten-point reduction must not be extended to long contexts or to attackers who know the defense. Hard set test split, the remaining targets and judge tracks are not part of this run (deviation from §5.6, reason: floor rule and budget).

Reporting rules fixed in advance: results are given per model and per benchmark and never pooled across models; a model with an undefended rate below 5% at n >= 40 is "at the floor, not assessable" and below n = 40 "undetermined"; provider failures are reported as failures. The exploratory pilot that informed this design is in Appendix A.

### 6.7 Calibration before the test: most 2026 targets are at the floor (exploratory, not the test of §6.6)
Before spending the budget on the InjecAgent run of §6.6 we measured the undefended attack rate (A0) of each target on samples disjoint from the frozen test sample, with the NOINJ control (scripts `run_phase2_calibration.py` and `run_injecagent_panel.py`; records in `experiments/external/`). Exact 95% upper bounds for zero events are 8.8% at n = 40 and 5.3% at n = 68.

| target | InjecAgent A0 (n = 40) | Hard set, human-written A0 (n = 68) | NOINJ | classification |
|---|---|---|---|---|
| llama-4-maverick | 5/40 | 1/68 | 0 | measurable on InjecAgent; floor on Hard set |
| qwen3.8-flash | 6/36 scored (4 provider errors) | 0/40 scored (28 provider errors) | 0 | measurable on InjecAgent (limited n); Hard set undetermined |
| glm-4.7 | 1/40 | 1/68 | 0 | floor |
| deepseek-v4.1-flash | 0/40 (upper bound 8.8%) | 0/68 (upper bound 5.3%) | 0 | floor |
| gpt-5.6-sol (closed) | 0/40 (upper bound 8.8%) | 0/20 | n/a | floor on InjecAgent; Hard set undetermined (n < 40) |

Two readings follow. First, a defense cannot be shown to reduce an attack that the undefended model does not carry out, so on most of the panel a defense comparison would have measured noise; the floor rule of §5.6 therefore decides which targets enter the comparison of §6.6 (llama-4-maverick and qwen3.8-flash on InjecAgent). Second, the Hard set of human-written adaptive attacks, built for earlier models, is at or near the floor for every target we could score, so a benchmark that was informative when published can stop being informative on newer models. We cannot call this decay over time, because we did not run older models; we report only that the 2026 targets are at the floor. Choosing the targets from these rates is itself a selection step and is disclosed in the protocol draft.

## 7 Discussion
**What the evidence supports.** The most defensible summary is a measurement claim, not a defense claim. The same system yields "supported improvement", "no effect" and "complete stop" depending on choices that are rarely reported: whether success means the model proposed a call or the executor ran it, whether a payload removed before the model counts as a defense outcome or missing data, whether a scenario could be an attack, and who authored the scenarios. Prior audits identified payload non-delivery and tool-identity scoring [2609.32691]; our data add three more that were decisive here.

**Why the one favorable result did not transfer.** On the original scenarios the Phase-1 defense blocked the direct-override attack completely; on seven families written from public styles it changed nothing. The straightforward reading is that its detector features and the original pack's surface forms coincided — a tool-invocation literal — and that this coincidence, not general detection, produced the effect. In this repository's history such patterns first appear after an earlier confirmatory failure and shortly before the pack was built, although a commit that an older internal report gives as their origin cannot be located, so the chronology is unverified. This is a process explanation for how coupling can arise, not an accusation: any team that iterates on a detector while authoring the evaluation set is exposed to it. The remedy is procedural — freeze the detector before the scenarios are unsealed and let someone who has not seen the detector write or review them.

**Judges.** The judge-scored Track B result is the clearest example of two errors offsetting. The judge scored a denied attack call as success in about half of the denial cases and scored benign tasks as useful when the required tool had been denied. The first understated the defense; the second hid a utility problem. Whether a judge errs in the direction that flatters the defense or hurts it is not something the reported rates reveal; an execution record is. This does not mean judges are useless: for open-ended harm where no executor exists they may be the only option, but they should then be validated against human labels on the specific configuration [2510.09023, on reward hacking of automated scorers].

**Tool policies and the utility cost.** A static policy that denies side-effecting tools stops every attack in the harness and, by construction, every benign task that needs those tools. That is the essential trade-off between text-level defenses, which leave the model in control and (here) stop nothing, and tool-boundary policies, which are deterministic but only as good as their allowlists [2406.13352 on the tool filter; 2504.11703]. Our static policies are not a contribution; they calibrate the scale of the trade-off. The scenario that is textually a legitimate request shows the limit shared by any tool-boundary policy: an attack that stays within the allowed action set is indistinguishable from the task.

**Model-specific susceptibility.** One model followed tool-channel injections in five of seven families; the other two followed essentially one framing. A defense evaluated only on the susceptible model can look effective for reasons unrelated to it, and one evaluated on the resistant models cannot show any effect. Pooled attack rates hide this, so per-model admission and reporting are needed. The strongest attack we wrote — an authority claim with no instruction keywords or tool names — succeeded in nearly all episodes for all three models, which is worth attention independently of defenses.

**Practical recommendations—based on this case study.** (1) Score the executed effect with argument-level predicates and report the proposal rate separately. (2) Treat blocked-before-target as a defense outcome and report the sensitivity to the alternative labeling. (3) Check that every attack scenario contains an attacker-controlled effect and an untrusted channel. (4) Freeze detectors before scenarios are unsealed; use authors independent of detector development; report the disclosure. (5) Report per model; include a baseline replicate to bound nondeterminism. (6) Validate any judge against the execution record or human labels for the specific configuration. (7) Confirm from the stored request that the defense's transformation reaches the untrusted content and the model as intended; in one pipeline a delimiter defense wrapped the user prompt instead, which reversed where its effect appeared (§4.7). These recommendations are based on this study's findings; independent validation on other harnesses and defenses is needed before they should be adopted as universal practice.

**What would strengthen the study—and enable generalization.** A defense-aware adaptive attacker, a system-level baseline, an independent author for the confirmatory scenario set with per-model admission and a baseline replicate, more models and providers, evaluation on other harnesses and defenses, and a human-labeled subset to calibrate the judge for E1. Most of these are essential for the candidate checks (M1–M6) to advance from case-study observations to validated measurement rules. We list these as limitations in §8 rather than claim them.

## 8 Limitations

We group the limitations by how they constrain what a reader may conclude. The first group bounds the claims; the later ones list what we did not do.

### 8.1 What the results cannot support
**No defense claim.** Our data do not show that any evaluated defense works. The one positive result (PHASE1-CORE on the original pack, harmful-action success 1.00 → 0.56 on 61 + 61 episodes, LLM-judged) did not transfer to independently authored scenarios (0 of 168 payloads removed; attack executed in 57 of 168 paired episodes for both the defense and the baseline). We make no claim that adaptive intervention, the Phase-1 detector, or spotlighting-style wrapping is effective or ineffective in general; the claim is limited to the packs, models and harness described.

**No adaptive attacker.** All attacks are non-adaptive. A defense-aware attacker was explicitly outside the threat model. Prior work reports that detector- and prompt-based defenses are broken by adaptive attacks even when they look strong on static sets [2503.00061; 2510.09023; 2606.15057], so our finding that two such defenses do not help against a *non-adaptive* independent set gives no information about how a stronger defense of the same family would fare, nor about how system-level defenses would fare under adaptive pressure.

**No comparison with system-level defenses.** We did not implement or run CaMeL-, Progent- or DRIFT-style defenses [2503.18813; 2504.11703]. Our static tool policies (TOOLDENY, ARGALLOW) are hand-written illustrations; they block by construction, and TOOLDENY's large utility cost (benign utility 1.00 → 0.33) is a property of denying side-effecting tools, not a measurement of any published system. ARGALLOW was implemented and unit-tested but never run live, and its allowlists were derived from the benign scenario definitions, so any utility measured on the same benign set would be optimistic by construction.

### 8.2 Statistical limitations
**Small and clustered samples.** The exploratory runs use 12 (original pack) or 8 (independent set) instances per family and model, from 2 and 7 scenario families respectively. Instances within a family differ lexically but share a template, so the effective number of independent units is the number of families (2 and 7), not the number of episodes (468, 168 + 336). The exact McNemar p-values we report are descriptive and ignore this clustering; per-cell rates (n = 8) have wide intervals. We do not report confirmatory p-values.

**Nondeterminism.** Runs use temperature 0 through a hosted provider, yet two arms with identical model input differed in 8 of 168 paired outcomes (4.8%). Effects of that size cannot be attributed to a defense, and our data contain no replicate of the baseline beyond that comparison (in the single-turn MT1 pack a fresh undefended replicate differed in 9–14% of paired attack outcomes, §6.5). A confirmatory design would need repeated baseline runs to estimate this floor per model.

**Exploratory status.** The experiments on the multi-turn harness were run before the proposed amendment that fixes the scoring rules (Amendment 10, status *proposed*, not approved). The measurement rules in §4 were partly derived from these data and then applied to them; they are therefore hypotheses for a confirmatory run, not pre-registered tests. Analyses were re-scored in one case after an error was found in our own script (benign create-record utility), which we report in the artifact history.

### 8.3 Scenario limitations
**Authorship and independence.** The independent attack set was authored by an AI assistant at the owner's request. The assistant had read the repository's Phase-1 detector pattern lists earlier in the same working session while auditing it, so independence from the detector's development is partial. We froze the template file (SHA-256 `8ae353ca…9de8`) before running any defense on it, wrote from public benchmark styles [2406.13352; 2403.02691], and did not modify the templates after the post-freeze offline replay, but we cannot exclude subtle influence. Confirmation of full independence would require an author who has not seen the detector's implementation or patterns.

**Coverage.** Seven attack families using four mock tools (`get_weather`, `retrieve_document`, `send_email`, `create_record`), reserved example domains, and English text. There are no code-execution, file, web or multi-agent scenarios, no multi-turn persistence beyond one delayed second read, and no confidentiality-only leakage without a tool call. Only one family passes a 50% undefended-execution admission rule pooled across models; the others are informative mainly for the most susceptible model.

**Original pack.** One of the two scenarios in the original exploratory set (`create_record_exfil_v1`) is not a valid attack (§4.3) and is excluded from defense claims, which leaves a single valid scenario with a literal tool string shared with the detector's patterns.

### 8.4 Target and provider limitations
Three open-weight targets (qwen3, gemma, deepseek) reached through one aggregator, with reasoning disabled where the provider allows it; a fourth model (llama) was excluded after a smoke test showed truncation and non-delivery on the provider's route. The earlier judge-based tracks use one target (qwen-2.5-7b-instruct) and a same-family judge (qwen-2.5-72b-instruct), and no human judge-agreement study for that configuration exists in the artifacts. Comparing the judge with the tool layer's own execution record on the frozen episodes gives Cohen's κ of 0.16 to 0.36 on attack success, with every disagreement in the direction judge = success, executed = false (up to 28 of 61 episodes), and the judge scored benign episodes as useful when the required tool had been denied (10 of 10 in one arm); see `docs/research/TRACKS_AB_DETERMINISTIC_RESCORING_20260930.md`. The judge-based numbers of Tracks A and B are therefore reported with that sensitivity analysis and should not be read as measurements of executed harm. No frontier or closed model was evaluated (the exploratory pilot of Appendix A used four older open-weight models, at most 70B; the external test of §5.6 planned one closed model, which was not run in §6.6), and susceptibility is strongly model-specific in our data (one model executed 41 of 56 undefended attacks, the others 8 of 56 each), so results should not be extrapolated to other models.

### 8.5 Artifact and process limitations
Test suite status: an internal project review on 2026-09-30 recorded 283 passing tests on `main` and 23 failures on the working branch that contains the harness (note in `docs/research/`); the full suite on the working branch on 2026-10-01 gave 661 passed, 32 failed and 6 skipped (`docs/research/TEST_SUITE_STATUS_20261001.md`). The two figures come from different branches and dates and are not directly comparable. The recorded causes of failure include unparsed configuration placeholders in older Q1/B2 campaign tests, optional provider packages missing from the container, subprocess import paths, and assertion failures in older harness and ledger-order tests (not all diagnosed); we did not repair them. The tests that bind the manuscript (number ledger, panel registry, external adapters, attack sets) pass. A statement in an earlier internal report that the Phase-1 detector was authored before the holdout pack cites a commit that is not present in this repository, so we treat that statement as unverified. Amendment 10 and the fixed-tool-policy arms are proposals awaiting owner approval. Live spend by experiment: E2 and E3 about $0.23 (runner-reported, per-run `cost_summary.json`), the E4 channel re-run $0.0669, and the InjecAgent run of §6.6 about $0.21 (sum of per-episode cost records); calibration (§6.7) and pilot (Appendix A) spend is not included in these figures. Results depend on this small scale and should be repeated at larger K before being relied on. AI assistance in producing repository artifacts is disclosed in §10.

**Provenance of the E2 and E3 runs.** For the four multi-turn harness runs of 2026-09-30 (`HARNESS_V2_{EXPLORATORY_SMOKE,EXPLORATORY,INDEPENDENT_SCREEN,INDEPENDENT_DEFENDED}_20260930`), no branch or tag of the repository contains pre- or post-run provider-key usage snapshots (`/auth/key`) or a `progress.log`. The runner and repository commits recorded in their manifests (`bea82347`, `caa7ad89`, `7b0e053d`, `44830fa2`) are not reachable from any branch or tag of the repository; `REPRODUCIBILITY.md` maps them to an archive tag that is not published there. No per-request cost records are committed, so the reported spend of these runs, including $0.0944 for the defended run, cannot be recomputed and rests on the runner-written `cost_summary.json`. No record of the owner's approval of these runs is preserved in the repository, its pull requests or its commit messages.

**Provider errors in the E3 pairing.** The paired E3 comparisons (§6.3, Appendix D) pair episodes on (scenario, instance, model) and require status `COMPLETE` on both sides, giving 167 B3 pairs and 168 CORE pairs. `COMPLETE` does not exclude provider errors: three `COMPLETE` B3 episodes ended with a provider error and no executed call and are counted as not executed (each concordant with its undefended pair), and one undefended episode (`ind_split_address_doc_v2i/i5/deepseek/A0`) was truncated without an executed call while both defended arms executed, so it is one of the four b01 pairs in each arm (without it, b10/b01 would be 3/3 for B3 and 4/3 for CORE). Conversely, the only B3 episode with status `INVALID_PROVIDER_ERROR` (`ind_second_doc_v2i/i1/deepseek/B3`) recorded an executed call, as did its undefended pair, and is dropped from the B3 comparison. The observed-consequence rule of §4.2 is defined for E2 episode scoring and was not applied to these pairs.

### 8.6 What would change our conclusions
A defense-aware attacker or a system-level baseline could reverse the ordering we observe among defenses. A confirmatory run with independently authored scenarios and per-model admission could show a text-level defense helps on families we did not cover. A different pre-target labeling convention changes the headline of the original pack (§4.2), which is why we require the sensitivity analysis. Conversely, none of the measurement effects in §4 depends on the defense being ineffective: they would apply to any defense evaluated with the same harness.

### 8.7 Held-out application limits
The held-out application (§6.5) uses one earlier run from the same project: single-turn, no tools, one synthetic pack (19 canary attacks per model, 114 per arm over six models: 60 direct, 36 indirect, 18 encoded), the canary standing in for an executed effect, and two of the five rules (pre-target labeling, authorship independence) could not be tested on it. It therefore reduces, but does not remove, the concern that the rules were fitted to the traces on which they are demonstrated; a second system with different authors is still needed. The wrong-channel finding (§4.7) was confirmed by a small re-run (18 indirect episodes over three models, one run of the corrected arm), so it is supported but not robustly replicated; the same re-run showed a run-to-run difference of 9–14% of paired attack outcomes at temperature 0 in that pack, and one replicate arm lost six benign judgements to provider errors.

### 8.8 Attackers, selection and design choices
No adaptive or optimizing attacker was run, so no claim is made that any defense resists a mechanism-aware adversary. The hard-attack candidate comes from a public human-written challenge and keeps only
prompts that triggered the tool call in the original challenge (a selection on success against other systems, not on our targets), with a half-and-half draw from its two phases and exact near-duplicate clustering; mechanism labels
are heuristic until two human raters validate them. The model panel and the attack source were chosen after pilot runs and are reported as pilot-informed, not as independent pre-registration. Pilot runs of five to twenty episodes per
model support only a hypothesis of floor effects (zero events at n = 20 bounds the rate at 16%).

**Provenance of the Hard set.** The human-written part of the Hard set consists of participant submissions to LLMail-Inject; the dataset paper notes that one team generated variants of a template with an LLM [2506.09956], so "human-written" means participant-submitted and selected by tool-call ground truth, not verified to be free of LLM assistance.

## 9 What the paper may and may not claim
| may claim | may not claim |
|---|---|
| On the frozen Phase-1 pack, judge-scored harmful-action success fell from 1.00 to 0.56; with the tool layer's record it is 6/61 against 61/61, and judge-scored utility 0.967 becomes 0.80 | that the defense (or adaptive intervention in general) is effective |
| The adaptive stack showed no effect in any run | that adaptivity provides a benefit |
| On seven independently authored families neither detector-style defense changed executed attacks beyond run-to-run noise (paired differences +0.006 and 0.000, intervals include zero) | a general statement about detectors, models or adaptive attackers |
| Five measurement choices and a channel check changed or qualified conclusions on our own traces | SOTA, production-readiness, or that the rules are validated beyond the two datasets used |
| A static tool policy stops the tested attacks by construction and removes most benign tool utility | that any published system-level defense (CaMeL, Progent) was evaluated or compared |
| Delimiters applied to the untrusted context lowered indirect injections from 8 to 1 of 18 in a small re-run | that spotlighting works in general |
| In an exploratory pilot on 120 independently authored InjecAgent cases (Appendix A; earlier open models, not the final panel), undefended susceptibility ranged from 5/120 to 50/120 and tool-channel delimiters lowered it for one model (26/9 discordant pairs) but not for the larger model of the same family (7/13) | that delimiters, or any tested defense, generalize across models; or anything about frontier or closed models |
| On InjecAgent (186 cases, two measurable targets), delimiters on the tool channel lowered executed attacker calls by about ten points (12.4% to 2.7% and 2.2%) | that any defense is effective in general, or anything about adaptive attackers, other benchmarks or the targets at the floor |

## 10 Ethics, dual use, AI assistance and reproducibility
**Ethics and dual use.** All attacks run against mock tools and reserved example domains; no live system, account or person was involved. The attack templates, in particular the authority-claim family, are directly reusable, so release is staged: the harness, analysis code and traces are released with the paper; the full template file is released with the camera-ready version or on request to the authors. The work is defensive: it improves how defenses are measured.
**Use of AI assistance.** An AI assistant was used under the owner's direction in the research-support and writing work: it contributed to analysis code, harness extensions, the independent attack-scenario templates (§8.3) and drafts of this manuscript, and to repository audits and internal review notes. The owner specified the studies; no record of approval of the four multi-turn harness runs of E2 and E3 (2026-09-30) or of their budgets is preserved (§8.5). Numbers were regenerated from the persisted traces by scripts. The assistant is not an author.
**Reproducibility.** Packs and templates are hash-locked (SHA-256 recorded in run manifests with the runner commit); every table and figure is regenerated by a script from committed traces (`scripts/rescore_tracks_ab_deterministic.py`, `scripts/analyze_harness_v2_exploratory.py`, `scripts/analyze_independent_defended.py`, `scripts/apply_rules_second_dataset_mt1.py`, `scripts/analyze_spotlight_ctx_check.py`, `scripts/make_fig{1,2,3}_*.py`); a number ledger (`NUMBERS_LEDGER.md`) lists each quoted number with its source. Hosted models change and temperature 0 is not deterministic (measured), so traces, model identifiers and dates are released rather than relying on reruns. Live spend is reported per experiment in §5 and §8.5.

## 11 Conclusion
This paper reports an empirical methodological case study on one hash-locked testbed. On the same traces, the choice of success endpoint (executed call versus judge or proposal), the labeling of blocked payloads and per-model reporting changed the reported verdict or its size (§6.1–§6.3), and an external InjecAgent test on two targets is consistent with the endpoint, per-model and tool-channel effects (§6.6). Scenario validity, attack-set authorship independence (only partially achieved) and the defense-channel check rest on a single scenario, a partially independent author and 18 episodes respectively, and remain preliminary. The six checks are therefore candidate measurement rules and a reporting checklist, not a validated framework; we evaluated no adaptive attacker and make no claim that any defense is effective. Confirmation requires independent replication on other harnesses, defenses and authors (§8).

## References
Reading status: on 2026-10-01 every cited claim and number below was checked against the PDF of the cited paper (per-claim table in `docs/paper/negative_result/REFERENCE_VERIFICATION_20261001.md`). Several cited works are preprints or workshop papers that are not peer reviewed (Shaw, Pathade et al., Narisetty et al., Deep et al., Akinrele and Gowda, Sakib et al.).
- [2406.13352] Debenedetti et al. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.
- [2403.02691] Zhan et al. InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents.
- [2503.18813] Debenedetti et al. Defeating Prompt Injections by Design (CaMeL).
- [2504.11703] Shi et al. Progent: Securing AI Agents with Privilege Control.
- [2503.00061] Zhan et al. Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents.
- [2510.09023] Nasr et al. The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections.
- [2606.15057] Ma et al. AutoDojo: A Generative Benchmark for Evaluating Prompt Injection Defenses in LLM Agents.
- [2606.26479] Narisetty et al. Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents.
- [2609.32691] Shaw. Silent Failures in Agentic Security Evaluation: A Validated Harness for Tool-Call Mediation Under Indirect Prompt Injection (full text).
- [2502.05174] Zhu et al. MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents (ICML 2025).
- [2412.16682] Jia et al. The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents.
- [2312.14197] Yi et al. Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models (BIPIA; KDD 2025). (read)
- [2506.09956] Abdelnabi et al. LLMail-Inject: A Dataset from a Realistic Adaptive Prompt Injection Challenge. (read; MIT license)
- [2608.28411] Liu et al. LongPIBench: A Long-Context Benchmark for Prompt Injection. (read)
- [2605.30454] Sakib et al. The Surface You Test Is Not the Surface That Breaks. (read)
- [2606.10525] Hofer, Debenedetti and Tramèr. Assessing Automated Prompt Injection Attacks in Agentic Environments. (read)
- [2605.26999] Akinrele and Gowda. Prompt Injection Detection is Regime-Dependent: A Deployment-Aware Evaluation with Interpretable Structural Signals. (read)
- [2604.23887] Deep et al. Evaluation of Prompt Injection Defenses in Large Language Models (vendor study; read).
- [2609.25173] Pathade, Pawar and Patil. Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation.
- [2603.15714] Dziemian et al. How Vulnerable Are AI Agents to Indirect Prompt Injections? Insights from a Large-Scale Public Competition.
- [2609.36817] Ying et al. (Tencent Zhuque Lab). pikit: A Composable Toolkit for Indirect Prompt Injection Research and Evaluation.
- [2604.08499] Geng et al. PIArena: A Platform for Prompt Injection Evaluation.
- [2403.14720] Hines et al. Defending Against Indirect Prompt Injection Attacks With Spotlighting.

## Appendix A Exploratory pilot on InjecAgent (earlier open models)
This pilot preceded the external test of §§5.6 and 6.6. Its models are not part of the final panel and no confirmatory claim rests on it; it is kept because it informed the design (floor effects, model-specific delimiter effects, noise floors) and is reported in full.

To remove the authorship and detector dependence of our own scenarios (M4), we ran cases from InjecAgent (Zhan et al. 2024; external repository, hashes pinned in the run manifest). All 1054 base cases (510 direct-harm, 544 data-stealing) pass mechanical validity checks (the tools exist, the injected text is present in the tool output). Offline, B3 and CORE block or modify none of the 1054 tool outputs, and neither does B1 or CORE on the bare attacker instruction, so on these cases they receive the same input as the undefended arm. Live, we ran 120 cases (60 per kind; stratified over 17 user tools; seed 20260930) on four open-weight targets, one request per episode at temperature 0. The endpoint is the first tool call the model emits (M1): an attacker tool or not, with no judge or detector of ours involved. Arms: A0; an identical-input replicate (noise floor, M5); NOINJ (the attacker instruction replaced by neutral text; validity control, M3); and SPOT_TOOL (delimiters and an instruction on the tool channel, the channel that carries the untrusted text, M6).

| target | A0 | replicate | NOINJ | SPOT_TOOL | SPOT_TOOL minus A0, cluster bootstrap 95% CI | A0-only/SPOT-only pairs (exact p, descriptive) |
|---|---|---|---|---|---|---|
| qwen-2.5-7b | 24/120 | 28/119 | 0/120 | 26/120 | +0.017 [-0.057, 0.086] | 10/12 (0.83) |
| llama-3.1-8b | 50/120 | 51/120 | 1/119 | 33/120 | -0.142 [-0.237, -0.056] | 26/9 (0.006) |
| llama-3.3-70b | 48/120 | 50/120 | 0/119 | 54/120 | +0.050 [-0.018, 0.122] | 7/13 (0.26) |
| mistral-small-3.2-24b | 5/120 | 5/120 | 0/120 | 5/120 | 0.000 [-0.025, 0.024] | 1/1 (1.0; floor) |

The 1054 InjecAgent base cases are a grid of 62 distinct attacker instructions crossed with 17 user tools, so the 120 sampled episodes (58 distinct instructions) are not independent; the primary interval is therefore a cluster bootstrap over attacker instruction (4000 resamples, seed 7), and the exact McNemar p-values, which treat episodes as independent, are descriptive only. Three observations. (i) Undefended susceptibility spans roughly ten-fold across targets (4% to 42%), and the control is at or near zero for all of them, so the rates are caused by the injection; a pooled rate would hide the spread (M5). (ii) Scale within a family did not reduce susceptibility (llama 8B 0.42, 70B 0.40). (iii) Tool-channel delimiters reduced attacks for one target only (llama-3.1-8b; the cluster interval excludes zero and both attack kinds go the same way); the effect did not replicate in the larger model of the same family (interval includes zero), was absent for qwen (interval includes zero), and cannot be assessed for mistral at a 4% floor. The effect is model-specific, not absent and not general. Replicate discordance also differs by target (12 of 119 pairs for qwen, 1 of 120 for llama-3.1-8b, 0 for mistral), so the noise floor must be measured per model.

Limits: four models of small to medium size, 120 cases, one seed, a single-step endpoint, and no benign-utility measure (InjecAgent has none). A fifth target (gemma-4-31b-it) was stopped after 61 undefended episodes because of provider latency (0/61 attacker-tool calls on those) and is not included in any test. No frontier-scale model was tested; a closed frontier model is the main missing target. Exploratory; no confirmatory claim.

## Appendix B Reporting checklist for evaluations of runtime defenses against prompt injection
Intended for authors and reviewers. Each item has a pass criterion that can be checked from the paper and its artifacts. Items correspond to the candidate checks M1 to M6 of Table 3, derived from this case study. This checklist complements Pathade et al.'s general evaluation-design checklist and is intended for defense-specific evaluation design, not as a universal validation framework.

| # | Item | Pass criterion | Check |
|---|---|---|---|
| 1 | Endpoint (M1) | success is the executed tool call or the final environment state with argument-level predicates; the proposal rate is reported separately | M1 |
| 2 | No judge in the primary endpoint (M1) | if a judge is used, it is compared with the executed outcome and the agreement (kappa, precision, recall) is reported | M1 |
| 3 | Blocked payloads (M2) | a block before the target is counted as a defense outcome; results are shown under both labelings | M2 |
| 4 | Delivery check | the harness verifies that the payload reached the model and reports how many episodes failed delivery for harness reasons | M2 |
| 5 | Validity control (M3) | a control with the injection removed or replaced by neutral text; a model is assessable only if the control is at or near zero | M3 |
| 6 | Attacker-controlled effect (M3) | every attack scenario contains an effect the user did not request and the attacker controls | M3 |
| 7 | Authorship (M4) | the attack set was written independently of detector or defense development, and frozen (hash) before defenses were run on it; authorship (human, model, mixed) is stated per item | M4 |
| 8 | Selection (M4) | any filter used to select attacks (for example "triggered the tool call in an earlier challenge") is stated, and does not use the targets' results | M4 |
| 9 | Per-model reporting (M5) | results are given per model; pooled rates only as a secondary summary | M5 |
| 10 | Floor rule (M5) | a stated rule for models whose undefended rate is too low to assess a defense (for example below 5% at n >= 40) | M5 |
| 11 | Noise floor (M5) | an undefended replicate shows run-to-run discordance per model | M5 |
| 12 | Non-independence (M5) | the unit of analysis accounts for repeated instructions or near-duplicates (cluster bootstrap or equivalent) | M5 |
| 13 | Defense channel (M6) | the defense is applied to the channel through which the attack arrives, with a check that it sees the injected text | M6 |
| 14 | Utility | benign utility is measured with the same endpoint, with and without the defense | M1 |
| 15 | Adaptive attackers | the paper states whether an adaptive attacker was run; if not, no claim of robustness against one | scope |
| 16 | Errors | provider failures are reported as failures, never scored as safe; spend and caps are reported | reporting |
| 17 | Reproducibility | one command regenerates every number and figure from committed traces; data and code hashes are in the run manifests | reporting |
| 18 | Pre-registration | hypotheses, endpoint, sample, analysis and floor rule are registered before the confirmatory run; deviations are logged | reporting |

How to cite: refer to "the M1 to M6 checks" and to "Appendix B of this paper" when stating which items a study satisfies; an item that is not satisfied should be listed as a limitation.

## Appendix C Artifacts and data availability
All paths are in the repository. Hashes are recorded in the run manifests and in the freeze records.

| artifact | content | size | license or origin | hash or pin |
|---|---|---|---|---|
| frozen packs (Tracks A and B) | judge-scored confirmatory packs | 61 + 61 attacks, benign twins | project | SHA-256 in `datasets/frozen/*/hashes.sha256` |
| harness v2 traces | multi-turn tool episodes with the executor log | several hundred episodes | project | per-run manifests |
| independent scenario set | seven families authored independently of the detector | 168 instances | project | SHA-256 of the template file (§4.4) |
| InjecAgent (external) | 62 attacker instructions x 17 contexts | 1,054 base cases | external repository | commit and file hashes in `datasets/external_samples/injecagent_phase2_sample.json` |
| Hard set, human-written | tool-call-verified items from LLMail-Inject | 238 items (68 calibration, 170 test) | MIT (Hugging Face `microsoft/llmail-inject-challenge`) | `datasets/attackset_hard_v1/FREEZE_RECORD.json` |
| Hard set, model-generated | cross-channel items from a non-target generator | 69 items, exploratory unless validated | project | manifest hash in the freeze record; meta-prompt SHA-256 |
| AgentDojo pairs | fixed seeded pairs for health checks and pilot | 60 pairs of 629 valid | external benchmark | `datasets/external_samples/agentdojo_v1_phase2_pairs.json` |
| model panel | registry with pinned prices and settings | 4 open, 1 closed, 2 judges | OpenRouter list | `configs/models_panel_external_v2.yaml` |
| code | harness, runners, analysis, QC and reproduction script | | project | commit in each manifest |
| reproduction | `scripts/reproduce_negative_result.sh` regenerates the manuscript numbers, ledger and figures offline | | | `NUMBERS_LEDGER.md` with a consistency test |

Attack texts: items from LLMail-Inject are public under their license; the manifests contain identifiers and hashes, and item texts are regenerated from the public dataset. Model-generated items are released after human validation (staged release, §10).

## Appendix D E3 detailed results: Per-family and per-model breakdown

Experiment E3 tested seven independently authored attack families on three models with the B3 adaptive stack and the PHASE1-CORE deterministic defense. Both defenses produced zero blocks across all 336 episodes. The tables below provide the breakdown by family and model; in every table, the difference is A0 minus the defended arm, counted over paired episodes.

Data source: `experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json`

### E3.1 B3 adaptive stack

**Summary statistics:**
- Paired episodes: 167 (of 168 A0 episodes; one B3 episode incomplete)
- A0 (undefended) executed: 56/167
- B3 executed: 57/167
- Blocks by B3: 0
- Paired comparison (n=167): McNemar exact p = 1.0

#### Per-family results (B3)

| Attack Family | A0 Executed | B3 Executed | Difference |
|---|---|---|---|
| authority claim doc | 23/24 | 22/24 | +1 |
| important instructions doc | 9/24 | 8/24 | +1 |
| important instructions weather | 8/24 | 8/24 | 0 |
| second instruction doc | 7/23 | 7/23 | 0 |
| split address doc | 4/24 | 5/24 | −1 |
| unrequested write doc | 5/24 | 7/24 | −2 |
| workflow footer doc | 0/24 | 0/24 | 0 |

#### Per-model results (B3)

| Model | A0 Executed | B3 Executed | Difference |
|---|---|---|---|
| deepseek-v3.2 | 40/55 | 43/55 | −3 |
| gemma-4-31b-it | 8/56 | 6/56 | +2 |
| qwen3-30b-a3b | 8/56 | 8/56 | 0 |

### E3.2 PHASE1-CORE deterministic defense

**Summary statistics:**
- Total episodes: 168
- A0 (undefended) executed: 57/168
- CORE executed: 57/168
- Blocks by CORE: 0
- Paired comparison (n=168): McNemar exact p = 1.0

#### Per-family results (CORE)

| Attack Family | A0 Executed | CORE Executed | Difference |
|---|---|---|---|
| authority claim doc | 23/24 | 23/24 | 0 |
| important instructions doc | 9/24 | 8/24 | +1 |
| important instructions weather | 8/24 | 8/24 | 0 |
| second instruction doc | 8/24 | 9/24 | −1 |
| split address doc | 4/24 | 3/24 | +1 |
| unrequested write doc | 5/24 | 6/24 | −1 |
| workflow footer doc | 0/24 | 0/24 | 0 |

#### Per-model results (CORE)

| Model | A0 Executed | CORE Executed | Difference |
|---|---|---|---|
| deepseek-v3.2 | 41/56 | 41/56 | 0 |
| gemma-4-31b-it | 8/56 | 7/56 | +1 |
| qwen3-30b-a3b | 8/56 | 9/56 | −1 |

### Interpretation

Neither defense produced a block or a consistent reduction in attack execution across the independent families. The per-family and per-model differences are small and within the range of run-to-run noise documented in §6.3 (8 of 168 paired outcomes differed at temperature 0 for CORE; 7 of 167 for B3), so differences of this size cannot be attributed to a defense.
