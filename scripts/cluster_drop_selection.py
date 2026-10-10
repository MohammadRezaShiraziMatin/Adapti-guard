"""Cluster-drop rule for attack source S-A (protocol §3, DRAFT, NOT FROZEN). Offline, pure Python.

To reach n = 150 per target, whole attacker-instruction clusters are dropped with a fixed seed: 12 of 62 clusters (36 cases),
keeping 50 whole clusters (150 cases). For gpt-5.6-sol H1 (n = 72), 24 whole clusters are kept with the same seeded rule.
The same retained case set is used for every target and arm.

Cluster key. The InjecAgent loader is not in this tree, so the attacker instruction itself cannot be read here. The
committed episode records carry each case's attacker tool list, and the 186 cases split into exactly 62 groups of 3 by that
list. The key used here is that list (sorted, joined by "|"). It is a proxy for the attacker instruction and must be checked
against the instruction ids when the loader is available (protocol §3).

Random selection uses random.Random(seed).sample on a sorted list, which is stable for a fixed seed.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261001  # the protocol's existing sample seed (§3); the author has not set a separate seed for this rule
KEEP_N150 = 50   # 50 clusters x 3 contexts = 150 cases per target
KEEP_GPT72 = 24  # 24 clusters x 3 contexts = 72 cases
SAMPLE = ROOT / "datasets/external_samples/injecagent_phase2_sample.json"
EPISODES = [
    ROOT / "experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json",
    ROOT / "experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json",
]
RECORD = ROOT / "docs/protocols/injecagent_S-A_retained_20261001.json"


def _is_int(x: object) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def clusters_from_episodes(episodes: Sequence[Mapping]) -> dict[str, str]:
    """case_id -> cluster key. Every episode of a case (any arm, any target) must give the same attacker tool list."""
    key_of: dict[str, str] = {}
    for e in episodes:
        cid = e["case_id"]
        key = "|".join(sorted(e["attacker_tools"]))
        if not key:
            raise ValueError(f"case {cid!r} has no attacker tools")
        if key_of.setdefault(cid, key) != key:
            raise ValueError(f"case {cid!r} has different attacker tools in different episodes")
    return key_of


def select_whole_clusters(cluster_keys: Sequence[str], *, keep: int, seed: int) -> list[str]:
    """Keep `keep` whole clusters chosen with random.Random(seed). Returns the kept keys, sorted."""
    if any(not isinstance(k, str) or not k for k in cluster_keys):
        raise ValueError("cluster keys must be non-empty strings")
    if len(set(cluster_keys)) != len(cluster_keys):
        raise ValueError("cluster keys must be unique")
    if not _is_int(keep) or not 1 <= keep <= len(cluster_keys):
        raise ValueError(f"keep must be an integer from 1 to {len(cluster_keys)}")
    if not _is_int(seed):
        raise ValueError("seed must be an integer, not a bool")
    rng = random.Random(seed)
    return sorted(rng.sample(sorted(cluster_keys), keep))


def retained_case_ids(case_to_cluster: Mapping[str, str], selected: Sequence[str]) -> list[str]:
    """Every case whose cluster was kept, sorted. Whole clusters only, by construction."""
    chosen = set(selected)
    return sorted(cid for cid, key in case_to_cluster.items() if key in chosen)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build_record() -> dict:
    """The retained-set record, built only from committed files. Refuses if the sample and the episodes disagree."""
    sample = json.loads(SAMPLE.read_text())
    sample_ids = sorted(sample["case_ids"])
    if _sha256_text("\n".join(sample_ids)) != sample["ids_sha256"]:
        raise ValueError("sample case_ids do not match ids_sha256 in the sample file")

    per_target = []
    for path in EPISODES:
        episodes = json.loads(path.read_text())["episodes"]
        a0_ids = sorted({e["case_id"] for e in episodes if e["arm"] == "A0"})
        if a0_ids != sample_ids:
            raise ValueError(f"{path.name}: A0 case ids differ from the sample")
        per_target.append(clusters_from_episodes(episodes))
    if per_target[0] != per_target[1]:
        raise ValueError("cluster keys differ between targets")
    case_to_cluster = per_target[0]

    clusters = sorted(set(case_to_cluster.values()))
    sizes = Counter(case_to_cluster.values())
    if len(clusters) != 62 or set(sizes.values()) != {3}:
        raise ValueError(f"expected 62 clusters of 3 cases, got {len(clusters)} clusters, sizes {sorted(set(sizes.values()))}")

    kept_150 = select_whole_clusters(clusters, keep=KEEP_N150, seed=SEED)
    kept_72 = select_whole_clusters(clusters, keep=KEEP_GPT72, seed=SEED)
    dropped_150 = sorted(set(clusters) - set(kept_150))
    retained_150 = retained_case_ids(case_to_cluster, kept_150)
    retained_72 = retained_case_ids(case_to_cluster, kept_72)
    assert len(retained_150) == 150 and len(retained_72) == 72

    return {
        "status": "DRAFT, NOT FROZEN",
        "rule": ("S-A cluster-drop: whole attacker-instruction clusters kept with random.Random(seed).sample on the sorted "
                 "cluster keys. n = 150 per target keeps 50 of 62 clusters (12 dropped, 36 cases). gpt-5.6-sol H1 keeps 24 "
                 "clusters (72 cases). Same retained set for every target and arm."),
        "seed": SEED,
        "cluster_key": "attacker tool list of the case, sorted and joined by '|' (proxy for attacker instruction, protocol §3)",
        "sample_file": "datasets/external_samples/injecagent_phase2_sample.json",
        "sample_ids_sha256": sample["ids_sha256"],
        "source_episodes": [str(p.relative_to(ROOT)) for p in EPISODES],
        "n_clusters": len(clusters),
        "n_cases": len(case_to_cluster),
        "dropped_clusters_n150": dropped_150,
        "kept_clusters_n150": kept_150,
        "retained_case_ids_n150": retained_150,
        "kept_clusters_gpt_n72": kept_72,
        "retained_case_ids_gpt_n72": retained_72,
    }


def record_text(record: dict) -> str:
    return json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    text = record_text(build_record())
    RECORD.write_text(text)
    print(f"wrote {RECORD.relative_to(ROOT)} sha256={_sha256_text(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
