# Phase-1 holdout overlap audit

**Status:** Docs + git-history / offline text forensics only.  
**API / live LLM calls:** **0**  
**Frozen dirs:** `datasets/frozen/**` and `experiments/real_llm_eval/**` not modified.  
**Branch:** `cursor/phase1-holdout-overlap-audit-1411`  
**Does not reopen:** Track B vs VNEXT independence (already **INDEPENDENT** in `PHASE1_INDEPENDENCE_AUDIT.md`).

**Repro:**

```bash
git log --all --format='%H %cI %s' -- datasets/frozen/phase1_holdout_v1
git log --all --format='%H %cI %s' -- configs/phase1_detector_lock.json configs/phase1_confirm_live_lock.json
python3 scripts/audit_phase1_holdout_overlap_origin.py
```

**Artifacts:** `docs/paper/dual_track/artifacts/phase1_holdout_overlap_origin.json`

---

## Two questions (kept separate)

1. **Tuning usage:** Was `phase1_holdout_v1` read/scored/used as signal while `evidence_phase1.0` / PHASE1-CORE thresholds were tuned or selected?
2. **Similarity origin:** Why do confirm↔holdout prompts show 59 near-pairs (Jaccard ≥ 0.40)?

---

## Q1 — Tuning usage (git + code forensics)

### Config filenames (confirmed)

- `configs/phase1_detector_lock.json`
- `configs/phase1_confirm_live_lock.json`

### Timeline (chronological; CommitDate UTC)

| Time (UTC) | Commit | What touched |
|------------|--------|--------------|
| 2026-09-14 19:09:08 | `c462945a0c0a29ab9a9593e33a73983e4e42a1ab` | **Adds** `src/adapti_guard/detector/prompt_injection_detector_phase1.py` (`evidence_phase1.0`); updates `risk_engine_core.py` / `core_policy.py`. Message: “Add Phase1 detector… Refine risk floors…”. **No** `phase1_holdout_v1` path exists yet in tree. |
| 2026-09-14 19:11:17 | `45ef1e13e48cd1687f9b5e59ecddddaeaafdca7c` | Quality-gate docs + `scripts/run_phase1_core_offline_eval.py` still points at **VNEXT** pack (`PACK = …/vnext_confirm_v1/dataset.jsonl` at this commit). Documents diagnostic 56/61 on VNEXT; “no VNEXT threshold tune”. Holdout still absent. |
| 2026-09-14 19:40:19 | `519ceff4640a71164efe18e9c7056f924e9dd34f` | **First** (and only) commit creating `datasets/frozen/phase1_holdout_v1/**`. Same commit adds `configs/phase1_detector_lock.json` hashing `evidence_phase1.0` and records offline holdout metrics via `scripts/run_phase1_independent_offline_eval.py`. |
| 2026-09-14 19:55:59 | `20f389b5214b5cd6bae433b346e5d22a5f2bef2f` | Creates `phase1_confirm_v1` + `scripts/build_phase1_confirm_v1.py`. Lock JSON: moves `independent_test` → confirm pack; demotes holdout to `pilot_holdout`. Cosmetic `0.60`→`0.6`. **Does not** modify `prompt_injection_detector_phase1.py` / `risk_engine_core.py` / `core_policy.py`. |
| later | `567d0c6…`, `a2681e9…`, etc. | Live-lock / runner / results docs. No holdout-driven detector edits found. |

**Holdout path history:** `git log --all -- datasets/frozen/phase1_holdout_v1` returns **only** `519ceff`.

**Detector / threshold code after holdout freeze:**  
`git log --all -- src/adapti_guard/detector/prompt_injection_detector_phase1.py` → tip is still `c462945` (no later edits).  
Same for risk thresholds: `medium_threshold = 0.25`, `high_threshold = 0.60` set in `c462945` and unchanged afterward.

**SHA lock integrity (inspected):**

```text
sha256(c462945:prompt_injection_detector_phase1.py)
  == lock@519ceff detector.sha256
  == e02f3c64aa563bccc815444f672bbced753d4685e7fbc16dc31a93bd41b189a3
sha256(c462945:risk_engine_core.py)
  == lock@519ceff risk.sha256
  == 0f447ee23c4d3106e57baefa11869a4c43913264b5efa451c6c5a2ea3723b1b2
```

