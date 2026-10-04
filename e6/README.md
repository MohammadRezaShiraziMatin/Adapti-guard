# E6 inputs

Flow: independent author content (`authoring_schema_v1.json`) -> deterministic renderer (`scripts/e6_render.py`) -> harness-native rendered scenario file (`e6-rendered-1`) -> frozen harness -> runner. The author never writes harness-internal JSON or the marker.
`harness_constants.json` records the hashes of the fixed system prompt and four tools. `INPUTS_STATUS.json` records that no independent author or pack exists and that the H4 neutral-twin rule is an open owner decision.
`scripts/e6_manifest.py` lists what is still missing before the protocol can be frozen. Synthetic fixtures are for tests only.
