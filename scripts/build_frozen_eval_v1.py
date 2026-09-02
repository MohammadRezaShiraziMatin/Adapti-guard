#!/usr/bin/env python3
"""Phase 2.5 — Build frozen eval_v1 candidates from benchmark_q1/test + external raw sources.

IMMUTABLE:
  - datasets/benchmark_q1/* (never written)
  - datasets/raw/* (never written)

OUTPUT:
  - datasets/processed/eval_v1_candidates.jsonl  (always)
  - datasets/frozen/eval_v1/                      (only if audit PASS)

Usage:
    python scripts/build_frozen_eval_v1.py
    python scripts/audit_frozen_eval_v1.py
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from role_attack_classifier import classify_trustllm_jailbreak_record

BENCHMARK_DIR = ROOT / "datasets" / "benchmark_q1"
RAW = ROOT / "datasets" / "raw"
PROCESSED = ROOT / "datasets" / "processed"
FROZEN = ROOT / "datasets" / "frozen" / "eval_v1"
AUDIT = ROOT / "datasets" / "audit" / "phase2_5_remediation"

SEED = 42
MIN_PER_CATEGORY = 110
TARGET_TOTAL = 770

ROLE_KW = re.compile(
    r"\b(DAN|you are now|act as|pretend to be|developer mode|"
    r"do anything now|jailbreak mode|ignore previous instructions)\b",
    re.I,
)
LEAK_KW = re.compile(
    r"(system prompt|initial instructions|repeat the instructions|"
    r"show me your system|system message|what were you told|"
    r"output the text above|repeat everything in the system prompt)",
    re.I,
)

CATEGORY_ORDER = [
    "prompt_injection",
    "jailbreak",
    "rag_security",
    "context_attack",
    "role_attack",
    "tool_abuse",
    "system_prompt_leakage",
]


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


@dataclass
class Sample:
    id: str
    text: str
    category: str
    source: str
    source_version: str = ""
    suite: str = ""
    task_id: str = ""
    injection_vector: str = ""
    injection_location: str = ""
    user_task: str = ""
    attack_objective: str = ""
    tool_context: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)
    sha256: str = ""
    benchmark_q1_id: str | None = None
    adaptive_template_derived: bool = False

    def finalize(self) -> None:
        self.sha256 = sha256_text(self.text)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "source": self.source,
            "source_version": self.source_version,
            "suite": self.suite,
            "task_id": self.task_id,
            "injection_vector": self.injection_vector,
            "injection_location": self.injection_location,
            "user_task": self.user_task,
            "attack_objective": self.attack_objective,
            "tool_context": self.tool_context,
            "provenance": self.provenance,
            "sha256": self.sha256,
            "benchmark_q1_id": self.benchmark_q1_id,
            "adaptive_template_derived": self.adaptive_template_derived,
        }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def verify_benchmark_immutable(before: dict[str, str]) -> dict[str, str]:
    after = {
        "train": sha256_file(BENCHMARK_DIR / "train.jsonl"),
        "validation": sha256_file(BENCHMARK_DIR / "validation.jsonl"),
        "test": sha256_file(BENCHMARK_DIR / "test.jsonl"),
        "hashes.json": sha256_file(BENCHMARK_DIR / "hashes.json"),
    }
    if before != after:
        raise RuntimeError(f"benchmark_q1 MUTATED: before={before} after={after}")
    return after


def load_exclusion_sets() -> dict[str, Any]:
    train_hashes = set()
    val_hashes = set()
    for split, target in [("train", train_hashes), ("validation", val_hashes)]:
        for row in load_jsonl(BENCHMARK_DIR / f"{split}.jsonl"):
            target.add(normalize_text(row.get("prompt", "") + "\n" + row.get("context", "")))

    infra_path = ROOT / "experiments" / "INFRA-SMOKE-001" / "config.json"
    infra_ids = set()
    if infra_path.exists():
        infra_ids = set(json.loads(infra_path.read_text())["dataset_meta"]["sample_ids"])

    return {
        "train_val_normalized_hashes": train_hashes | val_hashes,
        "infra_smoke_ids": infra_ids,
    }


def map_benchmark_category(row: dict[str, Any]) -> str | None:
    cat = row.get("category", "")
    text = (row.get("prompt", "") + " " + row.get("context", ""))
    if ROLE_KW.search(text):
        return "role_attack"
    if LEAK_KW.search(text):
        return "system_prompt_leakage"
    if cat == "direct_prompt_injection":
        return "prompt_injection"
    if cat == "indirect_prompt_injection":
        return "context_attack"
    if cat == "rag_injection":
        return "rag_security"
    if cat == "jailbreak":
        return "jailbreak"
    if cat == "adaptive_attacks":
        return "prompt_injection"
    if cat == "agent_tool_injection":
        return "tool_abuse"
    return None


def extract_benchmark_test(exclusions: dict[str, Any]) -> list[Sample]:
    out: list[Sample] = []
    for row in load_jsonl(BENCHMARK_DIR / "test.jsonl"):
        if row.get("label") != "attack":
            continue
        if row["id"] in exclusions["infra_smoke_ids"]:
            continue
        category = map_benchmark_category(row)
        if not category:
            continue
        text = row.get("prompt", "").strip()
        if row.get("context"):
            text = f"{text}\n\n[context]\n{row['context']}".strip()
        norm = normalize_text(text)
        if norm in exclusions["train_val_normalized_hashes"]:
            continue
        s = Sample(
            id=f"bq1_test_{row['id']}",
            text=text,
            category=category,
            source="benchmark_q1",
            source_version="test_split",
            provenance={
                "upstream_id": row["id"],
                "upstream_category": row.get("category"),
                "attack_type": row.get("attack_type"),
                "source_field": row.get("source"),
                "split": "test",
            },
            benchmark_q1_id=row["id"],
            adaptive_template_derived=(row.get("category") == "adaptive_attacks"),
        )
        s.finalize()
        out.append(s)
    return out


def extract_injecagent() -> list[Sample]:
    out: list[Sample] = []
    for fname in ["attacker_cases_dh.jsonl", "attacker_cases_ds.jsonl"]:
        path = RAW / "injecagent" / "data" / fname
        if not path.exists():
            continue
        for idx, row in enumerate(load_jsonl(path)):
            tools = row.get("Attacker Tools") or []
            instruction = row.get("Attacker Instruction", "").strip()
            if not instruction:
                continue
            tool_ctx = ", ".join(tools) if isinstance(tools, list) else str(tools)
            text = instruction
            if tool_ctx:
                text = f"[tool_context: {tool_ctx}]\n{instruction}"
            sid = f"ext_injecagent_{fname.replace('.jsonl','')}_{idx:04d}"
            s = Sample(
                id=sid,
                text=text,
                category="tool_abuse",
                source="injecagent",
                source_version=fname,
                tool_context=tool_ctx,
                attack_objective=row.get("Expected Achievements", ""),
                provenance={
                    "source_file": str(path.relative_to(ROOT)),
                    "record_index": idx,
                    "attack_type": row.get("Attack Type"),
                    "attacker_tools": tools,
                    "modified_flag": row.get("Modifed"),
                },
            )
            s.finalize()
            out.append(s)
    return out


def _goal_from_ast(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.strip()
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
            else:
                parts.append("{VAR}")
        return "".join(parts).strip()
    return None


def extract_agentdojo() -> list[Sample]:
    out: list[Sample] = []
    root = RAW / "agentdojo" / "AgentDojo" / "src" / "agentdojo" / "default_suites"
    if not root.exists():
        return out
    seen_goals: set[str] = set()
    for path in sorted(root.rglob("injection_tasks.py")):
        rel = path.relative_to(root)
        version = rel.parts[0]
        suite = rel.parts[1] if len(rel.parts) > 1 else "unknown"
        src = path.read_text(encoding="utf-8")
        mod = ast.parse(src)
        for node in mod.body:
            if not isinstance(node, ast.ClassDef) or not node.name.startswith("InjectionTask"):
                continue
            goal: str | None = None
            for item in node.body:
                if not isinstance(item, ast.Assign):
                    continue
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "GOAL":
                        goal = _goal_from_ast(item.value)
            if not goal:
                continue
            norm_goal = normalize_text(goal)
            if norm_goal in seen_goals:
                continue
            seen_goals.add(norm_goal)
            cls = node.name
            sid = f"ext_agentdojo_{version}_{suite}_{cls}"
            s = Sample(
                id=sid,
                text=goal,
                category="tool_abuse",
                source="agentdojo",
                source_version=version,
                suite=suite,
                task_id=cls,
                attack_objective=goal,
                provenance={
                    "repository": "AgentDojo",
                    "source_file": str(path.relative_to(ROOT)),
                    "extraction": "ast_GOAL_from_injection_tasks.py",
                    "note": "Injection task GOAL describes unauthorized tool action objective",
                },
            )
            s.finalize()
            out.append(s)
    return out


def _garak_attacks_path() -> Path | None:
    attacks_path = ROOT / ".venv/lib/python3.12/site-packages/garak/data/sysprompt_extraction/attacks.json"
    if attacks_path.exists():
        return attacks_path
    import glob

    hits = glob.glob(str(ROOT / ".venv/lib/python*/site-packages/garak/data/sysprompt_extraction/attacks.json"))
    return Path(hits[0]) if hits else None


def _load_garak_system_prompts() -> list[tuple[str, int, str]]:
    """Load Garak HF system-prompt datasets from local HuggingFace cache only."""
    from datasets import Dataset

    cache_root = Path.home() / ".cache/huggingface/datasets"
    sources = [
        (
            "garak-llm/drh-System-Prompt-processed",
            cache_root
            / "garak-llm___drh-system-prompt-processed/default/0.0.0/26bb2b284b0380268bc74fe51b1c5eeaccb02242/drh-system-prompt-processed-train.arrow",
            "systemprompt",
        ),
        (
            "garak-llm/tm-system_prompt",
            cache_root
            / "garak-llm___tm-system_prompt/default/0.0.0/005c0854fe0c95e6a56ed45e3ff1e755cf007394/tm-system_prompt-train.arrow",
            "prompt",
        ),
    ]
    rows: list[tuple[str, int, str]] = []
    for dataset_name, arrow_path, column in sources:
        if not arrow_path.exists():
            continue
        ds = Dataset.from_file(str(arrow_path))
        for idx, item in enumerate(ds):
            prompt_text = str(item.get(column) or "").strip()
            if len(prompt_text) > 20:
                rows.append((dataset_name, idx, prompt_text))
    return rows


def _load_leakage_sets(exclusions: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Normalized text hashes from benchmark train/val/test."""
    blocked: set[str] = set(exclusions["train_val_normalized_hashes"])
    for split in ["test"]:
        for row in load_jsonl(BENCHMARK_DIR / f"{split}.jsonl"):
            text = row.get("prompt", "")
            if row.get("context"):
                text = f"{text}\n{row['context']}"
            blocked.add(normalize_text(text))
    return blocked, exclusions["train_val_normalized_hashes"]


