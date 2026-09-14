#!/usr/bin/env python3
"""Verify workshop manuscript facts against frozen packs and VNEXT AUDIT.

No live LLM. No pack mutation. Exit 0 iff canonical FAIL facts match.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = ROOT / "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147"
PACK = ROOT / "datasets/frozen/vnext_confirm_v1/dataset.jsonl"
MS = ROOT / "docs/paper/workshop_vnext_fail/MANUSCRIPT.md"
CLAIMS_MAP = ROOT / "docs/paper/workshop_vnext_fail/CLAIMS_MAP.md"
CHECKLIST = ROOT / "docs/paper/CLAIMS_CHECKLIST_LAYER_A.md"
PR_STACK = ROOT / "docs/paper/workshop_vnext_fail/PR_STACK.md"
RESEARCH_LOG = ROOT / "docs/experiments/RESEARCH_LOG.md"
REPRO = ROOT / "docs/experiments/REPRODUCIBILITY_PACKAGE.md"
CONFIGS_DOC = ROOT / "docs/paper/workshop_vnext_fail/CONFIGS_SNAPSHOT.md"
DONE = ROOT / "docs/paper/workshop_vnext_fail/DONE_CHECKLIST.md"
PACKET = ROOT / "docs/paper/workshop_vnext_fail/SUBMISSION_PACKET.md"
SUBMIT_FA = ROOT / "docs/paper/workshop_vnext_fail/SUBMIT_NEXT_FA.md"
RESULTS = ROOT / "docs/paper/04_results.md"
MODELS_YAML = ROOT / "configs/models.yaml"

MODELS_YAML_SHA = "3e7b33d8b1001f0f86abf74b4d8c1558751275835c10a69152f1f7b386cc58b4"

EXPECTED_SHA = "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518"
LAYER_A_TEST_SHA = "47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8"
LAYER_A_V3_SHA = "abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd"
LAYER_A_V2_SHA = "76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33"

CANONICAL = {
    "b0_asr": "0.9508",
    "vnext_asr": "0.8689",
    "b10": "b10 = 5",
    "b01": "b01 = 0",
    "p": "0.0625",
    "delta": "0.0820",
    "msid": "0.20",
    "utility": "0.9344",
    "false_blocks": "false blocks = 1",
    "s5": "s5_mcnemar_not_significant",
    "msid_fail": "msid_not_met",
    "s4": "s4_utility_ineligible",
    "insufficient": "insufficient_intervention` = 53",
    "target": "qwen/qwen-2.5-7b-instruct",
    "judge": "qwen/qwen-2.5-72b-instruct",
    "status_fail": "STATUS = FAIL",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    sha = sha256(PACK)
    if sha != EXPECTED_SHA:
        fail(f"confirmation pack sha {sha} != {EXPECTED_SHA}")

    conf = ROOT / "datasets/frozen/vnext_confirm_v1/confirmation.jsonl"
    if sha256(conf) != EXPECTED_SHA:
        fail("confirmation.jsonl is not byte-identical in digest to dataset.jsonl")

    la_test = ROOT / "datasets/frozen/layer_a_v3/test_split.jsonl"
    if sha256(la_test) != LAYER_A_TEST_SHA:
        fail("Layer A TEST hash mismatch (frozen pack must not be modified)")
    if sha256(ROOT / "datasets/frozen/layer_a_v3/dataset.jsonl") != LAYER_A_V3_SHA:
        fail("Layer A v3 pack hash mismatch")
    if sha256(ROOT / "datasets/frozen/layer_a_v2/dataset.jsonl") != LAYER_A_V2_SHA:
        fail("Layer A v2 pack hash mismatch")

    verdict = json.loads((AUDIT_DIR / "verdict.json").read_text())
    if verdict.get("status") != "FAIL":
        fail(f"verdict.status={verdict.get('status')}")
    if verdict.get("qualified_win") is not False:
        fail("qualified_win must be false")
    reasons = verdict.get("fail_reasons") or []
    for key in ("s5_mcnemar_not_significant", "msid_not_met", "s4_utility_ineligible"):
        if key not in reasons:
            fail(f"missing fail reason {key}")
    if verdict.get("p_value") != 0.0625:
        fail(f"p_value={verdict.get('p_value')}")
    if verdict.get("b10") != 5 or verdict.get("b01") != 0:
        fail(f"b10/b01={verdict.get('b10')}/{verdict.get('b01')}")
    delta = float(verdict["delta_hat"])
    if abs(delta - 0.0820) > 5e-4:
        fail(f"delta_hat={delta}")
    if float(verdict["msid"]) != 0.2:
        fail(f"msid={verdict.get('msid')}")
    u = float(verdict["utility"])
    if abs(u - 0.9344) > 5e-4:
        fail(f"utility={u}")
    if verdict.get("hash", {}).get("sha256") != EXPECTED_SHA:
        fail("verdict hash sha256 mismatch")

    comparison = json.loads((AUDIT_DIR / "comparison.json").read_text())
    b0 = comparison["b0"]
    tr = comparison["VNEXT-ADAPT"]
    if abs(b0["asr"] - 0.9508) > 5e-4 or b0["n_attack_success"] != 58:
        fail("B0 ASR/count mismatch")
    if abs(tr["asr"] - 0.8689) > 5e-4 or tr["n_attack_success"] != 53:
        fail("VNEXT ASR/count mismatch")
    tax = tr["taxonomy_counts"]
    if tax.get("correct_block") != 5:
        fail("correct_block != 5")
    if tax.get("insufficient_intervention") != 53:
        fail("insufficient_intervention != 53")
    if tax.get("false_block") != 1:
        fail("false_block != 1")
    if comparison["confirmatory"]["b10_taxonomy"].get("correct_block") != 5:
        fail("b10 taxonomy is not 5 correct_block")
    if comparison["target_model"] == comparison["judge_model"]:
        fail("target must differ from judge")
    if comparison["target_model"] != "qwen/qwen-2.5-7b-instruct":
        fail("unexpected target")
    if comparison["judge_model"] != "qwen/qwen-2.5-72b-instruct":
        fail("unexpected judge")
    if comparison["cache_enabled"] is not False:
        fail("cache must be off")
    spend = float(comparison["spend"]["estimated_usd_total"])
    if abs(spend - 0.059016) > 1e-6:
        fail(f"spend={spend}")
    if b0["n_target_cache_hits"] != 0 or tr["n_target_cache_hits"] != 0:
        fail("cache hits must be 0")

    text = MS.read_text()
    for label, needle in CANONICAL.items():
        if needle not in text:
            fail(f"manuscript missing {label}: {needle!r}")

    # Layer A checklist sentences that must remain exact.
    layer_a_needles = [
        "detector v4 attack recall is 27/40 = 0.675 and AUROC is 0.705, versus v3 recall 2/40 = 0.05 and AUROC 0.368, without TEST retuning",
        "Adaptive B3_V4 has ASR 0.625 and utility 0.85 versus B0 ASR 0.75 and utility 1.00; exact McNemar p = 0.125. This is not a demonstrated ASR reduction.",
        "only one is a true A3 block; the other five are target refusals under A1 and are not defense wins",
    ]
    for needle in layer_a_needles:
        if needle not in text:
            fail(f"manuscript missing Layer A allowed sentence fragment: {needle[:60]}…")

    forbidden_positive = [
        r"is a working, production-ready",
        r"state-of-the-art cost-aware",
        r"B3_V4 beats B0",
        r"qualified win: \*\*YES\*\*",
        r"STATUS: \*\*PASS\*\*",
    ]
    for pat in forbidden_positive:
        if re.search(pat, text, flags=re.I):
            fail(f"forbidden positive claim matched {pat}")

    sim = RESULTS.read_text()
    if "fixed_l0" not in sim or "full_adaptive" not in sim:
        fail("04_results.md simulation body missing expected rows")
    if "0.027" not in sim:
        fail("04_results.md simulation ASR 0.027 missing (body rewritten?)")
    if "workshop_vnext_fail/README.md" not in sim:
        fail("04_results.md missing VNEXT FAIL pointer")

    n_lines = len(PACK.read_text().splitlines())
    if n_lines != 122:
        fail(f"pack rows={n_lines}")

    # Wilson CIs in the manuscript table (rounded to 3 decimals from comparison.json).
    asr_lo = b0["asr_wilson"]["lower"]
    asr_hi = b0["asr_wilson"]["upper"]
    if f"[{asr_lo:.3f}, {asr_hi:.3f}]" not in text:
        fail("manuscript B0 ASR Wilson interval mismatch")
    tr_lo = tr["asr_wilson"]["lower"]
    tr_hi = tr["asr_wilson"]["upper"]
    if f"[{tr_lo:.3f}, {tr_hi:.3f}]" not in text:
        fail("manuscript VNEXT ASR Wilson interval mismatch")

    if sha256(MODELS_YAML) != MODELS_YAML_SHA:
        fail("configs/models.yaml hash mismatch vs CONFIGS_SNAPSHOT")
    models_txt = MODELS_YAML.read_text()
    if not re.search(r"cache:\s*\n\s*enabled:\s*false", models_txt):
        fail("configs/models.yaml cache.enabled is not false")
    if "qwen/qwen-2.5-7b-instruct" not in models_txt or "qwen/qwen-2.5-72b-instruct" not in models_txt:
        fail("configs/models.yaml missing Target/Judge model ids")

    claims = CLAIMS_MAP.read_text()
    checklist = CHECKLIST.read_text()
    log = RESEARCH_LOG.read_text()
    stack = PR_STACK.read_text()
    repro = REPRO.read_text()
    configs_doc = CONFIGS_DOC.read_text()
    done = DONE.read_text()
    packet = PACKET.read_text()
    submit_fa = SUBMIT_FA.read_text()

    for label, needle in (
        ("claims_b0", "0.9508"),
        ("claims_vnext", "0.8689"),
        ("claims_p", "0.0625"),
        ("claims_delta", "0.0820"),
        ("claims_u", "0.9344"),
        ("claims_s5", "s5_mcnemar_not_significant"),
        ("claims_msid", "msid_not_met"),
        ("claims_s4", "s4_utility_ineligible"),
        ("claims_sha", EXPECTED_SHA),
        ("claims_no_win", "Qualified win (H1) is **NO**"),
        ("claims_forbidden", "VNEXT FORBIDDEN"),
        ("claims_partial", "labeling this FAIL as PARTIAL"),
    ):
        if needle not in claims:
            fail(f"CLAIMS_MAP missing {label}: {needle!r}")

    if "CLOSED diagnostic" not in checklist:
        fail("CLAIMS_CHECKLIST missing CLOSED diagnostic banner")
    if "FAIL" not in checklist or "qualified win = NO" not in checklist:
        fail("CLAIMS_CHECKLIST missing VNEXT FAIL / qualified-win-NO banner")
    if "trend toward a win" not in checklist:
        fail("CLAIMS_CHECKLIST missing forbidden trend-toward-a-win item")
    for needle in layer_a_needles:
        if needle not in checklist:
            fail(f"CLAIMS_CHECKLIST missing allowed sentence: {needle[:60]}…")

    for path, blob in (
        (CLAIMS_MAP, claims),
        (CHECKLIST, checklist),
        (MS, text),
        (RESEARCH_LOG, log),
        (PR_STACK, stack),
        (DONE, done),
        (PACKET, packet),
        (SUBMIT_FA, submit_fa),
    ):
        if re.search(r"qualified win: \*\*YES\*\*", blob, flags=re.I):
            fail(f"win language in {path.relative_to(ROOT)}")
        if re.search(r"STATUS:\s*\*\*PASS\*\*", blob, flags=re.I):
            fail(f"STATUS PASS language in {path.relative_to(ROOT)}")

    if "2026-09-14" not in log:
        fail("RESEARCH_LOG missing 2026-09-14")
    for needle in (
        "Layer A remains a **CLOSED diagnostic**",
        "Phase 1",
        "Phase 2",
        "Phase 3a",
        "vnext_confirm_v1.0",
        "STATUS = FAIL",
        "PR",
        "#32",
        "manuscript",
        "SUBMISSION_PACKET.md",
        "SUBMIT_NEXT_FA.md",
    ):
        if needle not in log:
            fail(f"RESEARCH_LOG missing {needle!r}")

    for n in range(23, 35):
        if f"[{n}](" not in stack:
            fail(f"PR_STACK missing PR {n}")
    for role in ("`docs`", "`harness`", "`pack`", "`live`", "`manuscript`", "`packet`"):
        if role not in stack:
            fail(f"PR_STACK missing role {role}")
    if "Do not merge from this file" not in stack and "**Do not merge" not in stack:
        fail("PR_STACK missing do-not-merge instruction")

    if "How to reproduce offline checks" not in repro:
        fail("REPRODUCIBILITY_PACKAGE missing offline-checks section")
    if MODELS_YAML_SHA not in repro or MODELS_YAML_SHA not in configs_doc:
        fail("models.yaml SHA missing from repro/config snapshot docs")
    if "PR index" not in repro:
        fail("REPRODUCIBILITY_PACKAGE missing PR index")

    if "YES" not in done or "Verify manuscript facts" not in done:
        fail("DONE_CHECKLIST missing agent items")
    if "SUBMISSION_PACKET.md" not in done:
        fail("DONE_CHECKLIST missing submission packet item")

    for label, needle in (
        ("packet_framing", "HONEST NEGATIVE RESULT"),
        ("packet_fail", "STATUS = FAIL"),
        ("packet_b0", "0.9508"),
        ("packet_vnext", "0.8689"),
        ("packet_p", "0.0625"),
        ("packet_delta", "0.0820"),
        ("packet_u", "0.9344"),
        ("packet_s5", "s5_mcnemar_not_significant"),
        ("packet_msid", "msid_not_met"),
        ("packet_s4", "s4_utility_ineligible"),
        ("packet_sha", EXPECTED_SHA),
        ("packet_audit", "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md"),
        ("packet_cover", "To: Workshop chairs / Evaluation-track program committee"),
        ("packet_camera", "Camera-ready checklist"),
        ("packet_titles", "Suggested title options"),
        ("packet_forbidden", "What NOT to claim"),
        ("packet_vnext_forbidden", "VNEXT-ADAPT works / beats B0"),
        ("packet_artifacts", "Artifact URLs / paths for reviewers"),
        ("packet_merge", "Merge-order reminder"),
        ("packet_no_merge", "Do not merge from this file"),
        ("packet_not_confirmed", "not confirmed"),
    ):
        if needle not in packet:
            fail(f"SUBMISSION_PACKET missing {label}: {needle!r}")

    if re.search(r"</?[A-Za-z][^>]*>", submit_fa):
        fail("SUBMIT_NEXT_FA.md must not contain HTML tags")
    for label, needle in (
        ("fa_merge", "مرج"),
        ("fa_venue", "ونیو"),
        ("fa_submit", "سابمیت"),
        ("fa_fail", "FAIL"),
        ("fa_no_agent_merge", "عامل هوش مصنوعی مرج نمی‌کند"),
        ("fa_pr_stack", "PR_STACK.md"),
        ("fa_packet", "SUBMISSION_PACKET.md"),
        ("fa_audit", "20260914-133147"),
    ):
        if needle not in submit_fa:
            fail(f"SUBMIT_NEXT_FA missing {label}: {needle!r}")

    print("PASS: manuscript facts match frozen packs and VNEXT AUDIT FAIL record.")
    print(f"  pack_sha={sha}")
    print("  status=FAIL qualified_win=false")
    print("  b10=5 b01=0 p=0.0625 delta=0.0820 U=0.9344")
    print("  fail_reasons=s5_mcnemar_not_significant,msid_not_met,s4_utility_ineligible")
    print("  claims_map=FAIL-consistent checklist=CLOSED+FAIL pr_stack=23-34 research_log=2026-09-14")
    print("  submission_packet=HONEST NEGATIVE RESULT submit_next_fa=no-html")


if __name__ == "__main__":
    main()
