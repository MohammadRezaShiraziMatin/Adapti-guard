# AdaptiGuard

AdaptiGuard is an empirical case study showing how **measurement decisions in the evaluation of LLM-agent defenses can change conclusions on the same underlying traces**. The study re-scores and re-analyzes frozen runs of tool-using LLM agents under prompt-injection attacks, and examines how the choice of success endpoint, labeling rule and reporting unit changes what a defense evaluation appears to show.

This repository does **not** present a state-of-the-art defense, a production-ready security defense, or a general-purpose benchmark for all agents.

[![Tests](https://github.com/MohammadRezaShiraziMatin/adapti-guard/actions/workflows/tests.yml/badge.svg)](https://github.com/MohammadRezaShiraziMatin/adapti-guard/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/github/license/MohammadRezaShiraziMatin/adapti-guard)](https://github.com/MohammadRezaShiraziMatin/adapti-guard/blob/main/LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://github.com/MohammadRezaShiraziMatin/adapti-guard/blob/main/pyproject.toml)
[![Reproducible: Offline](https://img.shields.io/badge/reproducibility-offline-green.svg)](https://github.com/MohammadRezaShiraziMatin/adapti-guard/blob/main/REPRODUCIBILITY.md)

## Research focus

The study concentrates on measurement decisions in the evaluation of runtime defenses, treated as candidate checks rather than a validated framework:

- **Success endpoint**: whether an attack counts as successful when the model proposes a call or when the executor runs it.
- **Blocked-payload labeling**: how payloads stopped by a defense are labeled.
- **Scenario validity**: whether a scenario contains an attacker-controlled effect at all.
- **Authorship independence**: who wrote the attack scenarios relative to the defense under test.
- **Per-model reporting and noise floor**: whether results are reported per model and compared against run-to-run noise.
- **Defense-channel verification**: whether the defense is actually applied to the untrusted channel.

## Main research package

The publication package lives in [`docs/paper/negative_result/`](docs/paper/negative_result/):

- Manuscript: [`MANUSCRIPT_DRAFT_v1.md`](docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md) (assembled from the source sections in the same directory; do not edit by hand)
- Figures 1 to 3 (csv, png, svg): [`figures/`](docs/paper/negative_result/figures/)
- References: [`RELATED_WORK.md`](docs/paper/negative_result/RELATED_WORK.md) and [`references_extension.bib`](docs/paper/q1_findings/references_extension.bib)
- Number ledger: [`NUMBERS_LEDGER.md`](docs/paper/negative_result/NUMBERS_LEDGER.md)
- Appendices: [`APPENDIX_A_EXPLORATORY_PILOT.md`](docs/paper/negative_result/APPENDIX_A_EXPLORATORY_PILOT.md), [`APPENDIX_B_CHECKLIST.md`](docs/paper/negative_result/APPENDIX_B_CHECKLIST.md), [`APPENDIX_C_ARTIFACTS.md`](docs/paper/negative_result/APPENDIX_C_ARTIFACTS.md), [`APPENDIX_D_E3_DETAILED_RESULTS.md`](docs/paper/negative_result/APPENDIX_D_E3_DETAILED_RESULTS.md)
- Package index: [`README.md`](docs/paper/negative_result/README.md)

The preregistration text in this package is a local draft; the external test was not externally registered.

## Reproduce

```bash
git clone https://github.com/MohammadRezaShiraziMatin/adapti-guard.git
cd adapti-guard
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"            # requires Python >= 3.12
pytest -q                          # offline suite; no live LLM required
```

Offline reproduction of the manuscript numbers, figures, ledger and consistency check (no network, no key):

```bash
STRICT=1 bash scripts/reproduce_negative_result.sh
```

This regenerates, from committed traces, the numbers and figures of E1 to E3, the MT1 held-out application and the M6 channel check, then the manuscript and the number ledger, and with `STRICT=1` fails if a regenerated file differs from the committed copy. Sections 6.6 and 6.7 and Appendix A use committed derived artifacts; the scripts that produced them, the multi-turn harness and runner, and the attack-template files and generator are not in this repository (staged release). The commits cited in the E2/E3 run manifests are unpublished historical states, so the chronology of those runs is not publicly verifiable (see `REPRODUCIBILITY.md`).

Never commit `.env` or API keys. Copy `.env.example` only if you intentionally run live providers.

## Repository layout

| Path | Role |
|------|------|
| `src/adapti_guard/` | Installable package (`import adapti_guard`) |
| `configs/` | YAML/JSON configs |
| `scripts/` | CLI entrypoints, including manuscript assembly and figure scripts |
| `tests/` | Pytest, including the number-ledger check |
| `docs/paper/negative_result/` | Manuscript package (main research package) |
| `datasets/` | Frozen packs and pinned external samples; frozen packs are read-only |
| `experiments/` | Run artifacts, including the external InjecAgent runs cited by the manuscript; read-only |

## Research status

- Manuscript package: verified
- Manuscript assembly: verified
- Number-ledger validation: verified
- CI: passing
- Historical and live evaluation artifacts: frozen and read-only where applicable
- Offline reproduction of E1 to E3, MT1 and M6: `scripts/reproduce_negative_result.sh` (`STRICT=1`)
- Full historical reproduction (harness, runner, §6.6 and §6.7 analysis scripts, run chronology): not possible from this repository

## Limitations

- The study examines measurement validity; it makes no general claim that any defense is better than another.
- Some historical artifacts, the harness and runner, the attack-template files and some analysis scripts remain outside this publication transfer.
- Frozen evidence must not be re-run or modified without an explicit human gate.

## Historical material

Earlier dual-track work (a confirmatory negative result and a separate scoped result on a different pack) and its workshop packet are kept for provenance and are not the main result of this study: [`docs/paper/dual_track/`](docs/paper/dual_track/), [`docs/paper/workshop_vnext_fail/`](docs/paper/workshop_vnext_fail/), [`docs/paper/q1_findings/`](docs/paper/q1_findings/), [`docs/archive/`](docs/archive/). Reviewer entry point for the repository as a whole: [`docs/START_HERE.md`](docs/START_HERE.md).

## Citation

See [`CITATION.cff`](CITATION.cff). Do not cite this repository as a confirmed, state-of-the-art or production defense.

```bibtex
@software{adapti_guard,
  author = {Shirazi Matin, Seyed Mohammadreza},
  title  = {AdaptiGuard: An Empirical Case Study of Measurement Validity in the Evaluation of LLM-Agent Defenses},
  year   = {2026},
  url    = {https://github.com/MohammadRezaShiraziMatin/adapti-guard/},
  note   = {Empirical case study of measurement validity in the evaluation of LLM-agent defenses; manuscript draft in docs/paper/negative_result/}
}
```
