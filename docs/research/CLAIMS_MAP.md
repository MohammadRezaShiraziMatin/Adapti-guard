# Claims map — Q1 research program (Phase 2)

**Manuscript-frozen claims:** [`docs/paper/q1_findings/CLAIMS_MAP.md`](../paper/q1_findings/CLAIMS_MAP.md) (AUDIT authority).  
This file maps **program RQs** to claim status for Phase 2 consistency.

Statuses: `SUPPORTED` | `PARTIALLY SUPPORTED` | `PLANNED` | `CONDITIONAL` | `BLOCKED` | `OUT OF SCOPE`

| Claim ID | Claim (bounded wording) | RQ | Required evidence | Current evidence | Status |
| --- | --- | --- | --- | --- | --- |
| C-CORE-1 | Runtime intervention was **evaluated** under locked confirmatory protocol | RQ-Core-1 | Live AUDIT + frozen packs | Track A/B AUDIT | **SUPPORTED** |
| C-CORE-2 | VNEXT-ADAPT meets qualified win on Track A | RQ-Core-1 | MSID + McNemar + utility | Track A FAIL | **SUPPORTED** (negative) |
| C-CORE-3 | PHASE1-CORE improves vs B0 on Track B pack | RQ-Core-1 | Track B AUDIT | δ̂, CI in AUDIT | **SUPPORTED** (scoped) |
| C-CORE-4 | Track B reverses Track A FAIL | RQ-Core-1 | — | Dual-track docs | **OUT OF SCOPE** / forbidden |
| C-TRADE-1 | Joint security–utility–cost characterized | RQ-Core-2 | Utility + cost + ASR | Partial per track | **PARTIALLY SUPPORTED** |
| C-EXT-1 | Multi-turn defense **live-evaluated** | RQ-Ext-1 | Phase 7 traces | Offline harness only | **PLANNED** |
| C-EXT-2 | Adaptive attacker **live-evaluated** | RQ-Ext-2 | Phase 7 traces | Offline harness only | **PLANNED** |
| C-EXT-3 | Agentic Tool-HASR **live campaign** | RQ-Ext-3 | Phase 7 traces | Mock env tests | **PLANNED** |
| C-EXT-4 | Cross-model Q2 replication | RQ-Ext-4 | Q2 raw bundle | Not in workspace | **BLOCKED** |
| C-EXT-5 | External baseline superiority | RQ-Ext-6 | Baseline live arms | Registry only | **PLANNED** |
| C-TRUST-1 | Human-centered / trustworthy **layer defined** (not CPS-validated) | RQ-Trust-1 | Human study or CPS deployment evidence | `PHASE5_TRUSTWORTHY_APPLICATION.md`, `human_review_packet.py` | **DESIGN_ONLY** |
| C-METH-1 | Reusable rigorous evaluation **framework** (protocol + schema) | M1–M5 | Docs + reproducibility | Phase 2–3 artifacts | **CONDITIONAL** (framework); empirical ext **PLANNED** |

### Claim lifecycle (EAAI / program)

`DESIGNED` → `IMPLEMENTED` → `VALIDATED` (offline/tests) → `LIVE EVALUATED` (Phase 7 traces only).  
See [`EAAI_SPECIAL_ISSUE_COMPLIANCE.md`](EAAI_SPECIAL_ISSUE_COMPLIANCE.md) §J.

### Forbidden wording (program-wide)

SOTA, best, universal, solves prompt injection, production-ready, AgentDojo run, multi-turn live run (unless Phase 7 evidence exists).
