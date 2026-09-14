# vnext_confirm_v1

Frozen VNEXT confirmation pack (61 attack + 61 benign).

- Canonical: `dataset.jsonl` (identical to `confirmation.jsonl`)
- Card: `DATASET_CARD.md`
- Manifest / hashes: `manifest.json`, `hashes.sha256`

Layer A v2/v3 remain historical and must not be modified.

Regenerate with `python3 scripts/build_vnext_confirm_v1_pack.py` (overwrites this directory).

**Live eval:** do not score this pack until a human approves and the SHA-256 in
`docs/experiments/VNEXT_PROTOCOL_ADDENDUM.md` §4 matches `hashes.sha256`.
