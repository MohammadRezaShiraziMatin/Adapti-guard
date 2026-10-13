# Precision pass: every wording change in `MANUSCRIPT_DRAFT_v1.md`

Language and consistency only. No claim, number, table row or evidence was added, removed or reworded in substance. Each row is a word-level difference between the manuscript on #108's head and this pass.

| # | Before | After | Preceding words |
|---|---|---|---|
| 1 | `Labelling` | `Labeling` | …the payload never reaches the model. |
| 2 | `post-hoc.` | `post hoc.` | …MT1 r1 (held-out data); hypothesis formed |
| 3 | `post-hoc` | `post hoc` | …three models), the finding was discovered |
| 4 | `(kappa >=` | `(κ ≥` | …two independent human raters confirm it |
| 5 | `>=` | `≥` | …confirm it (kappa >= 0.70, agreement |
| 6 | `(4000` | `(4,000` | …Cluster bootstrap of the paired difference |
| 7 | `preregistered` | `pre-registered` | …a locally drafted plan, not a |
| 8 | `>=` | `≥` | …undefended rate below 5% at n |
| 9 | `5000` | `5,000` | …−0.0357 to +0.0357 at four decimals, |
| 10 | `kappa` | `κ` | …every number (for example the E1 |
| 11 | `1054` | `1,054` | …pinned in the run manifest). All |
| 12 | `1054` | `1,054` | …block or modify none of the |
| 13 | `1054` | `1,054` | …| 1/1 (1.0; floor) | The |
| 14 | `(4000` | `(4,000` | …a cluster bootstrap over attacker instruction |
| 15 | `(kappa,` | `(κ,` | …the executed outcome and the agreement |
| 16 | `>=` | `≥` | …(for example below 5% at n |
| 17 | `Per-family` | `per-family` | …## Appendix D E3 detailed results: |

## Why

- `Labelling` to `Labeling`, `post-hoc` to `post hoc`, `email` to `e-mail`, `preregistered` to `pre-registered`: one spelling per term (the manuscript already used the second form almost everywhere).
- `kappa >= 0.70`, `agreement >= 95%`, `n >= 40` to `κ ≥ 0.70`, `≥ 95%`, `n ≥ 40`, and `kappa` to `κ` in three places: the manuscript already used κ and ≥ elsewhere.
- `4000`/`5000 resamples` and `1054` to `4,000`, `5,000`, `1,054`: the manuscript already wrote `1,872`, `5,000` and `208,095` with commas.
- Heading of Appendix D: lower-case `per-family` after the colon, like the other headings.

## Checked and found consistent (no change)

- Every `§` reference resolves to an existing heading; every Table 1 to 4, Fig. 1 to 3 and Appendix A to D reference has a target.
- The ledger test passes; no ledger string changed.
- All 23 references were compared against their arXiv records on 2026-10-07 (title, first authors, venue or comments field); all agree with the list. No venue could be added for the others because their arXiv records state none.

## Noticed and deliberately not changed

- The section number `5.4b` (E4) is irregular. Renumbering would change `§` references in text, tests and the LaTeX build; it needs your decision.
- Reference entries `[2609.32691] ... (full text)` carry the note `(full text)`; left as is.
- `per-model` / `per model`: both forms appear, as adjective and as noun; left as is.
