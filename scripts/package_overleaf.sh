#!/usr/bin/env bash
# Build the Overleaf/arXiv zip from docs/paper/negative_result/arxiv (run build_arxiv_latex.py first); builds main.pdf (15 pages) and supplement.pdf.
# Compiles in a scratch directory, keeps the generated main.bbl in the package, and re-compiles from the unzipped package alone.
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)/docs/paper/negative_result/arxiv"
OUTZIP="${1:-/mnt/project-files/arxiv/adapti-guard-negative-result-overleaf.zip}"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
mkdir -p "$W/pkg" "$(dirname "$OUTZIP")"
cp -r "$SRC/main.tex" "$SRC/supplement.tex" "$SRC/references.bib" "$SRC/arxivid.bst" "$SRC/tables" "$SRC/figures" "$SRC/README.md" "$W/pkg/"
cp "$SRC/OWNER_DECISIONS.md" "$SRC/ARXIV_METADATA.md" "$W/pkg/"
build() { (cd "$1" && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && bibtex main >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null \
  && pdflatex -interaction=nonstopmode -halt-on-error supplement.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error supplement.tex >/dev/null); }
build "$W/pkg"
cp "$W/pkg/main.bbl" "$SRC/main.bbl"
(cd "$W/pkg" && rm -f main.aux main.log main.out main.blg main.pdf supplement.aux supplement.log supplement.out supplement.pdf && zip -qr "$OUTZIP" . -x '*.pdf')
# clean-directory check from the zip alone
mkdir "$W/clean" && unzip -q "$OUTZIP" -d "$W/clean"
build "$W/clean"
grep -E 'Undefined|undefined|Error' "$W/clean/main.log" "$W/clean/supplement.log" && { echo "log problems"; exit 1; } || true
cp "$W/clean/main.pdf" "${OUTZIP%.zip}-main.pdf"
cp "$W/clean/supplement.pdf" "${OUTZIP%.zip}-supplement.pdf"
unzip -l "$OUTZIP"
for f in main supplement; do echo "$f: $(pdfinfo "$W/clean/$f.pdf" | grep Pages)"; done