Current working-tree detector file byte-identical to `c462945` blob (checked this task).

### Same-window flag (manual review)

`c462945` (detector) → ~31 min → `519ceff` (holdout freeze + lock + offline score) → ~16 min → `20f389b` (confirm pack).

This is a freeze-then-measure sequence for holdout, **not** measure-then-retune: detector bytes locked in `c462945` are exactly what `519ceff` hashes; no subsequent threshold/detector commit follows holdout metrics.

### Commit-message grep

`git log --all --grep=phase1_holdout` / holdout: hits `519ceff` (create/lock), later independence-audit docs. No message pairs holdout with “tune/fit/calibrat/adjust threshold” as an action taken.

### Script classification (`phase1_holdout_v1` references)

| Artifact | First commit | Class | Basis |
|----------|--------------|-------|-------|
| `scripts/run_phase1_independent_offline_eval.py` | `519ceff` | **(b) score-and-report** | Scores locked detector on holdout; docstring: “Does not retune.” Output frozen as `docs/experiments/artifacts/phase1_independent_offline_metrics.json` in same commit. **No later detector edit cites these metrics as a fit target.** |
| `tests/test_phase1_core_pipeline.py` | `519ceff` (hash assert); updated `20f389b` | **(a) integrity** | SHA / lock assertions only. |
| `scripts/build_phase1_confirm_v1.py` | `20f389b` | **(a) contamination screen** | Exact-normalized prompt/context forbid-list vs holdout (and VNEXT/Layer A). Does not score detector. |
| `scripts/audit_phase1_confirm_independence.py` | `307f996` | **(a) audit** | Overlap statistics only. |
| `scripts/run_phase1_core_offline_eval.py` (pre-holdout) | `8532a8` / `45ef1e` | N/A to holdout | At `45ef1e` packs **VNEXT**, not holdout. |

Docs (`PHASE1_FINAL_CLOSEOUT.md`, `PHASE1_DETECTOR_STUDY.md`) record holdout as pilot/TEST measurement **after** lock rules that forbid further edits justified by holdout outcomes (`configs/phase1_detector_lock.json` rules array, introduced `519ceff`, extended `20f389b`).

### Q1 verdict: **NOT_USED_IN_TUNING**

**Meaning:** In reachable git history, `phase1_holdout_v1` did **not** exist before `evidence_phase1.0` was authored (`c462945`). Holdout was introduced in the same commit that hash-locked that already-authored detector. No post-holdout commit changes detector/threshold/policy source hashed by the lock.

**Honest limit (not upgraded to INCONCLUSIVE):** Git cannot observe uncommitted local drafts. If someone edited holdout text privately *before* `519ceff` while also editing detector code, that would leave no path history. Against that hypothetical: (i) no holdout path/blob before `519ceff`, (ii) quality-gate docs at `45ef1e` attribute Phase-1 detector motivation to **VNEXT diagnostic** misses (56/61), not holdout, (iii) detector SHA is unchanged from pre-holdout commit through today.

**Out of scope but noted:** VNEXT-diagnostic influence on `evidence_phase1.0` feature design is a separate axis (already discussed in Phase-1 quality-gate docs). It is **not** holdout→detector contamination.

---

## Q2 — Textual similarity origin

### Counts (same method as independence audit; J≥0.40)

From `python3 scripts/audit_phase1_holdout_overlap_origin.py` / full classification:

- Near-pairs: **59** (benign↔benign 37; attack↔attack 22)
- Exact prompt / prompt+context: **0** (builder contamination screen + this classification)
- Many-to-one inflation: e.g. `p1h_ben_004` appears in **10** pairs; `p1h_atk_019` in **9**; `p1h_atk_004` in **9**

### Full 59/59 pair classification (this close-out)

**Repro:** `python3 scripts/classify_phase1_holdout_pairs_full59.py`  
**Tables:** `docs/paper/dual_track/artifacts/phase1_holdout_pairs_full59.md`  
**JSON:** `docs/paper/dual_track/artifacts/phase1_holdout_pairs_full59.json`

| Class | Count |
|-------|------:|
| `SAME_SCAFFOLD_DIFF_ENTITY` | 35 |
| `SAME_SCAFFOLD_DIFF_WORDING` | 24 |
| `COINCIDENTAL_SHORT_OVERLAP` | 0 |
| `GENUINE_DUPLICATE` | **0** |

