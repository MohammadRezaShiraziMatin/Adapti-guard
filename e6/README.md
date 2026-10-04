# E6 inputs

`pack_schema_v1.json` defines the fresh scenario pack (schema `e6-pack-1`); `INPUTS_STATUS.json` records that no independent author and no fresh pack exist.
`scripts/e6_pack.py` validates a pack and computes its hash; `scripts/e6_freeze_check.py` lists what is still missing before the protocol can be frozen.
The pack must come from a real independent author (see the protocol, section 6). Synthetic fixtures are for tests only and never satisfy the checklist.
