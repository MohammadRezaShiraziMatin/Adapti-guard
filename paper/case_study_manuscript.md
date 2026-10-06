# TODO: Author Block / Venue / Anonymization

**Author block:** TODO  
**Venue:** TODO  
**Anonymization status:** TODO

# Measurement and Cost–Security Trade-offs in an Adaptive Prompt-Injection Guard: A Negative-Result Case Study

## Structured Abstract

### Background
Prompt injection is a security problem for language-model systems that process untrusted content. In agentic systems, defenses can intervene at different levels, but stronger intervention can also reduce utility or increase cost. Adaptive controllers are therefore attractive because they can change defense strength over time rather than applying one fixed level.

### Objective
This case study asks whether a threshold-based adaptive controller can operate reliably and whether adaptation improves a prespecified cost/security loss over the best fixed defense level on one prompt-injection guard stack.

### Method
We study a non-learning controller with four defense levels (L0–L3), hysteresis, benign-streak de-escalation, attack memory, bounded transition history, and validated inputs. The confirmatory F3 design was frozen before execution. It used meta-llama/llama-3.1-8b-instruct, 20 seeds, two streams, a fresh pool of 54 attacks and 32 benign prompts, the same detector and semantic guard for every arm, and the prespecified loss ASR + 0.5(1 - utility) + cost. The primary estimand was the paired per-seed loss difference between the dev-selected adaptive configuration and fixed L1.

### Results
The adaptive controller satisfies the tested reliability properties, including reachable de-escalation and bounded state. In the confirmatory run, adaptive minus fixed-L1 loss was -0.0118, with a 95% bootstrap confidence interval of [-0.0258, +0.0024], which is inconclusive under the frozen decision rule. The adaptive configuration had loss 0.2902 versus 0.3020 for fixed L1, with utility 0.613 versus 0.630 and cost 0.080 versus 0.100. An untuned escalating configuration was worse than fixed L1 by +0.0663 (95% CI [+0.0550, +0.0771]). Detector recall was 0.82 in the confirmatory run; earlier fresh-pool evaluation showed regex recall of 0.21–0.26 on 24 fresh attacks, while the semantic guard raised recall to 0.75 with 0/20 benign prompts flagged in the corresponding check.

### Conclusion
On this stack, adaptation produced a reliable controller operating on the security–cost trade-off, but the confirmatory experiment did not demonstrate an improvement over the best fixed level. The result is limited to the studied stack and protocol. It does not establish that adaptive defenses are generally ineffective. The main practical bottleneck was detector coverage rather than controller logic.

## 1. Introduction

Language-model agents increasingly process information originating outside the trusted user instruction. Prompt injection exploits this boundary by placing instructions or instruction-like content in untrusted inputs. Benchmarks such as BIPIA, Open-Prompt-Injection, InjecAgent, and AgentDojo have made it possible to measure different forms of prompt-injection vulnerability, including attacks embedded in external content and attacks that influence tool-using agents [1–4].

A recurring systems problem is that a defense has more than one possible intervention strength. A low intervention level may preserve utility and cost little but expose the system to attacks that evade the detector. A high level can reduce some attacks but may block legitimate work or consume more resources. A controller that adapts the level in response to observed pressure is therefore an intuitive design. However, adaptation itself introduces state, feedback delay, hysteresis requirements, and dependence on detector quality. A controller can be locally well behaved without improving the end-to-end security–utility–cost objective.

This case study therefore asks two separate questions: whether the controller can be engineered to behave reliably, and whether that reliability produces an end-to-end improvement over a fixed baseline.

### Research questions
**RQ1. Reliability.** Can a threshold-based adaptive prompt-injection controller satisfy basic operational requirements—reachable de-escalation, avoidance of oscillation, validated inputs, attack memory, and bounded state—without changing the frozen experiments on which earlier repository results depend?

**RQ2. Comparative benefit.** Under a frozen confirmatory protocol with the same detector, corpus, model, seeds, and loss definition across arms, does the dev-selected adaptive configuration improve the prespecified loss relative to the best fixed defense level?

### Contributions
1. A reliability-oriented controller case study with explicit hysteresis, de-escalation, attack memory, validation, and bounded transition history.
2. A frozen confirmatory comparison using paired per-seed loss differences and a prespecified equivalence margin.
3. A negative/inconclusive result: the primary comparison does not establish adaptive superiority over fixed L1.
4. A detector-bottleneck diagnosis showing that controller benefit is constrained by the quality of the feedback signal.

## 2. Related Work

