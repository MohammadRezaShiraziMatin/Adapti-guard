# Liu / JEV / trajectory-judge / Pathade read: 2026-10-15
Source PDFs and text: /workspace/pivot-checks/papers/ (arxiv.org/pdf, fetched today, all v1 except 2609.00038 v2). No model or API calls, no repo writes.

## 1. Liu 2610.03448 (read in full, incl. appendices A–E)
Title verified: "Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents". Zhuowen Liu (JAIST), v1, 2 Oct 2026. Code: github.com/lzwhehe/benign-instruction-bench (I did not open it).

- **Datasets (Table 1):**
  - General benign text: 7,504 chunks (READMEs, AESLC email, FineWeb-Edu).
  - AgentDojo **v1.2**, 4 suites (workspace, travel, banking, slack):
    - AD-Clean: 339 outputs from 97 tasks.
    - AD-Matched: important_instructions, ignore_previous, direct; 585 benign / 432 injected.
    - AD-Shift: tool_knowledge, injecagent, system_message, plus 2 important_instructions variants; 975 / 720.
  - τ-bench retail + airline: 675 tasks, 1,533 clean outputs. TB-Matched: InjecAgent attacks the author inserted into product names, 584 injected.
  - BIPIA: email QA, table QA, code; test-half attacks; 1,200 benign / 2,435 injected.
  - **AgentDyn: not used; it is not mentioned anywhere in the text.**
- **How detectors are invoked:**
  - Each detector is run "as its model card documents" (§4.1, App. A).
  - Prompt Guard 1/2 (both sizes) are listed as "segmented": long inputs are split into 512-token segments and the max over windows is taken.
  - Sheltron: overlapping windows, stride 768.
  - All other detectors are truncated to their context length (512–2,048).
  - Each tool output is scored separately. A task counts as blocked if any of its outputs is flagged. Nothing is concatenated across messages.
  - The judges see "User request + Tool <name> returned", with the output truncated to 6,000 characters.
- **Whole vs chunked PG2: not compared.** They report only the segmented configuration. There is no ablation of unchunked vs chunked or of truncation.
- **Agent ASR / utility: not measured.** Everything is offline replay of ground-truth calls with no LLM agent. Metrics are detector FPR, TPR at 1% FPR, AUROC, and a task-level "blocked" proxy: the share of tasks with at least one flagged benign output. That proxy is only a stand-in for lost utility. They do not run an agent, so ASR under a defense is not measured.
- **Benchmark-code detector invocation: not examined.** They mention that AgentDojo ships a detector baseline (§3, "the detector baseline that AgentDojo ships [7]"). They never inspect how AgentDojo's `TransformersBasedPIDetector` calls the pipeline (no truncation, no chunking), and they never re-score published AgentDojo/AgentDyn defense results.
- Other findings that overlap with us:
  - PG2-86M FPR on AD-Clean is 0.6%, and 0.0% on TB.
  - PG2-86M TPR at 1% FPR: 69.4% on AD-Matched, 57.9% on TB.
  - YAML key stripping moves FPR (Finding 5).
  - The differential-replay labelling pitfall (App. E) matches our caveat.
- **What remains for us:**
  - (a) AgentDyn suites: shopping, github, dailylife.
  - (b) The harness fidelity point: AgentDojo/AgentDyn call PG2 unchunked on outputs up to about 2.4k tokens (AgentDyn) and 9.4k tokens (AD workspace), against the 512-token card guidance.
  - (c) Whether that changes the *published* defended ASR/utility numbers.
  - (b) depends on how PG2 actually behaves past 512 tokens. That is unverified: our proxy test showed DeBERTa-family models still flag past 512 tokens.
  - The prior stats show only about 8% of injected outputs start past token 510.
- **Verdict:** (a)+(b) on their own are an **appendix / short workshop note**, not a paper. They could reach paper scale only if (c) shows a material shift in published defense rankings, or if they are bundled with Part 2 (judge-vs-checker) and run-to-run noise under a single "benchmark-harness fidelity" framing.

## 2. JEV 2609.34862 and trajectory-judge 2609.00038
- **2609.34862: verified.** "JEV as a Judge for Agent Trace Security: An Empirical Comparison with Generative LLM Judges". Zhiqiang Wang and Yichao Gao (USTC), 28 Sep 2026.
  - Compares the typed judge JEV against 4 generative judges on 5,219 saved trajectories (R-Judge, ATBench500, TraceSafe subset, MCPHunt) against benchmark or revised labels.
  - Reports F1, coverage, latency, and cost.
  - **No AgentDojo/AgentDyn, no deterministic-checker baseline, no per-defense breakdown, no defense ranking flips.** The only rankings it discusses are of judges across datasets.
