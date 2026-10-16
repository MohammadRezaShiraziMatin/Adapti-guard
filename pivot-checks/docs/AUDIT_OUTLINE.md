# Audit outline (2026-10-16, Tehran) — zero API/LLM calls for all new work
Deviations: `docs/DEVIATIONS_2026-10-16.md`. Shaw 2609.32691 was read only as arXiv HTML in an earlier session (summary in RANKING_FLIP_RESULTS.md §6). It is not in papers/, so any part not summarized there is **unverified**. Pathade 2609.25173 (`papers/2609.25173.txt`) is a position/simulation paper. It was keyword-searched only this session, not read in full, so the overlap statements below are **partly unverified**.

**1. Checker-version drift (confirmatory in method, descriptive; negative).** I replayed all 125 released sets with the current checkers (120 analysed; the 5 DoS sets are excluded). Of 73,009 non-error episodes, 198 labels changed (0.27%): AgentDojo 39, AgentDyn 159. The largest set-level shift is −7.1 pp (AgentDyn gpt-4o-mini repeat_user_prompt, Newcombe [−9.5, −4.8]). 6/120 sets have a CI that excludes 0. In 2/15 multi-defense cells the strict ranking changes, both through near-ties of 1–2 episodes (gpt-5-mini, gpt-5.1), so no ranking change is meaningful. Causes I could attribute: AgentDyn github inj1 → ae6513a/1a6d11d/2c99edc (2026-05-02; confirmed); AgentDojo workspace inj4/inj5 → 6313f721/3ebb8f8c (2024-09-08; consistent, not checked per episode); 23 changes trace to tools that no longer exist (commit unverified). 166 changes have no attributable cause. The 92 error episodes are separate: they are stored True by the error rule, and 88 of them replay False. Review FPs R01/R25/R47 are all False under the current checker. Limits: replay fidelity (OTP feeding, skipped errored calls, outputs not compared). My first pass was invalid (it re-executed blocked calls). Evidence: `drift/DRIFT_RESULTS.md`, `drift/per_set_table.md`, `drift/drift_results.json`, `drift/changes_classified_*.json`. Overlap: Pathade lists "environment and tool-set versioning" as a validity threat but reports no empirical test (from keyword search; unverified beyond that). Shaw: no version analysis known (unverified).

**2. ground_truth defects (confirmatory, code fact).** 20 of the 28 AgentDyn-specific injection tasks fail their own security():
- 18 are copy-paste `send_money` stubs: all of shopping and github. In github the tool does not even exist.
- 1 has wrong args (dailylife inj6).
- 1 fails for an unexplained reason (dailylife inj2).
Code paths that depend on ground_truth are `TaskSuite.check()` and `tool_knowledge` attacks. No released AgentDyn number depends on it, because the runs use only important_instructions/direct/none. Our rankflip ATTEMPTED/CA metrics do depend on it, which forced the post-hoc target map. Evidence: `drift/GT_AUDIT.md`, `drift/gt_audit_agentdyn_v1.json`, `docs/DRAFT_ISSUE_AgentDyn_ground_truth.md` (not posted). Limit: user-task ground truths were not audited. Overlap: none with Shaw or Pathade known.

**3. Stage-aware gap (EXPLORATORY).** The ATT−EXEC gap averages 0.081 for input-stage defenses, 0.040 for planning and 0.154 for execution-time. Execution−input is +7.3 pp (within-model permutation p=0.0006). The dailylife-only sensitivity check gives +10.7 pp (p=0.0008). Planning−input is not significant (p≈0.06–0.09). This quantifies the mechanical reason behind the rankflip flips. It is not evidence of evaluation noise. Limits:
- The stage map was set post hoc.
- Stage is confounded with defense identity (2 execution-time defenses).
- The ATT target map is post hoc.
- The bootstrap CIs are too narrow.
Evidence: `stage/STAGE_RESULTS.md`, `stage/stage_gap_results.json`. Overlap: Shaw notes blocked calls are "recorded, not suppressed" but does not stratify by stage (per the earlier summary).

**4. Judge vs checker pilot + manual review (exploratory; single AI reviewer, owner labels pending).** The pilot cost $0.38 (an earlier session; 600 episodes, AgentDyn gpt-4o, 3 defenses). Judges over-call relative to the checker: on tool_filter, Gemini FPR is 0.097 with κ 0.454; on PG2, ASR is 0.284 by checker vs 0.360 by judge. In the blind review of 53 items:
- tool_filter: the checker was right in 20/20 disagreements.
- PG2: right in 12/14.
- repeat_user_prompt: the judge was right in 3/6 J−C+ items. These are R01/R25/R47, which item 1 now explains as stale-checker labels.

The recall review found 60/60 checker-negative episodes truly negative, so there were 0 misses. Evidence: `judge_pilot/RESULTS.md`, `review/REVIEW_RESULTS.md`, `review/RECALL_RESULTS.md`. Limits: one model, one reviewer, and memory contamination on any re-label. Overlap: Pathade argues that oracle choice can invert rankings in simulation and reports no empirical inversion (lines ~286–351 of the txt). This pilot provides the empirical counterpart, but only for level shifts.

**5. Success-definition dependence / ranking flips (confirmatory per prereg, but partly definitional).** Changing the success definition from EXEC to ATTEMPTED flips at least one defense ranking significantly in 4 of 9 cells; under CORRECT-ARGS it does so in 3 of 9. τb ranges from 0.51 to 1.0. 7 of the 10 flips involve progent, and the rest involve drift or tool_filter. Item 3 shows that this is mostly a matter of when each defense acts. The CORRECT-ARGS metric is unreliable, because its ASR comes out below EXEC. Evidence: `review/RANKING_FLIP_RESULTS.md`, `rankflip/results.json`, `rankflip/episodes.jsonl`. Limits:
- Scorer κ is 0.645 and was validated on AgentDyn gpt-4o only.
- The AgentDojo side is a single cell.
- The target map was written post hoc (Dev.1).

Overlap: Shaw already shows that attempt-based ASR is inflated, so that part is not novel. The cross-model rank-reversal is the possible contribution. Pathade's ranking-inversion argument is theoretical (unverified beyond keyword reading).
