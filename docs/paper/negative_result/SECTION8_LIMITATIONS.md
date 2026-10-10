# §8 Limitations (phase-2 draft)

**Status:** draft prose for the phase-2 scope. Each limitation cites an artifact or states a gap. `[TODO owner]` marks statements that need the owner's confirmation before submission.

---

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
