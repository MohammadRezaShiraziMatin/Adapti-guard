"""E6 draft protocol: seed policy and randomized/interleaved run plan (offline; no API).

The plan is generated once, before any API call, from a seed derived from the three frozen hashes; its SHA-256 goes into
the run manifest and the runner executes it strictly in order. Unit of randomization: the instance block, which holds one
episode per condition (A0, A0 replicate, B3, PHASE1-CORE). Condition order inside a block is a uniform random permutation;
blocks (and the injection-free control episodes, as one-episode blocks) are then uniformly permuted across the whole run.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np

CONDITIONS = ("A0", "A0_REPLICATE", "B3", "CORE")
NOINJ_FAMILIES = 10


def seed_from_hashes(scenario_set_sha256: str, scoring_schema_sha256: str, analysis_sha: str, tag: str = "E6-v1") -> int:
    digest = hashlib.sha256("|".join([scenario_set_sha256, scoring_schema_sha256, analysis_sha, tag]).encode()).digest()
    return int.from_bytes(digest[:8], "big")


def make_plan(families: list[str], m: int, seed: int, conditions: tuple[str, ...] = CONDITIONS) -> list[dict]:
    rng = np.random.default_rng(seed)
    blocks: list[list[dict]] = []
    for f in families:
        for i in range(m):
            order = rng.permutation(len(conditions))
            blocks.append([{"family": f, "instance": i, "condition": conditions[j], "kind": "main"} for j in order])
    noinj = rng.choice(len(families), size=min(NOINJ_FAMILIES, len(families)), replace=False)
    for k in sorted(noinj):
        for i in range(m):
            blocks.append([{"family": families[k], "instance": i, "condition": "NOINJ", "kind": "noinj"}])
    plan = [e for b in (blocks[j] for j in rng.permutation(len(blocks))) for e in b]
    for pos, e in enumerate(plan):
        e["position"] = pos
    return plan


def plan_sha256(plan: list[dict]) -> str:
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
