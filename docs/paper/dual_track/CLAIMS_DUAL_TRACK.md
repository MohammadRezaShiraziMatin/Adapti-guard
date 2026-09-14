# Claims map — dual track (Track A FAIL vs Track B scoped)

Use with [`DUAL_TRACK_STATUS.md`](DUAL_TRACK_STATUS.md). Do not paraphrase a **FORBIDDEN** row into an **ALLOWED** row. Track A numbers are VNEXT AUDIT facts. Track B numbers are Phase-1 confirm AUDIT facts. They are not the same experiment.

Workshop FAIL-only map (Track A + Layer A): [`workshop_vnext_fail/CLAIMS_MAP.md`](workshop_vnext_fail/CLAIMS_MAP.md).

---

## Track A — allowed (VNEXT FAIL + Layer A CLOSED)

Cite only with FAIL framing. Pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`. AUDIT: `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`.

| ID | Allowed claim |
| --- | --- |
| A-FAIL-1 | On frozen pack `vnext_confirm_v1.0`, B0 ASR is 0.9508 and VNEXT-ADAPT ASR is 0.8689. |
| A-FAIL-2 | Intervention-mediated McNemar is b10=5, b01=0, p=0.0625 (α=0.05). This is **not statistically significant**. |
| A-FAIL-3 | δ̂=0.0820 is below locked MSID 0.20. Useful-intervention **fails**. |
| A-FAIL-4 | Treatment utility U=0.9344 is below U≥0.95. The run is **utility-ineligible**. |
| A-FAIL-5 | Qualified win (H1) is **NO**. Fail reasons: `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`. |
| A-LA | Layer A v4 detector lift and B3_V4 non-result remain CLOSED diagnostic wording in [`CLAIMS_CHECKLIST_LAYER_A.md`](CLAIMS_CHECKLIST_LAYER_A.md). |

Headline set D in the workshop claims map is the only authorized abstract/conclusion set for the negative-result package.

---

## Track B — allowed (Phase-1 confirmatory LIVE, scoped)

Cite only as PHASE1-CORE vs B0 on pack `phase1_confirm_v1` SHA-256 `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01`. AUDIT: `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md`. Classification **SUPPORTED_IMPROVEMENT**. This is not a VNEXT result.

| ID | Allowed claim |
| --- | --- |
| B-OK-1 | On locked `phase1_confirm_v1`, B0 harmful-action success is 1.0000 and PHASE1-CORE is 0.5574. |
| B-OK-2 | Intervention-mediated McNemar is b10=27, b01=0, exact two-sided p≈1.49e-8. |
| B-OK-3 | Paired effect δ̂=0.4426 (≈0.443) meets Phase-1 MSID 0.20 (MSID decision PASS). |
| B-OK-4 | CORE utility U≈0.9672 is ELIGIBLE (U≥0.95). |
| B-OK-5 | Classification is **SUPPORTED_IMPROVEMENT** on this pack, target, and judge. All 27 b10 events are `correct_tool_deny`. |
| B-OK-6 | Track B **does not reverse** Track A. VNEXT confirmation remains FAIL. |

Required qualifiers whenever Track B is stated: different pack from VNEXT; treatment is PHASE1-CORE not VNEXT-ADAPT; scoped to this confirm run; refusal ≠ defense win.

---

## Forbidden (both tracks)

Do not use, including with “preliminary,” “suggests,” or “on our pack.”

1. SOTA / state-of-the-art defense.
2. Production-ready / deployable product / “we built a working guard.”
3. “AdaptiGuard solves prompt injection” / solve-PI / keyword-free PI is solved.
4. VNEXT-reversed: “VNEXT is now PASS”; “Track B overturns FAIL”; mixing Track B numbers into the VNEXT AUDIT.
5. “VNEXT-ADAPT works / beats B0 / is a useful runtime defense.”
6. Relabeling Track A FAIL as PARTIAL, STATUS PASS, or “marginally significant therefore confirmed” (p=0.0625).
7. Treating Layer A `B3_V4` or Q1 simulation ASR as confirmatory.
8. Counting `target_refusal` or detector-hit-only as a defense win.
9. Generalizing Track B beyond `phase1_confirm_v1` + the recorded target/judge, or claiming Phase 2 / Multi-Turn results.
10. One unlabeled table mixing VNEXT ASR, Phase-1 harmful-action rates, Layer A TEST ASR, or historical simulation ASR.
