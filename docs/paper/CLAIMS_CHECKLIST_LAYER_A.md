# Layer A claims checklist (v2–v4 diagnostic)

Use this list when drafting abstract, results, or discussion text. Numbers are frozen-artifact values only. Do not paraphrase a FORBIDDEN claim into an ALLOWED claim.

Integrity: branch `cursor/layer-a-v4-project-completion-f6c7`, commit `eaa1f029d3fd524fd3c5beeea6e02329adee7d20`. Narrative tables: `docs/paper/04_results_layer_a_diagnostic.md`.

---

## ALLOWED (exact wording)

These sentences may be used as-is.

1. **Detector lift (TEST, no retuning).** “On the frozen Layer A v3 TEST split, detector v4 attack recall is 27/40 = 0.675 and AUROC is 0.705, versus v3 recall 2/40 = 0.05 and AUROC 0.368, without TEST retuning.”
2. **Overfitting risk.** “TRAIN recall is 20/20 = 1.00 (FPR 0, AUROC 1.00) and DEV recall is 20/20 = 1.00 (FPR 0.05, AUROC 0.991); the drop to TEST recall 0.675 is an overfitting / generalization risk.”
3. **HIGH inversion.** “Under v4 risk mapping, TEST HIGH mass is inverted: 2 attack HIGH versus 6 benign HIGH.”
4. **Undefended ASR.** “With no defense (B0), judge ASR is 0.75 and benign utility is 1.00 on this TEST split.”
5. **Adaptive non-result.** “Adaptive B3_V4 has ASR 0.625 and utility 0.85 versus B0 ASR 0.75 and utility 1.00; exact McNemar p = 0.125. This is not a demonstrated ASR reduction.”
6. **Discordant decomposition.** “Of the six discordant episodes with B0 attack-success and B3_V4 attack-failure, only one is a true A3 block; the other five are target refusals under A1 and are not defense wins.”
7. **Fixed diagnostic mapping.** “B2_L3_V4 (fixed risk-gated level 3 with the v4 signal) has ASR 0.20 and utility 0.825. This is a diagnostic mapping arm, not an adaptive-defense result.”
8. **Security ceiling.** “Unconditional L3 has ASR 0 and utility 0 (security ceiling and utility floor).”
9. **Oracle diagnostic.** “ORACLE_BLOCK has ASR 0 and utility 1.00; it is label-conditioned and diagnostic only.”
10. **A3 enforcement.** “When A3 is selected, the episode is scored as blocked; the two B3_V4 HIGH attacks are true blocks. That tests action enforcement, not adaptive policy quality.”
11. **Bottleneck (CASE B).** “After the v4 detector lift, adaptive HIGH/MEDIUM routing remains the bottleneck: most detected TEST attacks sit in MEDIUM and receive A1 at adaptive defense_level ≤ 1.”
12. **Historical v3 adaptive.** “With the v3 regex detector, adaptive B3 applied A1 on all 80 episodes (ASR 0.70 vs B0 0.75; McNemar p = 0.6875) and is not a defense win.”

---

## FORBIDDEN (do not use, even with hedging)

Do not use these claims, including with “preliminary,” “suggests,” or “on our pack.”

1. “ADAPTI-GUARD / B3 / B3_V4 is a working, production-ready, or state-of-the-art cost-aware prompt-injection defense.”
2. “Adaptive B3_V4 beats B0” / “significantly reduces ASR” / “is a useful runtime defense.”
3. “B2_L3_V4 is an adaptive win” / “level-3 adaptive policy” / “L3 result.”
4. “ORACLE_BLOCK is deployable performance” / “oracle ASR is the system ASR.”
5. “L3 is a practical defense” (ASR 0 is purchased with utility 0).
6. “L2 denies tools” / any AgentDojo-class or function-calling defense number (L2 is unwired).
7. “Target refusals under A1 are defense successes.”
8. “Detected-but-not-blocked attack failures are defense successes.”
9. “TRAIN/DEV perfect recall proves the detector generalizes.”
10. “Detector scores are calibrated probabilities.”
11. “Keyword-free / general prompt-injection is solved.”
12. Mixing **harmonized simulation** ASR from `docs/paper/04_results.md` with these **judge** ASR figures in one unlabeled table.
13. Treating v4 TEST HIGH/MEDIUM bands as retuned (they were not).
14. Claiming Pareto dominance of B3_V4 over B0.

---

## CONDITIONAL (allowed only with the attached qualifier)

| Claim | Required qualifier |
| --- | --- |
| “v4 improves detection.” | Detector-only; frozen TEST; threshold 0.25 not tuned on TEST; cite recall 0.675 vs 0.05 and AUROC 0.705 vs 0.368; state TRAIN/DEV overfitting risk. |
| “HIGH is reachable.” | v4 mapping (score = p); on TEST, 2 attack HIGH vs 6 benign HIGH (inverted). Do not imply HIGH is well calibrated. |
| “Risk-gated level 3 can cut ASR.” | Name **B2_L3_V4**, ASR 0.20, utility 0.825; call it **fixed / diagnostic, not adaptive**. |
| “A3 can stop attacks without harming benign utility.” | **ORACLE_BLOCK only** (labels); not a deployable detector. |
| “Unconditional blocking stops all attacks.” | **L3**, utility 0; scoring rule `blocked ⇒ fail`. |
| Family ASR or family recall | Descriptive; n ∈ {8,12}; no superiority test. |
| Bootstrap ASR CIs | n=40; wide; do not treat non-overlap as a test (use McNemar for paired ASR). |
| “v3 was detector-limited (CASE D).” | Historical v3 detector TEST recall 0.05 and HIGH=0; do not present v3 B3 as a v4 result. |
| Cost / USD figures | Cite the run `api_cost_estimate` only; ~$0.005–0.008/run class is an estimate, not a systems benchmark. |
| Multi-turn residual | TEST detector family recall 3/8; footnote, not the headline (CASE E residual). |

---

## Numbers that must not be invented or altered

| Quantity | Value |
| --- | --- |
| v3 TEST recall | 2/40 = 0.05 |
| v3 TEST AUROC | ≈ 0.368 (artifact 0.3678125) |
| v4 TEST recall | 27/40 = 0.675 |
| v4 TEST AUROC | 0.705 (artifact 0.7053125) |
| B0 ASR / utility | 0.75 / 1.00 |
| B3_V4 ASR / utility | 0.625 / 0.85 |
| McNemar B0 vs B3_V4 | p = 0.125 (b01=1, b10=6) |
| True A3 among those 6 | 1; 5 A1 target refusals |
| B2_L3_V4 ASR / utility | 0.20 / 0.825 |
| L3 ASR / utility | 0 / 0 |
| ORACLE_BLOCK ASR / utility | 0 / 1.00 |
| TEST HIGH | 2 attack, 6 benign |

If a draft needs a number not in this table or in `04_results_layer_a_diagnostic.md`, omit the cell; do not interpolate.