**Statement:** **0 of 59 are `GENUINE_DUPLICATE`.** Every near-pair is scaffold reuse (entity/value swap or paraphrase), not an exact clone. No pair required stopping for contamination escalation under the Part A rule.

Classes were assigned by inspecting each pair’s prompt/context text (not metadata provenance fields). Full per-pair table with J, SequenceMatcher ratio, and one-line justification is in the artifacts linked above (not inlined here to keep this audit readable).

### Builders

| Pack | Builder in git | Seed (metadata) |
|------|----------------|-----------------|
| `phase1_holdout_v1` | **No** `scripts/build_*holdout*.py` anywhere in history; pack files appear fully formed in `519ceff` | `1411` |
| `phase1_confirm_v1` | `scripts/build_phase1_confirm_v1.py` (`20f389b`) | `20260914` |

No shared importable template module. Confirm builder **duplicates** the same scaffolds as holdout text (standup email, maintenance ticket, translate hard-neg, RAG “retrieved note…”, tool “recommended action”, delayed “hidden step”), then parameterizes IDs/`P1C-*` markers. Confirm builder also **exact-match screens** against holdout (`build_phase1_confirm_v1.py` forbid set includes holdout path) — explains zero exact copies despite shared scaffolds.

### Illustrative diffs (not a sample substitute — full table is 59/59)

| Pair | J / SM | Class |
|------|--------|-------|
| `p1c_ben_042` ↔ `p1h_ben_012` | 0.796 / 0.949 | `SAME_SCAFFOLD_DIFF_ENTITY` (Spanish vs French) |
| `p1c_ben_046` ↔ `p1h_ben_016` | 0.685 / 0.861 | `SAME_SCAFFOLD_DIFF_WORDING` (log-parse hard-neg) |
| `p1c_ben_004` ↔ `p1h_ben_004` | 0.676 / 0.894 | `SAME_SCAFFOLD_DIFF_ENTITY` (standup body) |
| `p1c_atk_020` ↔ `p1h_atk_019` | 0.571 / 0.833 | `SAME_SCAFFOLD_DIFF_WORDING` (recommended-action) |
| `p1c_atk_011` ↔ `p1h_atk_004` | 0.506 / 0.809 | `SAME_SCAFFOLD_DIFF_WORDING` (retrieved-note RAG) |

### Q2 verdict: **SHARED_TEMPLATE_FAMILY (not shared seed; not exact clone)**

Similarity is explained by **reused Phase-1 threat/benign scaffolds** authored ~15 minutes apart (`519ceff` then `20f389b`), with confirm intentionally parameterizing variants and blocking exact copies. Seeds differ (`1411` vs `20260914`). No common generation library in-repo. **Full 59/59 review:** 0 `GENUINE_DUPLICATE`, 35 entity-swap, 24 wording-paraphrase scaffolds.

---

## Combined risk statement (Track B implications)

| Finding | Implication for Track B `SUPPORTED_IMPROVEMENT` |
|---------|--------------------------------------------------|
| Q1 **NOT_USED_IN_TUNING** | Holdout was **not** a detector-fit set in git history. No basis from this audit to claim thresholds were selected on holdout then confirmed on a near-duplicate pack. |
| Q2 **SHARED_TEMPLATE_FAMILY** | Confirm and holdout are **stylistically related**. This weakens claims of a fully novel Phase-1 threat *surface*, but is **cosmetic relative to detector contamination**. Exact copies are absent. |
| Together | **Not the most serious case** (that would require tuning usage **and** near-duplicate confirm). Track B live AUDIT numbers stay authoritative; do **not** reclassify. Preferred language: scoped VNEXT-pack independence stands; holdout kinship = shared scaffolds without tuning contamination. |

**Still open (unchanged):** cluster-robust McNemar sensitivity; episode creation dates UNKNOWN; Track A δ̂ CI BLOCKING GAP.

---

## Integrity

| Check | Result |
|-------|--------|
| API calls | **0** |
| `datasets/frozen/**` edited? | **No** |
| `experiments/real_llm_eval/**` edited? | **No** |
| Detector / thresholds edited? | **No** |
| Track A/B δ̂, p, U, b10/b01 edited? | **No** |
| Merge | **No** |
