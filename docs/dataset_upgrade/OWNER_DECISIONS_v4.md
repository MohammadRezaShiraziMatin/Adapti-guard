# Attack pack v4: owner decisions required

Each decision blocks a named stage. My recommendation is given where I have one. Nothing below has been decided; the work so far assumes only what is written in `SCHEMA_v4.md` and `PLAN_AND_COVERAGE_v4.md`.

## Required before Stage 3 (drafting)

**D1. Schema extensions.** Accept the four content fields (`turns`, `untrusted_content`, `pair_id`, `canary`) and the provenance fields (`redistributable`, `source_url`, `source_version`, `retrieved_at`), which the protocol's field list does not include. Without them a record cannot hold its own input or name its counterpart.
*Recommendation:* accept. Alternative: put content in a separate `prompt.md` per record, which is harder to validate and hash.

**D2. Reviewers and author split.** The protocol requires two independent human reviewers for at least 20% of examples, and asks that the attack author and defense evaluator differ. **I do not know whether any reviewers are available.** Until you name them, human review is recorded as "not conducted".
*Needed:* names or pseudonymous IDs of two reviewers, and their availability window. Confirm whether you (the owner) will write attacks, or whether a separate author will.

**D3. `attackset_hard_v1` status.** The repository contains only `datasets/attackset_hard_v1/FREEZE_RECORD.json` (verified). Its MANIFEST and item files are absent, so the claims of 238 human-authored LLMail-Inject items and 69 generated items cannot be verified. The record also names `microsoft/llmail-inject-challenge` under MIT.
*Options:* (a) restore the MANIFEST and items from the original source and verify the SHA-256 `786505…`; (b) mark the set as unverifiable and exclude it from v4; (c) use LLMail-Inject as a new, separately recorded source with its own licence and retrieval date.
*Recommendation:* (c) with a fresh retrieval, and treat `attackset_hard_v1` as unverified (legacy claim L9).

**D5. Hard-negative labelling.** Existing hard negatives are labelled `benign` (verified: 40 in `layer_a_v3`, 25 in `vnext_confirm_v1`). The protocol asks for `hard_negative`. Should v4 use the new label for counterparts, and should existing records be relabelled in a derived dataset? Relabelling an existing frozen file is not allowed; a derived version is.
*Recommendation:* new label in v4; leave the old files as they are.

**D6. Category, channel and turn constraints.** `SCHEMA_v4.md` section 3 fixes which channels and turn types each category may use (for example, multi-turn is user-turn-only for persistence and tool/doc/email/web for injection; jailbreak roleplay is user-turn-only). These are design choices.
*Needed:* approve or change the table. Changing it means editing `CATEGORY_RULES` and both documents.

## Required before Stage 5 (freeze)

**D4. Minimum multi-turn sample size.** Protocol target: at least 50 attacks per multi-turn family, or a justified smaller number. The power table gives 58 per arm for 80% power at 0.50 vs 0.25, and 60 is the design target I propose. The floor of 50 gives 74% power for that effect.
*Decision needed:* 60 per family (proposed), or 50 with the disclosed power of 0.74. Note that the current multi-turn data are 26 records, all on one pilot model, so the existing data cannot be used to size this.

**D7. Existing data routing.** `eval_v1` (770 attack-only rows) lacks `label`, `success_condition`, `tool_call` and `pair_id`, and has no benign rows. Option A: freeze v4 as a new dataset and leave `eval_v1` as legacy. Option B: publish a versioned, derived `eval_v1_v4view` that adds labels and counterparts, which is a new artifact. Option C: exclude `eval_v1` from analyses that need v4 fields.
*Recommendation:* C for v4 analyses; A for the paper's dataset section.

**D8. `injection_location` in `eval_v1`.** Empty in all 770 rows. Options: (a) a separately versioned derived dataset that fills it (requires annotation, so it needs reviewers, D2); (b) exclude `eval_v1` from any analysis that requires the field.
*Recommendation:* (b) now; (a) only if D2 is answered.

**D9. Legacy claims.** L1–L15 in `docs/baseline/LEGACY_CLAIMS.md` remain unapproved. Approving any of them, in particular L9 (`attackset_hard_v1` counts) and L12 (strong-model results, which do not exist), requires your written approval for each claim and the verification step listed there. Nothing in this upgrade relies on them.

**D10. External-source redistribution.** For each of garak, InjecAgent, TrustLLM, AgentDojo and LLMail-Inject, decide whether text may be redistributed under the source's terms. If not, the record carries identifiers and a retrieval script only (`redistributable = false`). I have not verified any source's licence or terms; the repository has no licence file for `datasets/external_samples/` (verified).

## Information I need to verify before deciding

- The repository's MIT licence (`LICENSE`) applies to self-authored content. Confirm that is the intended licence for v4.
- Whether the owner wants the working branch `claude/adoring-turing-4z5aol` merged, or kept as a review branch. No pull request has been opened.
