# Claims map — Q1 findings manuscript (dual-track)

**Authority:** Frozen `AUDIT.md` / `verdict.json` beat this file.  
**Align with:** [`docs/paper/CLAIMS_CHECKLIST.md`](../CLAIMS_CHECKLIST.md) · Track detail [`dual_track/CLAIMS_DUAL_TRACK.md`](../dual_track/CLAIMS_DUAL_TRACK.md) · Workshop Track A map [`workshop_vnext_fail/CLAIMS_MAP.md`](../workshop_vnext_fail/CLAIMS_MAP.md)

**Scope:** This manuscript reports **Track A (VNEXT FAIL)**, **Track B (Phase-1 scoped improvement)**, and **Layer A diagnostic** in **separate labeled sections**. Confirmatory V2 and optional P3 arms are **Future Work** only.

---

## Allowed (headline-safe with track label)

| ID | Wording |
| --- | --- |
| Q1-A1 | Track A VNEXT on `vnext_confirm_v1.0` is **FAIL**; qualified win (H1) = **NO**. |
| Q1-A2 | Track A: B0 ASR **0.9508** vs VNEXT-ADAPT **0.8689** (61+61); McNemar b10=5, b01=0, p=**0.0625** — **not** significant at α=0.05. |
| Q1-A3 | Track A: δ̂=**0.0820** &lt; MSID **0.20**; U=**0.9344** &lt; **0.95**; fail reasons `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`. |
| Q1-A4 | Track A: point δ̂=**0.0820** in AUDIT; **95% CI \[0.0164, 0.1639\]** only from offline artifact [`artifacts/vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json) — **not** in original AUDIT; label recomputed. |
| Q1-A5 | Track A: all five b10 events are `correct_block` (A3); **53** attacks remain `insufficient_intervention`. |
| Q1-A6 | Track A **offline** McNemar power/sensitivity ([`artifacts/vnext_track_a_power_sensitivity.json`](artifacts/vnext_track_a_power_sensitivity.json)): e.g. **~99%** power at θ=MSID under **b01=0 binomial scaffold**; observed b10=5 → **FAIL unchanged**; **not** “underpowered for MSID” as primary explanation. |
| Q1-B1 | Track B PHASE1-CORE vs B0 on `phase1_confirm_v1` is **SUPPORTED_IMPROVEMENT** (scoped); treatment ≠ VNEXT-ADAPT. |
| Q1-B2 | Track B: B0 ASR **1.0000**, CORE **0.5574**, δ̂=**0.4426**, 95% CI **[0.2757, 0.6096]**, p=**1.49012e-08**, b10/b01=**27/0**, U=**0.9672131147540983**. |
| Q1-B3 | Track B **does not reverse** Track A FAIL and is **not** a VNEXT PASS. |
| Q1-L1 | Layer A (CLOSED): v4 TEST recall **0.675**, AUROC **0.705**; B3_V4 McNemar p=**0.125** — **not** a demonstrated ASR reduction. |
| Q1-M1 | Target `qwen/qwen-2.5-7b-instruct` ≠ Judge `qwen/qwen-2.5-72b-instruct` on confirmatory live tracks. |
| Q1-M2 | Reusable artifact: hash-locked protocol, intervention taxonomy, utility gate — **not** a shipped product. |
| Q1-FW1 | Confirmatory V2 pack/live, AgentDojo-class loops, external SOTA baselines, `p1_mechanism_v1.0.0` live — **Future Work** (Q1-P2); optional P3 after budget. |

---

## Forbidden (never paraphrase into allowed)

| ID | Wording |
| --- | --- |
| Q1-F1 | “AdaptiGuard / VNEXT / PHASE1-CORE **solves** prompt injection” or **SOTA** / production-ready. |
| Q1-F2 | FAIL→PASS, “VNEXT works,” “Track B overturns FAIL,” or one table mixing Track A and Track B ASR without labels. |
| Q1-F3 | p=0.0625 as “marginally significant therefore confirmed” or FAIL relabeled PARTIAL/PASS. |
| Q1-F4 | `target_refusal`, detector hit, or block-rate alone as defense wins. |
| Q1-F5 | Simulation / `fixed_l3` / ORACLE / L3 ASR=0 as **live** confirmatory adaptive defense success. |
| Q1-F6 | Claim AgentDojo leaderboard, multi-turn Phase-2 live, or external baselines **were run** (they were not). |
| Q1-F7 | Invent Track A δ̂ 95% CI **as if in AUDIT**, or cite offline CI/power **without** offline/scaffold labeling. |
| Q1-F9 | Claim Track A was **underpowered for MSID 0.20** without the b01=0 planning scaffold and **FAIL-first** context. |
| Q1-F8 | Generalize beyond frozen pack SHA, target, and judge for either track. |

---

## Section → claim home

| Manuscript § | Primary claim IDs |
| --- | --- |
| Abstract / Conclusion | Q1-A1–A3, Q1-B1, Q1-B3, Q1-M2 |
| Results Track A | Q1-A1–A5 |
| Results Track B | Q1-B1–B3 |
| Layer A diagnostic | Q1-L1 |
| Limitations | Q1-A4, Q1-A6, Q1-FW1, Q1-F6 |

**Edit rule:** If a sentence is not in **Allowed**, it must not appear in abstract, conclusion, or figure captions.
