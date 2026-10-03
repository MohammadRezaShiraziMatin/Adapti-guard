## Appendix C Artifacts and data availability
Paths are in the repository unless stated otherwise; the multi-turn harness, the runner, the scenario template files and the template generator are withheld (staged release, §10). Pack hashes are recorded in the freeze records; the harness run manifests record code and docs commit SHAs only, not template hashes.

| artifact | content | size | license or origin | hash or pin |
|---|---|---|---|---|
| frozen packs (Tracks A and B) | judge-scored confirmatory packs | 61 + 61 attacks, benign twins | project | SHA-256 in `datasets/frozen/*/hashes.sha256` |
| harness v2 traces | committed `episodes.jsonl` of the multi-turn runs, with the executor log and the attack texts of the executed episodes | 972 episodes in three runs | project | per-run manifests (code and docs SHAs only) |
| independent scenario set | seven families authored independently of the detector; the template file is withheld, its attack text is public in the E3 `episodes.jsonl` | 168 instances | project | SHA-256 of the template file (§4.4), attested only at an unpublished commit (§8.5) |
| InjecAgent (external) | 62 attacker instructions x 17 contexts | 1,054 base cases | external repository | commit and file hashes in `datasets/external_samples/injecagent_phase2_sample.json` |
| Hard set, human-written | tool-call-verified items from LLMail-Inject | 238 items (68 calibration, 170 test) | MIT (Hugging Face `microsoft/llmail-inject-challenge`) | `datasets/attackset_hard_v1/FREEZE_RECORD.json` |
| Hard set, model-generated | cross-channel items from a non-target generator | 69 items, exploratory unless validated | project | manifest hash in the freeze record; meta-prompt SHA-256 |
| AgentDojo pairs | fixed seeded pairs for health checks and pilot | 60 pairs of 629 valid | external benchmark | `datasets/external_samples/agentdojo_v1_phase2_pairs.json` |
| model panel | registry with pinned prices and settings | 4 open, 1 closed, 2 judges | OpenRouter list | `configs/models_panel_external_v2.yaml` |
| code | analysis, figure, ledger and assembly scripts and the offline reproduction script (the harness, the runner and the scenario generator are not public) | | project | commits in the manifests are unpublished historical states (§8.5) |
| reproduction | `scripts/reproduce_negative_result.sh` regenerates the numbers and figures of E1 to E3, MT1 and the M6 channel check, the manuscript and the ledger offline; §6.6, §6.7 and Appendix A use committed derived artifacts | | | `NUMBERS_LEDGER.md` with a consistency test |

Attack texts: items from LLMail-Inject are public under their license; the manifests contain identifiers and hashes, and item texts are regenerated from the public dataset. Model-generated items are released after human validation (staged release, §10).
