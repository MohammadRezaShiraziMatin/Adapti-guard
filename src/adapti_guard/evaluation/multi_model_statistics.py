"""Statistical analysis for multi-model real LLM evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.adapti_guard.evaluation.statistics import (
    bootstrap_ci,
    cohens_d,
    holm_correction,
    mcnemar_test,
    proportion_ci_wilson,
    wilcoxon_signed_rank,
)


@dataclass
class EpisodeOutcome:
    episode_id: str
    label: str
    attack_succeeded: bool
    utility_success: bool
    blocked: bool
    baseline: str
    model_key: str


def load_predictions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def outcomes_from_predictions(
    rows: list[dict[str, Any]],
    *,
    baseline: str,
    model_key: str,
) -> list[EpisodeOutcome]:
    return [
        EpisodeOutcome(
            episode_id=str(r["id"]),
            label=str(r.get("label", "attack")),
            attack_succeeded=bool(r.get("attack_succeeded", False)),
            utility_success=bool(r.get("utility_success", False)),
            blocked=bool(r.get("blocked", False)),
            baseline=baseline,
            model_key=model_key,
        )
        for r in rows
    ]


def compute_baseline_statistics(
    outcomes: list[EpisodeOutcome],
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """Compute metrics + bootstrap CI for one baseline × model."""
    attacks = [o for o in outcomes if o.label == "attack"]
    benign = [o for o in outcomes if o.label != "attack"]

    attack_flags = [1.0 if o.attack_succeeded else 0.0 for o in attacks]
    asr_point, asr_lo, asr_hi = bootstrap_ci(attack_flags, seed=seed) if attack_flags else (0.0, 0.0, 0.0)
    n_attack_success = sum(1 for o in attacks if o.attack_succeeded)
    asr_wilson = proportion_ci_wilson(n_attack_success, len(attacks)) if attacks else (0.0, 0.0, 0.0)

    base = {
        "n_episodes": len(outcomes),
        "n_attack": len(attacks),
        "n_benign": len(benign),
        "asr": {
            "point": round(asr_point, 4),
            "bootstrap_ci_95": [round(asr_lo, 4), round(asr_hi, 4)],
            "wilson_ci_95": [round(asr_wilson[1], 4), round(asr_wilson[2], 4)],
        },
        "defense_rate": round(1.0 - asr_point, 4),
    }

    if not benign:
        base["fpr"] = None
        base["utility"] = None
        base["balanced_accuracy"] = None
        return base

    benign_fail = [1.0 if not o.utility_success else 0.0 for o in benign]
    fpr_point, fpr_lo, fpr_hi = bootstrap_ci(benign_fail, seed=seed)
    util_flags = [1.0 if o.utility_success else 0.0 for o in benign]
    util_point, util_lo, util_hi = bootstrap_ci(util_flags, seed=seed)
    tnr_point = 1.0 - fpr_point
    recall_point = base["defense_rate"]
    balanced_accuracy = 0.5 * (recall_point + tnr_point)

    base["fpr"] = {
        "point": round(fpr_point, 4),
        "bootstrap_ci_95": [round(fpr_lo, 4), round(fpr_hi, 4)],
    }
    base["utility"] = {
        "point": round(util_point, 4),
        "bootstrap_ci_95": [round(util_lo, 4), round(util_hi, 4)],
    }
    base["balanced_accuracy"] = {
        "point": round(balanced_accuracy, 4),
    }
    return base


def paired_baseline_comparison(
    outcomes_a: list[EpisodeOutcome],
    outcomes_b: list[EpisodeOutcome],
    *,
    reference: str = "B0",
    treatment: str = "B3",
) -> dict[str, Any]:
    """McNemar test on attack success (paired by episode_id)."""
    map_a = {o.episode_id: o for o in outcomes_a if o.label == "attack"}
    map_b = {o.episode_id: o for o in outcomes_b if o.label == "attack"}
    common_ids = sorted(set(map_a) & set(map_b))

    if not common_ids:
        return {
            "reference": reference,
            "treatment": treatment,
            "n_paired": 0,
            "mcnemar": {"p_value": 1.0, "method": "none"},
            "asr_delta": 0.0,
        }

    a_success = [map_a[i].attack_succeeded for i in common_ids]
    b_success = [map_b[i].attack_succeeded for i in common_ids]
    mcnemar = mcnemar_test(a_success, b_success)

    asr_a = sum(a_success) / len(a_success)
    asr_b = sum(b_success) / len(b_success)

    return {
        "reference": reference,
        "treatment": treatment,
        "n_paired": len(common_ids),
        "asr_reference": round(asr_a, 4),
        "asr_treatment": round(asr_b, 4),
        "asr_delta": round(asr_a - asr_b, 4),
        "asr_reduction": round(asr_a - asr_b, 4),
        "mcnemar": mcnemar,
        "significant_0.05": mcnemar["p_value"] < 0.05,
    }


def cross_model_comparison(
    model_outcomes: dict[str, list[EpisodeOutcome]],
    *,
    baseline: str,
) -> dict[str, Any]:
    """Compare ASR across models for the same baseline (not pooled)."""
    per_model: dict[str, Any] = {}
    asr_values: list[float] = []
    model_keys: list[str] = []

    for model_key, outcomes in sorted(model_outcomes.items()):
        stats = compute_baseline_statistics(outcomes)
        per_model[model_key] = stats
        asr_values.append(stats["asr"]["point"])
        model_keys.append(model_key)

    spread = max(asr_values) - min(asr_values) if asr_values else 0.0
    return {
        "baseline": baseline,
        "per_model": per_model,
        "asr_range": round(spread, 4),
        "model_keys": model_keys,
        "note": "Models evaluated on identical episodes; not pooled as independent samples.",
    }


@dataclass
class MultiModelStatisticalReport:
    experiment_id: str
    seed: int
    models: list[str]
    baselines: list[str]
    per_model_baseline: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)
    paired_comparisons: dict[str, dict[str, Any]] = field(default_factory=dict)
    cross_model: dict[str, dict[str, Any]] = field(default_factory=dict)
    holm_corrected: list[dict[str, Any]] = field(default_factory=list)
    status: str = "COMPLETED"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "seed": self.seed,
            "models": self.models,
            "baselines": self.baselines,
            "status": self.status,
            "per_model_baseline": self.per_model_baseline,
            "paired_comparisons": self.paired_comparisons,
            "cross_model": self.cross_model,
            "holm_corrected": self.holm_corrected,
            "notes": self.notes,
        }


def analyze_multi_model_results(
    results_root: Path,
    *,
    models: list[str],
    baselines: list[str],
    experiment_id: str = "EXP-004",
    seed: int = 42,
    reference_baseline: str = "B0",
    treatment_baseline: str = "B3",
) -> MultiModelStatisticalReport:
    """Analyze saved multi-model prediction artifacts."""
    report = MultiModelStatisticalReport(
        experiment_id=experiment_id,
        seed=seed,
        models=models,
        baselines=baselines,
    )

    # Load all outcomes
    all_outcomes: dict[str, dict[str, list[EpisodeOutcome]]] = {}
    for model_key in models:
        all_outcomes[model_key] = {}
        for baseline in baselines:
            pred_path = results_root / model_key / baseline / f"{baseline}_predictions.jsonl"
            rows = load_predictions(pred_path)
            all_outcomes[model_key][baseline] = outcomes_from_predictions(
                rows, baseline=baseline, model_key=model_key
            )

            if rows:
                report.per_model_baseline.setdefault(model_key, {})[baseline] = (
                    compute_baseline_statistics(all_outcomes[model_key][baseline], seed=seed)
                )

    if not any(all_outcomes[m][b] for m in models for b in baselines):
        report.status = "NO_DATA"
        report.notes.append("No prediction artifacts found for statistical analysis")
        return report

    # Paired McNemar: reference vs treatment per model
    raw_p_values: list[float] = []
    comparison_labels: list[str] = []

    for model_key in models:
        key = f"{model_key}:{reference_baseline}_vs_{treatment_baseline}"
        comp = paired_baseline_comparison(
            all_outcomes[model_key].get(reference_baseline, []),
            all_outcomes[model_key].get(treatment_baseline, []),
            reference=reference_baseline,
            treatment=treatment_baseline,
        )
        report.paired_comparisons[key] = comp
        raw_p_values.append(float(comp["mcnemar"]["p_value"]))
        comparison_labels.append(key)

    if raw_p_values:
        holm = holm_correction(raw_p_values)
        for label, h in zip(comparison_labels, holm):
            report.holm_corrected.append({
                "comparison": label,
                **h,
                "significant_0.05_holm": h["adjusted_p"] < 0.05,
            })

    # Cross-model ASR for each baseline
    for baseline in baselines:
        model_map = {
            m: all_outcomes[m].get(baseline, [])
            for m in models
        }
        report.cross_model[baseline] = cross_model_comparison(model_map, baseline=baseline)

    return report


def save_statistical_report(
    report: MultiModelStatisticalReport,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "statistical_analysis.json"
    json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    # CSV summary table
    csv_path = output_dir / "statistical_analysis.csv"
    lines = ["model,baseline,asr,asr_ci_lower,asr_ci_upper,fpr,utility,balanced_accuracy,n_attack,n_benign"]
    for model_key, baselines in report.per_model_baseline.items():
        for baseline, stats in baselines.items():
            asr = stats["asr"]
            fpr = stats.get("fpr")
            utility = stats.get("utility")
            balanced = stats.get("balanced_accuracy")
            fpr_point = "" if fpr is None else fpr["point"]
            util_point = "" if utility is None else utility["point"]
            bal_point = "" if balanced is None else (
                balanced["point"] if isinstance(balanced, dict) else balanced
            )
            lines.append(
                f"{model_key},{baseline},{asr['point']},"
                f"{asr['bootstrap_ci_95'][0]},{asr['bootstrap_ci_95'][1]},"
                f"{fpr_point},{util_point},{bal_point},"
                f"{stats['n_attack']},{stats['n_benign']}"
            )
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path
