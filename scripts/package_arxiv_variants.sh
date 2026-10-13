#!/usr/bin/env bash
# Build the two arXiv source zips (single-column and two-column) with main.bbl, then re-compile each from its unpacked
# files alone (arXiv does not run BibTeX). Run scripts/build_arxiv_latex.py first. Usage: package_arxiv_variants.sh OUTDIR TAG
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)/docs/paper/negative_result/arxiv"
OUT="${1:-/mnt/project-files/arxiv}"; TAG="${2:-REV}"
mkdir -p "$OUT"
for v in submission:singlecolumn twocolumn:twocolumn; do
  d="${v%%:*}"; n="${v##*:}"; W="$(mktemp -d)"; cp -r "$SRC/$d/." "$W/"
  (cd "$W" && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && bibtex main >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null)
  cp "$W/main.bbl" "$SRC/$d/main.bbl"
  Z="$OUT/adapti-guard-$TAG-arxiv-source-$n.zip"; rm -f "$Z"
  (cd "$W" && if [ "$d" = twocolumn ]; then zip -qr "$Z" main.tex main.bbl references.bib arxivid.bst tables figures; else zip -qr "$Z" main.tex main.bbl tables figures; fi)
  C="$(mktemp -d)"; unzip -q "$Z" -d "$C"
  (cd "$C" && for i in 1 2 3; do pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null; done)
  if grep -qE 'undefined|Undefined|\?\?' "$C/main.log"; then echo "$n: log problems"; exit 1; fi
  cp "$C/main.pdf" "$OUT/adapti-guard-$TAG-arxiv-$n-full.pdf"
  echo "$n: $(pdfinfo "$C/main.pdf" | grep Pages) bibitems=$(grep -c '\\bibitem' "$C/main.bbl") max-overfull=$(grep Overfull "$C/main.log" | sed 's/.*(\(.*\)pt.*/\1/' | sort -n | tail -1)pt"
done