### 2.1 Prompt-injection benchmarks and defenses
Liu et al. formalized prompt injection and evaluated multiple attacks and defenses across models and tasks [1]. Yi et al. introduced BIPIA for indirect prompt injection and studied boundary-awareness and reminder-based defenses [2]. InjecAgent evaluates indirect prompt injection in tool-integrated agents across 1,054 test cases and 17 user tools [3]. AgentDojo provides a dynamic environment with realistic tasks, tool interactions, security test cases, and adaptive attacks [4].

These works differ in threat model and endpoint. The present case study is narrower: it studies text-only probes and a defense-level controller, not a general benchmark for tool-using agents. The distinction matters because a controller can only react to the feedback available to it. A detector miss is therefore also a limit on the controller’s ability to escalate.

### 2.2 Defense-in-depth and adaptive intervention
Recent agent defenses place security mechanisms outside the base language model, including capability restrictions and control/data-flow separation. CaMeL, for example, explicitly separates trusted control and data flow to protect agents from prompt injection [5]. The present work does not compete with such architectures. Its question is narrower: given a small set of defense levels, can a controller select among them reliably and improve a composite loss?

### 2.3 Evaluation discipline and negative results
Dynamic environments such as AgentDojo emphasize that attacks and defenses interact with the evaluation environment itself [4]. This study adopts a related methodological principle at smaller scale: the primary comparison, comparator, and decision rule were fixed before confirmatory execution, while exploratory comparisons are explicitly labelled.

## 3. Case Study System

### 3.1 Architecture
The studied stack consists of a prompt-injection detector, an optional semantic guard, a risk/policy layer, a defense-action layer, and a threshold-based adaptive controller. The controller receives feedback about attack/legitimate pressure and selects one of four defense levels. It is not a learning algorithm, reinforcement-learning policy, or Bayesian optimizer.

### 3.2 Defense levels

| Risk | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| HIGH | BLOCK | BLOCK | BLOCK | BLOCK |
| MEDIUM | SANITIZE | SANITIZE | TOOL_RESTRICTION | BLOCK |
| LOW | NO_INTERVENTION | SANITIZE | SANITIZE | SANITIZE |

Sanitization in the studied runtime uses delimiting rather than the historical stripping mode. For medium risk, L1 and L2 both use delimiting; L3 additionally blocks flagged inputs. Action costs are 0, 0.1, 0.25, and 0.5 for A0–A3.

**Source:** docs/DEFENSE_LEVELS.md; docs/ADAPTIVE_CONTROLLER_SPEC.md; docs/F3_CONFIRMATORY_CONTRACT.md.

### 3.3 Controller mechanisms
The controller uses attack and legitimate pressure counters, benign-streak de-escalation, minimum dwell time, and attack-memory backoff. Hysteresis prevents an immediate escalation/de-escalation cycle. Attack memory increases the benign streak required after repeated escalation following a streak-driven down-move. Transition history is bounded to the most recent 1000 entries.

**Source:** docs/ADAPTIVE_CONTROLLER_SPEC.md.

### 3.4 Detector and threat model
The base detector is regex-based. The hardened variant adds normalization, base64 decoding, and additional multilingual/paraphrase patterns. The optional LayeredPromptInjectionDetector combines the hardened regex verdict with a semantic LLM-guard verdict using an OR rule.

The threat model is limited to synthetic text-only prompt-injection probes. There is no adaptive attacker, no live tool execution, and no claim of production-agent security. A detector false negative can remain invisible to the controller unless an independent outcome judge supplies feedback.

### 3.5 Loss
The confirmatory loss is Loss = ASR + 0.5 × (1 - utility) + mean cost, averaged per seed over the two streams.

**Source:** docs/F3_CONFIRMATORY_CONTRACT.md; results/f3_confirmatory/RESULTS.md.

## 4. Method

### 4.1 Design lock and frozen contract
The confirmatory F3 design was frozen at commit a00ef03 before the run. The confirmatory result was produced by one execution at commit c4421fa. The experiment was separate from the frozen Track A failure and did not modify or rerun that track.

The confirmatory model was meta-llama/llama-3.1-8b-instruct, selected from development evidence because the model showed separation between defense levels. Temperature was 0.3 and each run contained 150 episodes. Two streams were used: uniform25 and burst. Seeds 1000–1019 were disjoint from development seeds.

The fresh pool contained 54 attacks—22 leak and 32 marker—and 32 benign prompts. It was generated by mistralai/mistral-small-3.2-24b-instruct; the generator was not the detector author, guard model, or model under test. The pool was not used for tuning.

