#!/bin/bash
# Export everything after a board change.
# usage: tools/export.sh <render-revision>     e.g. tools/export.sh r8
# Run from anywhere; works on rack-power-board.kicad_pcb at the repo root.
# Writes: docs/top-<rev>.png, docs/bottom-<rev>.png, docs/assembly-top.pdf,
#         rack-power-board-gerbers.zip. Update the image names in README.md yourself
#         and delete the old docs/*-rN.png files (GitHub caches images by file name).
set -e
REV="${1:?usage: tools/export.sh rN}"
cd "$(dirname "$0")/.."
N=rack-power-board; PCB="$N.kicad_pcb"; T=$(mktemp -d)
python3 tools/render.py "$PCB" "$T"
cp "$T/top.png" "docs/top-$REV.png"; cp "$T/bottom.png" "docs/bottom-$REV.png"
mkdir -p "$T/g"
kicad-cli pcb export gerbers -o "$T/g/" --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,Edge.Cuts --subtract-soldermask "$PCB" >/dev/null
kicad-cli pcb export drill -o "$T/g/" --format excellon --excellon-separate-th "$PCB" >/dev/null
rm -f "$N-gerbers.zip"; (cd "$T/g" && zip -q -r - .) > "$N-gerbers.zip"
kicad-cli pcb export pdf -o docs/assembly-top.pdf --layers F.Cu,F.Silkscreen,F.Fab,Edge.Cuts "$PCB" >/dev/null
rm -rf "$T"
echo "done: docs/top-$REV.png docs/bottom-$REV.png docs/assembly-top.pdf $N-gerbers.zip"
