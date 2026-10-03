## Appendix C Artifacts and data availability
Unless a row says otherwise the artifact is in the repository. Pack hashes are recorded in the freeze records and `hashes.sha256` files; the multi-turn run manifests record commit SHAs, not file hashes. Items that are not in the public tree are marked.

| artifact | content | size | license or origin | hash or pin |
|---|---|---|---|---|
| frozen packs (Tracks A and B) | judge-scored confirmatory packs | 61 + 61 attacks, benign twins | project | SHA-256 in `datasets/frozen/*/hashes.sha256` |
| harness v2 traces | multi-turn tool episodes with the executor log (`episodes.jsonl`, manifests, cost summaries); the per-episode trajectories and HTTP streams are not in the tree | 468 (E2), 168 + 336 (E3) episodes | project | commit SHAs in per-run manifests |
| independent scenario set | seven families authored independently of the detector; the template file is not in the tree of any branch and is retrievable only by commit SHA (`e5135a6`) | 7 families × 24 authored instances; 8 per family run (56 instances, 168 episodes with three models) | project | SHA-256 of the template file (§4.4; `REPRODUCIBILITY.md`) |
| InjecAgent (external) | 62 attacker instructions x 17 contexts | 1,054 base cases | external repository | commit and file hashes in `datasets/external_samples/injecagent_phase2_sample.json` |
| Hard set, human-written | tool-call-verified items from LLMail-Inject | 238 items (68 calibration, 170 test) | MIT (Hugging Face `microsoft/llmail-inject-challenge`) | `datasets/attackset_hard_v1/FREEZE_RECORD.json` |
| Hard set, model-generated | cross-channel items from a non-target generator | 69 items, exploratory unless validated | project | manifest hash in the freeze record; meta-prompt SHA-256 |
| AgentDojo pairs | fixed seeded pairs for health checks and pilot | 60 pairs of 629 valid | external benchmark | `datasets/external_samples/agentdojo_v1_phase2_pairs.json` |
| model panel | registry with pinned prices and settings | 4 open, 1 closed, 2 judges | OpenRouter list | `configs/models_panel_external_v2.yaml` |
| code | public: analysis, figure, ledger and reproduction scripts. Not in the tree of any public branch or tag (present only in unreachable commits fetchable by SHA, `REPRODUCIBILITY.md`): the live harness (`src/adapti_guard/evaluation/harness_v2/`), the E2/E3 run scripts, the calibration and InjecAgent run scripts, the external-test analysis scripts and the harness test | | project | commit in each manifest (runner commits are retrievable by SHA, not reachable from any branch or tag) |
| reproduction | `scripts/reproduce_negative_result.sh` regenerates the E1 to E4 numbers, ledger and figures offline; the §6.6 and §6.7 numbers are read from committed records and are not regenerated | | | `NUMBERS_LEDGER.md` with a consistency test |

Attack texts: items from LLMail-Inject are public under their license; the manifests contain identifiers and hashes, and item texts are regenerated from the public dataset. Of the Hard set only `datasets/attackset_hard_v1/FREEZE_RECORD.json` is in the tree; the manifests it hashes (`MANIFEST.json`, `XCHANNEL_MANIFEST_full.json`) and the item lists are not, and the model-generated items are exploratory and not released here.
