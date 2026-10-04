"""Build the double-blind TMLR manuscript from the public manuscript and audit it for identity-bearing text.

Mechanical anonymization only: it changes no number, claim, method or conclusion, and leaves the public manuscript and the arXiv build alone.
Replacements: the project name, the package path, commit hashes (stable labels [commit C1]...), tag names. SHA-256 file hashes (written with an
ellipsis) are not commit identifiers and stay. It does not create an anonymous repository or dataset. The audit fails the build if an
identity-bearing pattern remains.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
N = ROOT / "docs/paper/negative_result"
SRC = N / "MANUSCRIPT_DRAFT_v1.md"
OUT = N / "tmlr_blind/MANUSCRIPT_TMLR_BLIND.md"
COMMIT = re.compile(r"`([0-9a-f]{7,40})`")
NOTE = (" In this double-blind version, repository locations, tag names and commit identifiers are withheld: commits appear as labels "
        "[commit C1] to [commit C{n}], and the project and package names are replaced by generic wording.")
FORBIDDEN = {"owner_or_author_name": r"mohammad|shirazi|matin|manzour", "project_name": r"adapti[-_ ]?guard", "repo_host": r"github\.com|githubusercontent|@gmail|mrshirazi",
             "branch_or_tag": r"claude/[a-z0-9]|cursor/[a-z0-9]|case-study-v1|historical-packages|backup/tier", "personal_path": r"/home/[a-z]+|/users/[a-z]+",
             "email": r"[\w.+-]+@[\w-]+\.[\w.]+", "bare_commit_hash": r"(?<![0-9a-f…])(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![0-9a-f…])"}


def blind(md: str) -> tuple[str, dict]:
    labels: dict[str, str] = {}

    def lab(h: str) -> str:
        """Stable label per commit; a short hash and a longer one with the same prefix are the same commit."""
        for k in list(labels):
            if k.startswith(h) or h.startswith(k):
                if len(h) > len(k):
                    labels[h] = labels.pop(k)
                    return labels[h]
                return labels[k]
        labels[h] = f"C{len(labels) + 1}"
        return labels[h]

    out = COMMIT.sub(lambda m: f"[commit {lab(m.group(1))}]", md)
    out = out.replace("(AdaptiGuard)", "(the testbed)").replace("ADAPTI-GUARD addresses", "Our work addresses")
    out = out.replace("ADAPTI-GUARD's six checks", "our six checks").replace("while ADAPTI-GUARD's checks", "while our checks").replace("ADAPTI-GUARD", "our work")
    out = out.replace("src/adapti_guard/", "src/<package>/").replace("`case-study-v1`", "[tag withheld]").replace("case-study-v1", "[tag withheld]")
    key = "Unless a row says otherwise the artifact is in the repository."
    assert key in out
    out = out.replace(key, key + NOTE.format(n=len(labels)), 1)
    return out, labels


def audit(text: str) -> dict:
    hits = {}
    for name, rx in FORBIDDEN.items():
        found = [m.group(0) for m in re.finditer(rx, text, re.I)]
        if found:
            hits[name] = sorted(set(found))[:8]
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--map-out", type=Path, help="write the label->hash map here (private; do not commit or submit it)")
    a = ap.parse_args(argv)
    out, labels = blind(SRC.read_text())
    hits = audit(out)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(out)
    if a.map_out:
        a.map_out.write_text(json.dumps({v: k for k, v in labels.items()}, indent=1) + "\n")
    print(json.dumps({"out": str(a.out), "commit_labels": len(labels), "audit_hits": hits}, indent=1))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
