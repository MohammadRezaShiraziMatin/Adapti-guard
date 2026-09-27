# Phase 6 — Pre-Experiment Validation & Statistical Readiness

**Status:** design/pre-registration complete for locked confirmatory tracks; extension live arms **INCOMPLETE** until Phase 7 authorization.  
**Does not authorize live API spend.** Phase 6 PASS ≠ Phase 7 live authorization.

---

## A. Experimental preconditions (matrix)

| condition_id | Phase 7 pre-run status | Notes |
| --- | --- | --- |
| COND-TRACK-A-B0 | NOT_APPLICABLE | `historical_locked`; AUDIT only — no re-run |
| COND-TRACK-A-VNEXT-ADAPT | NOT_APPLICABLE | same |
| COND-TRACK-B-B0 | NOT_APPLICABLE | same |
| COND-TRACK-B-PHASE1-CORE | NOT_APPLICABLE | same |
| COND-E1-STATEFUL-OFFLINE | INCOMPLETE | offline pipeline READY; live MT empirical **BLOCKED** (`phase7_required_for_empirical`) |
| COND-E2-ADAPTIVE-OFFLINE | INCOMPLETE | offline READY; live adaptive **BLOCKED** |
| COND-E3-AGENT-OFFLINE | INCOMPLETE | offline READY; live agentic **BLOCKED** |
| COND-EXT4-CROSSMODEL | BLOCKED | `evidence_not_in_workspace` |
| COND-EXT6-BASELINE | INCOMPLETE | protocol only; no live arms |
| COND-PHASE7-CAMPAIGN | BLOCKED | `live_budget_authorization` |

**Offline infrastructure (E1–E3):** `READY` for `run_offline()` + resolver smoke (Phase 4).

---

## B. Statistical analysis readiness

### Primary outcome (confirmatory — frozen)

| Track | Primary security outcome | Source RQ | Test | Effect / gate |
| --- | --- | --- | --- | --- |
| Track A | Paired **judge-ASR** cells (B0 vs VNEXT-ADAPT) | RQ-Core-1 | McNemar (exact binomial on discordant pairs) | MSID gate + δ̂ vs pre-registered MSID |
| Track B | Paired **judge-ASR** (B0 vs PHASE1-CORE) | RQ-Core-1 | McNemar | δ̂ + utility co-primary gate |

Co-primary: **Utility U** (protocol utility gate) — not a substitute for security failure on Track A.

### Secondary outcomes

| Outcome | Metric | Status |
| --- | --- | --- |
| Tool harm | Tool-HASR (where applicable) | Track B row; verifier-backed |
| Cost | Tokens / USD fields in AUDIT | Descriptive + paired where logged |
| Utility | Utility U | Co-primary gate |
| Extension MT/AA/Agent | per_turn_outcome, strategy_changed, privileged_execution | **pipeline_validation_only** offline; live **BLOCKED** |

### Extension statistical unit (pre-specified, no empirical N)

| Design | Unit of analysis | Aggregation | Independence |
| --- | --- | --- | --- |
| Stateful multi-turn | **Episode** (turns nested; not i.i.d. turns) | Episode → condition | Turns within episode correlated |
| Adaptive attacker | **Episode** (max_turns iterations) | Episode outcome; strategy shift descriptive | Iterations sequential — not independent samples |
| Agentic mock env | **Tool step / episode** | Episode → condition | Tool trace in `AgentEnvironment` |

---

## C. Comparisons (locked confirmatory)

| Comparison | Metric | Type | Paired? | Test | Effect | CI | Rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B0 vs VNEXT (Track A) | judge attack_success | binary | Yes (episode id) | McNemar | δ̂ (ASR diff) | Bootstrap/Wilson per SAP archive | MSID + utility gates |
| B0 vs CORE (Track B) | judge attack_success | binary | Yes | McNemar | δ̂ | per SAP | Utility gate |

Implementation: `src/adapti_guard/evaluation/statistics.py` (`mcnemar_test`, `bootstrap_ci`, etc.) — **fixture validation only**.

---

## D. Multiple comparisons

| Family | Scope | Strategy |
| --- | --- | --- |
| Confirmatory | Track A and Track B **separate** packs (disjoint) | No cross-track pooling; each track pre-registered |
| Extension (Phase 7) | RQ-Ext-1–3 exploratory until pre-registered | **Confirmatory vs exploratory** distinction preserved; no new α without SAP amendment |

---

## E. Sample size / seeds / repetitions

| Experiment | N / runs | Status |
| --- | --- | --- |
| Track A/B confirmatory | Fixed by frozen AUDIT packs | **NOT_APPLICABLE** (historical complete) |
| Phase 7 extension live | Episodes × seeds × trials | **BLOCKED** — budget + `live_budget_authorization` not granted |

No invented N or seeds.

---

## F. Stopping rules & missing data

Aligned with [`EXPERIMENT_PROTOCOL.md`](EXPERIMENT_PROTOCOL.md) §3:

| Event | Classification | ≠ attack_success |
| --- | --- | --- |
| provider_failure / timeout / invalid_response | exclude run | Yes |
| judge_failure | exclude | Yes |
| verifier_failure | exclude | Yes |
| target_failure (Phase 4) | `outcome: target_failure` | Yes |
| missing_evidence | BLOCKED analysis | Yes |

---

## G. Leakage / contamination (read-only checks)

| Check | Status |
| --- | --- |
| Frozen Track A/B not re-run via offline runner | Enforced (`offline_experiment_runner`) |
| Gold labels in core episode input | Forbidden (`EpisodeInput` guard) |
| Target ≠ Judge on matrix confirmatory rows | Enforced (`condition_resolver`) |
| Judge blind to treatment labels | Protocol §2 |
| Adaptive attacker gold leakage | `AdaptiveAttacker` / VNEXT docs — runtime-observable only |

---

## H. Evidence chain (Phase 7 target)

```text
condition_id → execution → raw_evidence → derived_metrics → statistics → evidence_record → human_review_packet (optional)
```

Schema: [`EVIDENCE_SCHEMA.yaml`](EVIDENCE_SCHEMA.yaml). Reproducibility: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

---

## I. Phase 7 execution gate (authorization separate)

All required before **human** live authorization (not granted by this doc):

```text
Phase 1–6 validators PASS (design)
condition resolvable for intended live arms
Target ≠ Judge configured
Dataset hash locked
Budget / LIVE_EVALUATION_GATE
Provider credentials
```

**Current:** `phase7_live_campaign: BLOCKED` in `EXPERIMENT_READINESS_GATE.json`.
