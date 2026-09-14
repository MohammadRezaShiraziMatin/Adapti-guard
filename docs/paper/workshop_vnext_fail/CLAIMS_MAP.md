# Claims map — Layer A checklist + VNEXT protocol (after FAIL)

**Consistency audit (2026-09-14 closeout).** Checklist items A1–A12 remain CLOSED diagnostic wording. VNEXT V1–V10 are FAIL-only. Headline set D is the only authorized abstract/conclusion claim set. Win language (beats B0, qualified win YES, STATUS PASS, SOTA, production-ready, PARTIAL, “trend toward a win”, “marginally significant therefore confirmed”) is **FORBIDDEN**.

Use this file when editing [`MANUSCRIPT.md`](MANUSCRIPT.md). Numbers are frozen-artifact values only.
Do not paraphrase a **FORBIDDEN** row into an **ALLOWED** row.

**Dual-track:** This file is Track A (Layer A CLOSED + VNEXT FAIL) only. It does not authorize Track B win language. Track B Phase-1 confirmatory LIVE claims live in [`docs/paper/dual_track/CLAIMS_DUAL_TRACK.md`](../dual_track/CLAIMS_DUAL_TRACK.md). Status index: [`docs/paper/dual_track/DUAL_TRACK_STATUS.md`](../dual_track/DUAL_TRACK_STATUS.md). Track B does not reverse this FAIL.

Sources:

- Layer A wording: [`docs/paper/CLAIMS_CHECKLIST_LAYER_A.md`](../CLAIMS_CHECKLIST_LAYER_A.md)
- VNEXT claims boundary: [`docs/experiments/protocols/VNEXT_PROTOCOL.md`](../../experiments/protocols/VNEXT_PROTOCOL.md) §16
- VNEXT win rule: [`docs/experiments/protocols/VNEXT_PROTOCOL_ADDENDUM.md`](../../experiments/protocols/VNEXT_PROTOCOL_ADDENDUM.md) §2
- Official FAIL record: `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`

---

## A. Layer A (CLOSED diagnostic)

These sentences may be used as-is (checklist items 1–12). They are **not** VNEXT confirmatory results.

| ID | Allowed wording (verbatim from checklist) | Manuscript home |
| --- | --- | --- |
| A1 | On the frozen Layer A v3 TEST split, detector v4 attack recall is 27/40 = 0.675 and AUROC is 0.705, versus v3 recall 2/40 = 0.05 and AUROC 0.368, without TEST retuning. | §6.1 Detector |
| A2 | TRAIN recall is 20/20 = 1.00 (FPR 0, AUROC 1.00) and DEV recall is 20/20 = 1.00 (FPR 0.05, AUROC 0.991); the drop to TEST recall 0.675 is an overfitting / generalization risk. | §6.1 Detector |
| A3 | Under v4 risk mapping, TEST HIGH mass is inverted: 2 attack HIGH versus 6 benign HIGH. | §6.1 / §7 |
| A4 | With no defense (B0), judge ASR is 0.75 and benign utility is 1.00 on this TEST split. | §6.1 Intervention |
| A5 | Adaptive B3_V4 has ASR 0.625 and utility 0.85 versus B0 ASR 0.75 and utility 1.00; exact McNemar p = 0.125. This is not a demonstrated ASR reduction. | §6.1 Intervention |
| A6 | Of the six discordant episodes with B0 attack-success and B3_V4 attack-failure, only one is a true A3 block; the other five are target refusals under A1 and are not defense wins. | §6.1 / §7 |
| A7 | B2_L3_V4 (fixed risk-gated level 3 with the v4 signal) has ASR 0.20 and utility 0.825. This is a diagnostic mapping arm, not an adaptive-defense result. | §6.1 Diagnostic arms |
| A8 | Unconditional L3 has ASR 0 and utility 0 (security ceiling and utility floor). | §6.1 Diagnostic arms |
| A9 | ORACLE_BLOCK has ASR 0 and utility 1.00; it is label-conditioned and diagnostic only. | §6.1 Diagnostic arms |
| A10 | When A3 is selected, the episode is scored as blocked; the two B3_V4 HIGH attacks are true blocks. That tests action enforcement, not adaptive policy quality. | §4 / §6.1 |
| A11 | After the v4 detector lift, adaptive HIGH/MEDIUM routing remains the bottleneck: most detected TEST attacks sit in MEDIUM and receive A1 at adaptive defense_level ≤ 1. | §7 |
| A12 | With the v3 regex detector, adaptive B3 applied A1 on all 80 episodes (ASR 0.70 vs B0 0.75; McNemar p = 0.6875) and is not a defense win. | §6.1 Historical v3 |

**Layer A FORBIDDEN (checklist):** production-ready / SOTA defense; “B3_V4 beats B0”; treating B2_L3_V4 as adaptive; ORACLE as deployable; L3 as practical; L2 tool-deny numbers; A1 refusals as defense successes; TRAIN/DEV saturation as generalization; calibrated probabilities; mixing simulation ASR with judge ASR; retuning TEST bands; Pareto dominance of B3_V4; relabeling FAIL as PARTIAL / “trend toward a win” / “marginally significant therefore confirmed”; mixing VNEXT ASR with Layer A TEST ASR.

---

## B. VNEXT confirmation (official FAIL)

Allowed only with the FAIL framing. These are **not** Layer A numbers and must not share an unlabeled table with Layer A judge ASR.

