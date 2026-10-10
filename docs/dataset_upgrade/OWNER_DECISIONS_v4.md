# Attack pack v4: owner decisions required

Each decision blocks a named stage. My recommendation is given where I have one. Nothing below has been decided; the work so far assumes only what is written in `SCHEMA_v4.md` and `PLAN_AND_COVERAGE_v4.md`. Decisions are listed by the stage they block, not by number.

## Required before Stage 3 (drafting)

**D1. Schema extensions.** Accept the content fields (`turns`, `untrusted_content`, `pair_id`, `canary`) and the provenance fields (`redistributable`, `source_url`, `source_version`, `retrieved_at`), which the protocol's field list does not include. Without them a record cannot hold its own input or name its counterpart.
*Recommendation:* accept.

**D11. Ratify `injection_span` and the pointer grammar (new).** The remediation added `injection_span` (the exact injection or decoy text) and changed `injection_location` from free text (for example `email body, paragraph 2`) to a pointer (`turns[<i>]` or `untrusted_content`). This is required to verify, in code, that the injection or decoy is actually present, which the audit found missing (including for `user_turn`). It is a change to the protocol's field set and to the documented example.
*Needed:* accept the field and grammar, or name an alternative that still makes the location checkable. If you choose an alternative, the evidence rule in `SCHEMA_v4.md` section 2 must be rewritten to match.
*Recommendation:* accept.

**D2. Reviewers and author split.** The protocol requires two independent human reviewers for at least 20% of examples, and asks that the attack author and defense evaluator differ. **I do not know whether any reviewers are available.** Until you name them, human review is recorded as "not conducted".
*Needed:* names or pseudonymous IDs of two reviewers and their availability window. Confirm whether you will write attacks, or whether a separate author will.

**D5. Hard-negative labelling and counterpart allocation.** Existing hard negatives are labelled `benign` (verified: 40 in `layer_a_v3`, 25 in `vnext_confirm_v1`). The protocol asks for `hard_negative`. Two questions: (a) should v4 use the new label for counterparts; (b) what proportion of counterparts should be hard negatives, and how should it be distributed across families? Relabelling an existing frozen file is not allowed; a derived version is. **The proportion is not chosen.** Earlier drafts proposed about one third; that figure is withdrawn and is not encoded in the generator (`PLAN_AND_COVERAGE_v4.md` section 2.1).
*Recommendation:* (a) new label in v4, leave old files as they are; (b) choose a proportion explicitly and encode it in the generator with a divisibility rule.

**D6. Category, channel and turn constraints.** `SCHEMA_v4.md` section 3 fixes which channels and turn types each category may use (for example, multi-turn is user-turn-only for persistence and tool/doc/email/web for injection; jailbreak roleplay is user-turn-only). These are design choices.
*Needed:* approve or change the table. Changing it means editing `CATEGORY_RULES` and `FAMILY_CATEGORY` and the document together.

**D13. Mock-tool restriction (new).** The validator does not check that tools are mock tools; it checks that they are declared and that `tool_call` refers to a declared tool. The audit asked for enforcement or narrowed documentation. The documentation has been narrowed.
*Needed:* decide whether a fixed mock-tool registry (a list of permitted tool names and argument schemas) should be added. If yes, provide the list; it is a design decision about which tools the threat model needs.
*Recommendation:* narrow now (done); add a registry only when the tool set is fixed.

## Required before Stage 5 (freeze)

**D4. Minimum multi-turn sample size.** Protocol target: at least 50 attacks per multi-turn family, or a justified smaller number. **The exact minimum for 80% power on the primary effect (0.50 vs 0.25, two-sided pooled z-test, α = 0.05, equal n) is 59 per arm, not 58.** The design target of 60 gives power 0.818. The floor of 50 gives power 0.745 for that effect.
*Decision needed:* 60 per family (proposed; meets the threshold with margin), or 50 with the stated power of 0.745. A calculation shows only the primary effect; secondary effects need more (for example 94 per arm for 0.50 vs 0.30). The current multi-turn data are 26 records on one pilot model, so the existing data cannot be used to size this.

**D12. Multiplicity (new).** No multiplicity adjustment is applied across 12 families and 28 primary cells, and the power calculation assumes one comparison. The family-wise error rate is therefore not controlled.
*Needed:* decide which comparisons are primary and whether to correct (for example Holm or Bonferroni over the pre-specified primary set), or to report all comparisons as exploratory. Also decide whether the design is paired (same attacks in each arm); the current calculation assumes independent arms.

**D7. Existing data routing.** `eval_v1` (770 attack-only rows) lacks `label`, `success_condition`, `tool_call`, `pair_id` and `injection_span`, and has no benign rows. Verified: none of its 770 rows is accepted by the v4 validator. Option A: freeze v4 as a new dataset and leave `eval_v1` as legacy. Option B: publish a versioned, derived `eval_v1_v4view` that adds labels and counterparts, which is a new artifact and needs its own validation. Option C: exclude `eval_v1` from analyses that need v4 fields.
*Recommendation:* C for v4 analyses; A for the paper's dataset section.

**D8. `injection_location` in `eval_v1`.** Empty in all 770 rows. Options: (a) a separately versioned derived dataset that fills it (requires annotation, so it needs reviewers, D2); (b) exclude `eval_v1` from any analysis that requires the field.
*Recommendation:* (b) now; (a) only if D2 is answered.

**D3. `attackset_hard_v1` status.** The repository contains only `datasets/attackset_hard_v1/FREEZE_RECORD.json` (verified). Its MANIFEST and item files are absent, so the claims of 238 human-authored LLMail-Inject items and 69 generated items cannot be verified. The record names `microsoft/llmail-inject-challenge` under MIT.
*Options:* (a) restore the MANIFEST and items from the original source and verify the SHA-256 `786505…`; (b) mark the set as unverifiable and exclude it from v4; (c) use LLMail-Inject as a new, separately recorded source with its own licence and retrieval date.
*Recommendation:* (c) with a fresh retrieval, and treat `attackset_hard_v1` as unverified (legacy claim L9).

**D9. Legacy claims.** L1–L15 in `docs/baseline/LEGACY_CLAIMS.md` remain unapproved. Approving any of them, in particular L9 (`attackset_hard_v1` counts) and L12 (strong-model results, which do not exist), requires your written approval for each claim and the verification step listed there. Nothing in this upgrade relies on them.

**D10. External-source redistribution.** For each of garak, InjecAgent, TrustLLM, AgentDojo and LLMail-Inject, decide whether text may be redistributed under the source's terms. If not, the record carries identifiers and a retrieval script only (`redistributable = false`). I have not verified any source's licence or terms. `datasets/external_samples/` contains two JSON files and no licence file (verified).

## Information I need

- The repository's MIT licence (`LICENSE`) is stated as the intended licence for self-authored content. Confirm.
- Whether the working branch `claude/adoring-turing-4z5aol` should be merged, or kept as a review branch. No pull request has been opened, and nothing has been pushed by this remediation.
