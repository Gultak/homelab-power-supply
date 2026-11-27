#!/bin/bash
# Export everything after a board change.
# usage: tools/export.sh
# Run from anywhere; works on rack-power-board.kicad_pcb at the repo root (KiCad 9 kicad-cli).
# Writes: docs/top.png, docs/bottom.png, docs/assembly-top.pdf, rack-power-board-gerbers.zip.
set -e
cd "$(dirname "$0")/.."
N=rack-power-board; PCB="$N.kicad_pcb"; T=$(mktemp -d)
python3 tools/render.py "$PCB" "$T"
cp "$T/top.png" docs/top.png; cp "$T/bottom.png" docs/bottom.png
mkdir -p "$T/g"
kicad-cli pcb export gerbers -o "$T/g/" --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,Edge.Cuts --subtract-soldermask "$PCB" >/dev/null
kicad-cli pcb export drill -o "$T/g/" --format excellon --excellon-separate-th "$PCB" >/dev/null
rm -f "$N-gerbers.zip"; (cd "$T/g" && zip -q -r - .) > "$N-gerbers.zip"
kicad-cli pcb export pdf -o docs/assembly-top.pdf --layers F.Cu,F.Silkscreen,F.Fab,Edge.Cuts "$PCB" >/dev/null
rm -rf "$T"
echo "done: docs/top.png docs/bottom.png docs/assembly-top.pdf $N-gerbers.zip"
