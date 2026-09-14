# Dual-track status (2026-09-14)

Two confirmatory tracks exist. They use **different packs, different treatments, and different AUDIT folders**. They are not interchangeable. Mixing them into one “AdaptiGuard works / fails” sentence is a claims error.

This file is documentation only. **No merge. No venue submit. No live LLM.**

---

## Track A — VNEXT confirmation (official FAIL)

| Field | Binding value |
| --- | --- |
| Outcome | **FAIL**. Qualified win (H1) = **NO**. |
| Pack | `vnext_confirm_v1.0` SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Treatment | `VNEXT-ADAPT` (`make_b3_adaptive_v4`) vs B0 |
| Numbers | B0 ASR 0.9508; VNEXT-ADAPT ASR 0.8689; b10=5 b01=0; p=0.0625; δ̂=0.0820 < MSID 0.20; U=0.9344 < 0.95 |
| Fail reasons | `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible` |
| AUDIT | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |

**Supports:** an honest negative result for adaptive cost-aware runtime intervention under `VNEXT-PROTOCOL-0.1` / `VNEXT-MSID-0.1`; Layer A remains a CLOSED diagnostic (see [`workshop_vnext_fail/CLAIMS_MAP.md`](../workshop_vnext_fail/CLAIMS_MAP.md)).

**Forbids:** “VNEXT-ADAPT works / beats B0”; relabeling FAIL as PARTIAL, PASS, or a trend toward a win; treating p=0.0625 as confirmed; SOTA; production-ready; reversing this FAIL with Track B.

**Immutable.** Do not edit the frozen pack or this AUDIT’s FAIL numbers.

---

## Track B — Phase-1 confirmatory LIVE (SUPPORTED_IMPROVEMENT)

| Field | Binding value |
| --- | --- |
| Outcome | **SUPPORTED_IMPROVEMENT** (scoped). MSID decision PASS. Utility ELIGIBLE. |
| Pack | `phase1_confirm_v1` SHA-256 `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |
| Treatment | `PHASE1-CORE` vs B0 (not VNEXT-ADAPT) |
| Run | `phase1_confirm_20260914T213022Z_a2681e92` (PR #39, draft) |
| Numbers | B0=1.0000; CORE=0.5574; δ̂=0.4426 (≈0.443); p≈1.49e-8; b10/b01=27/0; U≈0.9672 |
| AUDIT | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md` |

**Supports:** a scoped claim that PHASE1-CORE reduced intervention-mediated harmful-action success vs B0 on this locked Phase-1 confirm pack, with U above 0.95. Refusals are not wins; detector hit is not a win.

**Forbids:** treating Track B as a VNEXT reversal; claiming SOTA, production-ready, or “solves prompt injection”; generalizing beyond this pack/target/judge; claiming Multi-Turn or Phase 2 results (not run).

Track B **does not reverse** Track A.

---

## What neither track supports

- SOTA / production-ready / “AdaptiGuard solves prompt injection”
- One unlabeled table mixing VNEXT ASR with Phase-1 harmful-action rates or Layer A TEST ASR
- Q1 historical simulation or readiness scores as current confirmatory evidence
- New live LLM, retune, N change, or frozen-pack edits
- Agent merge or venue submit

Allowed wording: [`CLAIMS_DUAL_TRACK.md`](CLAIMS_DUAL_TRACK.md).  
PR index: [`workshop_vnext_fail/PR_STACK.md`](../workshop_vnext_fail/PR_STACK.md) (human merge only).  
Supervisor prompt: [`docs/experiments/MASTER_PROMPT.md`](../../experiments/MASTER_PROMPT.md).
