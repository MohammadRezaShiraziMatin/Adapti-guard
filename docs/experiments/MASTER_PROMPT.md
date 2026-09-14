# MASTER_PROMPT (durable supervisor)

Token-efficient standing orders. Read [`docs/paper/DUAL_TRACK_STATUS.md`](../paper/DUAL_TRACK_STATUS.md) before any claims, merge advice, or eval work.

`.cursor/rules` mirrors these standing orders (short form). This file remains canonical.

## AUTO constraints (do not violate)

- No merge. No force-push. Human merge only (`PR_STACK.md`).
- No arXiv / workshop / venue submit without explicit human approval in the prompt.
- No live LLM / OpenRouter / API eval without explicit human approval in the prompt. Default API=0.
- No Phase 2 implementation unless the human names Phase 2 as the task. Docs-only Phase 2 PRs stay unmerged unless asked.
- No retune. No N change. No edit of frozen JSONL packs.
- No edit of VNEXT FAIL numbers or `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/`.
- No edit of Phase-1 confirm AUDIT numbers in place.

## Dual-track honesty

- Track A: VNEXT confirmation **FAIL** (pack `523c8818…`, δ̂=0.0820, p=0.0625, U=0.9344). Immutable. Not PASS.
- Track B: Phase-1 confirmatory LIVE **SUPPORTED_IMPROVEMENT** on a **different** pack (`c789811a…`, PHASE1-CORE vs B0). Scoped. Does not reverse Track A.
- Never mix tracks in one unlabeled win/fail sentence. Claims file: [`docs/paper/CLAIMS_DUAL_TRACK.md`](../paper/CLAIMS_DUAL_TRACK.md).

## Q1 / sprawl

- `docs/Q1_*` and simulation `04_results.md` are historical. Not current confirmatory evidence. Do not revive Q1 SOTA or readiness scores as wins.
- Prefer one small docs/claims PR over new agent branches that restated the same FAIL/PASS.

## Forbidden claims (any track)

SOTA; production-ready; solves prompt injection; VNEXT-reversed; VNEXT-ADAPT beats B0; FAIL relabeled PARTIAL/PASS; refusal counted as defense win.

## If the ask is ambiguous

Docs + claims hygiene only. Point to DUAL_TRACK_STATUS. Do not start live eval, Phase 2 code, or venue text as a submit.
