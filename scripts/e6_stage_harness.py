"""Stage the sanitized E6 harness tree from an archived commit into a SCRATCH directory (never pushes, tags or commits).

Files: the audited import closure listed in section 3 of HARNESS_RELEASE_PROVENANCE_MAP_DRAFT.md (read from the archived commit with
`git show`, so history is not rewritten) plus the E6 tooling from the working tree. Private approval documents, templates, key and
usage snapshots, pilot artifacts and `configs/datasets.yaml` are never copied. Every staged file is scanned for personal paths, owner
names and key labels; findings are reported and `--strict` makes them fatal. A `SANITIZED_MANIFEST.json` lists file hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs/paper/negative_result/HARNESS_RELEASE_PROVENANCE_MAP_DRAFT.md"
ARCHIVE_COMMIT = "1ae0fb4dd96129dcbf21ce0bad8646f5411b75b7"
E6_EXTRA = ["requirements-core.txt", "LICENSE", "scripts/e6_analysis.py", "scripts/e6_manifest.py", "scripts/e6_render.py", "scripts/e6_replay.py", "scripts/e6_run_plan.py",
            "scripts/e6_launcher.py", "scripts/e6_protocol_simulation.py", "scripts/e6_stage_harness.py",
            "tests/test_e6_analysis.py", "tests/test_e6_prefreeze.py", "tests/test_e6_end_to_end.py",
            "docs/paper/negative_result/PROTOCOL_CONFIRMATORY_E6_DRAFT.md", "docs/research/artifacts/e6_protocol_simulation_20261004.json",
            "e6/README.md", "e6/AUTHORING_GUIDE.md", "e6/authoring_schema_v1.json", "e6/authoring_template_v1.json",
            "e6/harness_constants.json", "e6/INPUTS_STATUS.json"]
# Archived harness regression tests that read the payload-bearing E3 template files by fixed path (found empirically: they fail in a tree
# without the templates). Not staged by default; `--with-templates` stages them together with the two template files (owner decision).
TEMPLATE_DEPENDENT_TESTS = tuple("tests/" + n + ".py" for n in (
    "test_harness_v2_amendment7c", "test_harness_v2_amendment8_cancelled_timeout", "test_harness_v2_amendment8_combined_integration",
    "test_harness_v2_amendment8_delayed_inject", "test_harness_v2_amendment8_http_cap_mid_429", "test_harness_v2_amendment8_http_cap_remaining_invalid",
    "test_harness_v2_amendment8_http_cap_tool_round_cut", "test_harness_v2_amendment8_incomplete_response_matrix", "test_harness_v2_amendment8_provider_error",
    "test_harness_v2_amendment8_usd_cap_mid_episode", "test_harness_v2_amendment8_wired_integration", "test_harness_v2_amendment9_final", "test_harness_v2_amendment9_lastpatch",
    "test_harness_v2_amendment9_pilot_label", "test_harness_v2_amendment9_request_snapshot", "test_harness_v2_amendment9_round4",
    "test_harness_v2_amendment9_round5", "test_harness_v2_amendment9_smoke_cli", "test_harness_v2_amendment9_wire_main_local_server",
    "test_harness_v2_exploratory_arms", "test_harness_v2_smoke_scripts_family_kw"))
TEMPLATE_FILES = ("experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES.json", "experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES_INDEPENDENT_V2.json")
FORBIDDEN_ANY = re.compile(r"(local_private|datasets\.yaml|APPROVAL_RECORD|(^|/)\.env)", re.I)
FORBIDDEN_DOC = re.compile(r"(AMENDMENT|PREREG|PILOT\d*_CRITERIA|usage|limit_snapshot|aborted|SCENARIO_INSTANCE_TEMPLATES)", re.I)  # non-code files only


def forbidden_path(rel: str) -> bool:
    return bool(FORBIDDEN_ANY.search(rel)) or (not rel.endswith(".py") and bool(FORBIDDEN_DOC.search(rel)))
FORBIDDEN_TEXT = {"personal_path": re.compile(r"/home/(?!user\b)[A-Za-z0-9_.-]+|/Users/[A-Za-z0-9_.-]+"), "owner_name": re.compile(r"Mohammad|Shirazi", re.I),
                  "key_label": re.compile(r"sk-or-v1-[0-9a-fA-F]{3,}(\.\.\.|…)|sk-or-v1-[0-9a-f]{20,}")}


def archived_closure(map_path: Path = MAP) -> list[str]:
    sec = re.search(r"^## 3\..*?```\n(.*?)```", map_path.read_text(), re.S | re.M).group(1)
    return [l.strip() for l in sec.splitlines() if l.strip()]


def git_show(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{commit}:{path}"])


def scan(rel: str, data: bytes) -> list[dict]:
    out = [{"file": rel, "kind": "forbidden_path"}] if forbidden_path(rel) and rel not in TEMPLATE_FILES else []
    if rel == "scripts/e6_stage_harness.py":
        return out  # the scanner necessarily contains its own patterns
    text = data.decode("utf-8", "replace")
    for kind, rx in FORBIDDEN_TEXT.items():
        for m in rx.finditer(text):
            out.append({"file": rel, "kind": kind, "line": text.count("\n", 0, m.start()) + 1, "match": m.group(0)[:40]})
    return out


def init_git(out: Path) -> dict:
    """Local scratch commit of the staged tree (the runner resolves HEAD and tree ids). Never pushed; fixed identity and dates."""
    env = {"GIT_AUTHOR_NAME": "e6-stage", "GIT_AUTHOR_EMAIL": "e6-stage@example.invalid", "GIT_COMMITTER_NAME": "e6-stage",
           "GIT_COMMITTER_EMAIL": "e6-stage@example.invalid", "GIT_AUTHOR_DATE": "2026-10-04T00:00:00Z", "GIT_COMMITTER_DATE": "2026-10-04T00:00:00Z",
           "PATH": __import__("os").environ["PATH"], "HOME": str(out)}
    run = lambda *a: subprocess.check_output(["git", "-C", str(out), *a], env=env, text=True).strip()
    run("init", "-q")
    run("add", "-A")
    run("commit", "-q", "-m", "staged sanitized E6 harness (local scratch commit)")
    return {"scratch_commit": run("rev-parse", "HEAD"), "tree_oid": run("rev-parse", "HEAD^{tree}")}


def stage(out: Path, commit: str = ARCHIVE_COMMIT, exclude: tuple[str, ...] = (), git: bool = False, with_templates: bool = False) -> dict:
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing to stage into a non-empty directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    (out / ".gitignore").write_text("__pycache__/\n*.pyc\n.pytest_cache/\nruns/\n*.log\n")
    files, findings, skipped = {}, [], []
    plan = [("archive", p) for p in archived_closure()] + [("worktree", p) for p in E6_EXTRA]
    if with_templates:
        plan += [("archive", p) for p in TEMPLATE_FILES]
    for src, rel in plan:
        if rel in TEMPLATE_DEPENDENT_TESTS and not with_templates:
            skipped.append({"file": rel, "reason": "needs the payload-bearing E3 template files (owner decision: --with-templates)"})
            continue
        if rel in TEMPLATE_FILES:
            pass  # explicitly requested; exempt from the forbidden-path rule below
        elif rel in exclude:
            skipped.append({"file": rel, "reason": "excluded by option"})
            continue
        elif forbidden_path(rel) and rel not in E6_EXTRA:
            skipped.append({"file": rel, "reason": "forbidden path"})
            continue
        try:
            data = git_show(commit, rel) if src == "archive" else (ROOT / rel).read_bytes()
        except (subprocess.CalledProcessError, FileNotFoundError):
            skipped.append({"file": rel, "reason": "not found in " + src})
            continue
        hits = scan(rel, data)
        findings += hits
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        files[rel] = hashlib.sha256(data).hexdigest()
    tree = hashlib.sha256("\n".join(f"{k}:{v}" for k, v in sorted(files.items())).encode()).hexdigest()
    manifest = {"source_commit": commit, "files": files, "tree_sha256": tree, "skipped": skipped, "findings": findings,
                "not_published": "staged in a scratch directory only; nothing pushed, tagged or released"}
    (out / "SANITIZED_MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    if git:
        manifest["git"] = init_git(out)
    return manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--commit", default=ARCHIVE_COMMIT)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--with-templates", action="store_true", help="also stage the two payload-bearing E3 template files and the tests that need them (owner decision)")
    ap.add_argument("--git", action="store_true", help="make a local scratch commit in the staged tree (needed by the runner; never pushed)")
    a = ap.parse_args(argv)
    m = stage(a.out, a.commit, tuple(a.exclude), a.git, a.with_templates)
    print(json.dumps({"files": len(m["files"]), "tree_sha256": m["tree_sha256"], "skipped": m["skipped"], "findings": m["findings"], "git": m.get("git")}, indent=1))
    return 1 if (a.strict and m["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
