## 2 Related work

All claims below come from full-text reads of the arXiv HTML versions; section references are to those versions [src: review/RELATED_FULLREAD.md; review/RELATED_WORK_ROUND10.md; papers/*.txt].

**Measurement validity of IPI evaluation.** Shaw (2609.32691) audits one unnamed IPI benchmark. Its defect classes include success scored by tool identity (D2, §IV), and re-scoring identical traces gives 21.7% ASR under tool-identity scoring vs 1.2% at argument level (§VII-A). Pre-flight checks reject attacker goals that name an absent tool (§V-A, §V-D), and blocked calls are recorded (§V-F). Pathade, Pawar and Patil (2609.25173) define six axes of ASR, including the success oracle (§III), and derive ranking inversion analytically without running defenses (§V-B, §VIII). Because of Shaw's D2, our earlier function-name attempt scorer is now only a tool-identity reference, and the primary attempt scorer is argument-level (ATT-ARG, §3).

**Benchmark audits.** Zhu et al. (2507.02825, ABC) recommend verifying ground-truth correctness and shipping an automatic oracle solver (items T.7–T.9, §4.1). Our self-check is an application of T.9, so the principle is known. BenchGuard (2604.24955) names "errors in the reference solution" as a defect category (§3.2, Table 1) and audits ScienceAgentBench and BIXBench with LLMs (§5). Vaghasiya, Bhat et al. (2607.02577) audit evaluator validity in BFCL v4, τ²-bench and LiveMCPBench (§3.4, §4.3). Abrich (2610.09142) injects faults into reference solutions that are assumed correct, to find verifier false accepts in AppWorld and WorkArena (§2, §3). Luo et al. (2609.34262) detect unearned passes, e.g. reference solutions leaked via git history (§4–§5). The closest work is Bellibatlu, Wang and Zhang (2609.37315). They audit, by execution at pinned commits, whether mutating *tools* honour their advertised contracts in four benchmarks, including the full 25-tool AgentDojo v1 surface (§V-B1, §V-B3). They do not audit injection-task reference solutions or AgentDyn.

**Prior identification of part of our main finding.** AutoDojo (2606.15057; code xhOwenMa/AutoDojo at aa458794) builds on AgentDojo and AgentDyn (§4.1, App. D). A note in its shopping injection-task file, dated 2026-06-14, says the original `send_money(recipient="")` stubs "matched no security() check" and replaces them. Afterwards 6 of 9 pass `check()`, and three remain OTP-gated (per the code note). We found no statement of this in the paper text. We credit AutoDojo with the first public fix of the shopping stubs. Its github and dailylife tasks are unchanged.

**What is known and what is new.** *Known:* the principle that reference solutions must satisfy their own checks (ABC T.7–T.9; BenchGuard's GT class; Shaw §V-A); executed audits of AgentDojo artifacts at the tool layer (Bellibatlu et al.); the AgentDyn shopping stubs (AutoDojo); tool-identity inflation of ASR (Shaw §VII-A); analytical ranking inversion (Pathade et al.). *New, as far as we found:*
- the executed, complete census of 20/28 AgentDyn injection-task reference-solution failures, including github (9, tool absent) and dailylife (2) and the root cause of dailylife injection_task_2;
- the cross-benchmark defect table;
- the str-only cause of the "not injectable" self-check message;
- the downstream-exposure census;
- an empirical, argument-level rank-reversal analysis on released third-party runs.

We do **not** claim to be the first audit of an AgentDojo-derived prompt-injection benchmark.

**Other work.** The Same Zero (Yin, 2610.04504) reports AgentDojo banking state checks missing 11/75 tool-level attacks [partial read]. Liu (2610.03448) re-evaluates detectors offline. Hardy et al. (2610.00651) apply generalizability theory to agent leaderboards. Benchmarks and defenses (AgentDojo 2406.13352, InjecAgent 2403.02691, CaMeL 2503.18813, Progent 2504.11703) are cited in the references.
