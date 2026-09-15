# layer_a_v3

Frozen mixed prompt-injection eval for Layer A (v3).

- Canonical full pack: `dataset.jsonl` (identical to `test.jsonl`)
- Splits: `train.jsonl`, `dev.jsonl`, `test_split.jsonl` (final eval)
- Card: `DATASET_CARD.md`
- Manifest / hashes: `manifest.json`, `hashes.sha256`

Layer A v2 remains historical under `datasets/frozen/layer_a_v2/`.

Regenerate with `python3 scripts/build_layer_a_v3_pack.py` (overwrites this directory).
