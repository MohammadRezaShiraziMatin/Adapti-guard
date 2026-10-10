# §4 Measurement validity (phase-2 draft)

**Status:** draft prose. Every number cites `NUMBERS_LEDGER.md`. Each check is a candidate rule: its status in Table 2 says whether we demonstrate the effect on our traces.

---

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
