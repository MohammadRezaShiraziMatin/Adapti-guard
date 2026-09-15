# Reconstructed prompt — Q1 raise of Phase-1 scientific report

**Role:** Canonical audit-trail reconstruction of the instruction that the Q1 raise of `docs/paper/dual_track/PHASE1_SCIENTIFIC_REPORT.md` was meant to satisfy.  
**Use:** Reproducibility / intent record; template for future “raise doc X to Q1 internal standard” tasks.  
**Not:** A request to re-run live eval or retune.

Paths below match **this** repository’s dual-track layout (equivalent to the abstract `docs/paper/dual_track/…` naming in the original reconstruction brief).

---

```
TASK: Raise docs/paper/dual_track/PHASE1_SCIENTIFIC_REPORT.md to Q1 internal-documentation
statistical/claims standard. Docs only. No new live run. No retune.

REQUIREMENTS

1. Statistics completeness
   - Pull Track B’s δ̂ 95% CI directly from the frozen AUDIT / metrics
     (experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/).
     Quote it exactly; do not invent precision beyond the artifact.
   - Check whether Track A AUDIT / verdict contains an equivalent CI for δ̂. If it does not,
     state this explicitly as a gap ("BLOCKING GAP — not in AUDIT"). Do NOT compute, estimate,
     or backfill a CI for Track A that isn’t in the frozen artifact.
   - Add a secondary Bayes-factor note: BF10 ≈ (b10+1)/(b01+1) (Laplace-smoothed), computed from
     the frozen b10/b01 counts for both tracks. Cite Kass & Raftery (1995) grading bands and state
     which band each track’s BF10 falls into. Do not use the Bayes factor to argue Track A should
     be reclassified — descriptive context only.
   - Add a brief power/MSID note: given N=61 and MSID=0.20, state the implied minimum detectable
     effect relationship in plain terms (no new simulation — short explanatory note only).
   - Recheck every reported p-value and cost figure against the frozen AUDIT/verdict/metrics exactly.
     If any drafted number drifted from the source, correct it to match the frozen artifact and note
     the correction in a changelog at the bottom of the doc.

2. A-vs-B tension section (§4.3 or equivalent)
   - State plainly: Track A FAIL, Track B SUPPORTED_IMPROVEMENT, on different packs and
     different treatments (and, if true per configs, different target models — check this).
   - Explain that different scope/treatment and different realized effect size relative to
     MSID are sufficient explanations for the divergent classifications, without needing to
     invoke or assume anything about pack independence.
   - Explicitly disclaim: this section does NOT use pack-independence (or its absence) as the
     explanation for the A-vs-B difference — that stays a separate question.

3. Move the independence question to Limitations (until an audit closes it)
   - The unresolved pack-independence question (episode-level provenance not yet audited)
     should live in a clearly labeled Limitations subsection, with:
     - explicit statement that it is unresolved, not resolved-by-assumption
     - the direction of bias if packs were NOT independent
     - an explicit list of forbidden phrasing until closed
   - Later close-out (separate task): offline independence audit may update §5.1 status without
     changing frozen Track A/B numbers.

4. Claims tightening
   - Cross-check every claim against docs/paper/dual_track/CLAIMS_DUAL_TRACK.md allowed/forbidden
     phrasing. Soften or remove any sentence that drifts into forbidden territory (e.g., anything
     implying Track B validates or rehabilitates Track A).

5. Reproducibility + changelog
   - Add/update a REPRO section listing exact run_ids, pack SHAs, and file paths a human needs
     to re-derive every number quoted in the report.
   - Add a changelog table at the bottom: each row = one substantive correction/addition in this
     pass, with short justification and section affected.

HARD CONSTRAINTS
- Do not touch datasets/frozen/** or experiments/real_llm_eval/** — read-only sources.
- Do not change classification, MSID decision, or utility eligibility for either track.
- 0 live LLM/API calls for this task.
- No merge — PR for human review only.

DELIVERABLE
Single commit/PR updating docs/paper/dual_track/PHASE1_SCIENTIFIC_REPORT.md primarily (call out
any necessary cross-reference fixes separately). PR description must state: which numbers were
verified against which exact frozen file/field, and confirm freeze-check ALL_PASS with the actual
verification method used (not just the phrase "ALL_PASS" — show what was compared).
```

## Mapping note (delivered Q1 raise)

The implemented Q1 raise lived on the Phase-1 confirmatory live-run branch and:

- Quoted Track B CI `[0.2757, 0.6096]` from AUDIT; flagged Track A δ̂ CI as **BLOCKING GAP**
- Justified BF₁₀≈28 from frozen 27/0 via Kass & Raftery; left Track A FAIL untouched
- Added §4.3 A-vs-B tension (scope / realized effect / method)
- Parked independence in Limitations until the offline audit (`PHASE1_INDEPENDENCE_AUDIT.md`)
- Kept AUDIT δ̂ / p / U / b10/b01 frozen
