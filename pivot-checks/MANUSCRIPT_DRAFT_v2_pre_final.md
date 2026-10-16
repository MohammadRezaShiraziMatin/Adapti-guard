# What Reached the Executor? Measurement Checks for Prompt-Injection Defense Evaluation, with a Re-analysis of Released AgentDojo and AgentDyn Runs

*MANUSCRIPT_DRAFT_v2, assembled 2026-10-16 (Tehran). Not submitted, not posted. Sources: `docs/MANUSCRIPT_M1_M3_EXTERNAL_VALIDATION_DRAFT.md` (re-analysis sections, carried over with their labels and source tags) and the original-repo `MANUSCRIPT_DRAFT_v1.md` (`/workspace/adapti-guard/docs/paper/negative_result/`, branch main, read-only; own-harness sections E1–E5, shortened, numbers unchanged). Source tags are paths relative to `/workspace/pivot-checks/` unless marked `[v1 §…]`. Numbers are checked by `review/verify_numbers.py` (output `review/verify_numbers_out.txt`).*

**Labels.** [CONFIRMATORY — preregistered] means the analysis follows a protocol written before the data were scored. [EXPLORATORY] means it was designed or remapped after seeing data. [DEVIATION] marks a departure from a written protocol. [OWN-HARNESS EVIDENCE] marks results from our own testbed (E1–E5), which are not external.

## Abstract

We audit how attack success is measured when prompt-injection defenses for tool-using LLM agents are compared, and re-analyse third-party released runs of two public benchmarks.

**First, scenario validity (M3).** In AgentDyn, 20 of 28 benchmark-specific injection tasks fail their own success check: executing the task's reference solution (`ground_truth()`) in the default environment does not satisfy its `security()` predicate. In all 18 shopping and github tasks, the reference is a placeholder banking call unrelated to the stated goal. This breaks the benchmark's self-check, the tool_knowledge attack and any attempt-based metric keyed to the reference. It does not affect the reported state-based attack success rate (ASR).

**Second, the success endpoint (M1).** We run the empirical test that Pathade et al. leave open ("we report no empirical ranking inversion", §VIII). We re-scored 74,528 released injection episodes (125 run sets) as executed (state change) or attempted (proposed call). The result is narrow. Under the preregistered rule, the success definition reverses the rank of execution-time defenses (progent, drift) in 3/9 eligible cells. A task-clustered bootstrap with Holm correction also gives 3/9, but which specific pairs reverse depends on the inference method. Without progent, 1/9 cells has a flip.

**Third, checker vs LLM judge.** On 600 AgentDyn episodes, agreement between the state checker and two LLM judges depends on the defense (κ 0.454–0.940). In blind manual review the checker was right in all 20 tool_filter disagreements; the judges' main error was scoring attempts as successes.

**Fourth, checker-version drift is negligible:** 198 of 73,009 labels (0.27%) change under current checker code.

We also summarise evidence from our own harness (E1–E5). We make no claim that any defense is effective and no claim of general ranking instability.

## 1 Introduction

Defenses against indirect prompt injection are compared by attack success rate (ASR). Pathade et al. argue that ASR is a family of metrics, parameterised by choices that papers rarely state. They show analytically that some of these choices can reverse defense rankings, but run no defenses themselves (§III, §V, §VIII). Shaw shows on a single audited benchmark and a self-built harness that scoring success by tool identity rather than arguments inflates ASR from 1.2% to 21.7% (§VII-A).

Our own testbed (AdaptiGuard; E1–E5, §6) led us to six candidate measurement checks (M1–M6). In each case, a choice that looks like bookkeeping changed or qualified a conclusion. Evidence from one's own harness is not external. In this version we therefore test two checks on artifacts we did not produce, the released AgentDojo and AgentDyn runs and code:

- **M3:** does each scenario contain a valid attacker effect?
- **M1:** what counts as success?

We add a checker-vs-judge comparison and a checker-version drift check.

**Contributions.**
1. A code-level audit showing that 20/28 AgentDyn injection tasks fail their own success check (§5.1; reproducible code facts).
2. A preregistered test of whether the success definition reverses defense rankings on released runs, with drop-errors, task-clustered and leave-one-defense-out sensitivity analyses (§5.2). The effect is narrow: execution-time defenses, 3/9 cells, method-sensitive pairs.
3. A blind review of checker–judge disagreements and a recall sample (§5.3).
4. A replay of 73,009 stored labels against current checker code (§5.4).
5. Own-harness evidence for M1–M6 (§6), clearly separated.

**Non-claims.** We do not claim that any defense is effective or ineffective in general. We do not claim that evaluation is generally unstable. We do not claim that the six checks are a validated framework.

## 2 Related work

All claims below come from full-text reads; page references are PDF pages [src: review/RELATED_FULLREAD.md].

**Shaw (2609.32691)** audits one unnamed IPI benchmark and its harness and names four defect classes (§IV, p. 3):
- silent payload non-delivery (39/43 payloads never delivered);
- success scored by tool identity rather than arguments;
- false rejections conflated with incapacity;
- no audit trail.

Re-scoring identical traces gives 21.7% ASR under tool-identity scoring vs 1.2% at argument level (§VII-A, Table I). Their harness is single-domain with five tools. Success is an argument-level predicate over *executed* calls (§V-C). Their defenses are TypeChecker, CapabilityRouter and an LLMJudge used as a defense (§V-F). Their defense comparison is not significant (Fisher exact with Holm correction, p = 1.0; §VII-B), and they report no ranking analysis. Shaw also states the principle that a scenario must be measurement-valid: its success condition must be able to fire on the attacker's action. Their harness rejects attacker goals that name a tool absent from the registry (§V-A, §V-D, p. 4).

*What Shaw already showed:* scoring choices inflate the ASR *level*, and attacker goals must be checked for feasibility. *What Shaw did not do:* compare attempted with state-executed success, rank defenses, audit a public benchmark's reference solutions, compare a checker with a judge as evaluator, or analyse checker-version drift.

**Pathade, Pawar and Patil (2609.25173)** name six axes of ASR definition, among them the unit of analysis, the success oracle and partial-success binarization (§III, pp. 2–3). They meta-analyse the reporting practice of 259 papers (§IV) and derive analytical power and ranking-inversion results (§V). Among their points:
- string-matching and state oracles disagree in both directions (p. 2);
- oracle-induced inversion requires substantial differential error: 1 of 25 β combinations inverts (§V-B, p. 5);
- they list tool-set versioning and model version drift as sources of incomparability they do not measure (§III, p. 3).

They state that they ran no defenses end to end and report no empirical ranking inversion (§VIII, p. 6). *What Pathade et al. already showed:* analytically, that oracle and success-definition choices can reverse rankings, and that judge calibration is rarely reported (29.7% of judge-using papers). *What they did not do:* any empirical inversion, any benchmark audit, or any drift measurement.