| ID | Allowed claim | Protocol / stop rule | Artifact |
| --- | --- | --- | --- |
| V1 | On frozen pack `vnext_confirm_v1.0` (SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`; 61+61), B0 ASR is 0.9508 (58/61) and VNEXT-ADAPT ASR is 0.8689 (53/61). | Protocol §3, §11; addendum §4 | `AUDIT.md`, `verdict.json` |
| V2 | Intervention-mediated McNemar is b10 = 5, b01 = 0, exact two-sided p = 0.0625 (α = 0.05). This is **not statistically significant**. | Protocol §10, stop **S5** | `comparison.json` `confirmatory` |
| V3 | δ̂ = 0.0820 is below locked MSID 0.20. The useful-intervention claim **fails** regardless of detector metrics. | `VNEXT-MSID-0.1`; addendum §3 fail rule | `verdict.json` `msid_not_met` |
| V4 | Treatment utility U = 0.9344 is below the co-primary gate U ≥ 0.95 (false blocks = 1). The run is **utility-ineligible**. | Protocol §8, stop **S4** | `AUDIT.md` Utility |
| V5 | All five b10 events are taxonomy `correct_block` (A3). `insufficient_intervention` = 53. Target refusals are not counted as defense wins. | Protocol §4; addendum §2 \(\mathcal{W}\) | `AUDIT.md` Taxonomy |
| V6 | Qualified win (H1) is **NO**. Fail reasons: `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`. | Protocol §2, §13 | `verdict.json` |
| V7 | Target `qwen/qwen-2.5-7b-instruct` ≠ Judge `qwen/qwen-2.5-72b-instruct`; cache off; estimated spend ~$0.059 (0.059016 list-rate aid). | Protocol §15; request contract | `AUDIT.md` Spend |
| V8 | Family ASR cells are **descriptive** (n ∈ {10,11}); not powered superiority tests. | Protocol §9–§11; power memo §8 | `AUDIT.md` Family ASR |
| V9 | Mixed ASR McNemar is reported and is **not** a qualified defense win by itself. | Addendum §2 items 5–6; S2/S6 | `comparison.json` |
| V10 | Layer A TEST `47b975f7…` was not used and was not retuned. VNEXT is a new pack with disjoint IDs. | Protocol §11, S8 | `AUDIT.md` Non-claims |

**VNEXT FORBIDDEN:** “VNEXT-ADAPT works / beats B0 / is a useful runtime defense”; SOTA; production-ready; changing MSID after unblinding; topping up N; counting `target_refusal` as b10; labeling this FAIL as PARTIAL or as a trend toward a win; treating p = 0.0625 as “marginally significant therefore confirmed.”

---

## C. Conditional Layer A claims (checklist table)

Use only with the attached qualifier.

| Claim | Required qualifier |
| --- | --- |
| “v4 improves detection.” | Detector-only; frozen TEST; threshold 0.25 not tuned on TEST; recall 0.675 vs 0.05 and AUROC 0.705 vs 0.368; TRAIN/DEV overfitting risk. |
| “HIGH is reachable.” | v4 mapping; TEST 2 attack HIGH vs 6 benign HIGH (inverted). Not well calibrated. |
| “Risk-gated level 3 can cut ASR.” | Name **B2_L3_V4**, ASR 0.20, utility 0.825; **fixed / diagnostic, not adaptive**. |
| “A3 can stop attacks without harming benign utility.” | **ORACLE_BLOCK only** (labels). |
| “Unconditional blocking stops all attacks.” | **L3**, utility 0; `blocked ⇒ fail`. |
| Cost / USD | Cite `api_cost_estimate` only; not a systems benchmark. |

---

## D. Five allowed claims after FAIL (headline set)

These five sentences are the only headline claims this package authorizes after VNEXT FAIL. They appear in the abstract, introduction close, and conclusion.

1. **Layer A detector lift (diagnostic, CLOSED).** On the frozen Layer A v3 TEST split, detector v4 attack recall is 27/40 = 0.675 and AUROC is 0.705, versus v3 recall 2/40 = 0.05 and AUROC 0.368, without TEST retuning.
2. **Layer A adaptive non-result (CLOSED).** Adaptive B3_V4 has ASR 0.625 and utility 0.85 versus B0 ASR 0.75 and utility 1.00; exact McNemar p = 0.125. This is not a demonstrated ASR reduction.
3. **VNEXT confirmatory FAIL.** On the locked 61+61 pack (SHA-256 `523c8818…`), intervention-mediated McNemar is b10 = 5, b01 = 0, p = 0.0625; δ̂ = 0.0820 < MSID 0.20; U = 0.9344 < 0.95. Qualified win: **NO**.
4. **Attribution, not mixed ASR.** The five b10 events are `correct_block` (A3); 53 attacks remain `insufficient_intervention`. Target refusals are not defense wins.
5. **Evaluation contribution, not a defense product.** The hash-locked protocol (label-blind controller, intervention taxonomy, pre-registered MSID, utility gate) is the reusable artifact. Adaptive cost-aware intervention is **not confirmed**. No SOTA or production claim.

---

## E. Historical simulation (`04_results.md`)

The simulation tables in [`docs/paper/04_results.md`](../04_results.md) remain **LEGACY_SIMULATION_ONLY**. They must not be mixed unlabeled with Layer A or VNEXT judge ASR (checklist forbidden item 12; protocol §16). This package adds a pointer only; it does not rewrite that file’s simulation body.
