## Appendix C Artifacts and data availability
All paths are in the repository. Hashes are recorded in the run manifests and in the freeze records.

| artifact | content | size | license or origin | hash or pin |
|---|---|---|---|---|
| frozen packs (Tracks A and B) | judge-scored confirmatory packs | 61 + 61 attacks, benign twins | project | SHA-256 in `datasets/frozen/*/hashes.sha256` |
| harness v2 traces | multi-turn tool episodes with the executor log | several hundred episodes | project | per-run manifests |
| independent scenario set | seven families authored independently of the detector | 168 instances | project | SHA-256 of the template file (§4.4) |
| InjecAgent (external) | 62 attacker instructions x 17 contexts | 1,054 base cases | external repository | commit and file hashes in `datasets/external_samples/injecagent_phase2_sample.json` |
| Hard set, human-written | tool-call-verified items from LLMail-Inject | 238 items (68 calibration, 170 test) | MIT (Hugging Face `microsoft/llmail-inject-challenge`) | `datasets/attackset_hard_v1/FREEZE_RECORD.json` |
| Hard set, model-generated | cross-channel items from a non-target generator | 69 items, exploratory unless validated | project | manifest hash in the freeze record; meta-prompt SHA-256 |
| AgentDojo pairs | fixed seeded pairs for health checks and pilot | 60 pairs of 629 valid | external benchmark | `datasets/external_samples/agentdojo_v1_phase2_pairs.json` |
| model panel | registry with pinned prices and settings | 4 open, 1 closed, 2 judges | OpenRouter list | `configs/models_panel_external_v2.yaml` |
| code | harness, runners, analysis, QC and reproduction script | | project | commit in each manifest |
| reproduction | `scripts/reproduce_negative_result.sh` regenerates the manuscript numbers, ledger and figures offline | | | `NUMBERS_LEDGER.md` with a consistency test |

Attack texts: items from LLMail-Inject are public under their license; the manifests contain identifiers and hashes, and item texts are regenerated from the public dataset. Model-generated items are released after human validation (staged release, §10).
