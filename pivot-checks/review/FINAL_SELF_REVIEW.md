# Final self-review of MANUSCRIPT_DRAFT_v2.md (hostile-reviewer reading, 2026-10-16)

Backups: `backups/MANUSCRIPT_DRAFT_v2.pre_selfreview.md` and `backups/MANUSCRIPT_DRAFT_v2.pre_selfreview_1416.md`. A concurrent edit by another session at 14:12 had already fixed 70→55 (`MANUSCRIPT_DRAFT_v2_pre_gtfix.md`, erratum in drift/GT_AUDIT.md); this review builds on that version.

## Severity 1: would sink the paper
1. **Venue scope (not a text issue).** Computers & Security currently excludes the security of LLM systems (moratorium; see review/JOURNAL_REQUIREMENTS.md). UNFIXABLE in the text; needs an owner decision.
2. **Single AI reviewer who also designed the analyses produced every manual label.** This affects checker-vs-judge precision and recall, scorer validation (κ 0.645) and the remapping. Already disclosed (§7.1, §7.3, §8). UNFIXABLE without human labels; owner labels are pending (§7 of the plan; `review/owner_agreement.py` is ready).
3. **The confirmatory M1 result is narrow and method-sensitive.** Under task-clustered Holm the full data keep 1/9 cells, and the confirmatory pairs change. FIXED as wording: the abstract now says "reverses at least one significant pairwise order involving an execution-time defense … in 3/9 cells", not "reverses the rank of execution-time defenses". The robustness table is the only claim basis.

## Severity 2: overclaims and label errors (fixed)
4. **M3 labelled "[CONFIRMATORY — code fact]".** The audit was never preregistered. FIXED → "[CODE FACT — deterministic audit, not a preregistered test]".
5. **Drift labelled "[CONFIRMATORY in method]".** The prereg file logs the replay as "unplanned" (deviation list item 3). FIXED → "[EXPLORATORY — unplanned replay …]".
6. **The abstract presented the "checker right in 20/20" result without saying who judged.** FIXED: "by a single AI reviewer".
7. **70 vs 55.** RESOLVED (by the concurrent edit, verified here): AgentDyn `get_suites("v1")` and the audit output hold 55 injection tasks (21 fail, 20 defects); "70" in drift/GT_AUDIT.md is not reproducible and is marked as an erratum there. The manuscript uses 55. No [CHECK] tag remains.

## Severity 3: missing limitations (fixed)
8. The preregistered bootstrap resamples episodes and applies no multiplicity correction over 290/299 pairs, and each AgentDyn confirmatory cell has only 20 user-task clusters. ADDED to §7.1 "Statistics".
9. The confirmatory subset retains dailylife injection tasks 2 and 6, which fail their own check. ADDED as a §7.1 bullet (it was previously only in §5.2).

## Severity 4: notation (fixed)
10. Flip, cell, pairs tested, τb, κ, b10/b01, δ̂ and J+C−/J−C+ were used before being defined. ADDED a notation block in §3.

## Related work vs review/RELATED_FULLREAD.md
11. All Shaw and Pathade statements in §2 and §5.2 were checked against RELATED_FULLREAD.md:
    - Shaw: §IV D2, §VII-A, §VII-B, §V-A, §V-D, §V-F.
    - Pathade: §III, §V-B, §VIII; 29.7%; 1 of 25.
    - Consistent; no change.
12. The Same Zero (11/75) and Hardy et al. rest on partial reads. They are already tagged as partial; UNFIXABLE without a full read.
13. Liu 2610.03448 rests on LIU_JUDGE_READ.md, not RELATED_FULLREAD.md. Kept, with its source tag.

## Remaining, not fixable without new data or decisions
- Owner labels (16 items) are absent. Placeholder text is in place, and an alternative paragraph is ready (`review/OWNER_LABELS_PARAGRAPHS.md`).
- The AgentDyn maintainers have not been contacted (issue draft only).
- No independent reproduction.
- The own-harness E1–E5 evidence is taken from the unpublished v1 and cannot be checked from this folder. Its numbers are verified against the v1 text only (verify_numbers Part 2).
- The CA scorer deviates from the preregistration (substring match), so it is used for no claim.
- The AgentDyn paper citation (arXiv 2602.03117) is named in the preregistration file, but its title and authors were not verified from the paper. It is marked [CITATION TO VERIFY] in the submission.

## Number check after the fixes
`python3 review/verify_numbers.py` → hard-check mismatches 0; text-search unmatched 0 (on MANUSCRIPT_DRAFT_v2.md).
