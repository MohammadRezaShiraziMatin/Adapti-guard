#!/usr/bin/env python3
"""Build datasets/benchmark_v2 from available public sources.

Does NOT fabricate benchmark rows. Sources absent from disk are marked
DATASET_UNAVAILABLE in the manifest.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "datasets" / "benchmark_v2"

SOURCE_PATHS = {
    "NotInject_train": ROOT / "dataset/processed/NotInject/train_final.json",
    "NotInject_valid": ROOT / "dataset/raw/NotInject/datasets/valid.json",
    "BIPIA": ROOT / "BIPIA",
    "InjecAgent": ROOT / "dataset/raw/InjecAgent",
    "TensorTrust": ROOT / "dataset/raw/TensorTrust",
    "PIArena": ROOT / "dataset/raw/PIArena",
    "AgentHarm": ROOT / "dataset/raw/AgentHarm",
    "AgentDojo": ROOT / "dataset/raw/AgentDojo",
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_notinject(path: Path, split: str) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = json.load(f)
    out = []
    for i, row in enumerate(rows):
        label = int(row.get("label", 0))
        prompt = row.get("prompt") or row.get("text") or ""
        out.append(
            {
                "id": f"notinject_{split}_{i:06d}",
                "category": "prompt_injection",
                "subcategory": row.get("source", "notinject"),
                "prompt": prompt,
                "source": "NotInject",
                "severity": "high" if label == 1 else "none",
                "attack_type": "injection" if label == 1 else "benign",
                "label": label,
                "split": split,
                "metadata": {
                    "original_index": i,
                    "source_file": str(path),
                },
            }
        )
    return out


def deduplicate_exact(rows: list[dict]) -> tuple[list[dict], dict]:
    seen: set[str] = set()
    kept: list[dict] = []
    removed = 0
    for row in rows:
        key = normalize_text(row["prompt"])
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept.append(row)
    before = len(rows)
    after = len(kept)
    report = {
        "method": "exact_normalized_prompt",
        "before": before,
        "after": after,
        "removed": removed,
        "duplicate_rate": removed / before if before else 0.0,
    }
    return kept, report


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    availability: dict[str, str] = {}
    all_rows: list[dict] = []
    source_reports: dict[str, Any] = {}

    for name, path in SOURCE_PATHS.items():
        if path.exists():
            if path.is_file() and name.startswith("NotInject"):
                split = "train" if "train" in name else "validation"
                rows = load_notinject(path, split)
                availability[name] = f"LOADED ({len(rows)} rows)"
                all_rows.extend(rows)
                source_reports[name] = {"records": len(rows), "path": str(path)}
            elif path.is_dir():
                availability[name] = "PRESENT_UNPARSED — manual importer required"
            else:
                availability[name] = "UNKNOWN_FORMAT"
        else:
            availability[name] = "DATASET_UNAVAILABLE"

    # Internal smoke subset (NOT publication evidence) — only if no external data
    if not all_rows:
        from scripts.generate_attack_stream import generate_stream

        stream = generate_stream(100)
        benign = [
            "What is the capital of Germany?",
            "Summarize the benefits of regular exercise.",
            "Explain what a database is.",
        ]
        for i, row in enumerate(stream[:50]):
            all_rows.append(
                {
                    "id": f"internal_smoke_attack_{i:04d}",
                    "category": row["attack_family"],
                    "subcategory": "template",
                    "prompt": row["payload"],
                    "source": "internal_attack_stream",
                    "severity": "medium",
                    "attack_type": row["attack_family"],
                    "label": 1,
                    "split": "test",
                    "metadata": {"warning": "SMOKE_ONLY_NOT_PUBLICATION_EVIDENCE"},
                }
            )
        for i, text in enumerate(benign):
            all_rows.append(
                {
                    "id": f"internal_smoke_benign_{i:04d}",
                    "category": "benign",
                    "subcategory": "qa",
                    "prompt": text,
                    "source": "internal_benign_tasks",
                    "severity": "none",
                    "attack_type": "benign",
                    "label": 0,
                    "split": "test",
                    "metadata": {"warning": "SMOKE_ONLY_NOT_PUBLICATION_EVIDENCE"},
                }
            )
        availability["internal_smoke"] = f"GENERATED ({len(all_rows)} rows, smoke only)"

    deduped, dedup_report = deduplicate_exact(all_rows)

    # Simple split assignment if all same split
    train, valid, test = [], [], []
    for row in deduped:
        split = row.get("split", "test")
        if split == "train":
            train.append(row)
        elif split == "validation":
            valid.append(row)
        else:
            test.append(row)

    if not train and not valid and test:
        # hold out nothing — document as test-only smoke
        pass

    write_jsonl(OUT_DIR / "train.jsonl", train)
    write_jsonl(OUT_DIR / "validation.jsonl", valid)
    write_jsonl(OUT_DIR / "test.jsonl", test)

    labels = Counter(r["label"] for r in deduped)
    categories = Counter(r["category"] for r in deduped)
    sources = Counter(r["source"] for r in deduped)

    manifest = {
        "dataset": "benchmark_v2",
        "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "availability": availability,
        "source_reports": source_reports,
        "dedup_report": dedup_report,
        "counts": {
            "total": len(deduped),
            "train": len(train),
            "validation": len(valid),
            "test": len(test),
            "label_0": labels.get(0, 0),
            "label_1": labels.get(1, 0),
        },
        "category_distribution": dict(categories),
        "source_distribution": dict(sources),
        "sha256": {
            "test.jsonl": sha256_file(OUT_DIR / "test.jsonl") if test else None,
            "train.jsonl": sha256_file(OUT_DIR / "train.jsonl") if train else None,
            "validation.jsonl": sha256_file(OUT_DIR / "validation.jsonl") if valid else None,
        },
        "publication_ready": bool(
            any(v.startswith("LOADED") for v in availability.values())
        ),
    }
    with (OUT_DIR / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with (OUT_DIR / "dedup_report.json").open("w", encoding="utf-8") as f:
        json.dump(dedup_report, f, indent=2)
        f.write("\n")

    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