- **2609.00038: verified.** "trajectory-judge: What Outcome-Only LLM Judges Miss on Agent Trajectories". Hadi Mohammadi (Utrecht), v2, 2 Oct 2026, NeurIPS 2026 workshop.
  - Uses its own deterministic support-desk testbed with a strict rule checker and a fault injector; 400 trajectories are labelled exactly.
  - Measures the paired discrimination of a 14B judge (outcome-only vs step-wise) against the checker.
  - **Not prompt injection, no defenses, no ranking flips.**
- **Overlap with Part 2: low.** Both are methodological neighbours, worth citing for "judge error vs exact labels" (trajectory-judge's paired-vs-clean idea is reusable). Neither measures judge-vs-checker error *per defense* on defended AgentDojo/AgentDyn runs, or whether defense rankings flip. Pathade (below) motivates exactly this analytically.

## 3. Run-to-run noise / ranking stability
- **Pathade, Pawar, Patil 2609.25173: verified.** Exact limitation wording (§VIII): "We have not run defenses end to end, so we report no empirical ranking inversion; that experiment is the natural next step and needs model access we did not have."
  - Their claim about rankings is analytical: two defenses whose true ASRs differ by 5 points are ranked in the wrong order about 21% of the time at m=100.
  - On judges: "That is the finding: not that judges do invert rankings, but that their calibration is unmeasured" (§V-B). This also directly motivates our Part 2.
- Brief web search (2 queries), nearby work only:
  - REDAgentBench 2608.10669: 43 local model-ranking inversions across judging views; these are models, not defenses, and the inversions come from judging view, not seeds.
  - Threat-Preserving Representation Sensitivity 2610.03585: lists whether defense rankings reverse as future work.
  - A general-LLM prompt-ranking stability paper, 2606.24381.
  - An iThome blog that reran AgentDojo 10 times (one config, no defense ranking).
- **Not found:** any 2026 paper that empirically measures run-to-run stability of prompt-injection *defense* rankings. This is a brief search, so treat it as unverified.

## 4. Plan (not run): one-day test, PG2-86M whole vs 512-chunked; cost $0 on the user's machine
Prerequisites:
- An HF account that has accepted the Llama 4 / Prompt Guard 2 license at huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M, plus `huggingface-cli login`.
- CPU is fine (86M params). About 3k–10k outputs × ≤10 windows takes minutes to about 1 h on CPU.

Steps:
1. Set up the environment: `python -m venv v && pip install torch transformers` plus the AgentDyn and AgentDojo packages (local clones, `pip install -e`). No LLM keys are needed.
2. Build the corpus, reusing `replay.py`:
   - For each suite in 7 suites × user tasks, replay `GroundTruthPipeline` in the clean environment, then in an environment injected with each attack template (important_instructions, ignore_previous, direct, tool_knowledge).
   - Label an output as injected iff it differs from the clean output for the same call (differential replay, as in Liu App. E).
   - Also include the tool messages from the released undefended gpt-4o traces that Part 1 already used (`dyn_gpt4o.csv`, `ad_gpt4o.csv` sources), because these contain post-hijack outputs.
   - Write a JSONL with fields suite, task, call, label, text, n_tokens (PG2 tokenizer), and the injection start offset.
3. Score each output three ways in `score_pg2.py`:
   - A. As benchmarked: `pipeline("text-classification", model=PG2)(text)` with no truncation. This mirrors `TransformersBasedPIDetector.detect`, so first confirm in `dyn/` that it actually runs at all past 512 tokens, or whether it errors or truncates silently.
   - B. Truncated to 512 tokens.
   - C. Card-style: 512-token windows (non-overlapping, plus a variant with stride 256), taking the max of the malicious probability.
   - Record the score and the flag at 0.5.
4. Metrics: FPR on benign and TPR on injected for A/B/C at 0.5 and at 1% FPR, stratified by length bucket (≤512, 512–2k, >2k) and by injection start (before or after token 510). Count flip cases in both directions: outputs flagged by C but not A, and the reverse.
5. Task-level proxy: for each (user task, injection task), compute "blocked" under A vs C. Because the PG2 defense drops flagged outputs, a change in flags on the output that carries the injection suggests a possible change in ASR/utility. Report this explicitly as a proxy, not agent ASR. Real ASR would need agent reruns, which are out of scope.
6. Sanity checks: reproduce Liu's PG2-86M numbers on AD-Clean / AD-Matched (FPR 0.6%, TPR at 1% FPR 69.4%) with config C. If they match, our pipeline agrees with theirs.
7. Output a single `pg2_whole_vs_chunk.md` with a table and a list of diverging examples.

Decision rule:
- If A and C differ on fewer than ~1% of injected outputs, the issue is cosmetic and goes in a footnote or appendix.
- If they differ on the more than 8% of outputs that are long and inject late, and that changes task-level blocking, it is worth a short paper section combined with Part 2.
