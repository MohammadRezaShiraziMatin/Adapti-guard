"""Deterministic Q1 P1 episode ordering and pair-boundary budget helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

ARMS = ("A0", "B3")


@dataclass(frozen=True)
class EpisodePair:
    attack_id: str
    target_model_id: str
    a0_index: int
    b3_index: int


def build_round_robin_attack_target_order(
    targets: Sequence[str],
    attack_ids: Sequence[str],
) -> list[tuple[str, str]]:
    """For each attack_id, visit every target in fixed target order (round-robin block)."""
    order: list[tuple[str, str]] = []
    for aid in attack_ids:
        for target in targets:
            order.append((aid, target))
    return order


def group_a0_b3_pairs(episode_indices: Sequence[dict[str, Any]]) -> list[EpisodePair]:
    """Expect consecutive A0 then B3 rows sharing attack_id and target_model_id."""
    pairs: list[EpisodePair] = []
    i = 0
    while i + 1 < len(episode_indices):
        a, b = episode_indices[i], episode_indices[i + 1]
        if (
            a.get("defense_arm") == "A0"
            and b.get("defense_arm") == "B3"
            and a.get("attack_id") == b.get("attack_id")
            and a.get("target_model_id") == b.get("target_model_id")
        ):
            pairs.append(
                EpisodePair(
                    attack_id=str(a["attack_id"]),
                    target_model_id=str(a["target_model_id"]),
                    a0_index=int(a["episode_index"]),
                    b3_index=int(b["episode_index"]),
                )
            )
            i += 2
        else:
            raise ValueError(
                f"invalid pair boundary at index {i}: "
                f"{a.get('defense_arm')}/{b.get('defense_arm')} "
                f"{a.get('attack_id')}/{b.get('target_model_id')}"
            )
    if i < len(episode_indices):
        raise ValueError("trailing unpaired episode at end of schedule")
    return pairs


def targets_seen_balanced(completed_rows: Iterable[dict[str, Any]], targets: Sequence[str]) -> bool:
    counts = {t: 0 for t in targets}
    for row in completed_rows:
        counts[str(row["target_model_id"])] = counts.get(str(row["target_model_id"]), 0) + 1
    if not counts:
        return True
    vals = list(counts.values())
    return max(vals) - min(vals) <= 1


def pair_boundary_stop_ok(completed_episode_count: int) -> bool:
    """Stop is valid only after an even number of episodes (full A0/B3 pairs)."""
    return completed_episode_count % 2 == 0
