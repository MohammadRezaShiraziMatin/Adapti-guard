# Pivot checks: does defense evaluation measure the right thing from the defense side?
Date: 2026-10-15 (Tehran). Read-only. No LLM or API calls. The only model runs were local CPU tokenizer/classifier checks on free Hugging Face models. No repo writes.
Artifacts are in /workspace/pivot-checks/: clones `ad/` (agentdojo) and `dyn/` (AgentDyn), shallow clones at HEAD on 2026-10-15; `replay.py`, `replay_out.txt`, `measure.py`, `dyn_gpt4o.csv`, `ad_gpt4o.csv`, `stats.txt`, `longinput_test.txt`.

## Verdict
- **Part 1 is feasible. The truncation hypothesis, as stated, is false for these harnesses. Novelty is low to partial.**
  - Offline ground-truth replay works for all 157 user tasks in 7 suites (AgentDyn package).
  - The harness does not truncate. The HF pipeline is called without `truncation`, and these DeBERTa-v2 models use relative positions, so the detector sees the whole tool output.
  - Injections in AgentDyn mostly start early. The ad-banner (`injection_web_*`) outputs are short (median 177–360 tokens).
  - Liu 2610.03448 already does "replay ground-truth tool calls without an LLM, plus Prompt Guard 2 on AgentDojo tool outputs, with 512-token segmentation".
  - What remains open: AgentDyn suites, and the out-of-window issue. Prompt Guard 2 is documented for 512 tokens but is applied to up to ~2.4k tokens (AgentDyn) and ~9.4k tokens (AgentDojo workspace) with no chunking. One option is a measured comparison of unchunked (as benchmarked) vs Meta-recommended chunking, as a fidelity check on reported detector results. It is a narrower claim than "never scanned".
- **Part 2 is partially novel.** Judge vs deterministic disagreement is known (Hofer 2606.10525; the harness/judge paper in RELATED_2026; our own E1). I found no one doing a per-defense ranking-flip analysis on the released AgentDojo/AgentDyn defended traces (unverified beyond the 4 papers read plus the prior notes). Running it needs judge LLM calls, which were out of scope today.

## Task 1: traces, replay, detector code
**Traces: yes, full per-episode JSON.**
- Example file: `dyn/runs/google_gemini-2.5-flash-prompt_guard_2_detector/github/user_task_12/important_instructions/injection_task_4.json`.
- Keys: suite_name, pipeline_name, user_task_id, injection_task_id, attack_type, `injections` (exact injected text per vector), `messages` (system/user/assistant/tool, with full tool outputs), error, benchmark/package version, duration, `utility`, `security`.
- AgentDojo runs have the same schema. In older runs, message content is a plain string rather than blocks.
- **Defense I/O is not logged.**
  - There is no detector score or input.
  - The only trace is that flagged tool messages are overwritten in place with `<Data omitted because a prompt injection was detected>` (`pi_detector.py` L49–55, L111–112).
  - So the binary detector decision is recoverable, but the scores are not. Unflagged tool content equals the detector input in `mode="message"`.
- Count of files containing that marker:
  - AgentDojo: 622 (gpt-4o-2024-05-13-transformers_pi_detector).
  - AgentDyn: 19–638 per detector pipeline (e.g., PG2: 203–337 for most models, 19 for llama-3.3-70b).

**Offline replay: yes.**
- `GroundTruthPipeline` (`dyn/src/agentdojo/agent_pipeline/ground_truth_pipeline.py` L12–39) calls `task.ground_truth(env)`, then `runtime.run_function(...)`. It is also used in `task_suite.py` L432 and L462 and in `attacks/base_attacks.py` L52.
- I ran it with a marker injected into every vector (`replay.py`, output in `replay_out.txt`): 0 failures.

| suite | user tasks | tool outputs | outputs containing injection |
|---|---|---|---|
| workspace | 40 | 84 | 53 |
| travel | 20 | 124 | 29 |
| banking | 16 | 33 | 16 |
| slack | 21 | 98 | 29 |
| shopping (AgentDyn) | 20 | 190 | 46 |
| github (AgentDyn) | 20 | 119 | 36 |
| dailylife (AgentDyn) | 20 | 125 | 47 |

Caveat: replaying only the user task's ground truth does not reproduce tool calls the agent makes after it is hijacked. Liu (§4.2, App. E) warns that substring labelling fails because of YAML re-wrapping and uses differential replay instead.

**Detector code: no truncation and no chunking.**
- `TransformersBasedPIDetector.detect` (`ad/...pi_detector.py` L156–159, identical in dyn) runs `self.pipeline(tool_output)[0]`. There is no `truncation=` and no chunking.
- `mode="message"` scans each tool message separately (L68–96). `full_conversation` concatenates everything.
- AgentDyn wires PG2 as `meta-llama/Llama-Prompt-Guard-2-86M` with threshold 0.5 and mode "message" (`dyn/.../agent_pipeline.py` L609–628). AgentDyn also adds `trust_remote_code=True` and case-insensitive label matching (diff L154 and L158).
- AgentDojo ships only the ProtectAI detector (`agent_pipeline.py` L238–246).
- **Empirical check** (`longinput_test.txt`, CPU, free model protectai/deberta-v3-base-prompt-injection-v2):
  - The tokenizer's `model_max_length` is about 1e30, so even `truncation=True` does not cut anything.
  - The config is deberta-v2 with `position_biased_input: False` and relative attention, so a 3,863-token input runs without error.
  - An injection placed at the end of 3.8k tokens of HTML filler is still flagged (score 0.99999).
  - The mdeberta-v3-base config (the PG2-86M base) has the same position settings.
  - **Unverified for PG2 itself:** the model is gated and I did not access it. Its custom tokenizer and remote code might differ.

