**To:** The Editors, [PLACEHOLDER: venue] — [PLACEHOLDER: do not send. Computers & Security's AI/ML moratorium excludes LLM security (review/JOURNAL_REQUIREMENTS.md); the audit (audit/CONTRIBUTION.md) judges the reframed paper suitable for a workshop and not yet for TMLR. A venue decision is needed first.]
**From:** [PLACEHOLDER: corresponding author, affiliation, e-mail]
**Date:** [PLACEHOLDER]

Dear Editors,

Please consider our manuscript "Reference Solutions That Fail Their Own Checks, and Other Measurement Pitfalls in Released AgentDyn Prompt-Injection Runs".

**Problem.** Prompt-injection defenses for tool-using agents are compared on public benchmarks, whose measurement plumbing is rarely audited.

**Findings, from AgentDyn's released code and runs, which we did not author:**
1. **Main result.** 20 of AgentDyn's 28 benchmark-specific injection tasks ship a reference solution that fails the task's own security check (18 copy-paste banking stubs, one wrong-argument call, one missing OTP step). We confirm all 20 by executing the suites' own check logic offline. The suite self-check and reference-keyed metrics are broken; the released state-based success rates are not. The nine shopping stubs had already been replaced in AutoDojo's public code; the github and dailylife defects, the complete census, an audit of related code bases and a downstream-exposure census (two of five 2026 papers found are exposed) are, as far as we found, new. We do not claim to be the first audit of an AgentDojo-derived benchmark.
2. **Secondary, descriptive.** With an argument-level attempt scorer (ATT-ARG; 78/80 agreement, κ 0.95 with blind AI labels), attempted and executed scoring rank defenses broadly alike (Kendall τb 0.642–1.0 per cell). The preregistered flip rule finds reversals in 3 of 9 cells, all involving progent and all on AgentDyn; 1 of 9 under task-clustered inference and 0 of 9 without progent. The earlier tool-identity scorer is kept as a reference.
3. **Short results.** Checker-version drift is small in aggregate (0.27%) but up to 7.1 pp in one run set. In a one-model, three-defense case study, LLM judges counted blocked attempts as successes.

**What we do not claim.** No defense is called effective or ineffective, no general ranking instability is claimed, and AgentDojo contributes only one eligible ranking cell (no reversals).

**Preregistration and labels.** The ranking rule was preregistered (SHA-256 reproduces byte-exactly), but the preregistration was not blind to the mechanism, and the exclusion of two suites is a logged post-hoc deviation, so the all-suite analysis is primary. All labels come from a single AI assistant, not from humans; owner labels are [PLACEHOLDER].

**Disclosure.** The AgentDyn defects will be reported to the maintainers before any preprint [PLACEHOLDER: date filed, issue link, response]. The manuscript is not under consideration elsewhere. Generative-AI use is declared in the manuscript.

Sincerely,
[PLACEHOLDER: name]