def extract_role_attack_trustllm(
    exclusions: dict[str, Any],
    existing_normalized: set[str] | None = None,
) -> tuple[list[Sample], dict[str, Any]]:
    """Extract role_attack samples from TrustLLM jailbreak scenario subclass."""
    path = RAW / "role_attack" / "trustllm_jailbreak.json"
    audit: dict[str, Any] = {
        "source": "trustllm",
        "raw_file": str(path.relative_to(ROOT)) if path.exists() else None,
        "total_records": 0,
        "accepted": 0,
        "exclusions": [],
        "provenance": [],
    }
    if not path.exists():
        return [], audit

    blocked_norm, _ = _load_leakage_sets(exclusions)
    if existing_normalized:
        blocked_norm = blocked_norm | existing_normalized

    out: list[Sample] = []
    records = json.loads(path.read_text(encoding="utf-8"))
    audit["total_records"] = len(records)

    for idx, row in enumerate(records):
        decision = classify_trustllm_jailbreak_record(row)
        text = str(row.get("prompt") or "").strip()
        base_prov = {
            "source_file": str(path.relative_to(ROOT)),
            "original_dataset_name": "TrustLLM jailbreak",
            "original_index": idx,
            "original_labels": row.get("label"),
            "original_source_field": row.get("source"),
            "classification_reason": decision.reason,
            "classification_evidence": decision.evidence,
        }
        if not decision.is_role_attack:
            audit["exclusions"].append({
                "original_index": idx,
                "reason": decision.reason,
                "evidence": decision.evidence,
            })
            continue
        norm = normalize_text(text)
        if norm in blocked_norm:
            audit["exclusions"].append({
                "original_index": idx,
                "reason": "leakage_or_duplicate",
                "normalized_preview": norm[:120],
            })
            continue
        blocked_norm.add(norm)
        sid = f"ext_role_trustllm_{idx:05d}"
        s = Sample(
            id=sid,
            text=text,
            category="role_attack",
            source="trustllm",
            source_version="4b864211f32602fddb8cafc8d5154bed1e0ce01e",
            attack_objective="persona/role-play jailbreak via TrustLLM scenario subclass",
            provenance=base_prov,
        )
        s.finalize()
        out.append(s)
        audit["provenance"].append({
            "id": sid,
            "original_index": idx,
            "sha256": s.sha256,
            "classification_reason": decision.reason,
        })
        audit["accepted"] += 1

    return out, audit


