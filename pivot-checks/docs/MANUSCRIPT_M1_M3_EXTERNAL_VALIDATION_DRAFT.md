# DRAFT rewrite: §4.1 (M1), §4.3 (M3), checker vs LLM judge, and external validation framing

*Revision v2, 2026-10-16 12:30 Tehran (previous version saved as `MANUSCRIPT_M1_M3_EXTERNAL_VALIDATION_DRAFT_v1.md`). Draft written 2026-10-16 (Tehran). It is meant to replace the corresponding parts of `MANUSCRIPT_DRAFT_v1.md`; that file was not edited. Every number carries an inline source tag. Tags are paths relative to `/workspace/pivot-checks/`. No new API/LLM calls were made for this draft.*

**Labels used below.** [CONFIRMATORY — preregistered] means the analysis follows a protocol written before the data were scored. [EXPLORATORY] means the analysis was designed or remapped after seeing data. [DEVIATION] marks a departure from a written protocol.

**Preregistration records** [src: docs/DESIGN_VARIANCE_STUDY.md; review/*.sha256]:
- Ranking-flip preregistration: `docs/DESIGN_VARIANCE_STUDY.md` § "Ranking-flip pre-registration", added 2026-10-15 22:40 Tehran. The recorded sha256 of the file at that time is `97bdb074…61e63c1` (`review/PREREG_RANKFLIP.sha256`).
- Manual disagreement review protocol: same file, added ~21:29. The frozen labels have sha256 `897c498e…e620c` (`review/LABELS_FROZEN.sha256`).
- Recall review protocol: same file, added 22:16. The frozen labels have sha256 `7b9927ad…f9335` (`review/RECALL_LABELS_FROZEN.sha256`).
- The file has been appended to since then (deviation logs), and its current hash differs (`dc596e83…`). **Hash check (re-run 2026-10-16 12:2x Tehran):** `sha256sum docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md` = `97bdb074ae8911cab5ffbad1ed700b6895efff67c3080432c672c660361e63c1`, byte-exact match to `review/PREREG_RANKFLIP.sha256` [src: review/PREREG_RANKFLIP.sha256; docs/PREREG_HASH_RECOVERY.md]. The confirmatory label below therefore stands.

---

## 4.1 M1: Score what reached the executor, not what was proposed or attempted

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

**Checker-version drift (one paragraph) [CONFIRMATORY in method; descriptive; negative].** Stored labels might reflect older checker code, so we replayed the logged tool calls of all scorable episodes against the current checkers (AgentDojo 089ed468, AgentDyn 5353cf761) [src: docs/DEVIATIONS_2026-10-16.md #1]. The results [src: drift/DRIFT_RESULTS.md]:
- 198 of 73,009 labels changed (0.27%): AgentDojo 39, AgentDyn 159.
- The largest per-set shift was −0.071 (AgentDyn gpt-4o-mini repeat_user_prompt, Newcombe [−0.095, −0.048]).
- 6 of 120 sets have a CI that excludes zero.
- Strict defense order changed in 2 of 15 multi-defense cells, both near-ties decided by 1–2 episodes. No ranking change is meaningful.

One cause is confirmed by code diff: AgentDyn github injection_task_1 moved from a state-based to a trace-based check (commits ae6513a/1a6d11d/2c99edc, 2026-05-02). For 166 changes we could find no attributable cause.

**[DEVIATION]** A first replay pass re-executed calls that defenses had blocked. It was discarded as invalid [src: docs/DEVIATIONS_2026-10-16.md #2]. The replay also has fidelity limits: OTP feeding, and tool outputs are not compared to the logs. Pathade et al. list environment and tool-set versioning and model version drift as sources of incomparability they do not measure (§III, p. 3) [src: review/RELATED_FULLREAD.md].

## 4.3 M3: An attack scenario must contain a valid attacker-controlled effect

**Claim.** A scenario's own reference solution must satisfy its own success check. If it does not, then any metric derived from that reference measures nothing.

**Finding [CONFIRMATORY — code fact; no inferential statistics].** We executed each AgentDyn v1 injection task's `ground_truth()` in the default environment and then evaluated its `security()` [src: drift/gt_audit.py → drift/gt_audit_agentdyn_v1.json; drift/GT_AUDIT.md]. Of the 28 AgentDyn-specific injection tasks, 20 fail their own check. The 28 are dailylife 10, shopping 9 and github 9 [src: drift/gt_audit_agentdyn_v1.json, suite counts]. The 20 failures fall into four classes:
1. **`ground_truth()` does not reflect the injection goal, 18 tasks.** This is every shopping and every github task. Each one returns the same banking `send_money(recipient="", amount=0.01, …)` call, regardless of the stated goal (password change, purchase, download, leak).
2. **Tool absent from the suite.** In github, `send_money` does not even exist, so the reference raises ToolNotFoundError. These tasks are counted within the 18.
3. **Wrong arguments, 1 task (dailylife inj6).** The schema requires start/end times, and the date is today when the goal says tomorrow.
4. **Unexplained failure, 1 task (dailylife inj2).** The function and arguments are correct, but security is False. The root cause is unverified.

Across all 70 v1 tasks, 21 fail, and one of these (travel inj6, a text-only goal) is not a defect [src: drift/GT_AUDIT.md].

**Consequences (scope).** The defect affects three things: the benchmark self-check, the tool_knowledge attack, and attempt-based metrics keyed to `ground_truth()`. It does **not** affect the reported state-based ASR, which is computed by `security()` on the post-run environment and does not use `ground_truth()`.
- *The benchmark self-check fails.* `TaskSuite.check()` requires the ground-truth pipeline to pass security, so it fails for shopping, github and dailylife [src: drift/GT_AUDIT.md].
- *Attack generation.* Only the `tool_knowledge` attack embeds `ground_truth()` in injections. On these suites, it would instruct agents to call `send_money`. Based on the released runs in runs/, no reported number derives from the tool_knowledge attack; we could not trace the AgentDyn paper's tables to unreleased runs. The released AgentDyn attack directories contain only important_instructions, direct and none [src: drift/GT_AUDIT.md].
- *Our own analysis.* Any ATTEMPTED or CA metric keyed to the reference solution is invalid on these suites. This is what forced the post-hoc target map in M1 (**[DEVIATION]**) and what makes the stage analysis exploratory.
- *Scope limit.* User-task ground truths were not audited.

Neither paper audits a benchmark's reference solutions. Shaw states the general principle that a scenario's success condition must be able to fire on the attacker's action, and adds pre-flight checks that reject attacker goals naming a tool absent from the registry (§V-A, §V-D, p. 4). That overlaps our class 2 in concept; the AgentDyn-specific finding is ours. Pathade et al. do not address it [src: review/RELATED_FULLREAD.md]. An issue report has been drafted (`docs/DRAFT_ISSUE_AgentDyn_ground_truth.md`) and **not posted**.

**Plan: report to AgentDyn maintainers before any preprint.** The issue will be filed with the AgentDyn maintainers *before* any preprint or public posting of this section, and only after the owner explicitly approves the final issue text. The manuscript will wait for (or a fixed period after) their reply.

**Maintainers' response [PLACEHOLDER — not yet filed].** Date filed: —. Link: —. Response summary: —. Changes to this section resulting from it: —.

## 4.x Checker vs LLM judge [EXPLORATORY]

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
- **Analyst = labeller.** The same analyst (an AI agent) who designed the analyses, wrote the preregistrations, the target map and the stage map also produced the manual labels. This is a source of possible bias that blinding only partly addresses.
- **CA metric.** EXEC→CA results (confirmatory subset: 2/9 cells, 2 flips / 290 pairs; full data: 3/9 cells, 4 flips / 299 pairs) [src: review/results_conf.json; rankflip/results.json] are not preregistered as implemented (substring vs exact-normalised match) and are unreliable (CA < EXEC in places); they support no claim.
- **Remapping.** The 4-level remapping of the 53 prior episodes was done after unblinding, and the reviewer had already seen those items. It is [EXPLORATORY] [src: review/RANKING_FLIP_RESULTS.md §4].
- **Narrow data.** The judge and review results cover one model (AgentDyn gpt-4o) and three defenses. The AgentDojo side of M1 is effectively a single cell.
- **Statistics.** The replay has fidelity limits, and the bootstraps are not clustered by user task.
- **Literature reading.** Shaw and Pathade et al. were read in full (PDFs in `papers/`; review/RELATED_FULLREAD.md). No quotation is used in this section.

## Table: all numbers and sources

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
3. ~~Shaw and Pathade are not fully read.~~ **Resolved 2026-10-16:** full-text read in review/RELATED_FULLREAD.md.
4. AgentDyn maintainer issue: awaiting owner approval to file; response placeholder in §4.3.
5. dailylife inj2 root cause is unknown, and so is the cause of the R01/R47 drift.
6. A pooled Wilson bound for 0/60 is not in any file and was deliberately not stated.
