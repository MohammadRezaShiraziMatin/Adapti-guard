# What Reached the Executor? Measurement Checks for Prompt-Injection Defense Evaluation, with a Re-analysis of Released AgentDojo and AgentDyn Runs

*MANUSCRIPT_DRAFT_v2, assembled 2026-10-16 (Tehran). Not submitted, not posted. Sources: `docs/MANUSCRIPT_M1_M3_EXTERNAL_VALIDATION_DRAFT.md` (re-analysis sections, carried over with their labels and source tags) and the original-repo `MANUSCRIPT_DRAFT_v1.md` (`/workspace/adapti-guard/docs/paper/negative_result/`, branch main, read-only; own-harness sections E1–E5, shortened, numbers unchanged). Source tags are paths relative to `/workspace/pivot-checks/` unless marked `[v1 §…]`. Numbers are checked by `review/verify_numbers.py` (output `review/verify_numbers_out.txt`).*

**Labels.** [CONFIRMATORY — preregistered] means the analysis follows a protocol written before the data were scored. [EXPLORATORY] means it was designed or remapped after seeing data. [DEVIATION] marks a departure from a written protocol. [OWN-HARNESS EVIDENCE] marks results from our own testbed (E1–E5), which are not external.

## Abstract

We audit how attack success is measured when prompt-injection defenses for tool-using LLM agents are compared, and re-analyse third-party released runs of two public benchmarks.

**First, scenario validity (M3).** In AgentDyn, 20 of 28 benchmark-specific injection tasks fail their own success check: executing the task's reference solution (`ground_truth()`) in the default environment does not satisfy its `security()` predicate. In all 18 shopping and github tasks, the reference is a placeholder banking call unrelated to the stated goal. This breaks the benchmark's self-check, the tool_knowledge attack and any attempt-based metric keyed to the reference. It does not affect the reported state-based attack success rate (ASR).

**Second, the success endpoint (M1).** We run the empirical test that Pathade et al. leave open ("we report no empirical ranking inversion", §VIII). We re-scored 74,528 released injection episodes (125 run sets) as executed (state change) or attempted (proposed call). The result is narrow. Under the preregistered rule, the success definition reverses the rank of execution-time defenses (progent, drift) in 3/9 eligible cells. A task-clustered bootstrap with Holm correction also gives 3/9, but which specific pairs reverse depends on the inference method. Without progent, 1/9 cells has a flip.

**Third, checker vs LLM judge.** On 600 AgentDyn episodes, agreement between the state checker and two LLM judges depends on the defense (κ 0.454–0.940). In blind manual review the checker was right in all 20 tool_filter disagreements; the judges' main error was scoring attempts as successes.

**Fourth, checker-version drift is negligible:** 198 of 73,009 labels (0.27%) change under current checker code.

We also summarise evidence from our own harness (E1–E5). We make no claim that any defense is effective and no claim of general ranking instability.

## 1 Introduction

Defenses against indirect prompt injection are compared by attack success rate (ASR). Pathade et al. argue that ASR is a family of metrics, parameterised by choices that papers rarely state. They show analytically that some of these choices can reverse defense rankings, but run no defenses themselves (§III, §V, §VIII). Shaw shows on a single audited benchmark and a self-built harness that scoring success by tool identity rather than arguments inflates ASR from 1.2% to 21.7% (§VII-A).

Our own testbed (AdaptiGuard; E1–E5, §6) led us to six candidate measurement checks (M1–M6). In each case, a choice that looks like bookkeeping changed or qualified a conclusion. Evidence from one's own harness is not external. In this version we therefore test two checks on artifacts we did not produce, the released AgentDojo and AgentDyn runs and code:

- **M3:** does each scenario contain a valid attacker effect?
- **M1:** what counts as success?

We add a checker-vs-judge comparison and a checker-version drift check.

**Contributions.**
1. A code-level audit showing that 20/28 AgentDyn injection tasks fail their own success check (§5.1; reproducible code facts).
2. A preregistered test of whether the success definition reverses defense rankings on released runs, with drop-errors, task-clustered and leave-one-defense-out sensitivity analyses (§5.2). The effect is narrow: execution-time defenses, 3/9 cells, method-sensitive pairs.
3. A blind review of checker–judge disagreements and a recall sample (§5.3).
4. A replay of 73,009 stored labels against current checker code (§5.4).
5. Own-harness evidence for M1–M6 (§6), clearly separated.

**Non-claims.** We do not claim that any defense is effective or ineffective in general. We do not claim that evaluation is generally unstable. We do not claim that the six checks are a validated framework.

## 2 Related work

All claims below come from full-text reads; page references are PDF pages [src: review/RELATED_FULLREAD.md].

