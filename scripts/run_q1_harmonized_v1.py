#!/usr/bin/env python3
"""Run Q1 harmonized evaluation bundle (versioned, non-destructive)."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.harmonized_runner import (
    METRIC_VERSION,
    RUNNER_VERSION,
    SCHEDULE_PATTERN,
    HARMONIZED_METHODS,
    PolicyMode,
    attack_episode_ids,
    attack_stream_ids,
    build_schedule_75_25,
    legitimate_episode_ids,
    legitimate_task_ids,
    sha256_file,
    HarmonizedRunner,
)
from src.adapti_guard.experiments.harmonized_validation import (
    build_harmonized_results_payload,
    build_transition_statistics_payload,
    consolidated_validation,
    validate_schedule_75_25,
    write_json,
)


EXPERIMENT_VERSION = "q1_harmonized_v1"
OUTPUT_DIR = Path("results/phase8/q1_harmonized_v1")
STREAM_PATH = Path("results/common_attack_stream.json")
EPISODES = 100
SEED = 42  # deterministic protocol identifier; runner is deterministic given stream


def _git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return None


def _log_event(log_path: Path, event: str, message: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{stamp} | {event} | {message}\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def main() -> int:
    log_path = OUTPUT_DIR / "run.log"
    if log_path.exists():
        # preserve prior failed run per failure rule
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archived = OUTPUT_DIR / f"run_{stamp}.log"
        log_path.replace(archived)

    _log_event(log_path, "START", EXPERIMENT_VERSION)

    if not STREAM_PATH.exists():
        _log_event(log_path, "FINAL_STATUS", "FAIL missing attack stream")
        print(f"ERROR: missing {STREAM_PATH}", file=sys.stderr)
        return 1

    stream_hash = sha256_file(STREAM_PATH)
    schedule = build_schedule_75_25(EPISODES)

    with STREAM_PATH.open("r", encoding="utf-8") as handle:
        attack_stream = json.load(handle)

    _log_event(
        log_path,
        "INPUT_VALIDATION",
        f"stream={STREAM_PATH} sha256={stream_hash[:16]} episodes={EPISODES}",
    )

    schedule_check = validate_schedule_75_25(
        {
            "episode_count": len(schedule),
            "attack_count": len(attack_episode_ids(schedule)),
            "legitimate_count": len(legitimate_episode_ids(schedule)),
        }
    )
    if schedule_check["validity"] != "PASS":
        _log_event(log_path, "FINAL_STATUS", "FAIL schedule construction")
        return 1

    _log_event(
        log_path,
        "POPULATION_CONSTRUCTION",
        (
            f"pattern={SCHEDULE_PATTERN} attacks={schedule_check['attack']} "
            f"legitimate={schedule_check['legitimate']}"
        ),
    )

    runner = HarmonizedRunner.from_stream_path(
        STREAM_PATH,
        episodes=EPISODES,
    )

    results = {}
    for mode in HARMONIZED_METHODS:
        _log_event(log_path, "METHOD_START", mode.value)
        results[mode.value] = runner.run_method(mode)
        _log_event(log_path, "METHOD_COMPLETE", mode.value)

    payload = build_harmonized_results_payload(results)
    summaries = payload["summaries"]

    validation = consolidated_validation(
        results,
        summaries,
        OUTPUT_DIR,
        stream_hash=stream_hash,
        schedule_validity=schedule_check,
    )

    _log_event(log_path, "FAIRNESS_CHECK", validation["checks"]["population_fairness"])
    _log_event(log_path, "METRIC_CHECK", validation["checks"]["metric_integrity"])
    _log_event(log_path, "PARETO_CHECK", validation["checks"]["pareto_validity"])

    attack_ids = attack_stream_ids(attack_stream[:EPISODES], schedule)
    legit_ids = legitimate_task_ids(schedule)

    manifest = {
        "experiment_version": EXPERIMENT_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "configuration": {
            "episodes": EPISODES,
            "attack_count": 75,
            "legitimate_count": 25,
            "schedule_pattern": SCHEDULE_PATTERN,
            "attack_threshold": 2,
            "legitimate_threshold": 2,
            "use_historical_signal": True,
            "seed": SEED,
        },
        "attack_stream_version": "common_attack_stream_v1",
        "attack_stream_path": str(STREAM_PATH),
        "attack_stream_sha256": stream_hash,
        "attack_selection": (
            "75 attack episodes = all slots where episode_id % 4 != 0; "
            "each uses frozen stream[episode_id-1] payload/family. "
            "25 stream slots at episode_id in {4,8,...,100} are legitimate-only "
            "and not executed as attacks."
        ),
        "attack_ids": attack_ids,
        "legitimate_task_ids": legit_ids,
        "methods": [m.value for m in HARMONIZED_METHODS],
        "method_definitions": {
            "fixed_l0": "action_for_level(0); no policy updates",
            "fixed_l1": "action_for_level(1); no policy updates",
            "fixed_l2": "action_for_level(2); no policy updates",
            "fixed_l3": "action_for_level(3); no policy updates",
            "full_adaptive": (
                "DefensePolicyEngine.decide(risk, level) + full "
                "PolicyUpdateEngine escalation/de-escalation"
            ),
            "escalation_only": "full adaptive with de-escalation disabled",
            "de_escalation_only": "full adaptive with escalation disabled",
            "no_cost_gate": (
                "full adaptive with FeedbackEngine cost>=0.50 gate removed "
                "from REDUCE_DEFENSE triggers"
            ),
        },
        "metric_version": METRIC_VERSION,
        "runner_version": RUNNER_VERSION,
        "denominator_definition": payload["denominator_definition"],
        "source_artifacts": [str(STREAM_PATH)],
        "output_dir": str(OUTPUT_DIR),
        "frozen_artifacts_unmodified": True,
    }

    write_json(OUTPUT_DIR / "run_manifest.json", manifest)
    write_json(OUTPUT_DIR / "harmonized_results.json", payload)
    write_json(
        OUTPUT_DIR / "transition_statistics.json",
        build_transition_statistics_payload(results),
    )
    write_json(OUTPUT_DIR / "fairness_validation.json", validation["fairness_validation"])
    write_json(OUTPUT_DIR / "pareto_analysis.json", validation["pareto_analysis"])

    full_validation = {
        "validity": validation["validity"],
        "checks": validation["checks"],
        "schedule_validation": validation["schedule_validation"],
        "transition_validation": validation["transition_validation"],
        "policy_validation": validation["policy_validation"],
        "metric_validation": validation["metric_validation"],
        "artifact_validation": validation["artifact_validation"],
    }
    write_json(OUTPUT_DIR / "consolidated_validation.json", full_validation)

    _log_event(log_path, "ARTIFACT_WRITE", str(OUTPUT_DIR))
    _log_event(
        log_path,
        "REPRODUCIBILITY_CHECK",
        f"stream_sha256={stream_hash[:16]} runner={RUNNER_VERSION}",
    )
    _log_event(log_path, "FINAL_STATUS", validation["validity"])

    print("=" * 60)
    print("ADAPTI-GUARD Q1 HARMONIZED RUN")
    print("=" * 60)
    print(f"VALIDITY: {validation['validity']}")
    print(f"OUTPUT:   {OUTPUT_DIR}")
    for row in summaries:
        print(
            f"{row['method']:20s} ASR={row['asr']:.3f} "
            f"DR={row['defense_rate']:.3f} U={row['utility']:.3f} "
            f"C={row['defense_cost']:.3f}"
        )
    print("Pareto non-dominated:", validation["pareto_analysis"]["pareto_non_dominated"])
    print("=" * 60)

    return 0 if validation["validity"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
