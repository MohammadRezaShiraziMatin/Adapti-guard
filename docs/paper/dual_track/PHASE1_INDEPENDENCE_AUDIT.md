# Phase-1 confirmatory pack — independence audit

**Status:** Docs + offline verification only.  
**API / live LLM calls:** **0**  
**Frozen packs:** read-only (not modified).  
**Branch:** `cursor/phase1-independence-audit-1411`  
**Repro:** `python3 scripts/audit_phase1_confirm_independence.py`  
**Metrics JSON:** `docs/paper/dual_track/artifacts/phase1_independence_audit_metrics.json`

---

## Question

Does `phase1_confirm_v1` share prompts, seeds, paraphrase families, or scenario templates with:

1. the VNEXT confirmatory pack, or
2. any frozen pack that touched detector DEV/VAL / tuning surfaces?

---

## Packs checked

Paths confirmed via each pack’s `manifest.json` before read.

| Pack | Path | SHA-256 (`dataset.jsonl`) | Role |
|------|------|---------------------------|------|
| Phase-1 confirm (Track B) | `datasets/frozen/phase1_confirm_v1/dataset.jsonl` | `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` | Confirmatory TEST |
| VNEXT confirm (Track A) | `datasets/frozen/vnext_confirm_v1/dataset.jsonl` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` | Official VNEXT confirm |
| Layer A v2 | `datasets/frozen/layer_a_v2/dataset.jsonl` | `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33` | Legacy Layer A |
| Layer A v3 | `datasets/frozen/layer_a_v3/dataset.jsonl` | `abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd` | Layer A aggregate |
| Layer A v3 train/dev/test_split | `datasets/frozen/layer_a_v3/{train,dev,test_split}.jsonl` | (see metrics JSON) | DEV/VAL (+split view) |
| Phase-1 holdout pilot | `datasets/frozen/phase1_holdout_v1/dataset.jsonl` | `c42e979724cdb29d353366d0a77f5bccb28ad2cb337e775592a72b516da7b1bd` | Pilot N=40; not confirmatory N |
| eval_v1 | `datasets/frozen/eval_v1/dataset.jsonl` | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` | Broader eval surface |

---

## Method (deterministic; no LLM)

1. **Episode metadata** (as stored; no invented fields):
   - `metadata.provenance`, `metadata.generation_method`, `metadata.seed`, `metadata.attack_family`
   - creation date: **absent** → **UNKNOWN** for every episode
   - `derived_from_vnext_pack`: **field absent** (provenance string claims independence; not sole proof)
2. **Exact duplicate screen:** SHA-256 of whitespace-normalized `prompt`, and of `prompt+context`.
3. **Near-duplicate screen:** character 5-gram Jaccard on normalized prompts (+ `SequenceMatcher` ratio for pairs above threshold).
   - vs VNEXT: report Jaccard ≥ 0.25
   - vs other packs: report Jaccard ≥ 0.40
4. **Builder lineage (git, read-only):**
   - `scripts/build_phase1_confirm_v1.py` — seed `20260914`; exact-match contamination screen against VNEXT, Layer A, `phase1_holdout_v1`
   - `scripts/build_vnext_confirm_v1_pack.py` — seed `61`; separate builder
5. **Detector-touching packs (documented):**
   - `configs/phase1_detector_lock.json` + `docs/paper/phase1/PHASE1_DETECTOR_STUDY.md` (stub: `docs/experiments/PHASE1_DETECTOR_STUDY.md`): DEV/VAL = Layer A train/dev; confirm pack **no tuning**; holdout = pilot; lock forbids edits justified by holdout or confirm outcomes
   - Holdout manifest: not used to fit `evidence_phase1.0`

---

## Episode provenance summary (Track B; N=122)

| Field | Observed value | Coverage |
|-------|----------------|----------|
| `metadata.provenance` | `authored_phase1_confirm_v1_independent` | 122/122 |
| `metadata.generation_method` | `template_authored_no_llm_no_detector_fit` | 122/122 |
| `metadata.seed` | `20260914` | 122/122 |
| creation date | **UNKNOWN** (no date field) | 122/122 |
| `derived_from_vnext_pack` | **UNKNOWN** (field absent) | 122/122 |

VNEXT contrast: `provenance=synthetic_vnext_confirm_v1`, `generation_method=authored_synthetic_no_llm`, `seed=61` (122/122).

Marker tokens in text: Phase-1 `P1C-*` vs VNEXT `VNC1-*` — **zero string intersection** of marker families (offline scan).

---

## Results — overlap

| Comparator | Exact prompt | Exact prompt+context | Near-dupes | IDs |
|------------|--------------|----------------------|------------|-----|
| `vnext_confirm_v1` | **0** | **0** | **0** (J≥0.25) | — |
| `layer_a_v2` / `layer_a_v3` (+splits) | 0 | 0 | 0 (J≥0.40) | — |
| `eval_v1` | 0 | 0 | 0 (J≥0.40) | — |
| `phase1_holdout_v1` | **0** | **0** | **59** pairs (J≥0.40) | Top: `p1c_ben_042`↔`p1h_ben_012` (J≈0.796); `p1c_ben_046`↔`p1h_ben_016` (J≈0.685); attack paraphrases also present — full list in metrics JSON |

**Family-name overlap with VNEXT:** shared threat taxonomy labels (`DIRECT_OVERRIDE`, `OBFUSCATION`, `PRIVILEGE_EXFIL`, `TOOL_OUTPUT_INJECTION`, etc.). Name overlap ≠ shared origin: different builders, seeds, markers, and **zero** prompt near-dupes at J≥0.25.

**Holdout kinship:** builder blocks exact copies; residual **template paraphrase** similarity remains (same Phase-1 authoring style). Holdout is pilot / not confirmatory N / documented **non-fit** for `evidence_phase1.0`.

---

## Verdict

### **INDEPENDENT** (scoped to VNEXT confirmatory pack text)

Track B episode text is **independent of `vnext_confirm_v1`** under exact/near-duplicate screens, with distinct seed/builder/markers, and shows **no exact or near prompt overlap** with Layer A DEV/VAL / `eval_v1` surfaces checked here.

**Not claimed:**

- Chronological independence from detector iteration (creation dates **UNKNOWN**)
- Zero template kinship with pilot `phase1_holdout_v1` (near-pairs = 59; exact = 0)
- Track B reverses Track A `FAIL`
- Cluster-adjusted McNemar p/CI (not run; AUDIT numbers frozen)

### What would strengthen further

| Gap | Status | Closes if… |
|-----|--------|------------|
| Episode `created_at` | UNKNOWN | Future packs freeze dates at authoring (do not fabricate retroactively) |
| Holdout template register | Documented residual | Optional qualitative template-family map |
| Cluster-robust sensitivity | Not run | Separate stats task; does not edit frozen AUDIT |

---

## Claims impact

- **Allowed:** “separate confirmatory pack; episode audit found no prompt/seed/marker overlap with VNEXT confirm (`PHASE1_INDEPENDENCE_AUDIT.md`).”
- **Still forbidden:** “Track B reverses Track A,” “VNEXT now works,” unbounded generalization beyond `phase1_confirm_v1`.
- Holdout caveat required if claiming fully novel Phase-1 threat surface.

Frozen Track A/B δ̂ / p / U / b10/b01 **unchanged**.

---

## Integrity

| Check | Result |
|-------|--------|
| Track B SHA | `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |
| Track A SHA | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| `datasets/frozen/**` edited? | **No** |
| Live API calls | **0** |
| Detector / thresholds edited? | **No** |
| Merge performed? | **No** (PR for human review) |
