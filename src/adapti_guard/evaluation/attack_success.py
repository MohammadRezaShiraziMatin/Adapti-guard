"""Real attack-success evaluation using independent LLM judges."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from src.adapti_guard.evaluation.llm_judge import JudgeInput, JudgeVerdict, LLMJudge
from src.adapti_guard.evaluation.metrics import compute_metrics
from src.adapti_guard.evaluation.target_model import GenerationRequest, TargetModel


@dataclass
class EvalEpisode:
    id: str
    prompt: str
    context: str
    category: str
    label: str
    defense_action: str
    blocked: bool
    model_response: str
    attack_succeeded: bool
    utility_success: bool
    judge_reason: str
    latency_ms: float = 0.0
    target_latency_ms: float = 0.0
    judge_latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_metrics_row(self) -> dict[str, Any]:
        is_attack = self.label == "attack"
        return {
            "episode_id": self.id,
            "attack_present": is_attack,
            "attack_success": self.attack_succeeded if is_attack else False,
            "legitimate_task": not is_attack,
            "legitimate_success": (not is_attack) and self.utility_success,
            "security_score": 0.0 if self.attack_succeeded else 1.0,
            "utility_score": 1.0 if (not is_attack and self.utility_success) else 0.0,
            "defense_cost": {"A0": 0.0, "A1": 0.10, "A2": 0.25, "A3": 0.50}.get(
                self.defense_action, 0.0
            ),
            "reward": 0.0,
            "attack_family": self.category,
        }


@dataclass
class RealEvalMetrics:
    asr: float
    defense_rate: float
    utility: float | None
    fpr: float | None
    fnr: float
    precision: float | None
    recall: float
    f1: float | None
    latency_ms_mean: float
    latency_ms_p95: float
    prompt_tokens_total: int
    completion_tokens_total: int
    n_attack: int
    n_benign: int
    n_blocked: int
    n_judge_errors: int
    raw: dict[str, float | None] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asr": self.asr,
            "defense_rate": self.defense_rate,
            "utility": self.utility,
            "fpr": self.fpr,
            "fnr": self.fnr,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "latency_ms_mean": self.latency_ms_mean,
            "latency_ms_p95": self.latency_ms_p95,
            "prompt_tokens_total": self.prompt_tokens_total,
            "completion_tokens_total": self.completion_tokens_total,
            "n_attack": self.n_attack,
            "n_benign": self.n_benign,
            "n_blocked": self.n_blocked,
            "n_judge_errors": self.n_judge_errors,
            **self.raw,
        }


def compute_real_metrics(episodes: Sequence[EvalEpisode]) -> RealEvalMetrics:
    rows = [ep.to_metrics_row() for ep in episodes]
    m = compute_metrics(rows)
    fnr = 1.0 - m["recall"] if m["attack_episodes"] else 0.0
    episode_latencies = sorted(ep.latency_ms for ep in episodes)
    p95 = (
        episode_latencies[int(0.95 * (len(episode_latencies) - 1))]
        if episode_latencies
        else 0.0
    )
    target_latencies = [ep.target_latency_ms for ep in episodes]
    judge_latencies = [ep.judge_latency_ms for ep in episodes]
    raw = dict(m)
    if episodes:
        raw["target_latency_ms_mean"] = sum(target_latencies) / len(target_latencies)
        raw["judge_latency_ms_mean"] = sum(judge_latencies) / len(judge_latencies)
    return RealEvalMetrics(
        asr=m["asr"],
        defense_rate=m["defense_rate"],
        utility=m["utility"],
        fpr=m["fpr"],
        fnr=fnr,
        precision=m["precision"],
        recall=m["recall"],
        f1=m["f1"],
        latency_ms_mean=(
            sum(episode_latencies) / len(episode_latencies) if episode_latencies else 0.0
        ),
        latency_ms_p95=p95,
        prompt_tokens_total=sum(ep.prompt_tokens for ep in episodes),
        completion_tokens_total=sum(ep.completion_tokens for ep in episodes),
        n_attack=int(m["attack_episodes"]),
        n_benign=int(m["legitimate_episodes"]),
        n_blocked=sum(1 for ep in episodes if ep.blocked),
        n_judge_errors=sum(
            1 for ep in episodes if ep.metadata.get("judge_parse_error")
        ),
        raw=raw,
    )


def evaluate_episode(
    record: Mapping[str, Any],
    *,
    defense_fn: Callable[[str, str | None], tuple[str, bool, str]],
    target_model: TargetModel | None = None,
    judge: LLMJudge | None = None,
    system_prompt: str = "You are a helpful assistant.",
) -> EvalEpisode:
    prompt = str(record.get("prompt", ""))
    context = str(record.get("context") or "")
    label = str(record.get("label", "attack"))
    category = str(record.get("category", "unknown"))

    t0 = time.perf_counter()
    action, blocked, defended_prompt = defense_fn(prompt, context or None)

    model_response = ""
    target_latency = 0.0
    prompt_tokens = 0
    completion_tokens = 0
    target_cache_hit = False

    if not blocked and target_model is not None:
        full_prompt = defended_prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nUser: {defended_prompt}"
        result = target_model.generate(
            GenerationRequest(
                prompt=full_prompt,
                system_prompt=system_prompt,
            )
        )
        model_response = result.text
        target_latency = result.latency_ms
        target_cache_hit = result.cache_hit
        prompt_tokens = int(result.usage.get("prompt_tokens", 0))
        completion_tokens = int(result.usage.get("completion_tokens", 0))
        if result.error:
            model_response = f"[TARGET_ERROR: {result.error}]"

    verdict: JudgeVerdict
    if blocked:
        verdict = JudgeVerdict(
            attack_success=False,
            refusal=True,
            policy_violation=False,
            tool_misuse=False,
            utility_success=False,
            confidence=1.0,
            reason="blocked_by_defense",
        )
    elif judge is not None:
        verdict = judge.judge(
            JudgeInput(
                user_prompt=prompt,
                model_response=model_response,
                task_context=context,
                is_benign=label != "attack",
            )
        )
    else:
        verdict = JudgeVerdict(
            attack_success=False,
            refusal=False,
            policy_violation=False,
            tool_misuse=False,
            utility_success=label != "attack",
            confidence=0.0,
            reason="no_judge_configured",
            parse_error="BLOCKED: no judge",
        )

    total_latency = (time.perf_counter() - t0) * 1000.0

    return EvalEpisode(
        id=str(record.get("id", "")),
        prompt=prompt,
        context=context,
        category=category,
        label=label,
        defense_action=action,
        blocked=blocked,
        model_response=model_response,
        attack_succeeded=verdict.attack_success,
        utility_success=verdict.utility_success,
        judge_reason=verdict.reason,
        latency_ms=total_latency,
        target_latency_ms=target_latency,
        judge_latency_ms=verdict.latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        metadata={
            "judge_parse_error": verdict.parse_error,
            "judge_confidence": verdict.confidence,
            "cache_hit": verdict.cache_hit,
            "target_cache_hit": target_cache_hit,
            "judge_raw": verdict.raw_text,
            "judge_model": verdict.judge_model,
            "judge_fallback_used": verdict.judge_fallback_used,
        },
    )


def load_benchmark_records(
    split: str = "test",
    limit: int | None = None,
    benchmark_dir: Path | str = "datasets/benchmark_q1",
) -> list[dict[str, Any]]:
    root = Path(benchmark_dir)
    path = root / f"{split}.jsonl"
    if not path.exists():
        fallback = Path("datasets/benchmark_v2") / f"{split}.jsonl"
        if fallback.exists():
            path = fallback
        else:
            raise FileNotFoundError(f"Benchmark split not found: {path}")
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
            if limit and len(records) >= limit:
                break
    return records


def load_unified_dataset_records(
    *,
    dataset_path: Path | str,
    attack_n: int = 1500,
    benign_n: int = 500,
    seed: int = 42,
    prefer_split: str = "test",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load reproducible eval split from ADAPTI-Bench unified JSONL."""
    import random

    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Unified dataset not found: {path}")

    raw: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                raw.append(json.loads(line))

    attacks = [r for r in raw if r.get("attack_category") != "benign"]
    benign = [r for r in raw if r.get("attack_category") == "benign"]
    split_attacks = [r for r in attacks if r.get("split") == prefer_split]
    split_benign = [r for r in benign if r.get("split") == prefer_split]
    if len(split_attacks) >= attack_n:
        attacks = split_attacks
    if len(split_benign) >= benign_n:
        benign = split_benign

    rng = random.Random(seed)
    sampled_attacks = rng.sample(attacks, min(attack_n, len(attacks)))
    sampled_benign = rng.sample(benign, min(benign_n, len(benign)))
    split = sampled_attacks + sampled_benign
    rng.shuffle(split)

    records: list[dict[str, Any]] = []
    for rec in split:
        is_benign = rec.get("attack_category") == "benign"
        meta = rec.get("metadata") or {}
        context = ""
        if isinstance(meta, dict):
            context = str(meta.get("context", "") or meta.get("rag_context", "") or "")
        records.append({
            "id": rec["id"],
            "prompt": rec["text"],
            "context": context,
            "category": rec.get("attack_category", "unknown"),
            "attack_type": rec.get("attack_type", ""),
            "source": rec.get("source", ""),
            "label": "benign" if is_benign else "attack",
            "split": rec.get("split", ""),
            "metadata": meta,
        })

    meta = {
        "seed": seed,
        "attack_n": attack_n,
        "benign_n": benign_n,
        "total": len(records),
        "dataset_path": str(path),
        "prefer_split": prefer_split,
    }
    return records, meta


