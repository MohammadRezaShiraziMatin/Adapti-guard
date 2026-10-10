"""Cluster-drop rule for attack source S-A (protocol §3, DRAFT, NOT FROZEN). Offline, pure Python.

To reach n = 150 per target, whole attacker-instruction clusters are dropped with a fixed seed: 12 of 62 clusters (36 cases),
keeping 50 whole clusters (150 cases). For gpt-5.6-sol H1 (n = 72), 24 whole clusters are kept with the same seeded rule.
The same retained case set is used for every target and arm.

Cluster key. The attacker instruction is the sha256 of its text in the public InjecAgent release (commit f19c9f2), taken from
docs/protocols/injecagent_S-A_release_map_20261001.json, which scripts/verify_injecagent_release.py writes from a checkout
whose file hashes match the registered pins. The earlier proxy (the attacker tool list) gave the same partition; the build
records whether the retained set changes when the key changes.

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
RELEASE_MAP = ROOT / "docs/protocols/injecagent_S-A_release_map_20261001.json"
EPISODES = [
    ROOT / "experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json",
    ROOT / "experiments/external/injecagent_registered_20261001/qwen__qwen3.8-flash.json",
]
RECORD = ROOT / "docs/protocols/injecagent_S-A_retained_20261001.json"
PILOT = ROOT / "docs/protocols/injecagent_S-A_pilot_20261001.json"
PILOT_CLUSTERS = 10  # 10 whole clusters = 30 cases, drawn from the 12 clusters dropped for n = 150


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


def clusters_from_release_map(rows: Sequence[Mapping]) -> dict[str, str]:
    """case_id -> attacker-instruction identifier (sha256 of the release text), from the committed release map."""
    key_of = {}
    for r in rows:
        key_of[r["case_id"]] = r["attacker_instruction_sha256"]
    return key_of


def retained_case_ids(case_to_cluster: Mapping[str, str], selected: Sequence[str]) -> list[str]:
    """Every case whose cluster was kept, sorted. Whole clusters only, by construction."""
    chosen = set(selected)
    return sorted(cid for cid, key in case_to_cluster.items() if key in chosen)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build_record() -> dict:
    """The retained-set record, built only from committed files. Refuses if the sample, the release map and the
    registered episodes disagree."""
    sample = json.loads(SAMPLE.read_text())
    sample_ids = sorted(sample["case_ids"])
    if _sha256_text("\n".join(sample_ids)) != sample["ids_sha256"]:
        raise ValueError("sample case_ids do not match ids_sha256 in the sample file")

    release_map = json.loads(RELEASE_MAP.read_text())
    if any(not pin["match"] for pin in release_map["pins"]):
        raise ValueError("release map records a pin mismatch")
    rows = release_map["cases"]
    if sorted(r["case_id"] for r in rows) != sample_ids:
        raise ValueError("release map case ids differ from the sample")

    episodes = json.loads(EPISODES[0].read_text())["episodes"]
    by_case = {r["case_id"]: r for r in rows}
    for e in episodes:
        if e["arm"] != "A0":
            continue
        r = by_case.get(e["case_id"])
        if r is None or (r["user_tool"], r["attacker_tools"]) != (e["user_tool"], sorted(e["attacker_tools"])):
            raise ValueError(f"{e['case_id']}: release map disagrees with the registered episode")

    case_to_cluster = clusters_from_release_map(rows)
    clusters = sorted(set(case_to_cluster.values()))
    sizes = Counter(case_to_cluster.values())
    if len(clusters) != 62 or set(sizes.values()) != {3}:
        raise ValueError(f"expected 62 clusters of 3 cases, got {len(clusters)} clusters, sizes {sorted(set(sizes.values()))}")

    # Sanity: the instruction-text partition equals the earlier tool-list partition.
    tool_key = {r["case_id"]: "|".join(r["attacker_tools"]) for r in rows}
    def groups(key_of):
        g = {}
        for cid, k in key_of.items():
            g.setdefault(k, set()).add(cid)
        return {frozenset(v) for v in g.values()}
    partitions_equal = groups(case_to_cluster) == groups(tool_key)

    kept_150 = select_whole_clusters(clusters, keep=KEEP_N150, seed=SEED)
    kept_72 = select_whole_clusters(clusters, keep=KEEP_GPT72, seed=SEED)
    retained_150 = retained_case_ids(case_to_cluster, kept_150)
    retained_72 = retained_case_ids(case_to_cluster, kept_72)
    assert len(retained_150) == 150 and len(retained_72) == 72

    # Retained set under the earlier tool-list key, same seed, for the change report.
    tool_clusters = sorted(set(tool_key.values()))
    old_150 = retained_case_ids(tool_key, select_whole_clusters(tool_clusters, keep=KEEP_N150, seed=SEED))
    dropped_150 = sorted(set(clusters) - set(kept_150))

    return {
        "status": "DRAFT, NOT FROZEN",
        "rule": ("S-A cluster-drop: whole attacker-instruction clusters kept with random.Random(seed).sample on the sorted "
                 "cluster identifiers. n = 150 per target keeps 50 of 62 clusters (12 dropped, 36 cases). gpt-5.6-sol H1 keeps "
                 "24 clusters (72 cases). Same retained set for every target and arm."),
        "seed": SEED,
        "seed_status": "author-confirmed (the protocol's existing sample seed)",
        "cluster_key": "sha256 of the attacker instruction text in the public InjecAgent release (f19c9f2)",
        "release_map": str(RELEASE_MAP.relative_to(ROOT)),
        "release_map_sha256": _sha256_text(RELEASE_MAP.read_text()),
        "sample_file": "datasets/external_samples/injecagent_phase2_sample.json",
        "sample_ids_sha256": sample["ids_sha256"],
        "instruction_partition_equals_tool_list_partition": partitions_equal,
        "retained_set_changed_vs_tool_list_key_n150": set(old_150) != set(retained_150),
        "n150_shared_with_tool_list_key": len(set(old_150) & set(retained_150)),
        "n150_only_in_tool_list_key": len(set(old_150) - set(retained_150)),
        "n150_only_in_release_key": len(set(retained_150) - set(old_150)),
        "n_clusters": len(clusters),
        "n_cases": len(case_to_cluster),
        "dropped_clusters_n150": dropped_150,
        "kept_clusters_n150": kept_150,
        "retained_case_ids_n150": retained_150,
        "kept_clusters_gpt_n72": kept_72,
        "retained_case_ids_gpt_n72": retained_72,
    }


def build_pilot_record() -> dict:
    """Pilot case set: 10 whole clusters drawn with the same seeded rule from the 12 clusters dropped for n = 150.
    These cases are outside the retained 150, so the pilot does not touch the confirmatory sample."""
    retained = json.loads(RECORD.read_text())
    release_map = json.loads(RELEASE_MAP.read_text())
    key_of = clusters_from_release_map(release_map["cases"])
    dropped = retained["dropped_clusters_n150"]
    if len(dropped) != 12:
        raise ValueError("expected 12 dropped clusters in the retained record")
    pilot_clusters = select_whole_clusters(dropped, keep=PILOT_CLUSTERS, seed=SEED)
    pilot_cases = retained_case_ids(key_of, pilot_clusters)
    if len(pilot_cases) != 3 * PILOT_CLUSTERS:
        raise ValueError("pilot clusters must be whole clusters of 3 cases")
    if set(pilot_cases) & set(retained["retained_case_ids_n150"]):
        raise ValueError("pilot overlaps the retained confirmatory set")
    return {
        "status": "PILOT, DRAFT, NOT FROZEN. Excluded from the confirmatory analysis.",
        "rule": ("10 whole clusters chosen with random.Random(seed).sample on the sorted identifiers of the 12 clusters "
                 "dropped for n = 150. Pilot runs A0 and SPOT_TOOL on llama-4-maverick, one request per episode."),
        "seed": SEED,
        "model": "meta-llama/llama-4-maverick",
        "arms": ["A0", "SPOT_TOOL"],
        "episodes": 2 * len(pilot_cases),
        "purpose": "check that the executed endpoint works on a live model and calibrate the per-episode cost estimate",
        "clusters": pilot_clusters,
        "case_ids": pilot_cases,
        "overlap_with_retained_150": 0,
        "release_map_sha256": retained["release_map_sha256"],
    }


def record_text(record: dict) -> str:
    return json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: Sequence[str] = ()) -> int:
    if "--pilot" in argv:
        text = json.dumps(build_pilot_record(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
        PILOT.write_text(text)
        print(f"wrote {PILOT.relative_to(ROOT)} sha256={_sha256_text(text)}")
        return 0
    text = record_text(build_record())
    RECORD.write_text(text)
    print(f"wrote {RECORD.relative_to(ROOT)} sha256={_sha256_text(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