### 4.2 Arms
The fixed arms were L1, L2, and L3. The primary adaptive arm, adaptive_dev, was selected as the lowest-loss configuration from a 16-configuration development grid. Its frozen parameters were attack threshold 3, legitimate threshold 2, pressure decay 1, benign streak 10, minimum dwell 3, and backoff cap 0.

adaptive_exp was a secondary experiment-scale configuration with thresholds 2/2, benign streak 10, dwell 5, and backoff 4. It was not the primary hypothesis test.

### 4.3 Estimand and decision rule
The primary estimand is the paired per-seed difference adaptive_dev − fixed_L1 using each seed’s mean loss over both streams. The 95% confidence interval is a percentile bootstrap over the 20 paired seeds with 5000 resamples and bootstrap seed 0.

The frozen decision rule defines adaptive improvement when the CI upper bound is below zero, worsening when the CI lower bound is above zero, equivalence when the entire CI lies inside ±0.02, and otherwise inconclusive.

### 4.4 Confirmatory/exploratory separation
The confirmatory comparison is only adaptive_dev versus fixed L1. Per-stream comparisons, comparisons against fixed L2/L3, and adaptive_exp comparisons are secondary descriptive analyses with no multiplicity correction. The earlier F3 v2 run is exploratory and was not preregistered.

A previous offline replay incorrectly treated L0 as equivalent to L1; that replay was corrected before the confirmatory design was frozen. The selected adaptive configuration was unchanged.

## 5. Results

### 5.1 Controller reliability
The redesign addressed unreachable de-escalation, L2–L3 oscillation, lack of attack memory, detector padding bypass, an unsafe stripping sanitizer, input validation, and a concurrency race. Regression tests cover these failure modes. These are software-reliability findings, not evidence that the resulting defense is more secure than a fixed policy.

**Source:** docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md; docs/ADAPTIVE_CONTROLLER_SPEC.md; PR #93 test evidence.

### 5.2 Exploratory F3 v2
The exploratory F3 v2 experiment used two models, five seeds, two streams, 150 episodes per run, and 120 runs. It found no adaptive configuration that dominated the fixed levels. On llama-3.1-8b-instruct, fixed L3 had the lowest ASR but the highest cost among the main fixed levels, while adaptive arms occupied intermediate security/cost positions. On gpt-4o-mini, fixed L1 dominated the adaptive arms in the reported comparison.

The fresh v2 pool exposed a detector generalization problem: recall was 0.258, compared with 0.943 on the v1 design pool. This evidence supports a detector-bottleneck interpretation rather than a controller-superiority interpretation.

**Source:** results/q1_f3_real_llm_v2/FINDINGS.md; results/q1_f3_real_llm_v2/SUMMARY.md.

### 5.3 Confirmatory F3

| Arm | Loss | ASR | Utility | Cost |
|---|---:|---:|---:|---:|
| Fixed L1 | 0.3020 [0.2881, 0.3155] | 0.017 | 0.630 | 0.100 |
| Fixed L2 | 0.3300 [0.3178, 0.3416] | 0.012 | 0.628 | 0.132 |
| Fixed L3 | 0.3779 [0.3699, 0.3860] | 0.003 | 0.622 | 0.186 |
| Adaptive dev | 0.2902 [0.2777, 0.3029] | 0.017 | 0.613 | 0.080 |
| Adaptive exp | 0.3683 [0.3563, 0.3798] | 0.008 | 0.619 | 0.169 |

**Source:** results/f3_confirmatory/RESULTS.md.

| Comparison | Mean difference | 95% CI | Interpretation |
|---|---:|---|---|
| Adaptive dev − Fixed L1 | -0.0118 | [-0.0258, +0.0024] | Inconclusive |

The interval crosses zero and extends beyond the ±0.02 equivalence margin. Thus the point estimate is favorable to adaptive dev, but the prespecified analysis does not establish superiority or equivalence.

**Source:** results/f3_confirmatory/RESULTS.md; docs/F3_CONFIRMATORY_CONTRACT.md.

### 5.4 Secondary analyses
The burst-only adaptive-dev comparison against fixed L1 was -0.0170 [-0.0339, -0.0007]. This is a secondary, uncorrected analysis and is not sufficient to overturn the primary inconclusive result.

Adaptive dev was lower-loss than fixed L2 and L3 in secondary pooled comparisons, but those levels were not the prespecified best-fixed comparator. Adaptive exp was worse than fixed L1 by +0.0663 [+0.0550, +0.0771]. These results illustrate configuration sensitivity.

**Source:** results/f3_confirmatory/RESULTS.md.

