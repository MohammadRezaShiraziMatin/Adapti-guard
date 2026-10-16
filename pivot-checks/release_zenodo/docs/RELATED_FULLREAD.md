# Full-text read: Shaw (2609.32691) and Pathade et al. (2609.25173)

Read 2026-10-16 (Tehran) from the arXiv PDFs in `papers/` (`2609.32691.pdf` was downloaded today and `2609.25173.pdf` was already present), converted with pdftotext. Page numbers are PDF pages. Titles and authors were checked on p1.

## Shaw, "Silent Failures in Agentic Security Evaluation: A Validated Harness for Tool-Call Mediation Under Indirect Prompt Injection" (Animesh Shaw, arXiv:2609.32691v1, 26 Sep 2026; 7 pp.)
- **What they measure:** audit of one unnamed "representative IPI benchmark and its harness". Four defect classes (p3, §IV):
  - D1: silent payload non-delivery (39/43 payloads never delivered);
  - D2: attack success scored by tool identity, not arguments;
  - D3: false rejections conflated with model incapacity;
  - D4: no audit trail.
- **Re-scoring:** they re-score identical traces under the defective and corrected definitions. D2 gives an ASR of 21.7% vs 1.2% (§VII-A, Table I, p4–5). A small model reported at 62.8% ASR scores 0% under the corrected harness (§VII-D, p5–6).
- **Harness:** their own harness ("Chokepoint"). Single domain, five tools (read/send_email, read/write_file, execute_sql_query), 95-scenario core suite and a 55-scenario reduced suite (§III-D, §VI). Success is an argument-level predicate over the *executed* tool calls C(s) (§V-C, eq. 1, p4).
- **Models:** gpt-5.6-terra, llama3.1:8b, gemma4:12b, qwen2.5-coder:7b.
- **Defenses:** TypeChecker, CapabilityRouter, and LLMJudge (an LLM *used as a defense*) (§V-F, p4).
- **Ranking analysis:** none. The frontier defense comparison is not significant (Fisher exact, Holm, p=1.0; §VII-B, p5), and they explicitly decline to name a best defense.
- **Reference-solution / ground_truth audit:** no audit of a benchmark's reference solutions. They do, however, add *feasibility checks* that reject a suite if "a success condition names a tool absent from the registry … (an attacker goal that can never fire)" (§V-D, p4), and they define "measurement validity": the success condition must be able to fire on the attacker's action (§V-A).
- **Checker version / replay:** no checker-version drift and no replay against newer checker code. Their re-scoring is offline on persisted traces under defect vs corrected definitions (§VII-A).
- **Checker vs LLM judge:** not studied. The LLM appears only as a defense; they report judge-defense calibration (AUC 0.63, §VII-F).
- **Verbatim quote (p4, §V-F):** "A blocked call is recorded, not merely suppressed". (The earlier paraphrase "recorded, not suppressed" was not verbatim.)

**Overlap per finding:**
- **M1 (success-definition ranking flips):** partly new. Shaw shows that how success is scored (tool identity vs argument level, both on executed calls) inflates the *level* of ASR, on one self-built single-domain suite. Shaw has no proposed/attempted vs state-executed contrast, no defense ranking, and no released third-party runs. Our rank reversal of execution-time defenses across models, on two public benchmarks' released runs, is not in Shaw.
- **M3 (AgentDyn ground_truth vs security):** partly new. Shaw states the general principle (a scenario must be measurement-valid; an attacker goal naming an absent tool "can never fire") and builds pre-flight checks for it (§V-A, §V-D). This overlaps our class 2 (send_money absent in github) in concept. Our concrete finding is new: 20/28 AgentDyn injection tasks whose own `ground_truth()` fails `security()`.
- **Checker vs judge:** new relative to Shaw (who has no LLM-as-evaluator comparison).
- **Drift (checker-version drift):** new relative to Shaw. Shaw does record the git commit and suite SHA in run manifests (§XI), but runs no drift analysis.

## Pathade, Pawar, Patil, "Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation" (arXiv:2609.25173v1, 21 Sep 2026; 7 pp.)
- **What they measure:**
  - six axes along which ASR is defined: unit, oracle, trials, adaptivity, defense knowledge, partial-success binarization (§III, p2–3);
  - a meta-analysis of the reporting practice of 259 arXiv papers (§IV);
  - analytical power and ranking-inversion results (§V).
- **No benchmark, harness or defenses run.** "We have not run defenses end to end, so we report no empirical ranking inversion" (§VIII, p6).
- **Ranking analysis:** analytical only.
  - Sampling: closed-form normal approximation plus a 200,000-trial Monte Carlo check (§V-A).
  - Oracle-induced inversion: closed form eq. 2. The condition is "demanding": 1 of 25 β combinations inverts (§V-B, p5).
  - They claim A1, A2, A4 and A5 can reverse rankings (§III, p2).
  - A2 notes that string-matching and state oracles disagree in both directions, e.g. an agent emits the target string "while never issuing the tool call that would cause harm" (p2). A6 names "recognition without execution" and other partial-success cases (p3).
- **Reference-solution / ground_truth audit:** none.
- **Checker version / replay:** none. Tool-set versioning and model version drift are listed as sources "we do not measure" (§III, Interactions and scope, p3).
- **Checker vs judge:** argued analytically (differential judge error across defenses can invert rankings) and measured as a reporting rate (29.7% of judge-using papers report human agreement). No empirical judge-vs-checker comparison.
- **Quote:** none used.

**Overlap per finding:**
- **M1:** partly new. Pathade predicts analytically that oracle/success-definition choice can reverse defense rankings, but says no empirical inversion was run. Our contribution is the empirical reversal on released runs (though narrow: execution-time defenses, 3/9 cells, method-sensitive pairs).
- **M3:** new relative to Pathade (no audit of reference solutions).
- **Checker vs judge:** partly new. Pathade gives the mechanism (differential judge error correlated with defense) analytically. We give an empirical case: κ varies by defense, judges score attempts as successes, and there is a judge-induced PG2 vs repeat order flip that manual review does not support.
- **Drift:** new relative to Pathade (only listed as unmeasured).

## Weakening novelty
- M1's direction (success definition changes ASR level and, in principle, rankings) is anticipated: by Shaw for the level (tool identity vs arguments) and by Pathade analytically for rankings. Only the empirical reversal on third-party runs is ours.
- M3's principle (a scenario must be able to register attacker success; check goals against the tool registry) is in Shaw §V-A/§V-D. Ours is a specific benchmark audit.
