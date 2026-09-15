# DATASET CARD — `p1_mechanism_v1.0-candidate`

**Status:** CANDIDATE (offline). **Not** under `datasets/frozen/`. **Not live-evaluated.**

| Field | Value |
| --- | --- |
| Rows | 96 (44 attack / 52 benign) |
| Hard negatives | 8 |
| SHA-256 | `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235` |
| Seed | 20260915 |
| Taxonomy | P1 mechanism A1–F4; **C4 = 0 rows (out of scope)** |
| Twins | 1:1 attack↔benign for 42 pairs |
| Runtime shape | confirm-pack compatible: prompt/context/tools/tool_call/success_condition |

## Estimands

Supported **after** freeze-before-live + gated live eval only:

- harmful-action rates by mechanism family
- utility / FPR via benign twins and hard negatives

**Not** supported: live multi-turn ASR; adaptive attacker ASR; pooling with `common_attack_stream`.

## Provenance

Authored synthetic templates (`generation_method=template_authored_no_llm_no_detector_fit`).
Contamination-screened for exact normalized prompt/context collision against Phase-1/VNEXT/Layer A frozen packs.

## Non-claims

Publishing this candidate does not claim improved security, ASR, utility, or detection.
