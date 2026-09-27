#!/usr/bin/env python3
"""Build LITERATURE_EXTRACTIONS.yaml from verified bib + cached arxiv abstracts."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs/research/phase1_sources"
OUT = ROOT / "docs/research/LITERATURE_EXTRACTIONS.yaml"

RECORDS = [
    ("perez2022ignore", "2211.09527", "references.bib"),
    ("greshake2023not", "2302.12173", "references.bib"),
    ("liu2023prompt", "2307.08487", "references.bib"),
    ("yi2023bipia", "2312.14197", "references.bib"),
    ("wallace2024instruction", "2404.06409", "references.bib"),
    ("debenedetti2024agentdojo", "2406.13352", "references.bib"),
    ("zhan2024injecagent", "2406.03092", "references.bib"),
    ("inan2023llama", "2312.06674", "references.bib"),
    ("rebedea2023nemo", "2310.10501", "references.bib"),
    ("chen2024struq", "2402.06363", "references.bib"),
    ("chen2024secalign", "2410.05451", "references.bib"),
    ("owasp2023llm", None, "references.bib"),
    ("mcnemar1947note", None, "references.bib"),
    ("chao2023pair", "2310.08419", "references_extension.bib"),
    ("zou2023gcg", "2307.15043", "references_extension.bib"),
    ("russinovich2024crescendo", "2404.01833", "references_extension.bib"),
    ("toyer2023tensortrust", "2311.01011", "references_extension.bib"),
    ("li2024injecguard", "2410.22770", "references_extension.bib"),
    ("chang2025chatinject", "2509.22830", "references_extension.bib"),
]

TAXONOMY = {
    "perez2022ignore": ["direct_pi", "jailbreak_adjacent"],
    "greshake2023not": ["indirect_pi"],
    "liu2023prompt": ["direct_pi", "indirect_pi"],
    "yi2023bipia": ["indirect_pi", "rag_pi"],
    "wallace2024instruction": ["instruction_hierarchy"],
    "debenedetti2024agentdojo": ["agent_tool_use", "agent_environment"],
    "zhan2024injecagent": ["agent_tool_injection", "indirect_pi"],
    "inan2023llama": ["defense_input", "detection"],
    "rebedea2023nemo": ["defense_runtime", "agent_tool_defense"],
    "chen2024struq": ["defense_context", "instruction_separation"],
    "chen2024secalign": ["defense_input"],
    "owasp2023llm": ["standards"],
    "mcnemar1947note": ["methods_statistics"],
    "chao2023pair": ["adaptive_feedback_guided", "jailbreak_adjacent"],
    "zou2023gcg": ["adaptive_iterative", "obfuscation"],
    "russinovich2024crescendo": ["multi_turn_stateful", "jailbreak_adjacent"],
    "toyer2023tensortrust": ["direct_pi", "indirect_pi", "defense_input"],
    "li2024injecguard": ["defense_input", "detection"],
    "chang2025chatinject": ["multi_turn_stateful", "agent_tool_injection", "indirect_pi"],
}


def load_abstract(arxiv_id: str | None) -> tuple[str | None, str | None]:
    if not arxiv_id:
        return None, None
    meta_path = SRC / f"abs_{arxiv_id}.meta.json"
    abs_path = SRC / f"abs_{arxiv_id}.abstract.txt"
    meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
    abstract = abs_path.read_text().strip() if abs_path.is_file() else None
    return abstract, meta.get("source")


def mt_flags(key: str, abstract: str | None) -> dict:
    a = (abstract or "").lower()
    return {
        "stateful_multi_turn": key in {"russinovich2024crescendo", "chang2025chatinject"} or "multi-turn" in a,
        "persistent_memory": "persistent" in a and "conversation" in a,
        "delayed_attack": "delayed" in a,
        "cross_turn_dependency": key in {"russinovich2024crescendo", "chang2025chatinject"},
        "multi_turn_adaptive": False,
    }


def ad_flags(key: str, abstract: str | None) -> dict:
    a = (abstract or "").lower()
    closed_loop = key in {"chao2023pair", "zou2023gcg"} or (
        "iterative" in a and ("refine" in a or "feedback" in a or "queries" in a)
    )
    return {
        "static_only": key in {"perez2022ignore", "greshake2023not", "liu2023prompt"},
        "iterative": key in {"zou2023gcg"} or "iterative" in a,
        "feedback_guided": key in {"chao2023pair"} or "refine" in a,
        "defense_aware": "defense" in a and "adapt" in a,
        "closed_loop_attacker": closed_loop,
    }


def ag_flags(key: str, abstract: str | None) -> dict:
    a = (abstract or "").lower()
    env = key in {"debenedetti2024agentdojo", "zhan2024injecagent", "chang2025chatinject"}
    return {
        "tool_use": "tool" in a or env,
        "tool_invocation": env,
        "environment_execution": key in {"debenedetti2024agentdojo", "zhan2024injecagent"},
        "state_transition": key in {"debenedetti2024agentdojo"},
        "authorization": "Not reported in abstract" if not abstract else ("authorization" in a or key in {"debenedetti2024agentdojo", "zhan2024injecagent"}),
        "conceptual_only": key in {"liu2023prompt", "greshake2023not"} and not env,
    }


def nine_fields(abstract: str | None) -> dict:
    if not abstract:
        return {f: "Not reported (no abstract cached; bibliographic entry only)" for f in [
            "problem", "threat_model", "attack", "dataset", "model", "defense",
            "evaluation_protocol", "metrics", "limitations_research_gap",
        ]}
    sent = abstract.split(". ")[0] + "."
    return {
        "problem": f"{sent} [evidence: abstract sentence 1]",
        "threat_model": _extract_threat(abstract),
        "attack": _extract_attack(abstract),
        "dataset": _field_or_not(abstract, ["dataset", "benchmark", "corpus", "game"]),
        "model": _field_or_not(abstract, ["llm", "model", "gpt", "chatgpt", "gemini"]),
        "defense": _field_or_not(abstract, ["defend", "defense", "guard", "mitigat", "safeguard"]),
        "evaluation_protocol": _field_or_not(abstract, ["evaluat", "benchmark", "experiment", "study"]),
        "metrics": _field_or_not(abstract, ["rate", "accuracy", "success", "asr", "robustness"]),
        "limitations_research_gap": "Not reported in abstract (see primary paper for limitations).",
    }


def _field_or_not(abstract: str, keywords: list[str]) -> str:
    if any(k in abstract.lower() for k in keywords):
        return f"Mentioned in abstract; see primary source. [keywords matched: {', '.join(keywords)}]"
    return "Not reported in abstract"


def _extract_threat(abstract: str) -> str:
    a = abstract.lower()
    if "prompt injection" in a:
        return "Prompt injection / adversarial manipulation of LLM(-integrated) inputs. [abstract]"
    if "jailbreak" in a:
        return "Jailbreak / alignment bypass. [abstract]"
    if "paired" in a and "proportion" in a:
        return "Statistical comparison of paired binary outcomes (methods paper). [abstract]"
    return "Not reported in abstract"


def _extract_attack(abstract: str) -> str:
    a = abstract.lower()
    if "indirect" in a:
        return "Indirect injection via untrusted external content. [abstract]"
    if "multi-turn" in a or "crescendo" in a:
        return "Multi-turn escalation / dialogue-based jailbreak. [abstract]"
    if "iterative" in a or "refine" in a:
        return "Iterative / optimization-based attack generation. [abstract]"
    if "adversarial" in a and "suffix" in a:
        return "Universal adversarial suffix attacks. [abstract]"
    return "Attack mechanism described in abstract; see primary source for taxonomy detail."


def main() -> None:
    rows = []
    for key, arxiv_id, bib in RECORDS:
        abstract, source_url = load_abstract(arxiv_id)
        bib_verified = (ROOT / "docs/paper/q1_findings" / bib).is_file()
        abstract_verified = abstract is not None
        rows.append({
            "id": key,
            "bib_file": bib,
            "arxiv_id": arxiv_id,
            "url": source_url or ("https://owasp.org/www-project-top-10-for-large-language-model-applications/" if key == "owasp2023llm" else None),
            "taxonomy": TAXONOMY.get(key, []),
            "verification": {
                "bibliographic": bib_verified,
                "abstract_cached": abstract_verified,
                "source_verified": bib_verified and (abstract_verified or key in {"owasp2023llm", "mcnemar1947note"}),
            },
            "extraction": nine_fields(abstract),
            "multi_turn_audit": mt_flags(key, abstract),
            "adaptive_audit": ad_flags(key, abstract),
            "agentic_audit": ag_flags(key, abstract),
        })
    header = (
        "# Auto-generated Phase 1 extractions. Re-run: scripts/build_phase1_extractions.py\n"
        "schema_version: 1\nrecord_count: 19\n"
    )
    import yaml
    OUT.write_text(header + yaml.safe_dump({"records": rows}, sort_keys=False, allow_unicode=True))
    print(f"Wrote {OUT} ({len(rows)} records)")


if __name__ == "__main__":
    main()
