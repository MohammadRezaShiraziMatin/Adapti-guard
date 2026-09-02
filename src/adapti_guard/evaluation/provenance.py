"""Provenance schema and validation for Q1 scientific experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


from src.adapti_guard.evaluation.evaluation_modes import LEGACY_ALIASES, LEGACY_SIMULATION_ONLY


class EvaluationMode(str, Enum):
    REAL_LLM_JUDGE = "real_llm_judge"
    LEGACY_SIMULATION_ONLY = "LEGACY_SIMULATION_ONLY"
    HARMONIZED_SIMULATION = "HARMONIZED_SIMULATION"
    DETECTOR_SIMULATION = "DETECTOR_SIMULATION"
    DEFENSE_SIMULATION = "defense_simulation"
    UNKNOWN = "unknown"


class ExperimentValidity(str, Enum):
  """Scientific validity classification for experiment artifacts."""

  VALID = "VALID"  # Real LLM + judge, sufficient samples, provenance complete
  INVALID = "INVALID"  # Artifacts exist but scientifically unusable (e.g. all API errors)
  BLOCKED = "BLOCKED"  # Could not execute
  SIMULATION = "SIMULATION"  # Valid simulation, not for LLM security claims
  PARTIAL = "PARTIAL"  # Incomplete provenance or sample size
  NOT_RUN = "NOT_RUN"


REQUIRED_PROVENANCE_FIELDS = [
    "experiment_id",
    "status",
    "evaluation_mode",
    "dataset",
    "dataset_hash",
    "seed",
    "git_commit",
    "timestamp",
    "target_model",
    "judge_model",
    "n_samples",
]

PUBLICATION_MIN_SAMPLES = {
    "smoke": 5,
    "pilot": 50,
    "full": 500,
}


@dataclass
class ProvenanceRecord:
    experiment_id: str
    path: str
    status: str
    validity: ExperimentValidity
    evaluation_mode: str
    n_samples: int = 0
    n_judge_errors: int = 0
    n_auth_errors: int = 0
    dataset: str = ""
    dataset_hash: str = ""
    seed: int | None = None
    git_commit: str = ""
    timestamp: str = ""
    target_model: str = ""
    judge_model: str = ""
    metrics_usable_for_publication: bool = False
    issues: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "path": self.path,
            "status": self.status,
            "validity": self.validity.value,
            "evaluation_mode": self.evaluation_mode,
            "n_samples": self.n_samples,
            "n_judge_errors": self.n_judge_errors,
            "n_auth_errors": self.n_auth_errors,
            "dataset": self.dataset,
            "dataset_hash": self.dataset_hash,
            "seed": self.seed,
            "git_commit": self.git_commit,
            "timestamp": self.timestamp,
            "target_model": self.target_model,
            "judge_model": self.judge_model,
            "metrics_usable_for_publication": self.metrics_usable_for_publication,
            "issues": self.issues,
            "notes": self.notes,
        }


def classify_real_llm_validity(
    metrics: dict[str, Any],
    *,
    min_samples: int = PUBLICATION_MIN_SAMPLES["pilot"],
) -> tuple[ExperimentValidity, list[str]]:
    """Determine whether real-LLM metrics are scientifically usable."""
    issues: list[str] = []
    status = str(metrics.get("status", "")).upper()

    if status == "BLOCKED":
        return ExperimentValidity.BLOCKED, ["Experiment blocked before execution"]

    inner = metrics.get("metrics", metrics)
    n_samples = int(inner.get("n_attack", 0) + inner.get("n_benign", 0))
    if n_samples == 0:
        n_samples = int(metrics.get("n_samples", 0))

    n_judge_errors = int(inner.get("n_judge_errors", metrics.get("n_judge_errors", 0)))
    prompt_tokens = int(inner.get("prompt_tokens_total", 0))
    eval_mode = str(metrics.get("evaluation_mode", inner.get("evaluation_mode", "")))

    if eval_mode in LEGACY_ALIASES or eval_mode == LEGACY_SIMULATION_ONLY:
            return ExperimentValidity.SIMULATION, ["LEGACY_SIMULATION_ONLY — not valid for LLM security claims"]

    if n_judge_errors >= n_samples and n_samples > 0:
        issues.append(f"All {n_samples} episodes had judge errors")
        return ExperimentValidity.INVALID, issues

    if prompt_tokens == 0 and n_samples > 0 and status == "COMPLETED":
        issues.append("Zero prompt tokens — target LLM likely did not respond")
        return ExperimentValidity.INVALID, issues

    if status == "COMPLETED" and n_judge_errors > n_samples * 0.5:
        issues.append(f"Judge error rate >50% ({n_judge_errors}/{n_samples})")
        return ExperimentValidity.INVALID, issues

    if n_samples < min_samples:
        issues.append(f"Sample size {n_samples} < minimum {min_samples} for publication")
        return ExperimentValidity.PARTIAL, issues

    if status != "COMPLETED":
        return ExperimentValidity.NOT_RUN, [f"Status is {status}"]

    return ExperimentValidity.VALID, issues
