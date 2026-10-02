# Related-work notes (read 2026-09-30)

**Evidence level.** Papers marked **[full text]** were retrieved as raw text (arXiv 2609.32691). The others were read through alphaXiv's *AI-generated structured report* of the paper, not the PDF. Treat every number below as **to be re-checked against the PDF before it appears in the manuscript**; the qualitative claims are stable across the reports. Papers not listed here remain `[VERIFY]` in the skeleton. Several 2026 arXiv items are recent preprints.

## Benchmarks
- **AgentDojo** (arXiv 2406.13352; ETH Zurich / Invariant Labs). Stateful multi-tool environments (Workspace, Slack, Banking, Travel), 97 user tasks, 27 injection tasks, 629 security cases; **deterministic state-based utility and security checks, not LLM evaluators**; metrics: benign utility, utility under attack, targeted ASR. Findings reported: capable models are easier to attack (an "inverse scaling" trend); the "important message" phrasing beats "ignore previous instructions"; attacks placed at the end of tool output work best; of the defenses tested, **a tool filter (restrict tools before reading untrusted data) was the most effective (ASR ≈ 7.5%)**, a BERT detector hurt utility through false positives, prompt sandwiching helped against static attacks but was not expected to survive adaptive ones.
  *Relation:* our execution-level endpoint follows the same principle (state/executor, not text/LLM judge). Our `ind_important_instr_*` families use its public "important message" style. Our TOOLDENY result (blocks by construction, large benign-utility cost) is the same trade-off as its tool filter; our text-level B3 and CORE match its finding that delimiter/detector-style defenses are weak.
- **InjecAgent** (arXiv 2403.02691; UIUC). 1,054 single-turn cases, 17 user tools × 62 attacker instructions, direct-harm and data-stealing categories, 30 agents; base vs "enhanced" setting with a fixed hacking prompt. Findings reported: prompted GPT-4 ASR ≈ 24% (≈ 47% enhanced), fine-tuned GPT-4 ≈ 7%; the **user case (what the retrieved content looks like) predicts success more than the attacker instruction**, and high content freedom raises ASR. Limitations it states: single fixed hacking prompt, attacker text is the entire content, single-turn.
  *Relation:* consistent with our finding that framing (authority claim 0.96 vs footer 0.00) and model matter more than the instruction itself; our harness is multi-turn and executes calls.

## Adaptive evaluation and why static results mislead
- **Zhan et al., "Adaptive Attacks Break Defenses Against IPI"** (arXiv 2503.00061; UIUC). Eight defenses (detection: fine-tuned/LLM/perplexity; input-level: instructional prevention, delimiters, sandwich, paraphrasing; adversarial fine-tuning) on InjecAgent with white-box GCG-family attacks on Vicuna-7B and Llama3-8B; **ASR > 50% against every defense**. Limitations it states: white-box, first-step actions, 100-case subset.
- **"The Attacker Moves Second"** (arXiv 2510.09023; multi-lab). 12 defenses (prompting incl. Spotlighting and Sandwiching, training incl. StruQ/MetaSecAlign, filters incl. PromptGuard/PIGuard, secret-knowledge incl. MELON) attacked adaptively (gradient, RL, search, 500+-participant human red-teaming); ASR > 90% for most; Spotlighting and Sandwiching > 95% on AgentDojo; MELON 76% without and 95% with knowledge of the defense; warns about reward hacking of automated scorers.
  *Relation:* our B3 (a spotlighting-style wrapper + detector) and PHASE1-CORE are exactly the families reported broken under adaptive attack; our results show they do not even move a **non-adaptive** independent attack set. No adaptive attacker was run here (explicit limitation).
- **AutoDojo** (arXiv 2606.15057; **read via the earlier full report**). Cheap black-box adaptive attacker recovers ASR against filter/prompt defenses (e.g. PIGuard 0.0% → 28.0% on GPT-4o-mini); system-level defenses (Progent, DRIFT) show no gap on under-specified tasks.

## System-level defenses (the comparators a defense paper would need)
- **CaMeL** (arXiv 2503.18813; Google/DeepMind/ETH). Privileged/quarantined LLMs, custom interpreter with data-flow tracking, capabilities and Python-defined policies; 77% task success with provable security vs 84% undefended on AgentDojo; 0 successful injections with policies (residual cases outside its threat model); token overhead ≈ 2.7–2.8×; explicit non-goals (text-to-text effects, phishing); side channels acknowledged.
- **Progent** (arXiv 2504.11703; UC Berkeley/UCSB). Deterministic privilege control at the tool-call boundary: allow/forbid rules on arguments, LLM-generated task policies, SMT-checked policy expansion; AgentDojo ASR 39.9% → 1.0%, ASB 70.3% → 3.9%; adaptive attacks raised it to ≤ 4.2% in its own tests; states failures when a malicious call is near-identical to a benign tool call within the task.
  *Relation:* our ARGALLOW is a static, hand-written cousin of this idea; our `create_record_exfil_v1` finding (an "attack" that is textually a legitimate request) is the same limitation the authors describe (attacks that stay inside the least-privilege set).
- **MELON** (2502.05174), **Task Shield** (2412.16682), **DRIFT**, **ActGuard** (2609.14987), **ToolFence** (2609.37196), **ROPE** (2608.27496) — abstracts only. `[VERIFY]`
- **arXiv 2606.26479** (out-of-band defenses; earlier full report): systematises CaMeL/FIDES/Progent/RTBAS/FORGE as reference-monitor designs and specifies an adaptive protocol; preliminary Progent run on Qwen2.5-7B.

## Evaluation validity
- **arXiv 2609.32691 [full text].** Four defect classes (silent payload non-delivery, tool-identity scoring, false-rejection conflated with incapacity, no audit trail); tool-identity scoring 21.7% vs argument-level 1.2%; a model reported at 62.8% ASR registers 0% after correction; recommends Fisher exact + Holm, Wilson intervals, a priori power; releases a harness with argument-level attacker predicates and mandatory trace persistence.
  *Relation:* the measurement-validity table in our manuscript (§4) extends it with (i) pre-target-block labelling, (ii) scenario construct validity when the user turn is the requester, (iii) authorship coupled to detector development, (iv) pooled vs per-model admission. Its Table I ablation style is the model for our Figure 1.

## Positioning statements the evidence supports
1. Static, self-authored packs overstate defenses (Zhan; Attacker Moves Second; AutoDojo; ours: 36/36 → 0/168).
2. Execution-level, state-based endpoints are the accepted standard (AgentDojo; 2609.32691); LLM-judge endpoints (our Tracks A/B) are weaker.
3. Tool-boundary policies dominate text-level defenses in the literature; our data agree (TOOLDENY/ARGALLOW by construction vs B3/CORE no effect), with the caveat that we did not implement CaMeL/Progent.
4. What is new here is not a defense but a **worked, self-contained case** of how four measurement choices reverse a conclusion on one system, with all traces released.

## Gaps to close before submission
- Re-verify quoted numbers against PDFs (reports may paraphrase).
- Read MELON, Task Shield, DRIFT and one 2026 system-level paper in full text.
- Decide whether to add a Progent-style or CaMeL-style baseline (needs implementation and an agent framework; not in scope of today's budget).
