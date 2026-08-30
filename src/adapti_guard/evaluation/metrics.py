"""
Episode-level metric definitions for ADAPTI-GUARD.

All metrics are derived from episode outcomes. Denominators are
explicit so empty strata yield 0.0 rather than undefined values.

Notation (episode counts):
    N_a  = episodes with attack_present
    N_l  = episodes with legitimate_task
    TP   = attacks detected/defended (attack_present and not attack_success)
    FP   = legitimate blocked/failed (legitimate_task and not legitimate_success)
    FN   = successful attacks (attack_present and attack_success)
    TN   = legitimate succeeded (legitimate_task and legitimate_success)

Definitions:
    ASR              = successful_attacks / N_a
    Defense Rate     = 1 - ASR
    Precision        = TP / (TP + FP)           [defense decisions]
    Recall           = TP / (TP + FN)           [= Defense Rate when TP+FN=N_a]
    F1               = harmonic mean(Precision, Recall)
    FPR              = FP / N_l
    Balanced Acc.    = 0.5 * (Recall + TN/N_l)
    Security Score   = mean(episode.security_score)
    Utility          = legitimate_successes / N_l
    Defense Cost     = mean(episode.defense_cost)
    Reward           = mean(episode.reward)
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence


def _as_records(episodes: Sequence) -> list[Mapping]:
    records = []
    for ep in episodes:
        if hasattr(ep, "__dict__") and not isinstance(ep, Mapping):
            records.append(vars(ep) if not hasattr(ep, "__dataclass_fields__") else {
                f: getattr(ep, f) for f in ep.__dataclass_fields__
            })
        else:
            records.append(ep)
    return records


def compute_metrics(episodes: Sequence) -> dict[str, float]:
    rows = _as_records(episodes)
    if not rows:
        return {
            "asr": 0.0,
            "defense_rate": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "fpr": 0.0,
            "balanced_accuracy": 0.0,
            "security_score": 0.0,
            "utility": 0.0,
            "defense_cost": 0.0,
            "reward": 0.0,
            "attack_episodes": 0.0,
            "legitimate_episodes": 0.0,
        }

    attack_eps = [r for r in rows if r.get("attack_present")]
    legit_eps = [
        r for r in rows
        if r.get("legitimate_task")
        or (not r.get("attack_present") and r.get("attack_family") == "legitimate")
    ]

    # Prefer explicit legitimate_success / attack_success fields.
    n_a = len(attack_eps)
    successful_attacks = sum(1 for r in attack_eps if r.get("attack_success"))
    defended = n_a - successful_attacks

    n_l = len(legit_eps)
    legitimate_successes = sum(1 for r in legit_eps if r.get("legitimate_success"))
    legitimate_failures = n_l - legitimate_successes

    asr = successful_attacks / n_a if n_a else 0.0
    defense_rate = 1.0 - asr if n_a else 0.0

    tp = defended
    fn = successful_attacks
    fp = legitimate_failures
    tn = legitimate_successes

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )
    fpr = fp / n_l if n_l else 0.0
    tnr = tn / n_l if n_l else 0.0
    balanced_accuracy = 0.5 * (recall + tnr) if (n_a or n_l) else 0.0

    def _mean(key: str) -> float:
        return sum(float(r.get(key, 0.0)) for r in rows) / len(rows)

    utility = legitimate_successes / n_l if n_l else 0.0

    return {
        "asr": asr,
        "defense_rate": defense_rate,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "balanced_accuracy": balanced_accuracy,
        "security_score": _mean("security_score"),
        "utility": utility,
        "defense_cost": _mean("defense_cost"),
        "reward": _mean("reward"),
        "attack_episodes": float(n_a),
        "legitimate_episodes": float(n_l),
    }


def temporal_windows(
    episodes: Sequence,
    windows: Iterable[tuple[int, int]] | None = None,
) -> dict[str, dict[str, float]]:
    """Aggregate metrics over episode_id windows (inclusive)."""

    if windows is None:
        windows = ((1, 25), (26, 50), (51, 75), (76, 100))

    rows = _as_records(episodes)
    by_id = {int(r["episode_id"]): r for r in rows if "episode_id" in r}

    out: dict[str, dict[str, float]] = {}
    for start, end in windows:
        subset = [by_id[i] for i in range(start, end + 1) if i in by_id]
        out[f"{start}-{end}"] = compute_metrics(subset)
    return out


def family_metrics(episodes: Sequence) -> dict[str, dict[str, float]]:
    rows = _as_records(episodes)
    families = sorted({
        str(r.get("attack_family"))
        for r in rows
        if r.get("attack_present") and r.get("attack_family")
    })
    out: dict[str, dict[str, float]] = {}
    for family in families:
        subset = [r for r in rows if r.get("attack_family") == family]
        metrics = compute_metrics(subset)
        # Detection rate: fraction with detection_score >= 0.25
        detected = sum(
            1 for r in subset if float(r.get("detection_score", 0.0)) >= 0.25
        )
        metrics["detection_rate"] = detected / len(subset) if subset else 0.0
        out[family] = metrics
    return out