### 5.5 Detector bottleneck
In the confirmatory run, all arms received the same semantic-plus-regex detector verdict for each prompt. Detector recall was 0.82 and benign-flag rate was 0.028. Earlier exploratory evaluation found regex recall of 0.21–0.26 on 24 fresh attacks, while the semantic guard raised fresh-pool recall to 0.75 with 0/20 benign prompts flagged in the corresponding check.

This is central to interpretation: a controller cannot escalate in response to an attack that its feedback channel does not identify.

**Source:** results/f3_confirmatory/RESULTS.md; docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md; results/q1_f3_real_llm_v2/FINDINGS.md.

## 6. Discussion

### 6.1 What the result establishes
The case study establishes that the adaptive controller can be engineered to satisfy the tested operational properties. The confirmatory experiment does not establish that these controller improvements translate into a statistically demonstrated gain over fixed L1.

### 6.2 Why was there no demonstrated gain?
One plausible explanation is limited headroom, but this is a hypothesis rather than a causal finding. In development evidence, L1 already provided much of the benefit obtainable from delimiting, while L3 added blocking and cost. Adaptation can save cost by spending time at L0 or lower levels, but the security gain available from escalation is constrained by detector coverage and lower-level performance.

The confirmatory data are consistent with this interpretation: adaptive dev used less defense cost than L1 (0.080 versus 0.100) but also had lower measured utility (0.613 versus 0.630), while ASR was equal at 0.017. The resulting loss difference was not sufficiently precise to establish a benefit.

This does not prove that headroom is the cause. A different detector, utility measure, task distribution, or model could produce a different result.

### 6.3 Detector coverage dominates controller sophistication
The strongest cross-experiment lesson is that adaptation cannot compensate for an inadequate feedback channel. The exploratory fresh-pool evaluation showed a large reduction in regex recall relative to the pool on which the patterns were designed. The semantic guard improved recall, but it adds an additional LLM dependency and its cost was excluded from the loss.

Future controller work should therefore treat detector quality as a first-class experimental factor rather than assuming a sufficiently strong detector.

### 6.4 What would change the conclusion?
A stronger claim would require multiple independently generated pools, multiple models, an independently specified utility metric, explicit accounting for semantic-guard cost, adaptive or held-out attackers, and enough seeds to narrow the primary confidence interval.

## 7. Threats to Validity and Limitations

**Construct validity.** Utility is measured with a keyword-based check. The confirmatory utility is 0.63 for every arm, including cases where the model may not have known the answer.

**Internal validity.** The primary adaptive configuration was selected from 16 development candidates. The semantic-guard prompt was developed after observing regex misses on earlier data, so the exploratory v2 guard result is not blind.

**External validity.** The confirmatory experiment uses one relatively small model, synthetic text-only probes, two streams, and 20 seeds. It does not evaluate long-horizon agents, real tools, persistent state, or adaptive attackers.

**Measurement validity.** Detector recall and utility directly affect feedback and the composite loss. Semantic-guard inference cost is excluded from the cost metric. Development replay ignores per-prompt effects.

**Data generation.** The confirmatory pool was written by one generator model. Different authorship from the model under test does not establish broad corpus independence.

**Security validity.** The controller does not eliminate prompt injection. Detector false negatives can prevent escalation, and the semantic guard is itself an LLM component.

**Implementation validity.** The controller is non-learning and threshold-based. Its behavior is not representative of learned adaptive policies. The runtime object is not thread-safe as a whole and is intended to use one instance per stream.

**Reproducibility scope.** Confirmatory analysis can be re-derived offline from committed traces, but live reruns require provider access and can produce different traces. The separate frozen Track A / harness snapshot must not be conflated with adaptive F3 evidence.

**Source:** docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md; docs/F3_CONFIRMATORY_CONTRACT.md; docs/ADAPTIVE_CONTROLLER_SPEC.md; REPRODUCIBILITY.md.

## 8. Ethics and Dual Use

Prompt-injection research contains adversarial examples. The public repository should expose only the minimum material needed to understand the threat model and reproduce the reported analysis. Operationally reusable payloads should be staged in a controlled artifact when required by the target venue or disclosure policy.

The manuscript does not reproduce payloads. Attack-template release is an explicit TODO rather than an implicit claim of unrestricted release.

AI assistance and dataset-generation provenance should be disclosed according to the target venue’s policy. Author, venue, anonymization, and exact disclosure language remain TODOs.

## 9. Reproducibility

