### 5.0 Primary attempt scorer: ATT-ARG vs name-match [EXPLORATORY; procedure hash-locked]

Name-match ATT is tool-identity scoring, the defect Shaw names D2 (§IV, §VII-A). It is kept below (§5.1–§5.4) as the preregistered reference. The primary attempt scorer from this revision is ATT-ARG (§3). Both scorers were rerun on the same reduced task set, from which the 27 excluded task-versions are removed; the rest of the pipeline (episode bootstrap 2000 reps, seed 20261015; task-clustered paired bootstrap with Holm; LODO) is unchanged [src: attarg/summary.txt; attarg/analyses_log.txt; attarg/out/]. Cells with ≥1 flip / flips / pairs:

| Analysis | ATT-ARG, full data | Name-match, full data | ATT-ARG, subset [DEVIATION] | Name-match, subset |
|---|---|---|---|---|
| Preregistered rule (episode bootstrap) | 3/9 / 5 / 299 | 4/9 / 6 / 299 | 2/9 / 4 / 290 | 2/9 / 4 / 290 |
| Task-clustered + Holm | 1/9 / 1 / 299 | 1/9 / 1 / 299 | 2/9 / 3 / 290 | 2/9 / 4 / 290 |
| Without progent (LODO) | 0/9 / 0 / 235 | 1/9 / 1 / 235 | 0/9 / 0 / 227 | 1/9 / 1 / 227 |
| Without tool_filter (LODO) | 2/9 / 3 / 238 | 3/9 / 4 / 238 | 2/9 / 2 / 230 | 1/9 / 1 / 230 |

ATT-ARG flips (full data): gpt-4o-2024-08-06 progent vs tool_filter; gpt-4o-mini progent vs prompt_guard_2_detector and progent vs repeat_user_prompt; llama-3.3-70b drift vs progent and progent vs tool_filter. Subset: gpt-4o-2024-08-06 progent vs spotlighting_with_delimiting and progent vs tool_filter; llama-3.3-70b drift vs progent and progent vs tool_filter. **Every ATT-ARG flip involves progent; none involves drift without progent**, and the name-match qwen3-235b drift flips disappear. Per-cell ATT-ARG τb (full data): AgentDojo 1.0 [0.8, 1.0]; gemini-2.5-flash 0.889; gemini-2.5-pro 1.0; gpt-4o-2024-08-06 0.817; gpt-4o-mini 0.911; gpt-5-mini 0.642 [−0.21, 0.734]; gpt-5.1 0.808; llama-3.3-70b 0.648 [0.5, 0.778]; qwen3-235b 0.944. ATT-ARG positives are a subset of name-match positives [src: attarg/crosstab.txt].

**Validation [AI LABELS].** We drew a new blind sample: AgentDyn important_instructions episodes from the flip cells, excluding all earlier samples, 10 per defense × ATT-ARG label for progent, drift, tool_filter and repeat_user_prompt (n = 80, seed 20261017). The same AI assistant labelled them from the goal and the proposed calls only, without defense or labels; the labels were hash-locked (sha256 `da667c0d…`) before comparison [src: attarg/validation/labels_AI.sha256; attarg/validation/comparison.json]. **These are AI labels, not human labels.**

| Defense | ATT-ARG agreement | κ | ATT-ARG precision | Name-match agreement | κ |
|---|---|---|---|---|---|
| progent | 20/20 | 1.0 | 10/10 | 20/20 | 1.0 |
| drift | 20/20 | 1.0 | 10/10 | 20/20 | 1.0 |
| tool_filter | 20/20 | 1.0 | 10/10 | 19/20 | 0.9 |
| repeat_user_prompt | 18/20 | 0.8 | 10/10 | 17/20 | 0.694 |
| All | 78/80 (97.5%, Wilson 0.913–0.993) | 0.95 | 40/40 (0.912–1.0) | 76/80 | 0.9 |

Both ATT-ARG disagreements are false negatives: a browsing step to the attacker's site, which is not a target function, and a call to a non-existent tool. The sample is stratified by the ATT-ARG label, which favours ATT-ARG in the comparison. A 40-episode human packet (key hashed, `human_packet/KEY_SEPARATE.sha256`) is prepared but not yet labelled.