def _write_role_attack_audit(audit: dict[str, Any]) -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    exclusions = audit.get("exclusions", [])
    provenance = audit.get("provenance", [])
    by_reason: Counter[str] = Counter(e["reason"] for e in exclusions)

    inventory = {
        "source": "trustllm",
        "raw_file": audit.get("raw_file"),
        "total_records": audit.get("total_records", 0),
        "accepted_candidates": audit.get("accepted", 0),
        "excluded_total": len(exclusions),
        "exclusion_by_reason": dict(by_reason),
        "classification": "TrustLLM scenario label + persona-mechanism filter",
    }
    (AUDIT / "role_attack_inventory.json").write_text(
        json.dumps(inventory, indent=2), encoding="utf-8"
    )
    with (AUDIT / "role_attack_exclusions.jsonl").open("w", encoding="utf-8") as fh:
        for row in exclusions:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (AUDIT / "role_attack_provenance.jsonl").open("w", encoding="utf-8") as fh:
        for row in provenance:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = {
        "role_attack_remediation": {
            "external_source": "trustllm",
            "raw_records": audit.get("total_records", 0),
            "accepted_after_filter": audit.get("accepted", 0),
            "excluded": len(exclusions),
            "duplicate_exclusions": sum(1 for e in exclusions if e["reason"] == "leakage_or_duplicate"),
            "invalid_uncertain_exclusions": sum(
                1 for e in exclusions if e["reason"] != "leakage_or_duplicate"
            ),
        }
    }
    (AUDIT / "role_attack_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )


def extract_garak_sysprompt() -> list[Sample]:
    """Build System Prompt Leakage samples using Garak's official probe pairing."""
    out: list[Sample] = []
    attacks_path = _garak_attacks_path()
    if not attacks_path:
        return out

    data = json.loads(attacks_path.read_text(encoding="utf-8"))
    attack_templates: list[tuple[str, int, str]] = []
    for garak_cat, templates in data.items():
        for idx, template in enumerate(templates):
            template = template.strip()
            if template:
                attack_templates.append((garak_cat, idx, template))

    system_prompts = _load_garak_system_prompts()
    if not system_prompts:
        # Fallback: attack templates alone (legacy path)
        for garak_cat, idx, template in attack_templates:
            sid = f"ext_garak_sysprompt_{garak_cat}_{idx:03d}"
            s = Sample(
                id=sid,
                text=template,
                category="system_prompt_leakage",
                source="garak",
                source_version="sysprompt_extraction/attacks.json",
                attack_objective="extract the model's system prompt",
                provenance={
                    "garak_probe": "SystemPromptExtraction",
                    "garak_category": garak_cat,
                    "template_index": idx,
                    "attacks_json": str(attacks_path),
                    "semantics": "attack template only (system prompt source unavailable offline)",
                },
            )
            s.finalize()
            out.append(s)
        return out

    combos: list[tuple[str, int, str, str, int, str]] = []
    for ds_name, sp_idx, sys_prompt in system_prompts:
        for garak_cat, atk_idx, attack in attack_templates:
            combos.append((ds_name, sp_idx, sys_prompt, garak_cat, atk_idx, attack))
    combos.sort(key=lambda x: (x[0], x[1], x[3], x[4]))

    for ds_name, sp_idx, sys_prompt, garak_cat, atk_idx, attack in combos:
        text = f"[system]\n{sys_prompt}\n\n[user]\n{attack}"
        sid = f"ext_garak_sysprompt_{ds_name.split('/')[-1]}_{sp_idx:04d}_{garak_cat}_{atk_idx:03d}"
        s = Sample(
            id=sid,
            text=text,
            category="system_prompt_leakage",
            source="garak",
            source_version="SystemPromptExtraction",
            attack_objective="extract the model's system prompt",
            provenance={
                "garak_probe": "SystemPromptExtraction",
                "system_prompt_dataset": ds_name,
                "system_prompt_record_index": sp_idx,
                "garak_attack_category": garak_cat,
                "attack_template_index": atk_idx,
                "attacks_json": str(attacks_path),
                "semantics": "Garak (system_prompt, attack_template) conversation pair",
            },
        )
        s.finalize()
        out.append(s)
    return out


def dedupe_samples(samples: list[Sample]) -> tuple[list[Sample], list[dict]]:
    seen_hash: set[str] = set()
    seen_id: set[str] = set()
    kept: list[Sample] = []
    audit: list[dict] = []
    for s in sorted(samples, key=lambda x: x.id):
        if s.id in seen_id:
            audit.append({"operation": "DROP_DUPLICATE_ID", "id": s.id})
            continue
        if s.sha256 in seen_hash:
            audit.append({"operation": "DROP_DUPLICATE_SHA256", "id": s.id, "sha256": s.sha256})
            continue
        seen_id.add(s.id)
        seen_hash.add(s.sha256)
        kept.append(s)
    return kept, audit


def select_balanced(samples: list[Sample]) -> tuple[list[Sample], dict[str, int]]:
    by_cat: dict[str, list[Sample]] = defaultdict(list)
    for s in samples:
        by_cat[s.category].append(s)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda x: x.id)

    selected: list[Sample] = []
    counts: dict[str, int] = {}
    for cat in CATEGORY_ORDER:
        pool = by_cat.get(cat, [])
        take = min(MIN_PER_CATEGORY, len(pool))
        selected.extend(pool[:take])
        counts[cat] = take
    return selected, counts


