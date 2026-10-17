# Start here

Reviewer entry point for this repository. Documentation only: nothing here changes frozen evidence, runs a live model or retunes a detector.

## What this repository is

AdaptiGuard is an empirical case study of measurement validity in the evaluation of LLM-agent runtime defenses. It re-scores and re-analyzes frozen runs and shows that the choice of success endpoint, labeling rule and reporting unit can change the conclusion of a defense evaluation on the same traces. It does not present a state-of-the-art or production defense, and it is not a general benchmark.

## Read in this order

1. [README.md](../README.md): scope, status and offline reproduction commands.
2. [Manuscript draft](paper/negative_result/MANUSCRIPT_DRAFT_v1.md): the main study. It is assembled from the source sections in the same folder and is not edited by hand. Companion files in that folder: NUMBERS_LEDGER.md, figures/, RELATED_WORK.md and appendices A to D.
3. [REPRODUCIBILITY.md](../REPRODUCIBILITY.md): what can and cannot be regenerated from the public tree.
4. [docs/paper/DOCS_INDEX.md](paper/DOCS_INDEX.md): map of current versus historical documents.

## Evidence status (frozen, do not mix)

- Track A VNEXT = FAIL (immutable). Pack vnext_confirm_v1.0, SHA-256 523c8818... Qualified win (H1) = NO. Do not edit the frozen pack, the AUDIT folder, or the FAIL numbers.
- Track B Phase-1 LIVE = SUPPORTED_IMPROVEMENT on a different pack (phase1_confirm_v1, SHA-256 c789811a...), treatment PHASE1-CORE vs B0. Scoped. Not a VNEXT PASS. Manuscript section 6.1 re-scores both tracks with the tool layer execution record and shows that the Track B classification depends on judge errors.
- Track B does NOT reverse Track A. Mixing VNEXT ASR with Phase-1 harmful-action rates in one unlabeled sentence is a claims error.
- Canonical AUDIT files (do not rewrite in place):
  - Track A: experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md
  - Track B: experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md
- Frozen packs live in datasets/frozen/ and run artifacts in experiments/. Both are read-only.

## Historical material

Earlier dual-track work and its workshop packet are kept for provenance and are not the main result: docs/paper/dual_track/, docs/paper/workshop_vnext_fail/, docs/paper/q1_findings/ and docs/archive/. Old documentation paths keep one-line "Moved to ..." stubs, so frozen cards and external links still resolve. Forward-looking protocols and design-only documents (docs/experiments/, docs/research/) are unevaluated.

## Repository layout

| Path | Role |
|---|---|
| src/adapti_guard/ | Installable package (import adapti_guard) |
| configs/ | YAML and JSON configs |
| scripts/ | CLI entrypoints, including manuscript assembly and figure scripts |
| tests/ | Pytest, including the number-ledger check |
| docs/paper/negative_result/ | Main research package (manuscript, figures, ledger, appendices) |
| docs/archive/ | Superseded and historical documents |
| datasets/frozen/ | Frozen packs (read-only) |
| experiments/real_llm_eval/ | Run artifacts and AUDIT files (read-only) |

## What is not public

The live multi-turn harness, the E2/E3 run scripts and the external-test runner are not in the public tree. See the "Reproduce" section of the README and REPRODUCIBILITY.md.

## Maintainer process documents

These files record the maintainer workflow. They are not needed to evaluate the science.

- [docs/paper/dual_track/DUAL_TRACK_STATUS.md](paper/dual_track/DUAL_TRACK_STATUS.md): Track A versus Track B on one page.
- [docs/paper/dual_track/CLAIMS_DUAL_TRACK.md](paper/dual_track/CLAIMS_DUAL_TRACK.md): allowed and forbidden claim wording.
- [docs/paper/workshop_vnext_fail/PR_STACK.md](paper/workshop_vnext_fail/PR_STACK.md): roles of open pull requests (human merge only). The workshop_vnext_fail folder name is frozen for citations.
- [docs/paper/dual_track/RELEASE_NEXT_FA.md](paper/dual_track/RELEASE_NEXT_FA.md): next steps for the maintainer (Persian).
- [docs/experiments/MASTER_PROMPT.md](experiments/MASTER_PROMPT.md): maintainer standing orders for automated agents.
