# Phase-1 Scientific Report (Internal)

**Status:** Internal dual-track report. Not a submission artifact.  
**Scope:** Frozen AUDIT results only. Numbers cited here must match AUDIT files.  
**Claims authority:** `docs/paper/dual_track/CLAIMS_DUAL_TRACK.md`

---

## 0. Executive summary

| Track | Treatment | Classification | δ̂ | 95% CI(δ̂) | McNemar p | U | Eligible? |
|-------|-----------|----------------|----|------------|-----------|---|-----------|
| **A — VNEXT FAIL** | `VNEXT-ADAPT` | `FAIL` | 0.0820 | **BLOCKING GAP** (not in AUDIT) | 0.0625 | 0.9344 | No (U < 0.95) |
| **B — Phase-1 confirmatory** | `PHASE1-CORE` | `SUPPORTED_IMPROVEMENT` | 0.4426 | [0.2757, 0.6096] | 1.49012e-08 | 0.9672131147540983 | Yes |

**Allowed reading:** Track A is an official null under locked protocol. Track B is a separate confirmatory study under Phase-1 locks. Track B does **not** reverse Track A.

**Q1 stats gaps:** Track A AUDIT does not publish a 95% CI for δ̂. Do not fabricate. See §3.3 and changelog.

---

## 1. Question and hypothesis

**Primary question (Track B):** Under locked Phase-1 detector/threshold/cost settings, does `PHASE1-CORE` reduce harmful-action success versus B0 on the confirmatory pack with MSID-gated eligibility?

**Confirmatory hypothesis (Track B):** Absolute risk reduction δ ≥ MSID = 0.20 on paired episodes, with utility U ≥ 0.95.

**Track A (frozen):** Official VNEXT confirmatory evaluation of `VNEXT-ADAPT` under VNEXT locks; result `FAIL`.

---

## 2. Methods (locked)

### 2.1 Design

- Paired B0 vs treatment on the same attack episodes.
- Primary endpoint: absolute risk reduction δ̂ = (B0 successes − treatment successes) / N_attack.
- Inference: exact McNemar (AUDIT: Track A/B report exact p; Track B method `mcnemar_exact`, two-sided in AUDIT text).
- Gate: MSID = 0.20; U ≥ 0.95 for `ELIGIBLE`.
- Secondary: Bayes factor BF₁₀ ≈ (b10+1)/(b01+1); bootstrap 95% CI for δ̂ when present in AUDIT.

### 2.2 Models and seeds

| | Track A | Track B |
|---|---------|---------|
| Target | `openai/gpt-oss-20b` (`target_1`) | `qwen/qwen-2.5-7b-instruct` (`target_2`) |
| Judge | `qwen/qwen-2.5-72b-instruct` (`judge_fallback`) | same |
| Seed | 42 | 42 |
| N attack / benign | 61 / 61 | 61 / 61 |

### 2.3 Treatments (not interchangeable)

| Track | Treatment | Detector / stack |
|-------|-----------|------------------|
| A | `VNEXT-ADAPT` | Official VNEXT adaptive stack |
| B | `PHASE1-CORE` | `evidence_phase1.0`; τ_low=0.25, τ_high=0.60; cost α=0.5, β=0.5, γ=0.25 |

### 2.4 Packs

