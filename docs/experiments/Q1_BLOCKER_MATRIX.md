# Q1 blocker matrix

**Author / owner:** Seyed Mohammadreza Shirazi Matin  
**Tip baseline:** `main` @ `e4870b9cc03a344835f341bfd61aa83d2bdf2bff`  
**Companion:** [`Q1_ROADMAP_4PHASE.md`](Q1_ROADMAP_4PHASE.md) · **P2 lock:** [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md)  
**Authority for numbers:** Frozen `AUDIT.md` / `verdict.json` — this table does **not** override them.

Severity: **BLOCKING** = cannot claim Q1-ready confirmatory story without fix or explicit Future Work boundary; **MAJOR** = weakens external credibility; **MINOR** = polish / process.

**P2 disposition tags:** **immutable** · **docs-fixed** · **P3-if-budget** · **Future Work** (see Q1-P2 §E).

| Blocker | Severity | Evidence today | Fix in which Q1 phase | P2 disposition | Honest alternative if unfixed |
| --- | --- | --- | --- | --- | --- |
| Track A VNEXT **FAIL** (immutable) | BLOCKING (for “win” claims) | FAIL; H1 qualified win = NO; AUDIT `VNEXT_CONFIRM/20260914-133147/` | — | **immutable** | Frame as **confirmed negative** under locked protocol; do not claim adaptive VNEXT success |
| Track A small **n = 61** attack (+61 benign) | MAJOR | Frozen pack manifest; same n in AUDIT | P2 ✓; optional P3 if V2 later | **Future Work** (V2); **docs-fixed** (power/sensitivity) | Offline power [`vnext_track_a_power_sensitivity.json`](../paper/q1_findings/artifacts/vnext_track_a_power_sensitivity.json): ~99% at true δ=MSID (b01=0 model); observed b10=5 → FAIL not mainly low-n for MSID |
| McNemar **p = 0.0625** (b10=5, b01=0) — not significant at α=0.05 | MAJOR | `DUAL_TRACK_STATUS.md`; VNEXT AUDIT | P2 ✓ | **docs-fixed** | State non-significance explicitly; forbid “marginally confirmed” |
| **MSID not met** (δ̂ = 0.0820 &lt; 0.20) | BLOCKING (for Track A win) | VNEXT AUDIT; fail reason `msid_not_met` | — for Track A historical run | **immutable** (Track A win); **docs-fixed** (discussion) | Negative result + estimand discussion; Track B MSID only on Track B pack |
| Track A **δ̂ 95% CI missing** in AUDIT | **BLOCKING GAP** (original artifact) | AUDIT point δ̂ only; CI via offline recompute | P2 + offline script | **docs-fixed** | CI **\[0.0164, 0.1639\]** from [`scripts/recompute_vnext_delta_ci.py`](../../scripts/recompute_vnext_delta_ci.py) + [`artifacts/vnext_delta_ci_offline.json`](../paper/q1_findings/artifacts/vnext_delta_ci_offline.json); never claim AUDIT contained CI |
| **Heuristic detector** / no AgentDojo-class tool loops | MAJOR | Phase-1 / VNEXT harness; no AgentDojo integration | P2 ✓ | **Future Work** | Scope claims to frozen single-turn confirmatory setting |
| **No external SOTA baselines** run | MAJOR | No third-party defense arm in live AUDIT folders | P2 ✓; optional P3 | **Future Work**; **P3-if-budget** | Compare to B0 and locked treatments only; no SOTA table |
| **Simulation ≠ real-LLM confirmatory** | BLOCKING (if mis-cited) | Historical sim in `04_results.md`; confirmatory = live AUDIT only | P1–P2 ✓ | **docs-fixed** | Never cite simulation ASR as live judge success ([`CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md) F6) |
| **Dual-track mixup** risk (A vs B packs/treatments) | BLOCKING | Separate packs, SHAs, AUDIT paths documented | P1–P2 ✓ | **docs-fixed** | Always label track; forbid one unlabeled ASR table |
| Confirmatory **V2**: D-22 names locked; allocation / episodes / SAP / pack | MAJOR | [`DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md`](DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md); Q1-P2 §A–B | P2 ✓ | **Future Work** (this cycle); **docs-fixed** (+1→`PRIVILEGE_EXFIL` when V2 authorized) | Track A/B n=61 only in paper; V2 deferred |
| **`p1_mechanism_v1.0.0` frozen** but **`live_evaluated=false`** | MAJOR | Freeze on tip; gate docs; no mechanism-pack live AUDIT | P2 ✓; P3 optional | **Future Work**; **P3-if-budget** | Cite benchmark spec + freeze SHA only; no live mechanism claims |
| **Venue TBD** / camera-ready | MINOR | Workshop checklist done; no venue marked submitted | P4 (human) | **docs-fixed** (P4 must-have); submit = human | Internal manuscript; venue choice deferred to Matin |
| **Overclaim risk** (ASR=0, L3 oracle, refusal-as-win) | BLOCKING (if violated) | [`CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md) F5–F7 | P1–P4 review | **docs-fixed** | Diagnostic layers and refusals labeled; harmful-action judge outcome only for confirmatory arms |
| Track A **utility ineligible** (U &lt; 0.95) | MAJOR | VNEXT AUDIT fail reason `s4_utility_ineligible` | P2 ✓ | **docs-fixed** | Report utility gate failure; no “deployable” wording |
| **Target ≠ Judge** discipline | MINOR (if maintained) / BLOCKING (if blurred) | qwen-7B target vs qwen-72B judge on confirmatory runs | P2–P4 | **docs-fixed** | Keep models explicit in every table caption |
| Optional historical **PR stack #23–#44** not merged | MINOR | [`PR_STACK.md`](../paper/workshop_vnext_fail/PR_STACK.md) | Human (outside Q1 phases) | **docs-fixed** | Tip `main` + merged #73 sufficient for current docs truth |

---

## Process

- **API=0** for maintaining this matrix unless Matin approves live work (Phase 3).
- Update this table when a blocker moves disposition — with pointer to decision doc or AUDIT path, not ad hoc numbers.
- **No Q1 acceptance guarantee:** clearing a row does not imply venue acceptance.

**Navigation:** [`Q1_ROADMAP_4PHASE.md`](Q1_ROADMAP_4PHASE.md) · [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md) · [`STATUS.md`](STATUS.md)
