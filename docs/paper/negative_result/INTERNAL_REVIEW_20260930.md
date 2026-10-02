# Hostile internal review of the draft manuscript (2026-09-30)

**Scope:** abstract, §1, §3–§8 drafts, figures 1–3, related-work notes, and the artifacts they cite. Written as a skeptical reviewer would write it, then used to fix the draft. Items marked **[fixed]** were corrected in this commit; the rest are open.

## 0. Verdict of the hostile reviewer
*Weak accept for a workshop / negative-result track if the open items in §2 are addressed; reject for a main track.* The measurement story is the contribution and it is real, but the evidence base is small, single-system, partly derived from the same data it is then shown on, and the scenarios and one comparator are the authors' own. The paper must present itself as a methodology case study, not as an evaluation of defenses.

## 1. Consistency and accuracy problems found
| # | Problem | Status |
|---|---|---|
| 1 | §6.3 said the authority-claim framing succeeded in "22 to 24 of 24 episodes for each model"; per-model cells are out of 8 (7/8, 8/8, 8/8) | **[fixed]** |
| 2 | §6.3 said "no instruction keywords", but the template contains "the assistant should email…" | **[fixed]** wording now "no 'ignore previous instructions'-style marker and no literal tool name" |
| 3 | Abstract mixed denominators ("65 vs 65 of 72" though A0 is 65/71; "57 vs 56 and 57 vs 57 of 168" though B3 has 167 pairs) | **[fixed]**; denominators explained in §5.5 and in the exploratory results note |
| 4 | Pattern-overlap count (33 of 42) came from whole JSON records that include metadata; on prompt and context text alone it is 36 of 42 | **[fixed]** both numbers reported in §4.4, the claims file, and the scientific report |
| 5 | Chronology "detector added after the earlier failure" was stated as an audit finding while the commit an older report cites (`c462945`) is not in the repository | **[fixed]** hedged as "in this repository's history … unverified" in §4.4 and §7 |
| 6 | "Reverses a conclusion" over-stated for the per-model reporting choice (it changes informativeness, not a verdict) | **[fixed]** "changes or qualifies" |
| 7 | §4.1 did not mention the judge-vs-executor evidence although the abstract and §6.1 rely on it | **[fixed]** sentence added |
| 8 | Two documents give A0 as 66/72 and 65/71 for the same run (provider-error episodes) | **[fixed]** explained in both places |
| 9 | Related-work numbers come from AI-generated reports, not PDFs | open (flagged everywhere) |

## 2. Substantive weaknesses a reviewer will raise
1. **Contribution size and novelty.** Two of the five measurement choices (scoring by proposal vs execution; non-delivery handling) are close to defects already catalogued [cite: 2609.32691]. The remaining three (scenario validity, authorship coupling, per-model reporting) carry the novelty, but rest on one system. Mitigation: state clearly that the paper is a case study; show at least one more system or benchmark if the venue expects generality.
2. **Small evidence, exploratory status.** About $0.23 of live spend, K = 8–12 per cell, 3 models via one provider, 2 + 7 scenario families, no confirmatory p-values, rules partly derived from the same data. A reviewer will say the measurement rules are hypotheses fitted post hoc. Mitigation: a confirmatory run under approved Amendment 10 with a new, independently authored scenario set.
3. **Circularity of the five rules.** The rules were identified while analysing these traces and are then demonstrated on them. **Partly addressed (2026-09-30):** applied unchanged to MT1 r1, generated earlier (`docs/research/SECOND_DATASET_MT1_RULES_20260930.md`): M5 replicates, M1 replicates only as an effect-size change (judge–executor gap is not general), M2/M4 not testable, and a new check (M6, defense applied to the wrong channel) emerged and was confirmed by a $0.07 re-run (`docs/research/SPOTLIGHT_CTX_CHECK_20260930.md`). Still open: a second system with different authors or an external benchmark.
4. **B3 is a straw man.** It never blocked in any run; a reviewer will say showing "no effect" for a stack that never intervenes is uninformative. Mitigation: state this explicitly, report its intervention counts (0 blocks; wrapping only), and avoid presenting it as representative of adaptive defenses; ideally add one working detector-style baseline.
5. **Comparators.** TOOLDENY is trivial by construction; ARGALLOW was never run; no CaMeL/Progent-style baseline. Mitigation: keep them as calibration only (already stated), and do not compare defenses with each other in the main claims.
6. **Authorship independence.** The independent set was authored by an AI assistant that had read the detector's patterns; a reviewer will discount "independent". Mitigation: independent human authorship or blind review of the confirmatory set; keep the disclosure prominent.
7. **E1 rescoring depends on a simulated tool layer.** "Executed" in the frozen tracks is the harness's simulated tool decision; for a tool-deny defense it is true by construction that denied calls are "not executed". The rescoring therefore measures whether the judge tracks the tool layer, not whether real-world harm occurred. Mitigation: word E1 as "judge vs tool-layer record" (drafted as such), not as "true harm".
8. **Utility rescoring for benign retrieval.** Counting a placeholder answer after a denied `retrieve_document` as failure is a task-definition choice. Mitigation: report both scorings (done) and the specific example.
9. **Forking paths.** During the work we fixed a scoring bug (benign create-record), changed R1's population, and added analyses after seeing results. The paper must list these changes; the artifact history contains them but §5.5 should say so plainly.
10. **Ethics and dual use.** The attack templates, especially the authority-claim family (0.96 across models), are directly reusable. A staged-release decision is needed `[TODO owner]`.
11. **Reproducibility of provider behaviour.** Hosted models change; temperature 0 is not deterministic (measured 4–5% flips). Mitigation: state model IDs, dates, and release traces so results can be recomputed offline.

## 3. Claims audit (draft sentence → evidence)
| Draft claim | Verified against | Result |
|---|---|---|
| Track B judge 34/61 vs executed 6/61; utility 59/61 vs 49/61 | `scripts/rescore_tracks_ab_deterministic.py` output; test reproduces frozen AUDIT numbers | ok |
| B3 65 vs 65 (E2), 57 vs 56 (E3) | analysis JSON of both runs | ok (denominators differ, stated) |
| CORE 36/36 blocked → 0/168 removed | E2 episodes; E3 replay and live b3_log | ok |
| Susceptibility deepseek 41/56, qwen3 8/56, gemma 8/56 | `fig2_susceptibility.csv` | ok |
| Noise floor 8/168 (CORE), 7/167 (B3) | `paired_vs_a0_analysis.json` | ok |
| Total live spend ≈ $0.23 | provider key usage 0.2303 | ok |
| "Static tool policy utility 1.00 → 0.33" | E2 analysis after benign scoring fix | ok |
| Related-work statements | AI-generated reports of each paper | **unverified against PDFs** |

## 4. Recommended order of work before any submission
1. Owner: approve or amend Amendment 10; choose venue; decide staged release; provide AI-assistance disclosure text.
2. Independent author for the confirmatory scenario set; run A0 replicate; run confirmatory arms per model under the approved rules.
3. Apply the five rules unchanged to a second dataset to address circularity.
4. Read the related-work PDFs; re-verify all numbers.
5. Add a working detector-style baseline in place of, or beside, B3.
6. Final consistency pass and figure regeneration from committed traces.