def build() -> dict[str, Any]:
    before_hashes = {
        "train": sha256_file(BENCHMARK_DIR / "train.jsonl"),
        "validation": sha256_file(BENCHMARK_DIR / "validation.jsonl"),
        "test": sha256_file(BENCHMARK_DIR / "test.jsonl"),
        "hashes.json": sha256_file(BENCHMARK_DIR / "hashes.json"),
    }

    exclusions = load_exclusion_sets()
    sources_log: list[dict] = []

    pools: list[Sample] = []
    role_audit: dict[str, Any] = {}
    for name, fn in [
        ("benchmark_q1_test", lambda: extract_benchmark_test(exclusions)),
        ("injecagent", extract_injecagent),
        ("agentdojo", extract_agentdojo),
        ("garak_sysprompt", extract_garak_sysprompt),
    ]:
        batch = fn()
        sources_log.append({"source": name, "extracted": len(batch)})
        pools.extend(batch)

    benchmark_norm = {normalize_text(s.text) for s in pools}
    role_batch, role_audit = extract_role_attack_trustllm(exclusions, benchmark_norm)
    sources_log.append({"source": "trustllm_role_attack", "extracted": len(role_batch)})
    pools.extend(role_batch)
    _write_role_attack_audit(role_audit)

    deduped, dedupe_audit = dedupe_samples(pools)
    selected, cat_counts = select_balanced(deduped)

    available = Counter(s.category for s in deduped)
    gaps = {
        cat: {"available": available.get(cat, 0), "selected": cat_counts.get(cat, 0), "required": MIN_PER_CATEGORY}
        for cat in CATEGORY_ORDER
    }

    PROCESSED.mkdir(parents=True, exist_ok=True)
    candidates_path = PROCESSED / "eval_v1_candidates.jsonl"
    with candidates_path.open("w", encoding="utf-8") as fh:
        for s in selected:
            fh.write(json.dumps(s.to_dict(), ensure_ascii=False) + "\n")

    after_hashes = verify_benchmark_immutable(before_hashes)

    meta = {
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "seed": SEED,
        "min_per_category": MIN_PER_CATEGORY,
        "target_total": TARGET_TOTAL,
        "selected_total": len(selected),
        "category_counts": cat_counts,
        "available_after_dedupe": dict(available),
        "gaps": gaps,
        "sources_log": sources_log,
        "benchmark_hashes_before_after": {"before": before_hashes, "after": after_hashes, "unchanged": True},
        "exclusions": {
            "infra_smoke_ids": sorted(exclusions["infra_smoke_ids"]),
            "train_val_hash_exclusion": True,
        },
        "adaptive_template_derived_count": sum(1 for s in selected if s.adaptive_template_derived),
        "dedupe_dropped": len(dedupe_audit),
        "role_attack_import": {
            "accepted_from_trustllm": role_audit.get("accepted", 0),
            "excluded_from_trustllm": len(role_audit.get("exclusions", [])),
        },
    }

    build_manifest = PROCESSED / "eval_v1_build_manifest.json"
    build_manifest.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    mutation_log = AUDIT / "mutation_audit_log.jsonl"
    AUDIT.mkdir(parents=True, exist_ok=True)
    with mutation_log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "operation": "BUILD_EVAL_V1_CANDIDATES",
            "reason": "Phase 2.5 remediation pipeline",
            "datasets_modified": [],
            "datasets_created": [str(candidates_path.relative_to(ROOT))],
            "benchmark_q1_unchanged": True,
            "timestamp": meta["build_timestamp"],
            "code_version": "scripts/build_frozen_eval_v1.py",
        }) + "\n")

    return meta


def main() -> int:
    meta = build()
    print(json.dumps({
        "selected_total": meta["selected_total"],
        "category_counts": meta["category_counts"],
        "available": meta["available_after_dedupe"],
        "gaps": meta["gaps"],
        "benchmark_unchanged": True,
        "output": str(PROCESSED / "eval_v1_candidates.jsonl"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
