"""Phase 7 artifact schema and stream consistency."""

import json
from pathlib import Path

ADAPTIVE = Path("results/phase7/adaptive_100.json")
BASELINES = Path("results/phase7/fixed_baselines_100.json")
STREAM = Path("results/common_attack_stream.json")

REQUIRED_FIELDS = {
    "episode_id",
    "attack_family",
    "risk_score",
    "detection_score",
    "defense_level",
    "defense_action",
    "reward",
    "adaptation_signal",
    "attack_present",
    "payload",
    "attack_success",
}


def test_adaptive_artifact_schema_and_stream_consistency():
    assert ADAPTIVE.exists()
    assert STREAM.exists()

    adaptive = json.loads(ADAPTIVE.read_text(encoding="utf-8"))
    stream = json.loads(STREAM.read_text(encoding="utf-8"))

    assert len(adaptive) == 100
    assert [e["episode_id"] for e in adaptive] == list(range(1, 101))

    mismatches = 0
    for s, a in zip(stream, adaptive):
        assert REQUIRED_FIELDS.issubset(a.keys())
        if (
            s["episode_id"] != a["episode_id"]
            or s["attack_family"] != a["attack_family"]
            or s["payload"] != a["payload"]
            or a["attack_present"] is not True
        ):
            mismatches += 1
    assert mismatches == 0


def test_baseline_artifact_fairness_counts():
    assert BASELINES.exists()
    baselines = json.loads(BASELINES.read_text(encoding="utf-8"))
    assert len(baselines) == 4
    for row in baselines:
        assert row["episodes"] == 100
        assert row["attack_episodes"] == 100
        assert row["legitimate_episodes"] == 0
        assert 0.0 <= row["asr"] <= 1.0
        assert abs(row["asr"] + row["defense_rate"] - 1.0) < 1e-9
