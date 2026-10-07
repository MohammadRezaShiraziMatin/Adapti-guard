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
| 17 | Reproducibility | one command regenerates the offline numbers and figures from committed traces (E1 to E4; external-test numbers are read from committed records); pack hashes are in `hashes.sha256` files and code commit SHAs are in the run manifests | reporting |
| 18 | Pre-registration | hypotheses, endpoint, sample, analysis and floor rule are registered before the confirmatory run; deviations are logged | reporting |

How to cite: refer to "the M1 to M6 checks" and to "Appendix B of this paper" when stating which items a study satisfies; an item that is not satisfied should be listed as a limitation.

**Self-assessment of this paper against the checklist.** Satisfied, as we read §4 to §6: items 1, 2, 3, 4, 9, 14, 16. Partly satisfied: items 8 and 10 (the inclusion and admission rules were fixed after the rates were seen, §4.4, §4.5), item 7 (the independent set is frozen by hash but authored by an AI assistant that had read the detector patterns, §8.3), item 12 (instance-cluster bootstrap for E3 only, §8.2), item 13 (checked in the E3 re-run only, §4.7), item 17 (offline numbers regenerate; the live harness and the external-test runner are not released). Not satisfied: item 5 (E2 has no injection-free control; the scenario filter used the either-clause rule of §4.3), item 11 (no undefended replicate in E2 or per model in E3; replicates exist for the external test only), item 15 (no adaptive attacker), item 18 (no external pre-registration). Table 3 gives the status of the checks themselves.