**Other work.**
- The Same Zero (Yin, 2610.04504) reports that AgentDojo banking state checks missed 11 tool-level attacks, a conditional miss rate of 11/75 [partial read; src: review/RECALL_RESULTS.md §6].
- Liu (2610.03448, read in full) re-evaluates prompt-injection detectors offline without agent ASR [src: LIU_JUDGE_READ.md].
- Hardy et al. (2610.00651) apply generalizability theory to agent leaderboards [abstract and introduction read].
- Benchmarks and defenses (AgentDojo 2406.13352, InjecAgent 2403.02691, CaMeL 2503.18813, Progent 2504.11703, and others) are as in [v1 §2].

**Net novelty.**
- The direction of M1 is anticipated: Shaw for the level effect, Pathade analytically for rankings. Our addition is an empirical, narrow reversal on third-party released runs.
- The principle behind M3 is in Shaw. Our addition is the concrete AgentDyn audit.
- The checker-vs-judge comparison is partly new: Pathade gives the mechanism analytically.
- The drift analysis is new relative to both papers.

## 3 Method: six measurement checks (M1–M6)

Definitions follow [v1 §4, Tables 3 and 3b]. The status of each check is given in brackets.

- **M1, success endpoint.** Success means that the attacker-specified effect reached the executor. In AgentDojo/AgentDyn this is the state-based `security()` check. A proposed or attempted call is reported separately. [Own harness: exploratory. External: tested in §5.2.]
- **M2, blocked payload.** A block before the target is a defense outcome, counted as a failed attack, not as a delivery failure. A sensitivity analysis under the alternative labelling is mandatory. [Own harness only; exploratory.]
- **M3, scenario validity.** An attack scenario must contain a valid attacker-controlled effect, and its reference solution must satisfy its own success check. [Own harness: one scenario. External: §5.1.]
- **M4, authorship independence.** The attack set must be authored independently of detector development and frozen before defenses are run. [Own harness; case-study observation; independence only partial.]
- **M5, per-model reporting.** Results are reported per model, with admission by undefended rate, the executor log preferred over reply text, and a baseline replicate for the noise floor. [Own harness; exploratory.]
- **M6, defense channel.** Confirm that the defense is applied to the channel the attack arrives through. [Own harness; preliminary; 18 indirect episodes.]

**External success definitions (§5.2).**
- EXECUTED: the stored state-based `security()` result.
- ATTEMPTED: the agent proposed a call to an injection ground-truth function, by name match.
- ATTEMPTED-CORRECT-ARGS (CA): preregistered secondary; not used for any claim (§7).

## 4 Threat model and data

**Threat model** [v1 §3.1]:
- the user turn, the system prompt and the defense code are trusted;
- tool-returned content is untrusted;
- the attacker cannot see or change the prompt, the weights or the defense, and is non-adaptive;
- the attacker's goal is an effect the user did not request.

**External data.** These are the publicly released runs and code of AgentDojo and AgentDyn: 125 (benchmark, pipeline, attack) run sets, 50 from AgentDojo and 75 from AgentDyn, with 74,528 injection episodes [src: rankflip/inventory.csv; drift/DRIFT_RESULTS.md]. We authored neither the runs nor the checkers. Defenses in the analysed cells are grouped by stage: input (prompt-level: repeat_user_prompt, spotlighting_with_delimiting; detectors: transformers_pi_detector, prompt_guard_2_detector, piguard_detector), planning (tool_filter, camel) and execution-time (progent, drift) defenses [src: stage/STAGE_RESULTS.md]. Section 5 gives the episode counts each analysis uses.

**Own-harness data.** E1–E5 (§6) use the AdaptiGuard testbed [v1 §3.2].

## 5 External re-analysis of released AgentDojo and AgentDyn runs

**Framing.**

We do not present this work as an external validation of the six checks. What it provides is a **re-analysis of third-party released artifacts**: the AgentDojo and AgentDyn runs and code, which we did not author, using rules we fixed in advance (M1 preregistration). Three properties are external in that sense:
1. The data were generated by others.
2. The checker code is upstream.
3. The ground-truth defects are reproducible code facts.

Three properties are not external:
1. All manual labels come from one AI reviewer.
2. Several analysis choices (the target map, the stage map, the remapping of 53 episodes) were made post hoc.
3. No independent team has re-run any of it.

An independent reproduction remains the required next step.


