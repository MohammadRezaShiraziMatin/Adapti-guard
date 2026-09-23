# Claims checklist — dual-track (one-liners)

**Authority:** Frozen `AUDIT.md` / `verdict.json` beat narrative docs.  
**Detail:** Track IDs in [`dual_track/CLAIMS_DUAL_TRACK.md`](dual_track/CLAIMS_DUAL_TRACK.md) · Track A workshop map [`workshop_vnext_fail/CLAIMS_MAP.md`](workshop_vnext_fail/CLAIMS_MAP.md) · Layer A [`CLAIMS_CHECKLIST_LAYER_A.md`](CLAIMS_CHECKLIST_LAYER_A.md) · Status [`dual_track/DUAL_TRACK_STATUS.md`](dual_track/DUAL_TRACK_STATUS.md).

**Author (manuscript / packet):** Seyed Mohammadreza Shirazi Matin — not a “Contributors” placeholder.

---

## Allowed (say only with correct track label)

| # | One-liner |
| --- | --- |
| A1 | Track A VNEXT on `vnext_confirm_v1.0` is **FAIL**; qualified win (H1) = **NO**. |
| A2 | B0 ASR 0.9508 vs VNEXT-ADAPT 0.8689 on the frozen confirmation pack (61+61). |
| A3 | McNemar b10=5, b01=0, p=0.0625 — **not** statistically significant at α=0.05. |
| A4 | δ̂=0.0820 **<** MSID 0.20; U=0.9344 **<** 0.95 (utility-ineligible). |
| A5 | Layer A v4 shows detector lift on frozen TEST; adaptive B3_V4 is **not** a demonstrated ASR reduction (McNemar p=0.125). |
| A6 | Target `qwen/qwen-2.5-7b-instruct` ≠ Judge `qwen/qwen-2.5-72b-instruct` on confirmatory live runs. |
| B1 | Track B PHASE1-CORE vs B0 on `phase1_confirm_v1` is **SUPPORTED_IMPROVEMENT** (scoped, different pack). |
| B2 | Track B δ̂≈0.44 meets Phase-1 MSID; utility eligible on that pack — **still not** a VNEXT PASS. |
| B3 | Track B **does not reverse** Track A FAIL. |
| B4 | Reusable artifact: hash-locked protocol, intervention taxonomy, utility gate — **not** a shipped guard. |

---

## Forbidden (never paraphrase into allowed)

| # | One-liner |
| --- | --- |
| F1 | “VNEXT-ADAPT works / beats B0 / confirms adaptive defense.” |
| F2 | “Track B overturns FAIL” or one table mixing VNEXT ASR with Phase-1 harmful-action rates. |
| F3 | SOTA, production-ready, “AdaptiGuard solves prompt injection,” or solve-PI. |
| F4 | Relabel FAIL as PARTIAL, PASS, or “marginally significant therefore confirmed” (p=0.0625). |
| F5 | Count **target_refusal**, detector hit, or block-rate alone as a defense win. |
| F6 | Cite **simulation** ASR in `docs/paper/04_results.md` or `fixed_l3` ASR=0 as real-LLM judge success or as “injection solved.” |
| F7 | Present **L3 / ORACLE_BLOCK** ASR=0 as adaptive or deployable defense (diagnostic ceiling only). |
| F8 | Claim Phase-2 multi-turn live eval, AgentDojo-class loops, or external SOTA baselines were run. |
| F9 | Impute judge API failures as defense success; treat missing judge ASR as ASR=0. |
| F10 | Generalize either track beyond its frozen pack, target, and judge. |

---

## Workshop manuscript scope

[`workshop_vnext_fail/MANUSCRIPT.md`](workshop_vnext_fail/MANUSCRIPT.md) is **Track A + Layer A diagnostic** only. Cite Track B only with [`dual_track/`](dual_track/) docs and **never** inside the FAIL abstract/conclusion as a win reversal.
