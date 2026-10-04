"""E6 draft protocol: seed policy and randomized/interleaved run plan (offline; no API).

The plan is generated once, before any API call, from a seed derived from the three frozen hashes; its SHA-256 goes into
the run manifest and the runner executes it strictly in order, sequentially. Unit of randomization: the instance block, which
holds one episode per arm (A0, A0 replicate, B3, PHASE1-CORE). Arm order inside a block is a uniform random permutation; blocks
(and the injection-free control episodes, as one-episode blocks) are then uniformly permuted across the whole run.

Entries are shaped like the harness's schedule rows (`scenario_id` = attack family, `instance_index`, `family` = model alias,
`condition` = harness condition) plus `arm`, `replicate`, `kind`, `position` and a unique `episode_id`. The harness has no
condition named for the replicate or the control, so both map to condition A0 and are distinguished by the episode id.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np

ARMS = ("A0", "A0R", "B3", "CORE")
HARNESS_CONDITION = {"A0": "A0", "A0R": "A0", "B3": "B3", "CORE": "CORE", "NOINJ": "A0"}
NOINJ_FAMILIES = 10
MODEL = "deepseek"


def seed_from_hashes(scenario_set_sha256: str, scoring_schema_sha256: str, analysis_sha: str, tag: str = "E6-v1") -> int:
    digest = hashlib.sha256("|".join([scenario_set_sha256, scoring_schema_sha256, analysis_sha, tag]).encode()).digest()
    return int.from_bytes(digest[:8], "big")


def episode_id(scenario_id: str, instance_index: int, arm: str, model: str = MODEL) -> str:
    """Unique id; for arms A0, B3, CORE it equals the harness's own id so the live runner and the plan agree."""
    base = f"{scenario_id}/i{instance_index}/{model}/{HARNESS_CONDITION[arm]}"
    return base + {"A0R": "/r1", "NOINJ": "/noinj"}.get(arm, "")


def make_plan(scenario_ids: list[str], m: int, seed: int, arms: tuple[str, ...] = ARMS, model: str = MODEL) -> list[dict]:
    rng = np.random.default_rng(seed)

    def entry(f: str, i: int, arm: str, kind: str) -> dict:
        return {"scenario_id": f, "instance_index": i, "family": model, "condition": HARNESS_CONDITION[arm], "arm": arm,
                "replicate": 1 if arm == "A0R" else 0, "kind": kind, "episode_id": episode_id(f, i, arm, model)}

    blocks: list[list[dict]] = []
    for f in scenario_ids:
        for i in range(m):
            order = rng.permutation(len(arms))
            blocks.append([entry(f, i, arms[j], "main") for j in order])
    noinj = rng.choice(len(scenario_ids), size=min(NOINJ_FAMILIES, len(scenario_ids)), replace=False)
    for k in sorted(noinj):
        for i in range(m):
            blocks.append([entry(scenario_ids[k], i, "NOINJ", "noinj")])
    plan = [e for b in (blocks[j] for j in rng.permutation(len(blocks))) for e in b]
    for pos, e in enumerate(plan):
        e["position"] = pos
    return plan


def plan_sha256(plan: list[dict]) -> str:
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
