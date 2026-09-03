# eval_v1 — Frozen Evaluation Dataset

**Frozen at:** 2026-09-02T08:58:48.825383+00:00

**Verdict:** FREEZE

**Samples:** 770

**SHA-256 (dataset.jsonl):** `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24`

## Category counts

- prompt_injection: 110
- jailbreak: 110
- rag_security: 110
- context_attack: 110
- role_attack: 110
- tool_abuse: 110
- system_prompt_leakage: 110

## Sources

- agentdojo: 46
- benchmark_q1: 497
- garak: 110
- injecagent: 62
- trustllm: 55

## Integrity

- benchmark_q1 immutable (verified at build time)
- No train/validation leakage
- Unique IDs and SHA-256 hashes
- Full per-sample provenance in `provenance.jsonl`
