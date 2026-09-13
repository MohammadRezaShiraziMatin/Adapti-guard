"""Detector-only evaluation utilities for Layer A (no target/judge calls)."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
from src.adapti_guard.risk.risk_engine import RiskEngine


@dataclass
class DetectorEpisodeScore:
    id: str
    label: str
    split: str
    attack_family: str
    attack_subtype: str
    difficulty: str
    source_type: str
    hard_negative: bool
    injection_probability: float
    risk_score: float
    risk_level: str
    indicators: list[str]
    y_true: int
    y_pred_at_025: int


def _row_text(row: dict[str, Any]) -> str:
    context = str(row.get("context") or "")
    prompt = str(row.get("prompt") or "")
    return f"{context}\n\n{prompt}".strip() if context else prompt


def _meta(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("metadata")
    return raw if isinstance(raw, dict) else {}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def score_rows(
    rows: Sequence[dict[str, Any]],
    *,
    detector: PromptInjectionDetector | None = None,
    risk_engine: RiskEngine | None = None,
) -> list[DetectorEpisodeScore]:
    detector = detector or PromptInjectionDetector()
    risk_engine = risk_engine or RiskEngine()
    out: list[DetectorEpisodeScore] = []
    for row in rows:
        meta = _meta(row)
        det = detector.detect(_row_text(row))
        risk = risk_engine.assess(det)
        y_true = 1 if row.get("label") == "attack" else 0
        p = float(det.injection_probability)
        out.append(
            DetectorEpisodeScore(
                id=str(row.get("id", "")),
                label=str(row.get("label", "")),
                split=str(row.get("split", "")),
                attack_family=str(
                    meta.get("attack_family")
                    or row.get("category")
                    or ("attack" if y_true else "benign")
                ),
                attack_subtype=str(meta.get("attack_subtype") or row.get("attack_type") or ""),
                difficulty=str(meta.get("difficulty") or ("none" if not y_true else "unknown")),
                source_type=str(meta.get("source_type") or row.get("source") or ""),
                hard_negative=bool(meta.get("hard_negative", False)),
                injection_probability=p,
                risk_score=float(risk.score),
                risk_level=risk.level.value if hasattr(risk.level, "value") else str(risk.level),
                indicators=list(det.indicators or []),
                y_true=y_true,
                y_pred_at_025=1 if p >= 0.25 else 0,
            )
        )
    return out


def _safe_div(n: float, d: float) -> float | None:
    if d == 0:
        return None
    return n / d


def confusion(y_true: Sequence[int], y_pred: Sequence[int]) -> dict[str, int]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def binary_metrics(y_true: Sequence[int], y_pred: Sequence[int]) -> dict[str, Any]:
    c = confusion(y_true, y_pred)
    precision = _safe_div(c["tp"], c["tp"] + c["fp"])
    recall = _safe_div(c["tp"], c["tp"] + c["fn"])
    fpr = _safe_div(c["fp"], c["fp"] + c["tn"])
    fnr = _safe_div(c["fn"], c["fn"] + c["tp"])
    f1 = None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    acc = _safe_div(c["tp"] + c["tn"], len(y_true)) if y_true else None
    return {
        **c,
        "n": len(y_true),
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "fnr": fnr,
        "attack_recall": recall,
        "benign_false_positive_rate": fpr,
    }


def threshold_sweep(
    scores: Sequence[DetectorEpisodeScore],
    thresholds: Sequence[float] | None = None,
) -> list[dict[str, Any]]:
    thresholds = list(thresholds or [i / 10 for i in range(1, 10)])
    y_true = [s.y_true for s in scores]
    rows = []
    for thr in thresholds:
        y_pred = [1 if s.injection_probability >= thr else 0 for s in scores]
        m = binary_metrics(y_true, y_pred)
        rows.append({"threshold": thr, **m})
    return rows


def _auc_trapezoid(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    area = 0.0
    for i in range(1, len(xs)):
        area += (xs[i] - xs[i - 1]) * (ys[i] + ys[i - 1]) / 2.0
    return area


def auroc(scores: Sequence[DetectorEpisodeScore]) -> float | None:
    """Mann-Whitney AUROC on injection_probability."""
    pos = [s.injection_probability for s in scores if s.y_true == 1]
    neg = [s.injection_probability for s in scores if s.y_true == 0]
    if not pos or not neg:
        return None
    # Handle ties via mid-rank average
    pairs = [(v, 1) for v in pos] + [(v, 0) for v in neg]
    pairs.sort(key=lambda x: x[0])
    n = len(pairs)
    i = 0
    rank_sum_pos = 0.0
    rank = 1.0
    while i < n:
        j = i
        while j < n and pairs[j][0] == pairs[i][0]:
            j += 1
        avg_rank = (rank + (rank + (j - i) - 1)) / 2.0
        for k in range(i, j):
            if pairs[k][1] == 1:
                rank_sum_pos += avg_rank
        rank += j - i
        i = j
    n_pos = float(len(pos))
    n_neg = float(len(neg))
    u = rank_sum_pos - n_pos * (n_pos + 1) / 2.0
    return u / (n_pos * n_neg)


def auprc(scores: Sequence[DetectorEpisodeScore]) -> float | None:
    pos = [s for s in scores if s.y_true == 1]
    if not pos or not scores:
        return None
    ordered = sorted(scores, key=lambda s: s.injection_probability, reverse=True)
    tp = 0
    fp = 0
    fn = len(pos)
    precs: list[float] = []
    recs: list[float] = []
    for s in ordered:
        if s.y_true == 1:
            tp += 1
            fn -= 1
        else:
            fp += 1
        precision = tp / (tp + fp)
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        precs.append(precision)
        recs.append(recall)
    # Add origin
    xs = [0.0] + recs
    ys = [1.0] + precs
    return _auc_trapezoid(xs, ys)


def expected_calibration_error(
    scores: Sequence[DetectorEpisodeScore],
    n_bins: int = 10,
) -> dict[str, Any]:
    if not scores:
        return {"ece": None, "bins": []}
    bins: list[dict[str, Any]] = []
    ece = 0.0
    n = len(scores)
    for b in range(n_bins):
        lo = b / n_bins
        hi = (b + 1) / n_bins
        members = [
            s
            for s in scores
            if (s.injection_probability >= lo and s.injection_probability < hi)
            or (b == n_bins - 1 and s.injection_probability == 1.0)
        ]
        if not members:
            bins.append({"lo": lo, "hi": hi, "n": 0, "conf": None, "acc": None})
            continue
        conf = sum(s.injection_probability for s in members) / len(members)
        acc = sum(s.y_true for s in members) / len(members)
        ece += (len(members) / n) * abs(acc - conf)
        bins.append({"lo": lo, "hi": hi, "n": len(members), "conf": conf, "acc": acc})
    return {"ece": ece, "bins": bins}


def slice_metrics(
    scores: Sequence[DetectorEpisodeScore],
    *,
    key: str,
    threshold: float = 0.25,
) -> dict[str, Any]:
    groups: dict[str, list[DetectorEpisodeScore]] = defaultdict(list)
    for s in scores:
        groups[str(getattr(s, key))].append(s)
    out: dict[str, Any] = {}
    for name, group in sorted(groups.items()):
        y_true = [g.y_true for g in group]
        y_pred = [1 if g.injection_probability >= threshold else 0 for g in group]
        out[name] = {
            "n": len(group),
            "n_attack": sum(y_true),
            "n_benign": len(group) - sum(y_true),
            **binary_metrics(y_true, y_pred),
            "mean_probability": sum(g.injection_probability for g in group) / len(group),
        }
    return out


def evaluate_detector_pack(
    rows: Sequence[dict[str, Any]],
    *,
    threshold: float = 0.25,
) -> dict[str, Any]:
    scores = score_rows(rows)
    y_true = [s.y_true for s in scores]
    y_pred = [1 if s.injection_probability >= threshold else 0 for s in scores]
    hard_neg = [s for s in scores if s.hard_negative]
    hard_neg_fp = sum(1 for s in hard_neg if s.injection_probability >= threshold)
    return {
        "threshold": threshold,
        "n": len(scores),
        "n_attack": sum(y_true),
        "n_benign": len(y_true) - sum(y_true),
        "overall": binary_metrics(y_true, y_pred),
        "auroc": auroc(scores),
        "auprc": auprc(scores),
        "calibration": expected_calibration_error(scores),
        "threshold_sweep": threshold_sweep(scores),
        "by_attack_family": slice_metrics(
            [s for s in scores if s.y_true == 1], key="attack_family", threshold=threshold
        ),
        "by_difficulty": slice_metrics(
            [s for s in scores if s.y_true == 1], key="difficulty", threshold=threshold
        ),
        "by_source_type": slice_metrics(scores, key="source_type", threshold=threshold),
        "hard_negatives": {
            "n": len(hard_neg),
            "false_positives": hard_neg_fp,
            "fpr": _safe_div(hard_neg_fp, len(hard_neg)),
        },
        "risk_level_counts": dict(Counter(s.risk_level for s in scores)),
        "scores": [asdict(s) for s in scores],
    }


def write_detector_eval_artifacts(result: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    scores = result.pop("scores")
    (out_dir / "detector_metrics.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "detector_scores.jsonl").write_text(
        "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in scores),
        encoding="utf-8",
    )
    # restore for caller convenience
    result["scores"] = scores
    sweep_path = out_dir / "threshold_sweep.csv"
    lines = [
        "threshold,tp,fp,tn,fn,precision,recall,fpr,f1\n",
    ]
    for row in result["threshold_sweep"]:
        lines.append(
            "{threshold},{tp},{fp},{tn},{fn},{precision},{recall},{fpr},{f1}\n".format(
                threshold=row["threshold"],
                tp=row["tp"],
                fp=row["fp"],
                tn=row["tn"],
                fn=row["fn"],
                precision=row["precision"],
                recall=row["recall"],
                fpr=row["fpr"],
                f1=row["f1"],
            )
        )
    sweep_path.write_text("".join(lines), encoding="utf-8")
