# Reporting standards checklist (status as of 2026-10-01)

Status: DONE, PARTIAL, MISSING, OWNER (needs the owner or a human).

## Structure (IMRaD for a security or ML-evaluation venue)
| item | status | note |
|---|---|---|
| Abstract, introduction with contributions | DONE | contributions listed; abstract mentions the sixth check |
| Related work with positioning against AgentDojo, InjecAgent, CaMeL, Progent | PARTIAL | numbers from the literature to be re-checked against PDFs (OWNER) |
| Threat model | DONE | section 3 |
| Method, measurement rules M1 to M6 | DONE | section 4 |
| Experiments with exact configurations | DONE | section 5 |
| Results with intervals and effect sizes | PARTIAL | section 6.6 is cluster-aware; earlier sections use paired bootstrap and exact tests |
| Limitations | DONE | section 8 |
| Claims table (may / may not claim) | DONE | section 9 |
| Ethics, dual use, AI-assistance disclosure | PARTIAL | disclosure text needs owner approval (OWNER) |

## Reproducibility (ML reproducibility checklist items)
| item | status | note |
|---|---|---|
| One-command offline reproduction | DONE | `scripts/reproduce_negative_result.sh` |
| Every number traceable to an artifact | DONE | `NUMBERS_LEDGER.md` plus test |
| Data hashes and external-data commit pinned | DONE | run manifests |
| Seeds and sampling rule stated | DONE | seed 20260930 (sampling), 7 (bootstrap) |
| Compute and cost reported | DONE | per-run spend in results docs |
| Raw episodes released | DONE | committed under `experiments/` |
| Environment pinned | PARTIAL | `requirements.txt` and CI on Python 3.12; AgentDojo runs in a separate venv |
| Released code license and citation | PARTIAL | `LICENSE` and `CITATION.cff` exist; CITATION still points at the workshop paper (OWNER) |

| Registered-report structure (design and analysis plan fixed before the confirmatory run; results pending) | DONE | sections 5.6 and 6.6; exploratory pilot in Appendix A |

## Statistical reporting
| item | status | note |
|---|---|---|
| Pre-registered protocol before confirmatory runs | PARTIAL | draft and registry text exist; not frozen and not yet submitted to OSF or AsPredicted (OWNER) |
| Multiplicity control | PARTIAL | Holm planned in the protocol, not yet applied to the 6.6 panel |
| Clustering and non-independence handled | DONE for InjecAgent | cluster bootstrap over attacker instruction |
| Noise floor and validity controls per model | DONE for InjecAgent | A0 replicate, NOINJ |
| Power analysis | DONE | in the protocol draft |
| Negative and null results reported | DONE | including the stopped gemma run and the discarded failed mistral attempt |

## Data quality
| item | status | note |
|---|---|---|
| Independent external benchmark | DONE | InjecAgent; AgentDojo health-checked, not yet run |
| Dataset audit (size, duplication, diversity) | DONE | `DATASET_AUDIT_20260930.md` |
| Human validation of labels, second annotator | PARTIAL | human-written items validated by provenance and tool-call ground truth; generated items and mechanism labels need two raters (OWNER); human subset frozen with a hash |
| Harder, adaptive attack set | MISSING | OWNER (needs a human reviewer) |
| Stateful multi-step environment | PARTIAL | AgentDojo feasibility done |

## Model panel
| item | status | note |
|---|---|---|
| Panel: 4 open targets, 1 closed target, 2 judges | PARTIAL | settled 2026-10-01 (protocol section 3), registered in `configs/models_panel_external_v2.yaml` with a validating loader and test; deviation 1 from the contract panel; floor calibration pending |
| Frontier closed model | MISSING | budget decision (OWNER) |
