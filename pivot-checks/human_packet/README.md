# human_packet

Blind labelling packet (40 episodes). See INSTRUCTIONS.md (for the labeller) and PROCEDURE_HUMAN_PACKET.md (locked procedure; hash in PROCEDURE_HUMAN_PACKET.sha256). The answer key is held outside the repository; only KEY_SEPARATE.sha256 is committed.

## Limitation (added 2026-10-17)

The answer key is **reconstructible from the public repository**: `make_packet.py`, its seed, and the committed episode files are enough to regenerate the episode-to-label mapping. Blinding therefore holds only if the labeller does not use this repository (code, seed or episode files) before submitting labels. This should be stated to the labeller and reported as a limitation.
