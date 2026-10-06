# Q1 Self-Review of the Case-Study Manuscript

## Overall assessment
The draft is substantially closer to a journal manuscript than the source technical report, but it is not submission-ready. The central claim is restrained. Remaining weaknesses concern evidence presentation, external validity, literature positioning, and venue-specific reporting.

## Section-by-section criticism

### Abstract
Reviewer concern: the study is numerically precise but narrow and single-model.
Action: keep the methodological lesson explicit and the scope limited.

### Introduction
Reviewer concern: the gap may look smaller than the general prompt-injection literature.
Action: emphasize separation of controller reliability from end-to-end benefit.

### Related Work
Reviewer concern: adaptive-control literature is underdeveloped.
Action: add only verified adaptive runtime, defense-in-depth, and evaluation papers.

### System
Reviewer concern: current description is still implementation-oriented.
Action: add one architecture figure and distinguish runtime defaults from experiment settings.

### Method
Reviewer concern: model selection, 16-config development selection, equivalence margin, and confirmatory independence need scrutiny.
Action: retain the exact frozen protocol and selection disclosure.

### Results
Reviewer concern: summary tables alone do not expose paired-seed variation.
Action: add a primary paired-difference figure and a per-seed plot generated from committed traces.

### Discussion
Reviewer concern: the headroom explanation could become a post-hoc causal story.
Action: label it explicitly as a hypothesis and identify discriminating future tests.

### Threats to Validity
Reviewer concern: single model, synthetic pool, noisy utility, and no adaptive attacker sharply limit generalization.
Action: keep the consolidated section prominent.

### Ethics
Reviewer concern: release policy is unresolved.
Action: decide the public/controlled artifact policy before submission.

### Reproducibility
Reviewer concern: multiple research tracks can be confused.
Action: give adaptive F3 its own reproduction subsection and clearly separate it from Track A/E1–E3.

### Conclusion
Reviewer concern: contribution may appear incremental.
Action: emphasize the methodological distinction between controller reliability, detector coverage, and end-to-end comparative benefit.

## Highest-priority remaining work
1. Add architecture figure.
2. Add primary paired-difference figure from committed F3 traces.
3. Expand Related Work with verified citations.
4. Verify every number against authoritative result files.
5. Resolve author/venue/anonymization and dual-use release policy.
6. Run a final hostile review after figures and bibliography are finalized.