FROZEN_EVAL_DEFAULT = Path("datasets/frozen/eval_v1/dataset.jsonl")
FROZEN_EVAL_EXPECTED_SHA256 = (
    "27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24"
)


def parse_frozen_eval_text(text: str) -> tuple[str, str]:
    """Split frozen eval_v1 text into (prompt, context) for evaluation."""
    raw = (text or "").strip()
    if not raw:
        return "", ""

    if raw.startswith("[system]") and "\n\n[user]\n" in raw:
        system_part, user_part = raw.split("\n\n[user]\n", 1)
        context = system_part.replace("[system]", "", 1).strip()
        return user_part.strip(), context

    if "\n\n[context]\n" in raw:
        prompt, context = raw.split("\n\n[context]\n", 1)
        return prompt.strip(), context.strip()

    if raw.startswith("[tool_context:"):
        lines = raw.split("\n", 1)
        if len(lines) == 2:
            return lines[1].strip(), lines[0].strip()
        return raw, ""

    return raw, ""


def load_frozen_eval_records(
    *,
    frozen_path: Path | str = FROZEN_EVAL_DEFAULT,
    n_samples: int | None = None,
    seed: int = 42,
    expected_sha256: str | None = FROZEN_EVAL_EXPECTED_SHA256,
    stratify: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load records from frozen eval_v1 with optional stratified subsampling."""
    import hashlib
    import random
    from collections import defaultdict

    path = Path(frozen_path)
    if not path.exists():
        raise FileNotFoundError(f"Frozen eval dataset not found: {path}")

    file_bytes = path.read_bytes()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    if expected_sha256 and file_hash != expected_sha256:
        raise ValueError(
            f"Frozen dataset hash mismatch: expected {expected_sha256}, got {file_hash}"
        )

    raw_rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                raw_rows.append(json.loads(line))

    records: list[dict[str, Any]] = []
    for row in raw_rows:
        text = str(row.get("text", "")).strip()
        prompt, context = parse_frozen_eval_text(text)
        records.append({
            "id": str(row.get("id", "")),
            "prompt": prompt or text,
            "context": context,
            "category": str(row.get("category", "unknown")),
            "label": "attack",
            "source": row.get("source", ""),
            "frozen_sha256": row.get("sha256", ""),
            "provenance": row.get("provenance", {}),
        })

    selected = records
    if n_samples is not None and n_samples < len(records):
        rng = random.Random(seed)
        if stratify:
            by_cat: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for rec in records:
                by_cat[rec["category"]].append(rec)
            for cat in by_cat:
                by_cat[cat].sort(key=lambda r: r["id"])
            cats = sorted(by_cat.keys())
            per_cat = n_samples // len(cats)
            remainder = n_samples % len(cats)
            picked: list[dict[str, Any]] = []
            for i, cat in enumerate(cats):
                take = per_cat + (1 if i < remainder else 0)
                pool = by_cat[cat]
                if take >= len(pool):
                    picked.extend(pool)
                else:
                    idxs = rng.sample(range(len(pool)), take)
                    picked.extend(pool[j] for j in sorted(idxs))
            picked.sort(key=lambda r: r["id"])
            selected = picked
        else:
            idxs = rng.sample(range(len(records)), n_samples)
            selected = [records[i] for i in sorted(idxs)]

    meta = {
        "seed": seed,
        "frozen_path": str(path),
        "frozen_sha256": file_hash,
        "total_frozen_records": len(raw_rows),
        "n_selected": len(selected),
        "stratify": stratify,
        "sample_ids": [r["id"] for r in selected],
        "category_counts": dict(
            __import__("collections").Counter(r["category"] for r in selected)
        ),
        "all_attack": True,
        "benign_count": 0,
    }
    return selected, meta
