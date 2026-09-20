# AdaptiGuard

AdaptiGuard is a hash-locked evaluation testbed for **prompt-injection and related LLM-agent attacks**, comparing fixed and adaptive discrete intervention policies (L0–L3) under shared security, utility, and cost metrics. Two confirmatory tracks are frozen: Track A (VNEXT) is a **negative result**; Track B (Phase-1 CORE) is a **scoped SUPPORTED_IMPROVEMENT** on a different pack — it does **not** reverse Track A.

**New contributors / reviewers:** start at [`docs/START_HERE.md`](docs/START_HERE.md).

[![Tests](https://github.com/MohammadRezaShiraziMatin/adapti-guard/actions/workflows/tests.yml/badge.svg)](https://github.com/MohammadRezaShiraziMatin/adapti-guard/actions/workflows/tests.yml)

## Key findings (frozen AUDIT only)

| Track | Pack / SHA-256 | Primary result | δ̂ / effect | p | Utility | b10/b01 | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| **A — VNEXT** | `vnext_confirm_v1.0` / `523c8818…721518` | B0 vs VNEXT-ADAPT, n=61+61 | δ̂ = **0.0820** (MSID 0.20 not met) | **0.0625** | U = **0.9344** | **5/0** | **FAIL** |
| **B — Phase-1** | `phase1_confirm_v1` / `c789811a…536d01` | B0 vs PHASE1-CORE, n=61+61 | δ̂ = **0.4426**, 95% CI **[0.2757, 0.6096]** | **1.49012e-08** | U = **0.9672** | **27/0** | **SUPPORTED_IMPROVEMENT** |

Sources (do not rewrite):

- Track A: [`experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`](experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md)
- Track B: [`experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md`](experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md)

Track A has **no** 95% CI for δ̂ in AUDIT (documented BLOCKING GAP — do not fabricate). Track B does **not** reverse Track A.

## Reproduce

```bash
git clone https://github.com/MohammadRezaShiraziMatin/adapti-guard.git
cd adapti-guard
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"            # pyproject.toml + requirements-core.txt + pytest
pytest -q                          # offline suite; no live LLM required
```

Offline scientific audits (API=0):

```bash
python scripts/audit_phase1_confirm_independence.py
python scripts/audit_phase1_holdout_overlap_origin.py
python scripts/classify_phase1_holdout_pairs_full59.py
```

Workshop manuscript fact check:

```bash
python docs/paper/workshop_vnext_fail/verify_manuscript_facts.py
```

Frozen packs and live AUDIT folders are **read-only**. Do not re-run confirmation evals unless a human explicitly gates live API use.

Optional tooling (not the primary harness): `scripts/garak_adapter.py` (thin Garak Generator adapter) and `inspect-test/` (Inspect AI sample). **Not integrated:** LangChain / LangGraph, PyRIT, promptfoo.

Never commit `.env` or API keys. Copy `.env.example` only if you intentionally run live providers.

## Limitations

- Track A FAIL is immutable; do not mix VNEXT ASR with Phase-1 harmful-action rates in one unlabeled claim.
- Track B independence vs VNEXT and holdout-scaffold overlap are documented; see the scientific report and completeness statement.
- Full detail: [`docs/paper/dual_track/PHASE1_SCIENTIFIC_REPORT.md`](docs/paper/dual_track/PHASE1_SCIENTIFIC_REPORT.md) and [`docs/paper/dual_track/PHASE1_COMPLETENESS_STATEMENT.md`](docs/paper/dual_track/PHASE1_COMPLETENESS_STATEMENT.md).
- Standing agent rules: [`docs/experiments/MASTER_PROMPT.md`](docs/experiments/MASTER_PROMPT.md).

## Repository layout

| Path | Role |
|------|------|
| `src/adapti_guard/` | Installable package (`import adapti_guard`) |
| `configs/` | YAML/JSON configs |
| `scripts/` | CLI entrypoints |
| `tests/` | Pytest |
| `docs/paper/dual_track/` | Track A vs Track B status and claims |
| `docs/paper/workshop_vnext_fail/` | Track A negative-result packet |
| `docs/archive/` | Superseded root audits and historical notes |
| `datasets/frozen/` | Frozen packs — **do not edit** |
| `experiments/real_llm_eval/` | Live AUDIT / metrics — **do not edit** |

## Citation

See [`CITATION.cff`](CITATION.cff). Do not cite this repository as a confirmed, SOTA, or production prompt-injection defense.

```bibtex
@software{adapti_guard,
  author = {Shirazi Matin, Seyed Mohammadreza},
  title  = {AdaptiGuard: A Hash-Locked Evaluation Testbed for Runtime LLM-Agent Intervention Policies},
  year   = {2026},
  url    = {https://github.com/MohammadRezaShiraziMatin/adapti-guard/},
  note   = {VNEXT confirmation STATUS=FAIL; Phase-1 confirm is a scoped result on a different pack}
}
```