**Shaw (2609.32691)** audits one unnamed IPI benchmark and its harness and names four defect classes (§IV, p. 3):
- silent payload non-delivery (39/43 payloads never delivered);
- success scored by tool identity rather than arguments;
- false rejections conflated with incapacity;
- no audit trail.

Re-scoring identical traces gives 21.7% ASR under tool-identity scoring vs 1.2% at argument level (§VII-A, Table I). Their harness is single-domain with five tools. Success is an argument-level predicate over *executed* calls (§V-C). Their defenses are TypeChecker, CapabilityRouter and an LLMJudge used as a defense (§V-F). Their defense comparison is not significant (Fisher exact with Holm correction, p = 1.0; §VII-B), and they report no ranking analysis. Shaw also states the principle that a scenario must be measurement-valid: its success condition must be able to fire on the attacker's action. Their harness rejects attacker goals that name a tool absent from the registry (§V-A, §V-D, p. 4).

*What Shaw already showed:* scoring choices inflate the ASR *level*, and attacker goals must be checked for feasibility. *What Shaw did not do:* compare attempted with state-executed success, rank defenses, audit a public benchmark's reference solutions, compare a checker with a judge as evaluator, or analyse checker-version drift.

**Pathade, Pawar and Patil (2609.25173)** name six axes of ASR definition, among them the unit of analysis, the success oracle and partial-success binarization (§III, pp. 2–3). They meta-analyse the reporting practice of 259 papers (§IV) and derive analytical power and ranking-inversion results (§V). Among their points:
- string-matching and state oracles disagree in both directions (p. 2);
- oracle-induced inversion requires substantial differential error: 1 of 25 β combinations inverts (§V-B, p. 5);
- they list tool-set versioning and model version drift as sources of incomparability they do not measure (§III, p. 3).

They state that they ran no defenses end to end and report no empirical ranking inversion (§VIII, p. 6). *What Pathade et al. already showed:* analytically, that oracle and success-definition choices can reverse rankings, and that judge calibration is rarely reported (29.7% of judge-using papers). *What they did not do:* any empirical inversion, any benchmark audit, or any drift measurement.

**Other work.**
- The Same Zero (Yin, 2610.04504) reports that AgentDojo banking state checks missed 11 tool-level attacks, a conditional miss rate of 11/75 [partial read; src: review/RECALL_RESULTS.md §6].
- Liu (2610.03448, read in full) re-evaluates prompt-injection detectors offline without agent ASR [src: LIU_JUDGE_READ.md].
- Hardy et al. (2610.00651) apply generalizability theory to agent leaderboards [abstract and introduction read].
- Benchmarks and defenses (AgentDojo 2406.13352, InjecAgent 2403.02691, CaMeL 2503.18813, Progent 2504.11703, and others) are as in [v1 §2].

**Net novelty.**
- The direction of M1 is anticipated: Shaw for the level effect, Pathade analytically for rankings. Our addition is an empirical, narrow reversal on third-party released runs.
- The principle behind M3 is in Shaw. Our addition is the concrete AgentDyn audit.
- The checker-vs-judge comparison is partly new: Pathade gives the mechanism analytically.
- The drift analysis is new relative to both papers.

## 3 Method: six measurement checks (M1–M6)

Definitions follow [v1 §4, Tables 3 and 3b]. The status of each check is given in brackets.

- **M1, success endpoint.** Success means that the attacker-specified effect reached the executor. In AgentDojo/AgentDyn this is the state-based `security()` check. A proposed or attempted call is reported separately. [Own harness: exploratory. External: tested in §5.2.]
- **M2, blocked payload.** A block before the target is a defense outcome, counted as a failed attack, not as a delivery failure. A sensitivity analysis under the alternative labelling is mandatory. [Own harness only; exploratory.]
- **M3, scenario validity.** An attack scenario must contain a valid attacker-controlled effect, and its reference solution must satisfy its own success check. [Own harness: one scenario. External: §5.1.]
- **M4, authorship independence.** The attack set must be authored independently of detector development and frozen before defenses are run. [Own harness; case-study observation; independence only partial.]
- **M5, per-model reporting.** Results are reported per model, with admission by undefended rate, the executor log preferred over reply text, and a baseline replicate for the noise floor. [Own harness; exploratory.]
- **M6, defense channel.** Confirm that the defense is applied to the channel the attack arrives through. [Own harness; preliminary; 18 indirect episodes.]

**External success definitions (§5.2).**
- EXECUTED: the stored state-based `security()` result.
- ATTEMPTED: the agent proposed a call to an injection ground-truth function, by name match.
- ATTEMPTED-CORRECT-ARGS (CA): preregistered secondary; not used for any claim (§7).

