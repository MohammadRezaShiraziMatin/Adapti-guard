# MASTER_PROMPT (durable supervisor)

Token-efficient standing orders. **Read [`docs/paper/dual_track/DUAL_TRACK_STATUS.md`](../paper/dual_track/DUAL_TRACK_STATUS.md) first** before any claims, merge advice, or eval work.

`.cursor/rules/adapti-guard.mdc` mirrors a compressed form of these rules. **This file is canonical** — if the mirror and this file ever disagree, fix the mirror.

Human entry: [`docs/START_HERE.md`](../START_HERE.md).

---

## Non-negotiable invariants (10)

1. **FROZEN MEANS FROZEN.**  
   `datasets/frozen/**`, `experiments/real_llm_eval/**`, and any file whose SHA-256 is quoted in an `AUDIT.md` or `verdict.json` are read-only. You may read and cite them. You may never edit, retune, regenerate, or “improve” them, regardless of framing (bugfix, cleanup, formatting, “just this once”).

2. **LABEL BLINDNESS IS ARCHITECTURAL, NOT OPTIONAL.**  
   The core detection/policy path (Phase-1 detector → RiskCore → CorePolicy → ActionLayer → ToolPermissionGate) must never receive gold labels (`is_attack` / `label` / `category`). Gold labels exist only in the separate, diagnostic-only scoring/oracle path. Any change that lets gold metadata leak into the core path — even transitively — is rejected.

3. **NO RETUNE ON EVALUATION DATA.**  
   `evidence_v4.0` / `evidence_phase1.0` and PHASE1-CORE thresholds may not be adjusted using signal from any pack that is also used to report results (`vnext_confirm_v1`, `phase1_confirm_v1`, or any future confirmatory pack). Fixes motivated by reviewing a pack must be validated on data that pack did not touch.

4. **SCORING TAXONOMY IS FIXED.**  
   `target_refusal` is never a defense win. Only `correct_block` / `correct_tool_deny` (or documented equivalents) count as intervention wins. Do not redefine this taxonomy to improve a number.

5. **QUALIFIED WIN REQUIRES ALL THREE GATES.**  
   MSID met (δ̂ ≥ 0.20) **and** statistically significant (protocol p-threshold / McNemar rule as locked) **and** utility eligible (U ≥ 0.95). A near-miss on any gate is still FAIL. Do not average, round, or reframe around a missed gate.

6. **NO LIVE LLM CALLS WITHOUT EXPLICIT GATE SATISFACTION.**  
   No live LLM / OpenRouter / API eval without explicit human approval in the prompt (and the gate sequence below). Default **API=0**.  
   Live API/LLM evaluation requires, in order: (a) independent holdout frozen and hashed, (b) detector/policy code frozen for the eval, (c) a written eval plan approved separately from protocol docs, (d) explicit human sign-off to spend budget. Do not run live evals to “just check” outside this sequence.

7. **RESULTS FROM DIFFERENT BENCHMARKS ARE DIFFERENT CLAIMS.**  
   Never blend, average, or narratively merge results from different frozen packs (e.g. VNEXT vs `phase1_confirm_v1`) into a single claim. State them side by side with their own gates, verdicts, and caveats. A positive result on Pack B does not reverse, soften, or contextualize away a FAIL on Pack A.

8. **HONESTY OVER POLISH.**  
   When a number, CI, or sensitivity analysis is missing from a frozen AUDIT artifact, say so explicitly (“BLOCKING GAP”, “not in AUDIT”, “unresolved”) rather than estimating, interpolating, or omitting the gap. Never fabricate a statistic that is not in the source artifact.

9. **AGENTS NEVER MERGE, NEVER CLOSE PRS VIA API, NEVER PUSH TO MAIN.**  
   Every deliverable is a PR/branch for human review. Human merge only (`docs/paper/workshop_vnext_fail/PR_STACK.md`). No force-push. No arXiv / workshop / venue submit without explicit human approval in the prompt.

10. **EVERY PR DESCRIPTION IS SELF-VERIFYING.**  
    Quote the exact frozen hashes touched/checked, the exact verification commands/output, and the exact API call count. Do not describe integrity checks vaguely (“looks fine”).

---

## Dual-track quick facts

- **Track A:** VNEXT confirmation **FAIL** (pack `523c8818…`, δ̂=0.0820, p=0.0625, U=0.9344). Immutable. Not PASS. Do not edit `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/`.
- **Track B:** Phase-1 confirmatory LIVE **SUPPORTED_IMPROVEMENT** on a **different** pack (`c789811a…`, PHASE1-CORE vs B0). Scoped. Does not reverse Track A. Do not edit Phase-1 confirm AUDIT numbers in place.
- Claims: [`docs/paper/dual_track/CLAIMS_DUAL_TRACK.md`](../paper/dual_track/CLAIMS_DUAL_TRACK.md).

## Q1 / sprawl

- `docs/Q1_*` and simulation `04_results.md` are historical. Not current confirmatory evidence. Do not revive Q1 SOTA or readiness scores as wins.
- Prefer one small docs/claims PR over new agent branches that restated the same FAIL/PASS.

## Allowed without asking

- Reorganize docs, fix links, standardize formatting — if `datasets/frozen` and `experiments/real_llm_eval` stay untouched and no scientific number changes.
- Add documentation, audits, glossaries, or explanatory material that report on frozen results without reinterpreting them.
- Write and run deterministic (non-LLM) tests.
- Propose (but not execute) plans for closing open scientific gaps; live LLM execution needs sign-off per rule 6.
- Docs-only Phase 2 PRs stay unmerged unless the human asks to merge; do not implement Phase 2 unless named as the task.

## Requires explicit human sign-off before start

- Any live LLM/API evaluation.
- Any change to detector thresholds, evidence rules, or policy tiers.
- Any new frozen pack (must be hashed and locked before code depends on it).
- Merging any PR.
- Closing any PR/issue via API.
- Venue / arXiv submit.

## If the ask is ambiguous

Docs + claims hygiene only. Point to `DUAL_TRACK_STATUS.md`. Do not start live eval, Phase 2 code, or venue text as a submit.
