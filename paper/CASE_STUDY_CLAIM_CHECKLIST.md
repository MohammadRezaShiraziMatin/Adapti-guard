# Case Study Claim-to-Evidence Checklist

| ID | Claim | Evidence | Type | Open issue |
|---|---|---|---|---|
| C1 | Controller reaches de-escalation and avoids prior oscillation | docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md; docs/ADAPTIVE_CONTROLLER_SPEC.md; controller tests | Implementation | Confirm final test count |
| C2 | Adaptive does not demonstrate superiority over best fixed level | results/f3_confirmatory/RESULTS.md | Confirmatory | Preserve inconclusive wording |
| C3 | Primary difference is -0.0118 with CI [-0.0258,+0.0024] | results/f3_confirmatory/RESULTS.md | Confirmatory | None |
| C4 | Adaptive-dev loss 0.2902 vs fixed-L1 0.3020; cost 0.080 vs 0.100 | results/f3_confirmatory/RESULTS.md | Confirmatory | None |
| C5 | Adaptive-exp is worse than fixed-L1 by +0.0663 [+0.0550,+0.0771] | results/f3_confirmatory/RESULTS.md | Secondary | Keep secondary |
| C6 | Burst-only adaptive-dev comparison is significant under uncorrected secondary CI | results/f3_confirmatory/RESULTS.md | Secondary | Do not elevate |
| C7 | Exploratory v2 found no adaptive domination | results/q1_f3_real_llm_v2/FINDINGS.md; SUMMARY.md | Exploratory | Keep separate |
| C8 | Fresh v2 regex recall was 0.258 vs 0.943 on v1 design pool | results/q1_f3_real_llm_v2/FINDINGS.md | Exploratory | Preserve denominator/context |
| C9 | Confirmatory detector recall 0.82; benign flag rate 0.028 | results/f3_confirmatory/RESULTS.md | Descriptive | Do not generalize |
| C10 | Semantic guard reached 0.75 recall with 0/20 benign flagged | docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md | Exploratory | Verify final source table |
| C11 | Loss = ASR + 0.5(1-utility) + cost | docs/F3_CONFIRMATORY_CONTRACT.md | Method | None |
| C12 | Confirmatory design frozen at a00ef03 and executed once | docs/F3_CONFIRMATORY_CONTRACT.md | Provenance | Verify final SHA wording |
| C13 | Confirmatory pool contains 54 attacks and 32 benign prompts | docs/F3_CONFIRMATORY_CONTRACT.md | Method | None |
| C14 | Confirmatory seeds are 1000–1019 | docs/F3_CONFIRMATORY_CONTRACT.md | Method | None |
| C15 | Adaptive-dev selected from 16 development configurations | docs/F3_CONFIRMATORY_CONTRACT.md | Method/limitation | Explicit disclosure |
| C16 | Detector is the principal bottleneck | v2 findings + case study + confirmatory results | Interpretation | Keep case-study scope |

## Numerical-source rule
Every numerical table/figure must retain a nearby source path. Authoritative adaptive sources are results/f3_confirmatory/RESULTS.md, runs_v3.json, episodes_v3.jsonl, results/q1_f3_real_llm_v2/SUMMARY.md, and FINDINGS.md.

## Open TODOs
1. Author block.
2. Venue.
3. Anonymization.
4. Attack-template release policy.
5. Venue-specific AI-assistance disclosure.
6. Verify final context-aware defense citation.
7. Verify final controller test-count number before stating it.
8. Venue-specific statistical reporting requirements.
9. Decide whether historical review scores belong in the paper.
10. Final independent copy-edit and reference verification.

## Citation TODOs
- [CITATION NEEDED] Context-aware prompt-injection defense/provenance-aware auditing paper if retained as a distinct related-work claim.