## Appendix B Reporting checklist for evaluations of runtime defenses against prompt injection
Intended for authors and reviewers. Each item has a pass criterion that can be checked from the paper and its artifacts. Items correspond to the candidate checks M1 to M6 of §4, derived from this case study. The checklist complements Pathade et al.'s general evaluation-design checklist and is intended for defense-specific evaluation design, not as a universal validation framework.

| # | Item | Pass criterion | Check |
|---|---|---|---|
| 1 | Endpoint | success is the executed tool call (argument-level predicate); the proposal rate is reported separately | M1 |
| 2 | Judge in the primary endpoint | if a judge is used, it is compared with the executed outcome and the agreement is reported | M1 |
| 3 | Blocked payloads | a block before the target is counted as a defense outcome; results are shown under both labelings | M2 |
| 4 | Delivery check | the harness verifies that the payload reached the model and reports how many episodes failed delivery, by cause | M2 |
| 5 | Validity control | a control with the injection removed; a model is assessable only if the control is at or near zero | M3 |
| 6 | Scenario validity | every attack scenario has an untrusted channel and an attacker-controlled effect, stated as a rule applied before results are seen | M3 |
| 7 | Authorship | the attack set was written independently of detector or defense development and frozen (hash) before defenses were run; authorship (human, model, mixed) is stated | M4 |
| 8 | Selection | any filter used to select attacks is stated and does not use the targets' results | M4 |
| 9 | Per-model reporting | results are given per model; pooled rates only as a secondary summary | M5 |
| 10 | Floor rule | a stated rule for models whose undefended rate is too low to assess a defense; undetermined targets are labelled as such | M5 |
| 11 | Noise floor | an undefended replicate shows run-to-run discordance per model | M5 |
| 12 | Non-independence | the unit of analysis accounts for repeated instructions (cluster bootstrap or equivalent) | M5 |
| 13 | Defense channel | the defense is applied to the channel through which the attack arrives, with a check that it sees the injected text, and a wrong-channel arm is run | M6 |
| 14 | Utility | benign utility is measured with the same endpoint, with and without the defense | M1 |
| 15 | Adaptive attackers | the paper states whether an adaptive attacker was run; if not, no claim of robustness against one | scope |
| 16 | Errors | provider failures are reported as failures, never scored as safe; spend and caps are reported | reporting |
| 17 | Reproducibility | one command regenerates the numbers and figures from committed traces; pack or template hashes and code commit SHAs are recorded | reporting |
| 18 | Pre-registration | hypotheses, endpoint, sample, analysis and floor rule are registered before the confirmatory run; deviations are logged | reporting |

How to cite: refer to "the M1 to M6 checks" and to "Appendix B of this paper" when stating which items a study satisfies. An item that is not satisfied should be listed as a limitation.

**Self-assessment of this paper.** Satisfied, as §4 to §6 read: items 1, 4, 9, 14 and 16 (E2 and E3 record delivery causes and executed endpoints per model; the external test reports failures as failures). Partly satisfied: item 3 (both labelings are shown for E2, but the scenario they are measured on fails item 6); items 6 and 8 (the M3 rule was adopted before the defense results were used, and E2 fails it); item 7 (the E3 set is frozen by hash, but partially independent, §8.3); item 10 (floor rule applied to the 2026 calibration, with one selection that departs from it, §6.3); item 11 and 12 (noise floor for E3 and the external test; cluster bootstrap for the external test and an instance-clustered check for E3). Satisfied: item 15 (no adaptive attacker was run, and the paper says so). Not satisfied: item 5 (E2 has no injection-free control), item 13 (no wrong-channel arm; M6 is only proposed), and item 18 (no pre-registration; the protocol was drafted locally, not registered).
