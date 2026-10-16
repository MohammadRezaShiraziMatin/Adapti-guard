**Extended audit of related code bases [CODE FACT; EXPLORATORY scope; procedure hash-locked before running].** We ran the same unchanged `check()` and per-task logic on every registered suite and version of four code bases [src: ext/EXT_AUDIT_RESULTS.md; ext/audit_{agentdojo,agentdyn,autodojo}.txt; ext/PROCEDURE_EXT_AUDIT.sha256]: AgentDojo (089ed468, MIT [license to verify]), AgentDyn (SaFo-Lab 5353cf76, MIT), AutoDojo (xhOwenMa/AutoDojo aa458794, MIT) and uber/ADR (a6076aa3, Apache-2.0). ADR does not import as a package. By diff it is AgentDojo v1/v1_1 with only import paths and a `TASK_TYPE` attribute changed, so it was not executed. Unique injection tasks failing their own reference-solution check, counted once per code base where they are introduced:

| Benchmark | Stub | Wrong args | Missing step | Tool absent | Other |
|---|---|---|---|---|---|
| AgentDojo (v1.2, v1.2.1, v1.2.2 workspace) | 8 (injection_task_6–13: `ground_truth()` returns `[]`) | 0 | 0 | 0 | 0 |
| AgentDyn (new suites) | 9 (shopping) | 1 | 1 | 9 (github; also stubs) | 0 |
| AutoDojo (beyond AgentDyn) | 0 (the 9 shopping stubs replaced) | 0 | 0 | 0 | 3 (shopping inj2/5/8: random-OTP gate a static call list cannot pass) |
| ADR | 0 (by diff; not executed) | 0 | 0 | 0 | 0 |

AutoDojo's ten new banking_v2/travel_v2 suites pass. AutoDojo leaves the github and dailylife defects unchanged. Whether the empty AgentDojo v1.2.x workspace references are intentional (security-only tasks) is unverified, and they are not counted in our 20. The original v1 AgentDojo suites pass.

**Downstream exposure [EXPLORATORY; procedure hash-locked; incomplete census].** We searched for 2026 papers evaluating on AgentDyn (web and DDG search; the Semantic Scholar citation API returned HTTP 429). We read each paper found in full and classified exposure to the defective reference solutions [src: exposure/EXPOSURE_TABLE.md; exposure/PROCEDURE_EXPOSURE.sha256]. This reports exposure only; we do not claim any paper's results are wrong.

| Paper | AgentDyn suites | Attacks | Reference-solution use | Exposure |
|---|---|---|---|---|
| AgentDyn (2602.03117v3) | all three | important_instructions; ignore-previous, completion, manual adaptive (§4.1, App. F) | none stated; utility/ASR from `security()` (Table 3) | not exposed |
| Agent-Sentry (2603.22868) | all three | benchmark injection tasks | trace labels from "the injection task's ground-truth signature" (§4.1.4) | exposed |
| AuthGraph (2605.26497) | not itemised | "diverse attack types" | none found | unknown |
| ActGov (2609.24446) | 60 user / 28 injection tasks | not specified | "native benchmark scorer" | unknown |
| AutoDojo (2606.15057) | all three (App. D) | important_instructions plus adaptive optimizer (§4.1) | optimizer prompt includes `ground_truth()` calls (code: variant_generation/suite_gen_utils.py); github/dailylife unchanged | exposed (code level; use in App. D runs unverified) |