The adaptive F3 raw traces needed to re-derive the confirmatory analysis are committed. Confirmatory design freeze: a00ef03. Confirmatory execution/write-up commit: c4421fa. Seeds: 1000–1019. Model: meta-llama/llama-3.1-8b-instruct. Pool: results/f3_confirmatory/pool_v3.json. Analysis: scripts/f3_confirmatory.py --analyze. Raw runs: results/f3_confirmatory/runs_v3.json. Episodes: results/f3_confirmatory/episodes_v3.jsonl. Guard cache: results/f3_confirmatory/guard_cache_v3.json. Cost record: results/f3_confirmatory/cost_v3.json.

The confirmatory experiment was a one-execution experiment; rerunning the live experiment is not part of the protocol. Offline analysis from committed traces is the preferred reproducibility path.

The repository-level reproduction command in REPRODUCIBILITY.md concerns the separate E1–E3 negative-result snapshot and must not be presented as reproducing the adaptive F3 live run.

**Source:** docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md; docs/F3_CONFIRMATORY_CONTRACT.md; REPRODUCIBILITY.md.

## 10. Conclusion and Future Work

This case study examined whether a threshold-based adaptive prompt-injection controller could be made reliable and whether adaptation could improve a frozen security–utility–cost objective over the best fixed defense level.

The controller can be made operationally reliable in the tested sense: de-escalation is reachable, oscillation is controlled, attack memory is represented, inputs are validated, and transition history is bounded. However, the confirmatory F3 result does not demonstrate a gain over fixed L1. The primary paired loss difference was -0.0118 with a 95% CI of [-0.0258, +0.0024], which is inconclusive under the prespecified rule.

The most important limitation is detector coverage. A controller cannot react to attacks that its feedback channel does not identify. The scientific value of this case study is therefore not evidence that adaptive defense is superior, but evidence that controller reliability and end-to-end security benefit are distinct questions and should be measured separately.

Future work should test the hypothesis under independent pools, stronger and more diverse models, adaptive attackers, realistic tool-using agents, better utility measures, and complete accounting of detector and guard costs.

# Appendix A. Frozen F3 Contract Summary
The authoritative contract is docs/F3_CONFIRMATORY_CONTRACT.md. This appendix summarizes rather than replaces it.

# Appendix B. Full Confirmatory Tables
The complete paired comparisons and per-seed loss values are in results/f3_confirmatory/RESULTS.md and should be treated as the numerical source of truth.

# Appendix C. Review History
The controller passed through iterative strict reviews. Earlier reviews identified operational defects including unreachable de-escalation, oscillation, weak attack memory, detector bypasses, unsafe sanitization, and validation/state-management issues. Later review judged the redesigned case study more favorably while retaining the absence of demonstrated superiority over the best fixed level.

**Source:** docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md and repository review/audit records.

# Appendix D. Claim-to-Evidence Map

| Claim | Primary evidence | Type |
|---|---|---|
| Controller reliability | docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md; docs/ADAPTIVE_CONTROLLER_SPEC.md | Implementation |
| Exploratory trade-off | results/q1_f3_real_llm_v2/FINDINGS.md; SUMMARY.md | Exploratory |
| Confirmatory primary result | results/f3_confirmatory/RESULTS.md | Confirmatory |
| Detector bottleneck | v2 findings + case-study document + confirmatory results | Mixed |
| Reproducibility scope | REPRODUCIBILITY.md + F3 contract | Method/provenance |

# References

[1] Yupei Liu, Yuqi Jia, Runpeng Geng, Jinyuan Jia, and Neil Zhenqiang Gong. “Formalizing and Benchmarking Prompt Injection Attacks and Defenses.” 33rd USENIX Security Symposium, 2024, pp. 1831–1847. DOI/URL verified.

[2] Jingwei Yi, Yueqi Xie, Bin Zhu, Emre Kiciman, Guangzhong Sun, Xing Xie, and Fangzhao Wu. “Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models.” DOI 10.1145/3690624.3709179.

[3] Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel Kang. “InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents.” Findings of ACL 2024, pp. 10471–10506. DOI 10.18653/v1/2024.findings-acl.624.

[4] Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr. “AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.” NeurIPS 2024 Datasets and Benchmarks Track. DOI 10.52202/079017-2636.

[5] Edoardo Debenedetti, Ilia Shumailov, Tianqi Fan, Jamie Hayes, Nicholas Carlini, Daniel Fabian, Christoph Kern, Chongyang Shi, Andreas Terzis, and Florian Tramèr. “Defeating Prompt Injections by Design.” arXiv:2503.18813, 2025.

[6] [CITATION NEEDED: verified context-aware prompt-injection defense/provenance-aware auditing paper for final venue-specific related-work coverage.]