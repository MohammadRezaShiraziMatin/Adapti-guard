# CONTRIBUTION assessment (adversarial), 2026-10-16 (Tehran)

## One-sentence thesis using only SUPPORTED claims
"In public prompt-injection benchmark artifacts, measurement plumbing can silently fail. 20 of 28 AgentDyn-specific injection tasks ship a reference solution that does not satisfy its own security check (18 are copy-paste banking stubs). In the released AgentDyn runs, every significant EXEC-vs-ATTEMPTED rank reversal involves one of the two execution-time defenses (progent, drift)."
This is possible only as a *descriptive, benchmark-specific* thesis. A thesis about "measurement checks" as a method, or about "two benchmarks", is not supported. AgentDojo contributes 1 cell with 0 flips, and M2/M4/M5/M6 are own-harness only and unverifiable here.

## Per finding
| Finding | Role | Recommendation |
|---|---|---|
| F1 AgentDyn ground_truth defect (§5.1) | **Core, the strongest and cleanest result** (code fact, reproducible). Weakness: inj2 cause unverified; self-check failure inferred, not executed | Keep as lead. Report "18 certain + 2 probable". Actually run `TaskSuite.check()`. Get maintainer confirmation |
| F2 EXEC vs ATTEMPTED ranking reversal (§5.2) | Supports the thesis only in narrow form. It is close to definitional (attempt metrics give no credit for execution-time blocking), and it is fragile (X1, X5, clustered-full 1/9) | Keep, but shorten and re-label as "preregistered rule on a post-hoc subset". Put the robustness table first and the headline second. Drop "mechanical, not noise" |
| F3 Stage gaps (§5.2) | Side result. n = 2 execution-time defenses, post hoc | Appendix, one sentence in main text |
| F4 Checker vs judge (§5.3) | Side result (1 model, 3 defenses, AI-only adjudication). Related to F2 mechanically (judges count attempts) | Shorten to one paragraph. Frame it as "a case study"; do not say "depends on the defense" in general |
| F5 Drift replay (§5.4) | Side result, negative. Novel relative to Shaw/Pathade, but the replay fidelity is limited | Short section or appendix. Possibly a separate short note |
| F6 Own-harness E1–E5 (§6) | Not evidence for this paper; it is the origin story. Unverifiable from the submitted artifacts | Cut to a short motivation paragraph and move to the supplement. Remove M2/M4/M5/M6 from the title and method |
| CA metric | Unreliable (CA < EXEC) | Cut entirely, including the "9 of 10" count in L228 |

## Versus prior work
- **Shaw (2609.32691).** §IV (D1–D4), §V-A (measurement validity), §V-C (argument-level predicate over *executed* calls), §V-D (feasibility pre-flight checks: a goal naming an absent tool "can never fire"), §V-F/p.4 ("A blocked call is recorded… distinguishable from one the agent never attempted"), §VII-A (21.7% vs 1.2%), §VII-B (no significant defense difference).
  - Overlap: the principles of F1 (M3) and of F2 (M1: executed vs attempted, block recording) are both in Shaw.
  - Increment: a concrete defect in a named public benchmark (F1), and an empirical *rank* effect on third-party runs (F2).
- **Pathade (2609.25173).** §III (six ASR axes, A2 oracle, A6 "recognition without execution"), §IV (259-paper meta-analysis), §V-B (oracle inversion is "demanding", 1 of 25), §VIII ("we report no empirical ranking inversion; … natural next step").
  - Overlap: the prediction behind F2 and the judge mechanism behind F4.
  - Increment: one empirical instance, mostly on one benchmark. It is not the factorial experiment Pathade envisages.
- Net: the paper is a **case-study complement** to these two papers, not a methods advance.

## Verdict: coherent only if reframed
As written, the paper mixes a six-check "framework" (own harness, unverifiable) with three or four unrelated external re-analyses. The headline is labelled confirmatory but rests on a post-hoc subset.
**Reframing:** an artifact audit of the AgentDyn/AgentDojo released runs with three findings, ordered by strength:
1. a benchmark defect;
2. a narrow, execution-time-defense-specific ranking sensitivity to the success definition, with all sensitivity analyses shown equally;
3. a negative drift result.

The judge comparison becomes a case study. M1–M6 and E1–E5 move to the supplement.

**Strongest honest title:** "Reference Solutions That Fail Their Own Checks, and Other Measurement Pitfalls in Released AgentDyn Prompt-Injection Runs"

**Abstract (3 sentences):**
1. Auditing the AgentDyn benchmark code, we find that 20 of its 28 benchmark-specific injection tasks ship a reference solution that fails the task's own security check (18 copy-paste banking stubs), which breaks the suite self-check and any metric keyed to the reference solution. The released state-based ASRs do not depend on it.
2. Re-scoring released AgentDyn runs by attempted instead of executed attacks reverses at least one significant defense pair in 3 of 9 model cells under a preregistered rule applied to an unaffected suite subset. Every reversal involves one of two execution-time defenses (progent, drift), and the effect largely disappears under task-clustered inference on all suites (1/9) or without progent (1/9).
3. A replay of 73,009 stored labels against current checker code changes 0.27% of them; a small LLM-judge case study (one agent model, three defenses, single AI adjudicator) finds that judges mostly count blocked attempts as successes.

## Venue fit, as-is
- **Workshop (e.g. security/ML-eval workshop): yes**, after the A-class fixes. It suits a short, honest case study.
- **TMLR-style: not as-is.** TMLR asks for claims matched by evidence. The overclaims (X1 label, "two benchmarks", "mechanical, not noise", abstract selectivity), the pending human labels and the AI-only adjudication would draw a major revision. It would be possible after A+B and the owner labels.
- **Benchmark/datasets track: plausible only if reframed** as an AgentDyn artifact audit with maintainer confirmation (C). The current framing is not a benchmark contribution.
- **Q1 security journal: no.** One benchmark in substance, two execution-time defenses, no human validation, no new experiments. The novelty over Shaw/Pathade is incremental.