## Task 2: Prompt Guard 2 window
- HF model card, https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M, fetched 2026-10-15: "Context length: Both Llama Prompt Guard 2 models support a 512-token context window. For longer inputs, split prompts into segments and scan them in parallel to ensure violations are detected."
- The card also points to "Inference utilities … for efficiently running Prompt Guard in parallel on long inputs".
- Base models per the card: 86M is mDeBERTa-base, 22M is DeBERTa-xsmall. The card applies to both. I did not fetch the 22M card separately, nor the llama.com / PurpleLlama docs.
- **Neither AgentDojo nor AgentDyn chunks** (see Task 1). They pass the whole tool output to the pipeline.
- **Measured** (`stats.txt`):
  - Method: tokenizer `microsoft/mdeberta-v3-base` as a proxy. PG2 uses a "modified tokenizer", so counts are approximate.
  - Data: tool messages in released undefended gpt-4o runs that contain the injection's first line.
  - This undercounts YAML-rewrapped injections.

| set | n | median tok | max | >512 tok | inj. start median tok | inj. starts >510 tok |
|---|---|---|---|---|---|---|
| AgentDyn dailylife | 406 | 238 | 1156 | 19% | 84 | 19% (mostly `injection_new_email`) |
| AgentDyn github | 284 | 1218 | 1559 | 57% | 19 | 0% |
| AgentDyn shopping | 276 | 533 | 2454 | 58% | 16 | 2% |
| AgentDojo workspace | 2467 | 466 | 9442 | 42% | 242 | 24% |
| AgentDojo travel/banking/slack | 4845 | 115–370 | ≤2037 | 0–27% | 20–213 | 0% |

  - Overall, 8.5% (AgentDyn) and 8.1% (AgentDojo) of injected outputs have the injection starting past token 510.
  - The AgentDyn ad-banner vectors (`injection_web_*`, "Injected content in a web page through advertisement") have median outputs of 177–360 tokens. This is not the long-HTML case.

## Task 3: papers (all four verified on arXiv abs and API)
1. **2610.03448**: "Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents". Zhuowen Liu (JAIST). Submitted 2026-10-02.
   - What they do: replay the ground-truth tool calls of AgentDojo and τ-bench without an LLM, label by differential replay, and evaluate 15 detectors including PG2 22M/86M (512 ctx, segmented, max over windows; App. A) plus 2 LLM judges. They report FPR, TPR at 1% FPR, and training-data audits.
   - Overlap with Part 1: **high (near-full on method)**. Not covered: AgentDyn; the fidelity of the benchmark harness's own detector call (they run detectors "as the card documents", not as AgentDojo does). Overlap with Part 2: partial (judges as detectors, not as outcome scorers).
   - **Threat: HIGH. Must cite and differentiate.**
2. **2610.19133**: "TRACER: Trace-Regularized Training Against Indirect Prompt Injection". Mishra, Lahlou, Lukas (MBZUAI). 2026-10-13.
   - What they do: channel-aware GRPO adversarial training on GSM8K. The "framing gap" is follow-up 18% vs RAG 53% ASR. Answer extraction is used for ASR.
   - Overlap: Part 1 none; Part 2 none (marginal: the same payload behaves differently by wrapper). Threat: low.
3. **2610.04504**: "The Same Zero: Why Identical ASR Can Imply Different Guarantees in LLM-Agent Security". Yajie Yin. 2026-10-03.
   - What they do: a VAL taxonomy (L0–L5) over 22 defenses, a self-built testbed plus AgentDojo banking. They note the official checks missed 11 tool-level attacks (a 14.7% conditional miss rate), plus a judge-reliability appendix.
   - Overlap: Part 1 none; Part 2 partial (deterministic-checker misses, the "anchor" of verdicts). Threat: low to medium.
4. **2605.30454**: "The Surface You Test Is Not the Surface That Breaks". Sakib, Haque, Amin, Arman (Univ. of Dhaka); the request's "Arman et al." is the corresponding author. 2026-05-28.
   - What they do: a byte-identical payload in a tool output vs a tool description, 13 models. 44.9% of model pairs invert their ranking, and defenses depend on the surface. They use deterministic predicates (3 banking predicates corrected).
   - Overlap: Part 1 partial (where the defense operates vs where the injection lands); Part 2 none to partial (ranking-flip methodology, but across surfaces, not across scorers). Threat: medium-low.

Other Part-2 prior art from earlier notes, not re-verified today: Hofer/Debenedetti/Tramèr 2606.10525 (judge precision 29–52%); the RELATED_2026 harness paper (a state judge gives +7.7–11.7 ASR over a trajectory judge).

## Suggested reframing
- Part 1: "Detectors as deployed in benchmarks differ from the detector as documented". This covers no chunking past the 512 window (PG2), per-message scanning, and the fact that only binary decisions are logged.
- The quantity to measure is the PG2 score unchunked vs chunked on the replayed outputs. It needs the gated PG2 weights, run locally (no API).
- Position it explicitly against Liu 2610.03448.