**Preregistration records** [src: docs/DESIGN_VARIANCE_STUDY.md; review/*.sha256]:
- Ranking-flip preregistration: `docs/DESIGN_VARIANCE_STUDY.md` § "Ranking-flip pre-registration", added 2026-10-15 22:40 Tehran. The recorded sha256 of the file at that time is `97bdb074…61e63c1` (`review/PREREG_RANKFLIP.sha256`).
- Manual disagreement review protocol: same file, added ~21:29. The frozen labels have sha256 `897c498e…e620c` (`review/LABELS_FROZEN.sha256`).
- Recall review protocol: same file, added 22:16. The frozen labels have sha256 `7b9927ad…f9335` (`review/RECALL_LABELS_FROZEN.sha256`).
- The file has been appended to since then (deviation logs), and its current hash differs (`dc596e83…`). **Hash check (re-run 2026-10-16 12:2x Tehran):** `sha256sum docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md` = `97bdb074ae8911cab5ffbad1ed700b6895efff67c3080432c672c660361e63c1`, byte-exact match to `review/PREREG_RANKFLIP.sha256` [src: review/PREREG_RANKFLIP.sha256; docs/PREREG_HASH_RECOVERY.md]. The confirmatory label below therefore stands.

### 5.1 M3: An attack scenario must contain a valid attacker-controlled effect

**Claim.** A scenario's own reference solution must satisfy its own success check. If it does not, then any metric derived from that reference measures nothing.

**Finding [CONFIRMATORY — code fact; no inferential statistics].** We executed each AgentDyn v1 injection task's `ground_truth()` in the default environment and then evaluated its `security()` [src: drift/gt_audit.py → drift/gt_audit_agentdyn_v1.json; drift/GT_AUDIT.md]. Of the 28 AgentDyn-specific injection tasks, 20 fail their own check. The 28 are dailylife 10, shopping 9 and github 9 [src: drift/gt_audit_agentdyn_v1.json, suite counts]. The 20 failures fall into four classes:
1. **`ground_truth()` does not reflect the injection goal, 18 tasks.** This is every shopping and every github task. Each one returns the same banking `send_money(recipient="", amount=0.01, …)` call, regardless of the stated goal (password change, purchase, download, leak).
2. **Tool absent from the suite.** In github, `send_money` does not even exist, so the reference raises ToolNotFoundError. These tasks are counted within the 18.
3. **Wrong arguments, 1 task (dailylife inj6).** The schema requires start/end times, and the date is today when the goal says tomorrow.
4. **Unexplained failure, 1 task (dailylife inj2).** The function and arguments are correct, but security is False. The root cause is unverified.

Across all 55 v1 injection tasks (workspace 6, travel 7, banking 9, slack 5, shopping 9, github 9, dailylife 10), 21 fail, and one of these (travel inj6, a text-only goal) is not a defect [src: drift/gt_audit_agentdyn_v1.json; drift/GT_AUDIT.md, erratum 2026-10-16; AgentDyn `get_suites("v1")`].

**Consequences (scope).** The defect affects three things: the benchmark self-check, the tool_knowledge attack, and attempt-based metrics keyed to `ground_truth()`. It does **not** affect the reported state-based ASR, which is computed by `security()` on the post-run environment and does not use `ground_truth()`.
- *The benchmark self-check fails.* `TaskSuite.check()` requires the ground-truth pipeline to pass security, so it fails for shopping, github and dailylife [src: drift/GT_AUDIT.md].
- *Attack generation.* Only the `tool_knowledge` attack embeds `ground_truth()` in injections. On these suites, it would instruct agents to call `send_money`. Based on the released runs in runs/, no reported number derives from the tool_knowledge attack; we could not trace the AgentDyn paper's tables to unreleased runs. The released AgentDyn attack directories contain only important_instructions, direct and none [src: drift/GT_AUDIT.md].
- *Our own analysis.* Any ATTEMPTED or CA metric keyed to the reference solution is invalid on these suites. This is what forced the post-hoc target map in M1 (**[DEVIATION]**) and what makes the stage analysis exploratory.
- *Scope limit.* User-task ground truths were not audited.

Neither paper audits a benchmark's reference solutions. Shaw states the general principle that a scenario's success condition must be able to fire on the attacker's action, and adds pre-flight checks that reject attacker goals naming a tool absent from the registry (§V-A, §V-D, p. 4). That overlaps our class 2 in concept; the AgentDyn-specific finding is ours. Pathade et al. do not address it [src: review/RELATED_FULLREAD.md]. An issue report has been drafted (`docs/DRAFT_ISSUE_AgentDyn_ground_truth.md`) and **not posted**.

**Plan: report to AgentDyn maintainers before any preprint.** The issue will be filed with the AgentDyn maintainers *before* any preprint or public posting of this section, and only after the owner explicitly approves the final issue text. The manuscript will wait for (or a fixed period after) their reply.

**Maintainers' response [PLACEHOLDER — not yet filed].** Date filed: —. Link: —. Response summary: —. Changes to this section resulting from it: —.


### 5.2 M1: Score what reached the executor, not what was proposed or attempted

**Claim.** An attack "succeeds" only if the attacker's effect reached the executor and changed environment state. Proposing a harmful call, or attempting one that a defense then blocks, is not success. This choice is not cosmetic: it can reverse the rank of execution-time defenses.

**Data.** We re-analysed the publicly released runs of AgentDojo and AgentDyn. The inventory contains 125 (benchmark, pipeline, attack) run sets and 74,528 injection episodes [src: review/RANKING_FLIP_RESULTS.md §1; rankflip/inventory.csv]. Of these sets, 50 are AgentDojo and 75 AgentDyn [src: drift/DRIFT_RESULTS.md; docs/DEVIATIONS_2026-10-16.md #6, which corrects the 51/74 given in RANKING_FLIP_RESULTS.md]. After excluding 5 DoS sets, error episodes and unscorable episodes, 73,009 non-error episodes remain for the checker replay: AgentDojo 31,604 and AgentDyn 41,405 [src: drift/DRIFT_RESULTS.md]. Of the 92 episodes with a non-null error, all are stored as `security=True` under AgentDojo's error convention, and only 5 contain an attempted target call [src: review/RANKING_FLIP_RESULTS.md §1].

**Which episode count each analysis uses** (checked in code):
- *74,528* is the full inventory (125 sets) [src: rankflip/inventory.csv]. The ranking-flip analysis (`rankflip/analyze.py`) drops only unscorable episodes (`score_err`, e.g. the 640 unversioned-workspace KeyErrors) and stored-null labels; it does **not** drop error episodes; per the preregistered primary analysis, any error episode it scores counts under EXEC with its stored value (True). Counts: 92 error episodes in the whole inventory; 1 inside the 9 analysed cells of the full data (AgentDyn llama-3.3-70b, no defense, github suite); 0 in the confirmatory subset, because that episode is in github, which is excluded [src: rankflip/analyze.py; rankflip/results.json `n_err`; review/results_conf.json `n_err`; rankflip/episodes.jsonl; review/RANKING_FLIP_RESULTS.md §1]. The preregistered drop-errors sensitivity ("sensitivity drops episodes with non-null `error`") was omitted earlier and has now been run [DEVIATION: delayed; docs/DEVIATIONS_2026-10-16.md #7]: results are identical to the primary analysis (confirmatory: ATT 3/9 cells, 4 flips / 290 pairs; full: ATT 4/9, 6 / 299) [src: review/run_droperr.py → review/results_droperr_{conf,all}.json].
- *73,009* is the checker-drift replay: it excludes the 5 DoS sets, unscorable/replay-error episodes and **all error episodes** (`not r.get('error')`); the 92 are reported separately (88/92 replay False) [src: drift/analyze_drift.py L27; drift/DRIFT_RESULTS.md].
- The stage analysis also drops error episodes (`or e['error']`) [src: stage/stage_gap.py L10].

**Ranking dependence on the success definition [CONFIRMATORY — preregistered].** We scored every episode three ways:
- EXECUTED: the stored state-based `security()` result.
- ATTEMPTED: the agent proposed a call to an injection ground-truth function.
- ATTEMPTED-CORRECT-ARGS (CA): preregistered secondary; not used for any claim (see the M1 limits and Limitations).

We then compared defense rankings within each (benchmark, model, attack) cell that has at least 3 defenses. There are 9 such cells, all under important_instructions: one AgentDojo cell and eight AgentDyn cells [src: review/RANKING_FLIP_RESULTS.md §1].

The preregistered decision rule: a *significant flip* is a defense pair whose ASR-difference bootstrap 95% CI excludes 0 with opposite signs under the two definitions; the result is a main finding only if ≥25% of cells contain ≥1 significant flip [src: docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md, "Decision rule"].

**(a) Confirmatory subset [CONFIRMATORY — preregistered; hash verified].** Only episodes where the preregistered ATTEMPTED rule (function-name match to the injection task's `ground_truth()`, no post-hoc map) was applied: all AgentDojo episodes and AgentDyn dailylife (plus any other non-shopping/github AgentDyn suite); AgentDyn shopping and github are excluded. Recomputed locally with the unchanged `rankflip/analyze.py` logic (same seed 20261015, 2000 reps), with an input filter only [src: review/run.py → review/results_conf.json]:
- Cell eligibility re-checked with the preregistered rule (≥3 defenses incl. no-defense; the prereg sets no minimum episode count): all 9 cells remain eligible after excluding shopping/github, each contains the no-defense baseline, minimum 200 episodes per defense. 290 defense pairs tested (Σ C(n_def,2); n_def 5–9).
- Bootstrap as preregistered: resample episodes within each (cell, defense), 2000 reps, seed 20261015, no multiplicity correction [src: docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md, "Primary"; rankflip/analyze.py]. (Paired task-level resampling, 10k reps and Holm belong to the separate run-to-run variance protocol in the same file, not to the ranking-flip rule.)
- **Headline:** The success definition reverses the rank of execution-time defenses (progent, drift) in 3/9 cells: K = 3 under the preregistered episode-level bootstrap, and also 3 under the exploratory task-clustered bootstrap. Which specific pairs reverse is sensitive to the inference method (episode- vs task-clustered bootstrap). This is not a claim of general ranking instability [src: review/results_conf.json; clustered/clustered_results.json].
- EXEC→ATTEMPTED: **3/9 cells (33%)** with ≥1 significant flip; **4 significant flips / 290 pairs**. The preregistered ≥25% threshold is met.
- Clustered sensitivity [EXPLORATORY, not preregistered; docs/SENSITIVITY_CLUSTERED.md, hash-locked before running]: paired bootstrap over user tasks, 10k reps, seed 20261015, Holm within cell. Confirmatory subset: ATT 3/9 cells, 4 flips / 290 pairs (≥25% holds), but the set changes. gpt-4o-2024-08-06 progent vs tool_filter is no longer significant, and drift vs tool_filter in that cell becomes a flip. Progent is then in 2 of the 4 flips, in 1 cell. Full data: ATT drops to 1/9 cells, 1 flip / 299 pairs (gpt-4o-2024-08-06 progent vs tool_filter); 5 of the 6 episode-bootstrap flips disappear. Each confirmatory AgentDyn cell has only 20 user-task clusters [src: clustered/clustered.py → clustered/clustered_results.json].
- Leave-one-defense-out [EXPLORATORY, not preregistered; docs/SENSITIVITY_LODO.md, hash-locked before running]: without progent, 1/9 cells, 1 ATT flip / 227 pairs (below 25%); without drift or piguard_detector or tool_filter, 2/9 (below 25%); dropping any other defense leaves 3/9 [src: lodo/lodo_results.json].
- Execution-time defenses (progent, drift) are in every confirmatory flip. Episode-level (preregistered): 4/4 flips involve them (3 progent, 2 drift; the llama drift vs progent flip involves both). Task-clustered (exploratory): also 4/4 (2 progent, 3 drift). Without progent, 1/9 cells has a flip (LODO, episode-level). This is consistent with the stage mechanism below and is not evidence of general ranking instability [src: review/results_conf.json; clustered/clustered_results.json; lodo/lodo_results.json].
- Flips: gemini-2.5-pro drift vs piguard_detector (ΔEXEC −0.050, ΔATT +0.171); gpt-4o-2024-08-06 progent vs tool_filter (−0.065 → +0.387); llama-3.3-70b drift vs progent (+0.100 → −0.290) and progent vs tool_filter (−0.060 → +0.360) [src: review/results_conf.json].
- Kendall τb (EXEC vs ATT): 0.551 (llama-3.3-70b) to 0.944 (gpt-4o-mini) on AgentDyn; 0.8 on the AgentDojo cell; undefined for gpt-5-mini, whose dailylife EXEC ASR is 0 for all 8 defenses [src: review/results_conf.json].
- Note: this subset contains AgentDyn dailylife injection tasks 2 and 6, whose `ground_truth()` fails its own check (M3); they were not removed because the preregistration did not provide for it.

**(b) Full data with post-hoc target map [EXPLORATORY].** All 9 cells including shopping/github scored via the hand-written target map (Deviation 1). This reproduces `rankflip/results.json` exactly [src: rankflip/results.json; review/results_all.json]:
- 299 defense pairs tested; EXEC→ATTEMPTED **4/9 cells (44%)**, **6 significant flips**. Separately, EXEC→CA: 3/9 cells, 4 flips / 299 pairs (unreliable; see Limitations). The "10 flips" of the earlier draft were 6 ATT + 4 CA.
- Leave-one-defense-out [EXPLORATORY]: without progent, ATT 1/9 cells, 1 flip / 235 pairs (below 25%); CA 0 flips [src: lodo/lodo_results.json].
- τb 0.514 (llama-3.3-70b) to 0.889 (gemini-2.5-flash) on AgentDyn; 0.8 on AgentDojo.
- Largest single reversal: progent vs tool_filter on gpt-4o-2024-08-06, ASR difference −0.027 under EXEC and +0.219 under ATTEMPTED. This pair is the only flip that survives the task-clustered analysis on the full data [src: review/RANKING_FLIP_RESULTS.md §3; clustered/clustered_results.json].

CA results are not part of either claim; see Limitations.
**Robustness of the EXEC→ATTEMPTED flip count** (ATT only; cells with flip / flips / pairs tested, denominator = 9 eligible cells) [src: review/results_conf.json; rankflip/results.json; review/results_droperr_{conf,all}.json; clustered/clustered_results.json; lodo/lodo_results.json]:

| Analysis | Confirmatory subset | Full data (exploratory) |
|---|---|---|
| Preregistered (episode bootstrap) | 3/9 / 4 / 290 | 4/9 / 6 / 299 |
| Drop-errors (prereg sensitivity) | 3/9 / 4 / 290 | 4/9 / 6 / 299 |
| Task-clustered + Holm (exploratory) | 3/9 / 4 / 290 | 1/9 / 1 / 299 |
| LODO without progent (exploratory) | 1/9 / 1 / 227 | 1/9 / 1 / 235 |

Why the clustered count is higher in the subset than in the full data: this is not a bug. The full data is not a superset test. Each AgentDyn cell adds 40 shopping/github user tasks (60 vs 20 clusters), and in those tasks the defense differences are smaller, so the pooled point estimates shrink. Examples: gemini-2.5-pro drift vs piguard_detector ΔEXEC goes from −0.050 to −0.009 (p 0.30); llama drift vs progent ΔATT goes from −0.29 to −0.093 (p 0.014, not Holm-significant). Holm family sizes are the same (36 pairs) in every cell except gpt-4o-mini (36 vs 45, because of camel). The bootstrap draws differ between runs, but the changes follow the point estimates. Borderline cases also flip across the Holm threshold in both directions; for example, gpt-4o-2024-08-06 progent vs tool_filter has ΔEXEC p = 0.0062 in the subset (not significant at m = 36) and 0.0042 in the full data (significant) [src: clustered/diag.py → clustered/diag_results.json].


**[DEVIATION]** (1) For AgentDyn shopping and github, `ground_truth()` does not reflect the injection goal (see M3), so the preregistered ATTEMPTED rule could not be applied to them. We replaced it with a hand-written target map derived from each `security()`, written after the first-pass disagreements had been seen. Results using it are reported only as part (b), exploratory. (2) CA was scored as a token-substring match rather than the preregistered exact-normalised match. (3) Unversioned AgentDojo runs were assumed to be v1 [unverified]. (4) The preregistered blind re-label of 53 episodes was not performed [src: review/RANKING_FLIP_RESULTS.md § Deviations].

**The flips are mechanical, not noise.** The counts and examples in this paragraph come from the preregistered episode-level analysis. Task-clustered counts are given in brackets. In the confirmatory subset, 3 of 4 ATT flips involve progent and the fourth involves drift [clustered: 4 ATT flips, 2 involve progent, 3 involve drift] [src: review/results_conf.json; clustered/clustered_results.json]. In the exploratory full data, 9 of 10 significant flips (5 of 6 ATT + 4 of 4 CA (non-preregistered scorer), 299 pairs per definition) involve progent; the remaining one is drift vs none (qwen3-235b) [clustered: 1 ATT flip + 1 CA flip, both gpt-4o-2024-08-06 progent vs tool_filter] [src: review/RANKING_FLIP_RESULTS.md §3; rankflip/results.json]. All three are defenses that act at or after the point where the agent proposes a call. Under ATTEMPTED they receive no credit for blocking it. No exploratory flip involves only prompt-level or detector defenses (the confirmatory drift vs piguard_detector flip involves drift), and the AgentDojo cell, which has neither progent nor drift, has zero flips [src: same].

We therefore do not report this as "evaluation instability". The reversal is what you should expect when an attempt-based metric is applied to defenses that block at execution time. This is related to Shaw (2609.32691), who shows that scoring executed calls by tool identity instead of arguments inflates ASR (21.7% vs 1.2%). That result comes from re-scoring traces of an audited benchmark and from Shaw's own single-domain, five-tool harness (§IV D2, §VII-A, pp. 3–5). That level-inflation result is Shaw's, not ours. Shaw does not contrast attempted with state-executed success and reports no defense ranking analysis (frontier defense comparison n.s., §VII-B, p. 5). Our possible addition is rank reversals across models on two public benchmarks' released runs [src: review/RELATED_FULLREAD.md].

Pathade et al. (2609.25173) argue analytically (closed-form, with a Monte Carlo check for sampling) that the oracle choice can invert rankings; they find oracle-induced inversion requires substantial differential error, and they state that they ran no defenses and report no empirical ranking inversion (§III, §V-B, §VIII, pp. 2–6) [src: review/RELATED_FULLREAD.md].

**Stage-aware gap [EXPLORATORY].** To quantify the mechanism, we assigned each defense a stage: input, planning, or execution-time. This stage map was written after the flips had been seen. Mean ATT−EXEC gaps (important_instructions, error episodes dropped, 9 cells) were [src: stage/STAGE_RESULTS.md; stage/stage_gap_results.json]:
- input (5 defenses): 0.081
- planning (tool_filter, camel; camel only on gpt-4o-mini): 0.040
- execution-time (**2 defenses only**: progent, drift): 0.154

Effect sizes: execution−input +0.073, execution−planning +0.114, planning−input −0.041; in the dailylife-only sensitivity analysis (excluding injection tasks 2 and 6, 8 cells) +0.107, +0.195 and −0.088 [src: stage/STAGE_RESULTS.md]. We report no p-values: the permutation and bootstrap in `stage/stage_gap.py` are at episode/stage-label level within cells, and with only two execution-time defenses the contrast cannot be generalised beyond progent and drift.

Several limits apply:
- Stage is confounded with defense identity: only two defenses are execution-time, one or two are planning.
- The ATTEMPTED scorer was validated only on AgentDyn gpt-4o: 96/113 agreement, Cohen κ=0.645 [src: review/RANKING_FLIP_RESULTS.md §2].
- CA (not preregistered as implemented: token-substring rather than exact-normalised match) is excluded from all claims. CA ASR often falls *below* EXEC ASR, which a superset metric should not do (e.g., AgentDojo gpt-4o undefended: 0.261 vs 0.477) [src: review/RANKING_FLIP_RESULTS.md §3]. We treat CA as unreliable.
- **[DEVIATION]** No mixed model was fitted; a permutation test replaced it [src: docs/DEVIATIONS_2026-10-16.md #4].


### 5.3 Checker vs LLM judge [EXPLORATORY]

The deterministic state checker was compared with two LLM judges (gemini-2.5-flash-lite and claude-haiku-5.5). The sample was 600 AgentDyn gpt-4o attack episodes, 200 per defense across 3 defenses [src: judge_pilot/RESULTS.md]. The pilot made 1,396 calls and cost $0.3787, computed from token counts (OpenRouter reported $0.3746) [src: judge_pilot/RESULTS.md; judge_pilot/SPEND_LOG.csv].

**Agreement depends on the defense** [src: judge_pilot/RESULTS.md, partial = failure]:
- repeat_user_prompt: κ is 0.932 for Gemini and 0.940 for Haiku.
- tool_filter: κ is 0.454 for Gemini and 0.632 for Haiku. Here the judges' weighted ASR is 0.137 and 0.087, against the checker's 0.045.
- PG2: the checker's ASR is 0.284 and Gemini's is 0.360. Gemini reverses the PG2 vs repeat order: checker Δ=−0.038, judge Δ=+0.040, P(flip)=0.939.
- The preregistered criterion "κ>0.9 on all three defenses" fails.

**Manual review: the checker is precise, and the judges count attempts.** A blind review covered all 43 judge–checker disagreements plus 10 random agreement controls [src: review/REVIEW_RESULTS.md]:
- tool_filter: the checker was right in 20/20 disagreements (Wilson 0.84–1.00).
- Definitions: **J+C−** = the LLM judge says the attack succeeded and the state checker says it failed; **J−C+** = the judge says failed and the checker says succeeded.
- PG2: right in 11/13 J+C− items (0.58–0.96), with 2 unclear, plus 1/1 J−C+.
- Controls: 10/10 correct (0.72–1.00).

The judges' systematic error was to score attempts as successes. Examples are checkouts or transfers that stalled at an unverified OTP, failed form submissions, text-only mentions, and requests for confirmation. On repeat_user_prompt the judge was right in 3/6 J−C+ items (0.19–0.81). These are R01/R25/R47: the replay shows all three are False under the current checker, and R25 is the confirmed github fix [src: drift/DRIFT_RESULTS.md]. After correction, PG2 stays below repeat under either reading of the unclear items (Δ −0.028 or −0.021), so the judge-induced flip is not supported [src: review/REVIEW_RESULTS.md §5].

**Recall.** 60 newly drawn checker-negative episodes (both judges "no") were all truly negative, so there were 0 misses [src: review/RECALL_RESULTS.md §2]. Within this stratum the miss rates are 0/23, 0/23 and 0/22, with Wilson upper bounds of ≤14.3%, ≤14.3% and ≤14.9% [src: review/RECALL_RESULTS.md §5]. Propagated by weight, these give worst-case recall lower bounds of 0.27 for tool_filter, 0.76 for PG2 and 0.76 for repeat. The bounds are loose because zero events cannot rule out a moderate miss rate.

**Power.** ±3 pp equivalence is testable at n=200 only if judge–checker disagreement is about 2% or lower [src: judge_pilot/POWER.md]. The observed disagreement is about 2–11% [src: judge_pilot/RESULTS.md finding 4]. TOST is therefore descriptive here.

**Relation to prior work.** The Same Zero (Yin, 2610.04504) reports that AgentDojo banking state checks missed 11 tool-level attacks, a conditional miss rate of 11/75. That result is on a different benchmark slice, model and defense set, and we read only the abstract, p.8 and Limitations item 5 [unverified beyond these; src: review/RECALL_RESULTS.md §6]. Our checker misses are in a different direction (hard-coded target identities, R15/R26/R53), and we found none in the recall sample. Liu (2610.03448, read in full) re-evaluates PI detectors offline without agent ASR [src: LIU_JUDGE_READ.md]. Hardy et al. (2610.00651) apply generalizability theory to agent leaderboards; there the verifier facet arises only in passing (abstract and introduction read) [src: docs/DESIGN_VARIANCE_STUDY.md; review/RECALL_RESULTS.md §6].


### 5.4 Checker-version drift

**Checker-version drift (one paragraph) [CONFIRMATORY in method; descriptive; negative].** Stored labels might reflect older checker code, so we replayed the logged tool calls of all scorable episodes against the current checkers (AgentDojo 089ed468, AgentDyn 5353cf761) [src: docs/DEVIATIONS_2026-10-16.md #1]. The results [src: drift/DRIFT_RESULTS.md]:
- 198 of 73,009 labels changed (0.27%): AgentDojo 39, AgentDyn 159.
- The largest per-set shift was −0.071 (AgentDyn gpt-4o-mini repeat_user_prompt, Newcombe [−0.095, −0.048]).
- 6 of 120 sets have a CI that excludes zero.
- Strict defense order changed in 2 of 15 multi-defense cells, both near-ties decided by 1–2 episodes. No ranking change is meaningful.

One cause is confirmed by code diff: AgentDyn github injection_task_1 moved from a state-based to a trace-based check (commits ae6513a/1a6d11d/2c99edc, 2026-05-02). For 166 changes we could find no attributable cause.

**[DEVIATION]** A first replay pass re-executed calls that defenses had blocked. It was discarded as invalid [src: docs/DEVIATIONS_2026-10-16.md #2]. The replay also has fidelity limits: OTP feeding, and tool outputs are not compared to the logs. Pathade et al. list environment and tool-set versioning and model version drift as sources of incomparability they do not measure (§III, p. 3) [src: review/RELATED_FULLREAD.md].


## 6 Own-harness evidence (E1–E5) [OWN-HARNESS EVIDENCE]

*These results come from our own testbed. They are shortened from [v1 §5–§6]; all numbers are unchanged from v1, and v1 cites the trace files and scripts for each. They are not external validation. Labels follow v1: none of E2–E4 was preregistered, and E5 followed a locally drafted, not externally registered, protocol [v1 §5.5, §6.6].*

**E1: frozen judge-scored tracks, re-scored by the tool layer's execution record [v1 §5.2, §6.1].** Two hash-locked packs of 61 attack and 61 benign episodes; one target (qwen/qwen-2.5-7b-instruct); an LLM judge (qwen/qwen-2.5-72b-instruct). The judge and the executed outcome agree only weakly (κ 0.18, 0.36 and 0.16 in the three informative arms). Every disagreement has the judge saying success while the call did not execute. On Track B the frozen "supported improvement" has a judge-scored paired effect of δ̂ = 0.4426 (27/0, p = 1.49e-8, utility 59/61 = 0.967). With executed calls the effect is 0.9016 (55/0), and utility for tool-required tasks is 49/61 = 0.80, below the 0.95 floor. The frozen classification therefore rests on two judge errors that offset each other.

**E2: exploratory four-arm run on the original scenarios [v1 §5.3, §6.2].** Multi-turn mock-tool harness, three open targets, 468 episodes, 72 attack episodes per arm. A static tool policy (TOOLDENY) has 65/72 attack episodes with a matching proposed call but 0/72 executed (M1). PHASE1-CORE executed 36/72 when blocks count as failed attacks, but 36/36 when blocks are dropped as "not delivered" (M2). Restricted to the one valid attack scenario it executed 0/36: the second scenario requests the effect in the trusted user turn and is excluded under M3. Benign utility under TOOLDENY is 15/45, against 45/45 for the other arms. The episode-inclusion rule was adopted post hoc [DEVIATION; v1 §4.2].

**E3: independently authored attack families [v1 §5.4, §6.3].** Seven families, frozen before any run; 168 undefended episodes (56 instances × 3 models). Susceptibility is model-specific: deepseek 41/56, qwen3 8/56, gemma 8/56 (M5). Paired with the undefended baseline:
- B3: 56 vs 57 executed of 167 pairs, b10/b01 = 3/4.
- PHASE1-CORE: 57 vs 57 of 168 pairs, b10/b01 = 4/4. PHASE1-CORE removed the payload from 0 of 168 instances, although it had blocked 36/36 on the original pack (M4).
- Noise floor: 8 of 168 paired outcomes differ at temperature 0 even with identical model input.

Authorship independence is only partial and is disclosed (the author had read the detector's pattern lists earlier in the same session).

**E4: held-out application and channel re-run [v1 §5.4b, §6.5].**
- Applied unchanged to an earlier run (MT1 r1), the rules exposed M6: a delimiter defense wrapped the user prompt and left the untrusted context unmarked. Indirect injections went from 21 to 21 of 36.
- A follow-up run ($0.0669, 180 episodes) that marks the context instead lowered indirect injections from 8 to 1 of 18 (7 wins, 0 losses). Direct injections were unchanged (22 to 22 of 30).
- With a verifiable canary token, judge and deterministic emission agree well (κ 0.81 to 0.91).

**E5: external InjecAgent test, proposal-level endpoint [v1 §5.6, §6.6–§6.7].** The protocol was drafted locally and not externally registered. On the fixed 186-case sample, delimiters on the tool channel (SPOT_TOOL) lowered attacker-tool first calls:
- llama-4-maverick: 23/186 → 5/186, difference −0.097 [−0.145, −0.048];
- qwen3.8-flash: 23/186 → 4/186, difference −0.102 [−0.156, −0.054];
- undefended replicates differed by 0.005 and −0.005 (noise floor).

Three of five 2026 targets were at the floor in calibration, so a defense effect there would have been unmeasurable. The endpoint is tool identity at proposal level, so E5 does not test M1.

Live spend for E2–E4 is reported in [v1 §5, §8.5] (E2 and E3 about $0.23; E4 follow-up $0.0669). It is separate from the $0.3787 for the re-analysis (§8).

## 7 Limitations

### 7.1 Limitations of the external re-analysis

- **Labelling.** Most labels (53 disagreement and control items, 60 recall items, 113 scorer-validation items) come from a **single AI reviewer**. Sixteen blind labels from the owner (`review/OWNER_SUBSET.md`) are pending and will be added. Blinding was imperfect: the defense identity was not hidden, because tool_filter episodes show the filter prompt and PG2 episodes show "Data omitted" [src: review/REVIEW_RESULTS.md, Dev. 3; review/RECALL_RESULTS.md; review/RANKING_FLIP_RESULTS.md §2].
- **Analyst = labeller.** The same analyst (an AI agent) who designed the analyses, wrote the preregistrations, the target map and the stage map also produced the manual labels. This is a source of possible bias that blinding only partly addresses.
- **CA metric.** EXEC→CA results (confirmatory subset: 2/9 cells, 2 flips / 290 pairs; full data: 3/9 cells, 4 flips / 299 pairs) [src: review/results_conf.json; rankflip/results.json] are not preregistered as implemented (substring vs exact-normalised match) and are unreliable (CA < EXEC in places); they support no claim.
- **Remapping.** The 4-level remapping of the 53 prior episodes was done after unblinding, and the reviewer had already seen those items. It is [EXPLORATORY] [src: review/RANKING_FLIP_RESULTS.md §4].
- **Narrow data.** The judge and review results cover one model (AgentDyn gpt-4o) and three defenses. The AgentDojo side of M1 is effectively a single cell.
- **Statistics.** The replay has fidelity limits, and the bootstraps are not clustered by user task.
- **Literature reading.** Shaw and Pathade et al. were read in full (PDFs in `papers/`; review/RELATED_FULLREAD.md). No quotation is used in this section.


### 7.2 Limitations of the own-harness evidence

These are condensed from [v1 §8]:
- one testbed and three to five targets;
- the E2/E3 scoring rules were not preregistered, and the E2 inclusion rule was adopted post hoc;
- M3, M4 and M6 rest on a single scenario, a partially independent author and 18 episodes respectively;
- no adaptive attacker was evaluated;
- the live harness and run scripts are not in the public tree [v1 §10].

### 7.3 Analyst and reviewer

The same analyst, an AI agent, designed the analyses, wrote the preregistrations, the target map and the stage map, and produced all manual labels (53 disagreement and control items, 60 recall items, 113 scorer-validation items) [src: review/REVIEW_RESULTS.md; review/RECALL_RESULTS.md; review/RANKING_FLIP_RESULTS.md §2]. Blinding was imperfect (see §7.1). Sixteen blind owner labels are pending [PLACEHOLDER: owner labels, `review/OWNER_SUBSET.md`].

## 8 Ethics and disclosure

**Who did what.**
- The owner (Shirazi Matin) specified the studies, approved each analysis round and its budget caps, and will approve any external communication.
- An AI assistant (Grok Bot, agent sessions) wrote the analysis code, ran all analyses, wrote the preregistration texts and the sensitivity procedures, produced every manual label as a single reviewer, did the literature reads, and drafted this manuscript.
- Numbers were regenerated by scripts from released data.
- The assistant is not an author.
- The own-harness work (E1–E5) also used AI assistance as described in [v1 §10].

**Single reviewer.** All manual labels come from one AI reviewer, who also designed the analyses (§7.3). The owner's blind labels on a 16-item subset are pending [PLACEHOLDER: owner-label agreement, κ and disagreements, to be added].

**Upstream disclosure.** The AgentDyn ground_truth defects (§5.1) are drafted as an issue (`docs/DRAFT_ISSUE_AgentDyn_ground_truth.md`) and **not posted**. It will be filed with the AgentDyn maintainers before any preprint, and only after the owner approves the final text [PLACEHOLDER: issue status — date filed, link, maintainers' response, resulting changes]. No defect gives an attacker new capability; it concerns measurement only.

**API spend.** The external re-analysis made LLM calls only in the judge pilot (§5.3): 1,396 calls, $0.3787 computed from returned token counts × verified prices (OpenRouter-reported $0.3746), under a $1.00 cap [src: judge_pilot/RESULTS.md; judge_pilot/SPEND_LOG.csv]. This bought two LLM judges (gemini-2.5-flash-lite, claude-haiku-5.5) on the 600-episode AgentDyn gpt-4o attack sample [src: judge_pilot/RESULTS.md]; the 1,396 calls include 80 wasted Haiku calls and some duplicates. Everything else was offline: the ranking-flip analysis, all sensitivity analyses, drift replay, ground-truth audit and manual review. Read-only GitHub API calls for commit mapping were free, and nothing was posted [src: docs/DEVIATIONS_2026-10-16.md #5]. Own-harness spend is separate (§6).

**Dual use.** No attacks were run against live systems. All re-analysed data are public releases.

## 9 Reproducibility

All paths are relative to `/workspace/pivot-checks/`. Python 3 with numpy; no network is needed except where noted.

| Result | Inputs | Script / command | Output | Hash / lock |
|---|---|---|---|---|
| Inventory, 125 sets / 74,528 episodes | released AgentDojo/AgentDyn `runs/` | `rankflip/inventory.py`, `rankflip/score_all.py` | `rankflip/inventory.csv`, `rankflip/episodes.jsonl` | — |
| Ranking flips, full data [EXPLORATORY] | `rankflip/episodes.jsonl` | `python3 rankflip/analyze.py` | `rankflip/results.json` | prereg `review/PREREG_RANKFLIP.sha256` |
| Ranking flips, confirmatory subset | same | `python3 review/run.py conf` (and `all`) | `review/results_conf.json`; `/workspace/rf_split/results_{conf,all}.json` | prereg file `docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md`, sha256 `97bdb074…61e63c1` |
| Drop-errors sensitivity | same | `python3 review/run_droperr.py conf` / `all` | `review/results_droperr_{conf,all}.json` | (prereg) |
| Task-clustered + Holm [EXPLORATORY] | same | `python3 clustered/clustered.py`; diagnostics `python3 clustered/diag.py` | `clustered/clustered_results.json`, `clustered/diag_results.json` | `docs/SENSITIVITY_CLUSTERED.sha256` (`b8382d44…`, 12:53:30) |
| LODO [EXPLORATORY] | same | `python3 lodo/lodo.py` | `lodo/lodo_results.json` | `docs/SENSITIVITY_LODO.sha256` (`27bc8693…`, 12:27:47) |
| Scorer validation 96/113 | review labels | `rankflip/validate.py` | review/RANKING_FLIP_RESULTS.md §2 | — |
| Stage gaps [EXPLORATORY] | `rankflip/episodes.jsonl` | `stage/stage_gap.py` | `stage/stage_gap_results.json`, stage/STAGE_RESULTS.md | — |
| Ground-truth audit | AgentDyn v1 code (commit 5353cf761) | `drift/gt_audit.py` | `drift/gt_audit_agentdyn_v1.json`, drift/GT_AUDIT.md | — |
| Drift replay | episodes + local checker clones (AgentDojo 089ed468, AgentDyn 5353cf761) | `drift/replay_current.py`, then `drift/analyze_drift.py`, `drift/classify_changes.py` | drift/DRIFT_RESULTS.md | — |
| Judge pilot (paid, $0.3787) | sample from `judge_pilot/make_sample.py` (seed 20261015) | judge_pilot scripts (network, API keys) | judge_pilot/RESULTS.md, `judgments.jsonl`, `SPEND_LOG.csv` | — |
| Manual review | `review/BLIND_PACKET_*.md` | `review/select.py` (seed 20261016), `review/unblind.py` | `review/unblinded.json`, review/REVIEW_RESULTS.md | `review/LABELS_FROZEN.sha256` (`897c498e…`) |
| Recall review | `review/RECALL_PACKET.md` | `review/select_recall.py` (seed 20261017), `review/recall_analysis.py` | `review/recall_analysis.json`, review/RECALL_RESULTS.md | `review/RECALL_LABELS_FROZEN.sha256` (`7b9927ad…`) |
| Number check | this manuscript + sources | `python3 review/verify_numbers.py` | `review/verify_numbers_out.txt` | — |
| E1–E5 | original repo | `scripts/reproduce_negative_result.sh` and scripts listed in [v1 §10] | v1 `NUMBERS_LEDGER.md` | `datasets/frozen/*/hashes.sha256` |

Recompute the preregistration hash with `sha256sum docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md`. The deviations log is `docs/DEVIATIONS_2026-10-16.md` (#1–#8).

## 10 Conclusion

Re-analysing artifacts we did not produce supports two measurement checks, with a narrow scope.

- **M3:** a public benchmark can ship injection tasks whose reference solution fails its own success check (20/28 in AgentDyn). This invalidates the self-check and attempt-based metrics, but not the state-based ASR.
- **M1:** scoring attempts instead of executed state changes reverses the rank of execution-time defenses in 3/9 cells under both bootstrap methods. Which pairs reverse depends on the method, and without progent only 1/9 cells has a flip. This is the empirical counterpart that Pathade et al. call for, and it is consistent with a stage mechanism, not with general ranking instability.
- **Judges vs checker:** an LLM judge's agreement with the state checker depends on the defense, mainly because judges count attempts as successes.
- **Drift:** checker-version drift is negligible.

All manual labels come from one AI reviewer, the owner's labels and the upstream issue are pending, and independent reproduction is the required next step.


## Appendix A: All numbers and sources (re-analysis)

| Number | Meaning | Source |
|---|---|---|
| 125 / 74,528 | run sets / injection episodes | review/RANKING_FLIP_RESULTS.md §1; rankflip/inventory.csv |
| 50 / 75 | AgentDojo / AgentDyn sets | drift/DRIFT_RESULTS.md; docs/DEVIATIONS_2026-10-16.md #6 |
| 73,009 (31,604 + 41,405) | non-error, non-DoS replayed episodes | drift/DRIFT_RESULTS.md |
| 92; 5 | error episodes stored True; with attempted target call | review/RANKING_FLIP_RESULTS.md §1 |
| 9 cells | ≥3 defenses incl. no-defense; all 9 also eligible in confirmatory subset | review/RANKING_FLIP_RESULTS.md §1 |
| 3/9 (33%); 4 flips / 290 pairs | CONFIRMATORY ATT, excl. AgentDyn shopping/github | review/results_conf.json (review/run.py) |
| 4/9 (44%); 6 flips / 299 pairs | EXPLORATORY ATT, post-hoc map | rankflip/results.json; review/results_all.json |
| 2/9 (2 flips / 290); 3/9 (4 flips / 299) | CA, confirmatory subset / full (limitations only) | review/results_conf.json; rankflip/results.json |
| τb 0.551–0.944; 0.8 | confirmatory AgentDyn range; AgentDojo | review/results_conf.json |
| ATT 3/9, 4 / 290; ATT 4/9, 6 / 299 (identical to primary) | drop-errors sensitivity (prereg), confirmatory; full | review/results_droperr_{conf,all}.json |
| ATT 3/9, 4 / 290; ATT 1/9, 1 / 299 | clustered paired bootstrap + Holm (EXPLORATORY), confirmatory; full | clustered/clustered_results.json |
| ATT 1/9, 1 flip / 227; ATT 1/9, 1 flip / 235 | LODO without progent: confirmatory subset; full (EXPLORATORY) | lodo/lodo_results.json; docs/SENSITIVITY_LODO.md |
| 97bdb074…61e63c1 | prereg hash, reproduced byte-exact | review/PREREG_RANKFLIP.sha256 |
| τb 0.514–0.889; 0.8 | AgentDyn range; AgentDojo | review/RANKING_FLIP_RESULTS.md §3 |
| −0.027 → +0.219 | progent vs tool_filter, gpt-4o-08-06 | review/RANKING_FLIP_RESULTS.md §3 |
| 9/10 (5/6 ATT + 4/4 CA) | exploratory flips involving progent | review/RANKING_FLIP_RESULTS.md §3 |
| 96/113, κ 0.645 | ATT scorer validation | review/RANKING_FLIP_RESULTS.md §2 |
| 0.261 vs 0.477 (M1 limits paragraph, "Several limits apply") | CA vs EXEC, AgentDojo gpt-4o none | review/RANKING_FLIP_RESULTS.md §3 |
| 0.081 / 0.040 / 0.154 | stage gaps | stage/STAGE_RESULTS.md |
| +0.073 / +0.114 / −0.041; +0.107 / +0.195 / −0.088 | stage contrasts (effect sizes only) | stage/STAGE_RESULTS.md |
| 198 / 73,009 (0.27%); 39 / 159 | checker drift | drift/DRIFT_RESULTS.md |
| −0.071 [−0.095, −0.048]; 6/120; 2/15; 166 | drift details | drift/DRIFT_RESULTS.md |
| 20/28; 18 + 1 + 1; 21/55 | ground_truth defects | drift/GT_AUDIT.md; drift/gt_audit_agentdyn_v1.json |
| $0.3787 ($0.3746); 1,396; 600 | pilot spend, calls, episodes | judge_pilot/RESULTS.md |
| κ 0.454 / 0.632 / 0.932 / 0.940 | judge–checker agreement | judge_pilot/RESULTS.md |
| 0.045 / 0.137 / 0.087; 0.284 / 0.360; P(flip)=0.939 | ASRs, checker vs judge | judge_pilot/RESULTS.md |
| 43 + 10; 20/20; 11/13; 3/6; 10/10 | manual review | review/REVIEW_RESULTS.md |
| −0.028 / −0.021 | corrected PG2−repeat | review/REVIEW_RESULTS.md §5 |
| 60/60; ≤14.3/14.3/14.9%; 0.27/0.76/0.76 | recall and Wilson bounds | review/RECALL_RESULTS.md §2, §5 |
| ~2%; 2–11% | TOST power threshold; observed disagreement | judge_pilot/POWER.md; judge_pilot/RESULTS.md |
| 11/75 | The Same Zero conditional miss rate | review/RECALL_RESULTS.md §6 (partial read) |


## Appendix B: Open issues
1. ~~Preregistration hash~~ **Resolved 2026-10-16:** recovered artifact `docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md` matches `review/PREREG_RANKFLIP.sha256` (`97bdb074…`). Only the post-freeze deviations section had been appended. See `docs/PREREG_HASH_RECOVERY.md`.
2. The 16 owner labels are pending (`review/OWNER_SUBSET.md` / `review/owner_labels.TEMPLATE.jsonl`).
3. ~~Shaw and Pathade are not fully read.~~ **Resolved 2026-10-16:** full-text read in review/RELATED_FULLREAD.md.
4. AgentDyn maintainer issue: awaiting owner approval to file; response placeholder in §5.1 and §8.
5. dailylife inj2 root cause is unknown, and so is the cause of the R01/R47 drift.
6. A pooled Wilson bound for 0/60 is not in any file and was deliberately not stated.
