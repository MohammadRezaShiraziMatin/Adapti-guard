# ADAPTI-GUARD — Phase 2 Claims Gate (LOCKED)

**Gate ID:** `PHASE2-CLAIMS-0.1`  
**Protocol:** `PHASE2-PROTOCOL-0.1`  
**Date (UTC):** 2026-09-14  

This gate constrains language used in papers, READMEs, PRs, talks, and agent summaries after any Phase-2 experiment. It also constrains claims **now**, before any Phase-2 live run exists.

---

## 1. Current evidence state (binding)

| Item | Claimable now? | Correct statement |
| --- | --- | --- |
| Phase-1 architecture / evidence quality gate | Yes | Phase 1 **PASS** for architecture/evidence; offline diagnostics only |
| Official VNEXT confirmation | Yes (historical) | **FAIL**; `qualified_win=false`; δ̂=0.0820 < MSID 0.20; p=0.0625 |
| Diagnostic `56/61` on VNEXT pack | Only as diagnostic | **Not** ASR, defense success, live performance, generalization, or superiority |
| Phase-2 multi-turn defense works | **No** | Protocol locked; **not yet evaluated** |
| PACK-FIT RISK | Yes | **HIGH** — motivates independent holdout |

---

## 2. Allowed claims (after a frozen Phase-2 run, if supported)

Use only if the locked experiment’s audit supports the statement:

| Allowed phrasing | Requires |
| --- | --- |
| “evaluated” under `PHASE2-PROTOCOL-0.1` | Run completed with frozen hashes |
| “reduced episode-level harmful-action success” vs B0 | Primary endpoint + reporting; prefer qualified-win language when claiming efficacy |
| “did not demonstrate significant improvement” | Non-significant McNemar and/or MSID not met |
| “improved intervention selectivity” | Pre-registered selectivity metrics support it |
| “failed to generalize” | Independent holdout shows loss vs DEV/VAL expectations |
| “utility-ineligible despite ASR drop” | \(U < 0.95\) |
| “null / mixed / regression / failure result” | Matches taxonomy in the SAP |

Always cite: protocol ID, dataset hash, model IDs, seed, runner/scorer versions.

---

## 3. Forbidden claims (unless independently demonstrated under a locked protocol)

Do **not** claim:

- solves prompt injection  
- robust defense (unqualified)  
- production-ready  
- SOTA / state-of-the-art  
- general solution  
- proven secure  
- “beats all baselines” without paired pre-registered comparisons  
- that Phase-1 diagnostic pack coverage equals Phase-2 security performance  
- that VNEXT FAIL was “fixed” by Phase-1 offline work  
- that Multi-Turn is implemented or evaluated (as of this documentation lock)

---

## 4. Attribution rules (always)

```text
target_refusal ≠ intervention_win
detector_hit ≠ intervention_win
canary_match ≠ primary security endpoint
```

Mixed ASR improvements driven by refusals under A0/A1 **must not** be marketed as adaptive defense wins.

---

## 5. Relationship to VNEXT claims

- VNEXT useful-intervention claim remains **not confirmed**.  
- Phase-2 does not rewrite VNEXT AUDIT numbers.  
- A future Phase-2 qualified win does **not** retroactively change VNEXT FAIL; it is a **different experiment** (multi-turn, new data).

---

## 6. Pre-run claim freeze

Until live eval is human-approved and completed:

> Phase-2 protocol is **designed and locked**. Multi-turn defense performance is **unevaluated**. LLM/API calls = **0**.

Violations of this gate in draft text should be corrected before merge of scientific communication PRs.
