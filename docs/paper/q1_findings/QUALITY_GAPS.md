# Quality gaps — Q1 findings vs venue bar (honest)

**Author:** Seyed Mohammadreza Shirazi Matin  
**Date:** ~2026-09-23  
**Evidence:** Frozen AUDIT only + offline recomputes explicitly labeled. **API=0.**

---

## What improved on `main` (PR #74 merged; scientific, not packaging)

| Item | Status |
| --- | --- |
| Track A δ̂ **95% CI** | [`recompute_vnext_delta_ci.py`](../../scripts/recompute_vnext_delta_ci.py) → [`artifacts/vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json) (**not** in AUDIT) |
| Track A **McNemar power / sensitivity** | [`recompute_vnext_mcnemar_power.py`](../../scripts/recompute_vnext_mcnemar_power.py) → [`artifacts/vnext_track_a_power_sensitivity.json`](artifacts/vnext_track_a_power_sensitivity.json) |
| Estimand / methods clarity | [`MANUSCRIPT.md`](MANUSCRIPT.md) §2 / §5.4 |
| Phase 3 arm gates (docs only) | [`DECISION_LOCK_Q1_P3_ARMS.md`](../../experiments/DECISION_LOCK_Q1_P3_ARMS.md) — **no runs** |
| Claim/number gate | [`verify_q1_findings_facts.py`](verify_q1_findings_facts.py) + [`CONTRIBUTION_CEILING.md`](CONTRIBUTION_CEILING.md) |
| Remaining blockers | Below; need **budget** for live arms |

---

## Findings-track vs main-track ceiling (current cycle)

| Dimension | Findings / workshop-style fit | Main-track Q1 bar (typical) | Today |
| --- | --- | --- | --- |
| **Negative result honesty** | Strong — pre-registered FAIL inspectable | Needs novelty beyond “we ran eval” | **Met for eval contribution** |
| **Dual-track reporting** | Strong — separate packs, non-reversal | Often expected clear single RQ | **Met with discipline** |
| **Sample size** | n=61 per track | Often larger or multi-seed | **Weak for generalization**; offline power ~**99%** at true δ=MSID under b01=0 scaffold — observed δ far below MSID |
| **Detector** | Heuristic evidence-gated | Learned / calibrated / multi-model | **Weak** |
| **Environment** | Single-turn authored packs | AgentDojo-class tool loops | **Not run** (Future Work) |
| **Baselines** | B0 + locked treatments | External SOTA arms | **Not run** (Future Work) |
| **Effect CI (Track A δ̂)** | Now documented offline | Often in primary AUDIT | **Partially closed** (offline artifact) |
| **Track B generalization** | Scoped one pack | Cross-model / cross-benchmark | **Weak** |

**Honest ceiling:** A **Findings**, **evaluation**, or **negative-result workshop** narrative is proportionate. A **main-track “new defense”** claim is **not** supported. See [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md) — do not rush ICLR 2027 **main**.

---

## Remaining blockers (from [`Q1_BLOCKER_MATRIX.md`](../../experiments/Q1_BLOCKER_MATRIX.md))

| Blocker | Disposition | Main-track impact |
| --- | --- | --- |
| Track A FAIL immutable | immutable | Cannot sell as win |
| n=61 | Future Work / P3; power artifact | Generalization; not “underpowered for MSID” under simplified model |
| No AgentDojo / multi-step | Future Work | Agent claims blocked |
| No external SOTA baselines | P3-if-budget | Comparison gap |
| Heuristic detector | Future Work | Credibility gap vs learned guards |
| Simulation ≠ confirmatory | docs-fixed | Must not cite sim as live |
| Confirmatory V2 | Future Work (Q1-P2) | No larger n in this cycle |
| p1_mechanism live | P3-if-budget | Mechanism benchmark unrated live |

---

## What Phase 3 would buy (optional; **not done**)

Only after **human budget** + gates — **API=0** until Matin signs cap; **no runs authorized** by docs alone. **Track A FAIL numbers stay immutable.** Priority lock: [`DECISION_LOCK_Q1_P3_ARMS.md`](../../experiments/DECISION_LOCK_Q1_P3_ARMS.md) · [`Q1_P3_PRIORITY.md`](../../experiments/Q1_P3_PRIORITY.md).

| Priority | ID | Phase 3 arm | Scientific value | Does **not** substitute for |
| --- | --- | --- | --- | --- |
| 1 | **P3-1** | External baseline (same protocol) | Commensurate comparison vs external defense on **same episode IDs** — not superiority | Honest Track A FAIL |
| 2 | **P3-5** | `p1_mechanism_v1.0.0` live | Mechanism-surface **attribution** (`live_evaluated=false` today) | AgentDojo; Track A/B tables |
| 3 | **P3-3/4** | Multi-model robustness (**merged** arm) | Target/Judge variants under **one** pre-locked design | Single-pair overclaim; run without new model-ID lock |
| 4 | **P3-2** | Confirmatory V2 pack + live | Larger n, D-22 families (**last** / heaviest) | Retconning VNEXT MSID on old pack; V2 without freeze/SAP authorization |

**No guarantee** Phase 3 moves a paper from Findings to main accept.

---

## Recommended narrative emphasis (quality over wrappers)

1. **Estimand-first** — defense-attributed McNemar cells, utility co-primary, δ̂ definition.
2. **FAIL-first** — Track A before Track B; CI for δ̂ labeled offline recompute.
3. **Limitations as results** — small n, heuristic detector, frozen synthetic packs.
4. **Defer packaging** — arXiv/venue docs exist but do not substitute for evidence.

**Navigation:** [`MANUSCRIPT.md`](MANUSCRIPT.md) · [`CLAIMS_MAP.md`](CLAIMS_MAP.md) · [`Q1_ROADMAP_4PHASE.md`](../../experiments/Q1_ROADMAP_4PHASE.md)