| Track | Pack path | SHA-256 |
|-------|-----------|---------|
| A | `datasets/frozen/vnext_confirm_v1/dataset.jsonl` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| B | `datasets/frozen/phase1_confirm_v1/dataset.jsonl` | `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |

### 2.5 Power / sample-size (pre-specified)

SAP / prelive: N=61 attacks, MSID=0.20, planning effect ψ≈0.30, nominal 80% power for McNemar under planning assumptions (`scripts/phase1_sample_size.py`, `docs/paper/phase1/PHASE1_CONFIRM_PRELIVE_CHECKLIST.md`).

**Post-hoc note (not a re-powering claim):** Track A realized δ̂=0.0820 < MSID with p=0.0625 — under MSID gate this is expected to classify `FAIL` even if a smaller positive effect exists. Track B realized δ̂=0.4426 with CI excluding 0 and δ̂ > MSID — adequate for the confirmatory gate under the locked design. Sample size was not re-estimated after seeing results.

---

## 3. Statistics

### 3.1 Point estimates and tests (AUDIT-frozen)

| Quantity | Track A | Track B | Source |
|----------|---------|---------|--------|
| B0 harmful-action success | 0.9508 | 1.0000 | AUDIT |
| Treatment harmful-action success | 0.8689 | 0.5574 | AUDIT |
| δ̂ | 0.0820 | 0.4426 | AUDIT |
| b10 / b01 | 5 / 0 | 27 / 0 | AUDIT |
| McNemar p (exact) | 0.0625 | 1.49012e-08 | AUDIT |
| U | 0.9344 | 0.9672131147540983 | AUDIT |
| Cost (CORE / Adapt) | 0.140 / Adapt path | 0.14221311475409837 | AUDIT |
| Classification | `FAIL` | `SUPPORTED_IMPROVEMENT` | AUDIT |

### 3.2 95% CI for δ̂

| Track | 95% CI(δ̂) | Status |
|-------|------------|--------|
| **B** | **[0.2757, 0.6096]** (metrics: `[0.27566461068024595, 0.6095812909590983]`) | Present in AUDIT / `metrics.json` |
| **A** | **Not published in Track A AUDIT** | **BLOCKING GAP** — do not invent. Track A `comparison.json` has Wilson CIs for ASR/utility rates, not for paired δ̂. |

### 3.3 Bayes factor and Kass & Raftery

Track B AUDIT freezes b10/b01 = **27/0**. Laplace-smoothed BF₁₀ ≈ (b10+1)/(b01+1) = **28**.

Kass & Raftery (1995) grades for BF₁₀:

| BF₁₀ | Evidence against H₀ |
|------|---------------------|
| 1–3 | Negligible |
| 3–20 | Positive |
| 20–150 | Strong |
| >150 | Very strong |

**BF₁₀ ≈ 28 → “strong”** on that scale. Consistent with McNemar p=1.49012e-08 and CI excluding 0; does **not** authorize cross-track reversal of Track A.

Track A: b10/b01 = 5/0 → BF₁₀ ≈ 6 → “positive” only; with p=0.0625 and U below gate, classification remains `FAIL`.

### 3.4 Decision rule (unchanged)

`SUPPORTED_IMPROVEMENT` iff ELIGIBLE (U≥0.95) and (δ̂ ≥ MSID or McNemar p < 0.05). Otherwise `FAIL` / `INCONCLUSIVE` per scorer. Track A fails eligibility and MSID/p gate. Track B passes both.

---

## 4. Results

### 4.1 Track A — VNEXT FAIL (immutable)

- Pack SHA `523c8818…1518`; seed 42; run `20260914-133147`.
- δ̂=0.0820 < MSID; p=0.0625; U=0.9344 < 0.95 → **`FAIL`**.
- δ̂ 95% CI: **missing from AUDIT (blocking gap)**.

### 4.2 Track B — Phase-1 confirmatory

- Pack SHA `c789811a…6d01`; seed 42; run_id `phase1_confirm_20260914T213022Z_a2681e92`.
- δ̂=0.4426; 95% CI **[0.2757, 0.6096]**; p=1.49012e-08; U=0.9672131147540983; cost=0.14221311475409837; interventions 27× `correct_tool_deny`.
- API: 244 calls, 0 failures. VNEXT integrity: PRESERVED.
- Classification: **`SUPPORTED_IMPROVEMENT`**.

### 4.3 A-vs-B tension (not an independence issue)

**Observation:** Track A = `FAIL`, Track B = `SUPPORTED_IMPROVEMENT`.

**Primary explanation — scope + method + realized effect size (not “Track B overturns Track A”):**

1. **Scope / treatment difference (dominant):** Track A evaluates `VNEXT-ADAPT` under VNEXT locks. Track B evaluates `PHASE1-CORE` under Phase-1 detector lock (`evidence_phase1.0`, fixed τ). Different defense stacks → different estimands. Results are not interchangeable.
2. **Realized effect / power relative to MSID:** Track A δ̂=0.0820 lies below MSID=0.20; Track B δ̂=0.4426 exceeds MSID with CI above MSID’s lower neighborhood. Same N=61 and similar McNemar machinery; the **observed effect sizes differ**, so the MSID gate yields opposite classifications without requiring a protocol bug.
3. **Method overlap, not method identity:** Both use paired McNemar + MSID + U gate, but models (target LLM), packs, and treatments differ. Shared methodology does not imply a single pooled claim.

**Not claimed:** Track B as independent replication of Track A’s estimand.  
**Not claimed:** Pack non-overlap as the reason A failed and B passed (see Limitations §6.2).

---

## 5. Independence of confirmatory packs

### 5.1 Status: INDEPENDENT (VNEXT pack text) — audit closed offline

Episode-level provenance + deterministic near-duplicate audit: [`PHASE1_INDEPENDENCE_AUDIT.md`](PHASE1_INDEPENDENCE_AUDIT.md) (metrics: `docs/paper/dual_track/artifacts/phase1_independence_audit_metrics.json`). **API=0.**

| Check vs `vnext_confirm_v1` | Result |
|-----------------------------|--------|
| Exact normalized prompt / prompt+context | **0** overlaps |
| Near-dupes (char-5gram Jaccard ≥ 0.25) | **0** |
| Seeds / builders / markers | Distinct (`20260914` / `build_phase1_confirm_v1.py` / `P1C-*` vs `61` / VNEXT builder / `VNC1-MARK-*`) |

**Verdict (scoped):** **INDEPENDENT** of the VNEXT confirmatory pack under those screens. Family *name* overlap is taxonomy only — not shared generator.

**Still open (not blocking VNEXT-pack independence):** (a) episode creation dates **UNKNOWN**; (b) cluster-robust McNemar sensitivity **not run** — see §6.2.

**Holdout kinship (narrowed):** `PHASE1_HOLDOUT_OVERLAP_AUDIT.md` — tuning usage **NOT_USED_IN_TUNING**; similarity = **SHARED_TEMPLATE_FAMILY** (scaffolds reused; exact copies 0; seeds differ). Does **not** reopen VNEXT independence and does **not** reclassify Track B numbers.

**Allowed language:** “separate confirmatory pack; audited with no VNEXT prompt/seed/marker overlap; holdout similarity is shared scaffolds without detector-tuning use.”  
**Disallowed:** “Track B reverses Track A” / unbounded “independent confirmation that VNEXT works.”

---

## 6. Limitations

### 6.1 Track A null — implications

- Official `FAIL` stands. A smaller-than-MSID positive effect (δ̂=0.0820, p=0.0625) is compatible with “no MSID-level improvement” under the locked gate; it is **not** proof of zero effect.
- Missing 95% CI(δ̂) in Track A AUDIT blocks interval-based comparison of precision across tracks (**blocking gap**).
- Track B success does **not** reclassify Track A or support “VNEXT works after all.”

### 6.2 §5.1 independence — VNEXT-pack audit closed; holdout kinship narrowed

**Closed:** VNEXT confirmatory pack text overlap (exact/near) — see §5.1 / `PHASE1_INDEPENDENCE_AUDIT.md`. Does **not** reclassify Track A.

**Holdout (further audit):** `PHASE1_HOLDOUT_OVERLAP_AUDIT.md`

- **Tuning usage:** **NOT_USED_IN_TUNING** in reachable git history (`evidence_phase1.0` authored in `c462945` before holdout path existed; lock hashes that pre-holdout blob; no post-holdout detector/threshold edits).
- **Similarity origin:** **SHARED_TEMPLATE_FAMILY** — confirm builder reuses holdout scaffolds with parameter swaps; exact copies blocked; many-to-one pair inflation. **Bias if over-claimed as fully novel surface:** optimistic generalizability within Phase-1 authored templates — **not** evidence of detector fit-on-holdout contamination.

**Residual:**

- **Clustering / variance:** Cluster-robust or mixed-effects sensitivity still **not** in frozen AUDIT. Magnitude unknown.
- **Creation dates UNKNOWN:** cannot prove chronology vs detector iteration from episode fields alone.
- **Git limit:** uncommitted local drafts are unobservable; documented as limit, not used to invent contamination.

### 6.3 AUDIT dataset generalizability bounds

Bound claims to:

- Frozen packs only (SHAs in §2.4 / §7).
- Stated target/judge models and seeds (§2.2).
- Harmful-action success + utility proxies as defined in runners/AUDIT — not arbitrary jailbreak benchmarks, not production multi-turn agents, not other model families.
- Single confirmatory N=61/61 per track; no multi-lab replication in AUDIT.

### 6.4 Other

- Internal report only; dual-track ≠ submission merge.
- Cost/utility are protocol-defined; external cost models may differ.

---

## 7. Reproducibility block

### 7.1 AUDIT / artifact paths

| Track | AUDIT | Verdict / metrics |
|-------|-------|-------------------|
| A | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` | `.../verdict.json`, `.../comparison.json` |
| B | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md` | `.../verdict.json`, `.../metrics.json` |

### 7.2 Hashes and seeds

| Item | Value |
|------|-------|
| Track A pack SHA-256 | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Track B pack SHA-256 | `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` |
| Track A seed | 42 (`comparison.json` / `manifest.json`) |
| Track B seed | 42 (`metrics.json`) |
| Track B run_id | `phase1_confirm_20260914T213022Z_a2681e92` |
| Track A run dir | `20260914-133147` |

### 7.3 Rerun commands (verification / offline)

```bash
# Pack SHA check
sha256sum datasets/frozen/vnext_confirm_v1/dataset.jsonl
sha256sum datasets/frozen/phase1_confirm_v1/dataset.jsonl

