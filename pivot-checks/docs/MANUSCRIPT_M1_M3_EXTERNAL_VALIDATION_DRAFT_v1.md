# DRAFT rewrite: §4.1 (M1), §4.3 (M3), checker vs LLM judge, and external validation framing

*Draft written 2026-10-16 (Tehran). It is meant to replace the corresponding parts of `MANUSCRIPT_DRAFT_v1.md`; that file was not edited. Every number carries an inline source tag. Tags are paths relative to `/workspace/pivot-checks/`. No new API/LLM calls were made for this draft.*

**Labels used below.** [CONFIRMATORY — preregistered] means the analysis follows a protocol written before the data were scored. [EXPLORATORY] means the analysis was designed or remapped after seeing data. [DEVIATION] marks a departure from a written protocol.

**Preregistration records** [src: docs/DESIGN_VARIANCE_STUDY.md; review/*.sha256]:
- Ranking-flip preregistration: `docs/DESIGN_VARIANCE_STUDY.md` § "Ranking-flip pre-registration", added 2026-10-15 22:40 Tehran. The recorded sha256 of the file at that time is `97bdb074…61e63c1` (`review/PREREG_RANKFLIP.sha256`).
- Manual disagreement review protocol: same file, added ~21:29. The frozen labels have sha256 `897c498e…e620c` (`review/LABELS_FROZEN.sha256`).
- Recall review protocol: same file, added 22:16. The frozen labels have sha256 `7b9927ad…f9335` (`review/RECALL_LABELS_FROZEN.sha256`).
- The file has been appended to since then (deviation logs), and its current hash differs (`dc596e83…`). Before submission, the 22:40 text must be shown to match the recorded hash (see Open issues).

---

## 4.1 M1: Score what reached the executor, not what was proposed or attempted

**Claim.** An attack "succeeds" only if the attacker's effect reached the executor and changed environment state. Proposing a harmful call, or attempting one that a defense then blocks, is not success. This choice is not cosmetic: it changes which defense looks best.

**Data.** We re-analysed the publicly released runs of AgentDojo and AgentDyn. The inventory contains 125 (benchmark, pipeline, attack) run sets and 74,528 injection episodes [src: review/RANKING_FLIP_RESULTS.md §1; rankflip/inventory.csv]. Of these sets, 50 are AgentDojo and 75 AgentDyn [src: drift/DRIFT_RESULTS.md; docs/DEVIATIONS_2026-10-16.md #6, which corrects the 51/74 given in RANKING_FLIP_RESULTS.md]. After excluding 5 DoS sets, error episodes and unscorable episodes, 73,009 non-error episodes remain for the checker replay: AgentDojo 31,604 and AgentDyn 41,405 [src: drift/DRIFT_RESULTS.md]. Of the 92 episodes with a non-null error, all are stored as `security=True` under AgentDojo's error convention, and only 5 contain an attempted target call [src: review/RANKING_FLIP_RESULTS.md §1].

**Ranking dependence on the success definition [CONFIRMATORY — preregistered].** We scored every episode three ways:
- EXECUTED: the stored state-based `security()` result.
- ATTEMPTED: the agent proposed a call to an injection ground-truth function.
- ATTEMPTED-CORRECT-ARGS (CA).

We then compared defense rankings within each (benchmark, model, attack) cell that has at least 3 defenses. There are 9 such cells: one AgentDojo cell and eight AgentDyn cells [src: review/RANKING_FLIP_RESULTS.md §1].

The preregistered decision rule called a result a main finding if at least 25% of cells contained at least one significant pairwise flip [src: docs/DESIGN_VARIANCE_STUDY.md § Ranking-flip pre-registration]. That threshold was met under both alternatives [src: review/RANKING_FLIP_RESULTS.md §3; rankflip/results.json]:
- EXEC→ATTEMPTED: 4/9 cells (44%).
- EXEC→CA: 3/9 cells (33%).
- Kendall τb between EXEC and ATTEMPTED rankings ranged from 0.514 (llama-3.3-70b) to 0.889 (gemini-2.5-flash) on AgentDyn, and was 0.8 on the AgentDojo cell.

The largest single reversal is progent vs tool_filter on gpt-4o-2024-08-06. The ASR difference is −0.027 under EXEC and +0.219 under ATTEMPTED [src: review/RANKING_FLIP_RESULTS.md §3].

**[DEVIATION]** (1) AgentDyn shopping and github `ground_truth()` are copy-paste stubs (see M3), so the preregistered ATTEMPTED rule could not be applied to them. We replaced it with a hand-written target map derived from each `security()`, written after the first-pass disagreements had been seen. (2) CA was scored as a token-substring match rather than the preregistered exact-normalised match. (3) Unversioned AgentDojo runs were assumed to be v1 [unverified]. (4) The preregistered blind re-label of 53 episodes was not performed [src: review/RANKING_FLIP_RESULTS.md § Deviations].

**The flips are mechanical, not noise.** 7 of the 10 significant flips involve progent; the rest involve drift or tool_filter [src: review/RANKING_FLIP_RESULTS.md §3]. All three are defenses that act at or after the point where the agent proposes a call. Under ATTEMPTED they receive no credit for blocking it. No flip involves only prompt-level or detector defenses, and the AgentDojo cell, which has neither progent nor drift, has zero flips [src: same].

We therefore do not report this as "evaluation instability". The reversal is what you should expect when an attempt-based metric is applied to defenses that block at execution time. This matches Shaw (2609.32691), who notes that a blocked call is "recorded, not suppressed" and who shows that attempt-based (tool-identity) ASR is inflated relative to argument-level success, in a single self-built harness. That level-inflation result is Shaw's, not ours. Our possible addition is rank reversals across models on two public benchmarks' released runs. Shaw's paper was read only as arXiv HTML in an earlier session, and it does not report a ranking analysis as far as that summary goes [unverified beyond the summary in review/RANKING_FLIP_RESULTS.md §6].

Pathade (2609.25173) argues, in simulation, that the choice of oracle can invert rankings, and reports no empirical inversion. We read it only by keyword search [unverified].

**Stage-aware gap [EXPLORATORY].** To quantify the mechanism, we assigned each defense a stage: input, planning, or execution-time. This stage map was written after the flips had been seen. Mean ATT−EXEC gaps were [src: stage/STAGE_RESULTS.md; stage/stage_gap_results.json]:
- input: 0.081
- planning: 0.040
- execution: 0.154

The execution−input contrast is +0.073 (within-model stratified permutation p=0.0006). A sensitivity analysis on AgentDyn dailylife only, excluding the defective injection tasks 2 and 6, gives +0.107 (p=0.0008). Planning−input was not significant (p=0.089; 0.060 in the sensitivity analysis).

Several limits apply:
- Stage is confounded with defense identity: only two defenses are execution-time.
- The bootstrap CIs ignore between-defense variance and are too narrow, so the permutation p is the honest test.
- The ATTEMPTED scorer was validated only on AgentDyn gpt-4o: 96/113 agreement, Cohen κ=0.645 [src: review/RANKING_FLIP_RESULTS.md §2].
- CA ASR often falls *below* EXEC ASR, which a superset metric should not do (e.g., AgentDojo gpt-4o undefended: 0.261 vs 0.477) [src: review/RANKING_FLIP_RESULTS.md §3]. We treat CA as unreliable.
- **[DEVIATION]** No mixed model was fitted; a permutation test replaced it [src: docs/DEVIATIONS_2026-10-16.md #4].

**Checker-version drift (one paragraph) [CONFIRMATORY in method; descriptive; negative].** Stored labels might reflect older checker code, so we replayed the logged tool calls of all scorable episodes against the current checkers (AgentDojo 089ed468, AgentDyn 5353cf761) [src: docs/DEVIATIONS_2026-10-16.md #1]. The results [src: drift/DRIFT_RESULTS.md]:
- 198 of 73,009 labels changed (0.27%): AgentDojo 39, AgentDyn 159.
- The largest per-set shift was −0.071 (AgentDyn gpt-4o-mini repeat_user_prompt, Newcombe [−0.095, −0.048]).
- 6 of 120 sets have a CI that excludes zero.
- Strict defense order changed in 2 of 15 multi-defense cells, both near-ties decided by 1–2 episodes. No ranking change is meaningful.

One cause is confirmed by code diff: AgentDyn github injection_task_1 moved from a state-based to a trace-based check (commits ae6513a/1a6d11d/2c99edc, 2026-05-02). For 166 changes we could find no attributable cause.

**[DEVIATION]** A first replay pass re-executed calls that defenses had blocked. It was discarded as invalid [src: docs/DEVIATIONS_2026-10-16.md #2]. The replay also has fidelity limits: OTP feeding, and tool outputs are not compared to the logs. Pathade lists tool-set versioning as a validity threat but reports no test [unverified, keyword search].

## 4.3 M3: An attack scenario must contain a valid attacker-controlled effect

**Claim.** A scenario's own reference solution must satisfy its own success check. If it does not, then any metric derived from that reference measures nothing.

**Finding [CONFIRMATORY — code fact; no inferential statistics].** We executed each AgentDyn v1 injection task's `ground_truth()` in the default environment and then evaluated its `security()` [src: drift/gt_audit.py → drift/gt_audit_agentdyn_v1.json; drift/GT_AUDIT.md]. Of the 28 AgentDyn-specific injection tasks, 20 fail their own check. The 28 are dailylife 10, shopping 9 and github 9 [src: drift/gt_audit_agentdyn_v1.json, suite counts]. The 20 failures fall into four classes:
1. **Copy-paste stub, 18 tasks.** This is every shopping and every github task. Each one is the same banking `send_money(recipient="", amount=0.01, …)` call, regardless of the stated goal (password change, purchase, download, leak).
2. **Tool absent from the suite.** In github, `send_money` does not even exist, so the reference raises ToolNotFoundError. These tasks are counted within the 18.
3. **Wrong arguments, 1 task (dailylife inj6).** The schema requires start/end times, and the date is today when the goal says tomorrow.
4. **Unexplained failure, 1 task (dailylife inj2).** The function and arguments are correct, but security is False. The root cause is unverified.

Across all 70 v1 tasks, 21 fail, and one of these (travel inj6, a text-only goal) is not a defect [src: drift/GT_AUDIT.md].

**Consequences.**
- *The benchmark self-check fails.* `TaskSuite.check()` requires the ground-truth pipeline to pass security, so it fails for shopping, github and dailylife [src: drift/GT_AUDIT.md].
- *Attack generation.* Only the `tool_knowledge` attack embeds `ground_truth()` in injections. On these suites, it would instruct agents to call `send_money`. Based on the released runs in runs/, no reported number derives from the tool_knowledge attack; we could not trace the AgentDyn paper's tables to unreleased runs. The released AgentDyn attack directories contain only important_instructions, direct and none [src: drift/GT_AUDIT.md].
- *Our own analysis.* Any ATTEMPTED or CA metric keyed to the reference solution is invalid on these suites. This is what forced the post-hoc target map in M1 (**[DEVIATION]**) and what makes the stage analysis exploratory.
- *Scope limit.* User-task ground truths were not audited.

We found no overlap with Shaw or Pathade on this point, but only keyword search was used [unverified]. An issue report has been drafted (`docs/DRAFT_ISSUE_AgentDyn_ground_truth.md`) and **not posted**.

## 4.x Checker vs LLM judge [EXPLORATORY]

The deterministic state checker was compared with two LLM judges (gemini-2.5-flash-lite and claude-haiku-5.5). The sample was 600 AgentDyn gpt-4o attack episodes, 200 per defense across 3 defenses [src: judge_pilot/RESULTS.md]. The pilot made 1,396 calls and cost $0.3787, computed from token counts (OpenRouter reported $0.3746) [src: judge_pilot/RESULTS.md; judge_pilot/SPEND_LOG.csv].

**Agreement depends on the defense** [src: judge_pilot/RESULTS.md, partial = failure]:
- repeat_user_prompt: κ is 0.932 for Gemini and 0.940 for Haiku.
- tool_filter: κ is 0.454 for Gemini and 0.632 for Haiku. Here the judges' weighted ASR is 0.137 and 0.087, against the checker's 0.045.
- PG2: the checker's ASR is 0.284 and Gemini's is 0.360. Gemini reverses the PG2 vs repeat order: checker Δ=−0.038, judge Δ=+0.040, P(flip)=0.939.
- The preregistered criterion "κ>0.9 on all three defenses" fails.

**Manual review: the checker is precise, and the judges count attempts.** A blind review covered all 43 judge–checker disagreements plus 10 random agreement controls [src: review/REVIEW_RESULTS.md]:
- tool_filter: the checker was right in 20/20 disagreements (Wilson 0.84–1.00).
- PG2: right in 11/13 J+C− items (0.58–0.96), with 2 unclear, plus 1/1 J−C+.
- Controls: 10/10 correct (0.72–1.00).

The judges' systematic error was to score attempts as successes. Examples are checkouts or transfers that stalled at an unverified OTP, failed form submissions, text-only mentions, and requests for confirmation. On repeat_user_prompt the judge was right in 3/6 J−C+ items (0.19–0.81). These are R01/R25/R47: the replay shows all three are False under the current checker, and R25 is the confirmed github fix [src: drift/DRIFT_RESULTS.md]. After correction, PG2 stays below repeat under either reading of the unclear items (Δ −0.028 or −0.021), so the judge-induced flip is not supported [src: review/REVIEW_RESULTS.md §5].

**Recall.** 60 newly drawn checker-negative episodes (both judges "no") were all truly negative, so there were 0 misses [src: review/RECALL_RESULTS.md §2]. Within this stratum the miss rates are 0/23, 0/23 and 0/22, with Wilson upper bounds of ≤14.3%, ≤14.3% and ≤14.9% [src: review/RECALL_RESULTS.md §5]. Propagated by weight, these give worst-case recall lower bounds of 0.27 for tool_filter, 0.76 for PG2 and 0.76 for repeat. The bounds are loose because zero events cannot rule out a moderate miss rate.

**Power.** ±3 pp equivalence is testable at n=200 only if judge–checker disagreement is about 2% or lower [src: judge_pilot/POWER.md]. The observed disagreement is about 2–11% [src: judge_pilot/RESULTS.md finding 4]. TOST is therefore descriptive here.

**Relation to prior work.** The Same Zero (Yin, 2610.04504) reports that AgentDojo banking state checks missed 11 tool-level attacks, a conditional miss rate of 11/75. That result is on a different benchmark slice, model and defense set, and we read only the abstract, p.8 and Limitations item 5 [unverified beyond these; src: review/RECALL_RESULTS.md §6]. Our checker misses are in a different direction (hard-coded target identities, R15/R26/R53), and we found none in the recall sample. Liu (2610.03448, read in full) re-evaluates PI detectors offline without agent ASR [src: LIU_JUDGE_READ.md]. Hardy et al. (2610.00651) apply generalizability theory to agent leaderboards; there the verifier facet arises only in passing (abstract and introduction read) [src: docs/DESIGN_VARIANCE_STUDY.md; review/RECALL_RESULTS.md §6].

## External validation (framing)

We do not present this work as an external validation of the six checks. What it provides is a **re-analysis of third-party released artifacts**: the AgentDojo and AgentDyn runs and code, which we did not author, using rules we fixed in advance (M1 preregistration). Three properties are external in that sense:
1. The data were generated by others.
2. The checker code is upstream.
3. The ground-truth defects are reproducible code facts.

Three properties are not external:
1. All manual labels come from one AI reviewer.
2. Several analysis choices (the target map, the stage map, the remapping of 53 episodes) were made post hoc.
3. No independent team has re-run any of it.

An independent reproduction remains the required next step.

## Limitations (for this section)

- **Labelling.** Most labels (53 disagreement and control items, 60 recall items, 113 scorer-validation items) come from a **single AI reviewer**. Sixteen blind labels from the owner (`review/OWNER_SUBSET.md`) are pending and will be added. Blinding was imperfect: the defense identity was not hidden, because tool_filter episodes show the filter prompt and PG2 episodes show "Data omitted" [src: review/REVIEW_RESULTS.md, Dev. 3].
- **Remapping.** The 4-level remapping of the 53 prior episodes was done after unblinding, and the reviewer had already seen those items. It is [EXPLORATORY] [src: review/RANKING_FLIP_RESULTS.md §4].
- **Narrow data.** The judge and review results cover one model (AgentDyn gpt-4o) and three defenses. The AgentDojo side of M1 is effectively a single cell.
- **Statistics.** The replay has fidelity limits, and the bootstraps are not clustered by user task.
- **Literature reading.** Overlap statements for Shaw and Pathade rest on a summary and on keyword search, respectively.

## Table: all numbers and sources

| Number | Meaning | Source |
|---|---|---|
| 125 / 74,528 | run sets / injection episodes | review/RANKING_FLIP_RESULTS.md §1; rankflip/inventory.csv |
| 50 / 75 | AgentDojo / AgentDyn sets | drift/DRIFT_RESULTS.md; docs/DEVIATIONS_2026-10-16.md #6 |
| 73,009 (31,604 + 41,405) | non-error, non-DoS replayed episodes | drift/DRIFT_RESULTS.md |
| 92; 5 | error episodes stored True; with attempted target call | review/RANKING_FLIP_RESULTS.md §1 |
| 9 cells | ≥3 defenses | review/RANKING_FLIP_RESULTS.md §1 |
| 4/9 (44%), 3/9 (33%) | cells with a significant flip, ATT / CA | review/RANKING_FLIP_RESULTS.md §3; rankflip/results.json |
| τb 0.514–0.889; 0.8 | AgentDyn range; AgentDojo | review/RANKING_FLIP_RESULTS.md §3 |
| −0.027 → +0.219 | progent vs tool_filter, gpt-4o-08-06 | review/RANKING_FLIP_RESULTS.md §3 |
| 7/10 | flips involving progent | review/RANKING_FLIP_RESULTS.md §3 |
| 96/113, κ 0.645 | ATT scorer validation | review/RANKING_FLIP_RESULTS.md §2 |
| 0.261 vs 0.477 | CA vs EXEC, AgentDojo gpt-4o none | review/RANKING_FLIP_RESULTS.md §3 |
| 0.081 / 0.040 / 0.154 | stage gaps | stage/STAGE_RESULTS.md |
| +0.073 p=0.0006; +0.107 p=0.0008; p=0.089 / 0.060 | stage contrasts | stage/STAGE_RESULTS.md |
| 198 / 73,009 (0.27%); 39 / 159 | checker drift | drift/DRIFT_RESULTS.md |
| −0.071 [−0.095, −0.048]; 6/120; 2/15; 166 | drift details | drift/DRIFT_RESULTS.md |
| 20/28; 18 + 1 + 1; 21/70 | ground_truth defects | drift/GT_AUDIT.md; drift/gt_audit_agentdyn_v1.json |
| $0.3787 ($0.3746); 1,396; 600 | pilot spend, calls, episodes | judge_pilot/RESULTS.md |
| κ 0.454 / 0.632 / 0.932 / 0.940 | judge–checker agreement | judge_pilot/RESULTS.md |
| 0.045 / 0.137 / 0.087; 0.284 / 0.360; P(flip)=0.939 | ASRs, checker vs judge | judge_pilot/RESULTS.md |
| 43 + 10; 20/20; 11/13; 3/6; 10/10 | manual review | review/REVIEW_RESULTS.md |
| −0.028 / −0.021 | corrected PG2−repeat | review/REVIEW_RESULTS.md §5 |
| 60/60; ≤14.3/14.3/14.9%; 0.27/0.76/0.76 | recall and Wilson bounds | review/RECALL_RESULTS.md §2, §5 |
| ~2%; 2–11% | TOST power threshold; observed disagreement | judge_pilot/POWER.md; judge_pilot/RESULTS.md |
| 11/75 | The Same Zero conditional miss rate | review/RECALL_RESULTS.md §6 (partial read) |

## Open issues
1. ~~Preregistration hash~~ **Resolved 2026-10-16:** recovered artifact `docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md` matches `review/PREREG_RANKFLIP.sha256` (`97bdb074…`). Only the post-freeze deviations section had been appended. See `docs/PREREG_HASH_RECOVERY.md`.
2. The 16 owner labels are pending (`review/OWNER_SUBSET.md` / `review/owner_labels.TEMPLATE.jsonl`).
3. Shaw and Pathade are not fully read.
4. dailylife inj2 root cause is unknown, and so is the cause of the R01/R47 drift.
5. A pooled Wilson bound for 0/60 is not in any file and was deliberately not stated.