# Offline alignment (no API): compare this report’s frozen numbers to AUDIT
python3 - <<'PY'
import hashlib, re, pathlib
root = pathlib.Path('.')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
a = '523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518'
b = 'c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01'
assert sha(root/'datasets/frozen/vnext_confirm_v1/dataset.jsonl') == a
assert sha(root/'datasets/frozen/phase1_confirm_v1/dataset.jsonl') == b
va = (root/'experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/verdict.json').read_text()
vb = (root/'experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/verdict.json').read_text()
assert '"FAIL"' in va and 'SUPPORTED_IMPROVEMENT' in vb
print('SHA+classification: PASS')
PY
```

Live Phase-1 runner (API; do not retune locks):

```bash
python3 scripts/run_phase1_confirm.py --help
# Full live re-run requires OPENROUTER_API_KEY and approved live lock;
# prefer comparing existing AUDIT/metrics.json rather than re-calling APIs.
```

Prelive / sample-size references: `scripts/run_phase1_prelive_gate.py`, `scripts/phase1_sample_size.py`, `docs/paper/phase1/PHASE1_CONFIRM_PRELIVE_CHECKLIST.md`.

---

## 8. Claims checklist (vs `CLAIMS_DUAL_TRACK.md`)

| Claim class | Wording in this report |
|-------------|------------------------|
| Track A | Official confirmatory **`FAIL`** under VNEXT locks — retained |
| Track B | **`SUPPORTED_IMPROVEMENT`** under Phase-1 locks — retained |
| Cross-track | B does **not** reverse A; separate estimands — retained |
| Certainty | Prefer **supported / consistent with / under locked protocol**; avoid proven / confirms / overturns |
| Independence | VNEXT-pack text: **INDEPENDENT**; holdout: **NOT_USED_IN_TUNING** + **SHARED_TEMPLATE_FAMILY** (`PHASE1_HOLDOUT_OVERLAP_AUDIT.md`) |

Edits this pass: holdout overlap forensics closed for tuning contamination; AUDIT numbers unchanged.

---

## 9. References (paths)

- `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`
- `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md`
- `docs/paper/dual_track/CLAIMS_DUAL_TRACK.md`
- `docs/paper/dual_track/DUAL_TRACK_STATUS.md`
- `docs/paper/phase1/PHASE1_CORE_DESIGN.md`
- `docs/paper/phase1/PHASE1_CONFIRM_PRELIVE_CHECKLIST.md`
- Kass, R. E., & Raftery, A. E. (1995). Bayes factors. *JASA*, 90(430), 773–795.

---

## Changelog (Q1 raise)

| # | Change | Rule |
|---|--------|------|
| 1 | Documented Track B δ̂ 95% CI [0.2757, 0.6096] from AUDIT; flagged Track A δ̂ CI as **BLOCKING GAP** (no fabrication) | STATS |
| 2 | Justified BF₁₀≈28 via Kass & Raftery (“strong”); noted Track A BF≈6 | STATS |
| 3 | Added power/sample-size note (N=61, MSID 0.20, ψ≈0.30, 80% planning); post-hoc realized-effect note | STATS |
| 4 | New §4.3 A-vs-B tension: scope + realized effect/MSID + method; removed from independence narrative | A-vs-B |
| 5 | §5.1 marked unresolved; bias direction/magnitude → §6.2 Limitations (no cluster-robust run this cycle) | §5.1 |
| 6 | Softened certainty language to CLAIMS_DUAL_TRACK phrasing (supported / consistent with / not reverse) | CLAIMS |
| 7 | Limitations cover Track A null implications, §5.1 status, AUDIT generalizability bounds | LIMITATIONS |
| 8 | §7 REPRO: AUDIT paths, SHAs, seeds, offline verify + runner pointers | REPRO |
| 9 | Aligned Track B p→1.49012e-08 and cost→0.14221311475409837 to AUDIT (removed drifted 1.485… / 0.1418…) | FREEZE |
| 10 | AUDIT numbers (δ̂, p, U, b10/b01; BF₁₀ derived from 27/0) left as AUDIT/formula | FREEZE |
| 11 | §5.1 → INDEPENDENT (VNEXT pack text) via `PHASE1_INDEPENDENCE_AUDIT.md`; §6.2 residual holdout/clustering/dates | INDEP |
| 12 | Holdout forensics: NOT_USED_IN_TUNING + SHARED_TEMPLATE_FAMILY (`PHASE1_HOLDOUT_OVERLAP_AUDIT.md`); numbers frozen | HOLDOUT |

**Numbers frozen (must match AUDIT):**  
A: δ̂=0.0820, p=0.0625, U=0.9344, b10/b01=5/0.  
B: δ̂=0.4426, p=1.49012e-08, U=0.9672131147540983, b10/b01=27/0, CI=[0.2757, 0.6096], BF₁₀≈28 from 27/0.
