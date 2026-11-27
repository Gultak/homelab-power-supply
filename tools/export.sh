#!/bin/bash
# Export everything after a board change.
# usage: tools/export.sh
# Run from anywhere; works on rack-power-board.kicad_pcb at the repo root (KiCad 9 kicad-cli).
# Writes: docs/top.png, docs/bottom.png, docs/assembly-top.pdf, rack-power-board-gerbers.zip.
# The work is done by the shared script in the agent-tools submodule (pcbtools/export.sh).
set -e
cd "$(dirname "$0")/.."
exec tools/agent-tools/pcbtools/export.sh rack-power-board.kicad_pcb docs rack-power-board-gerbers.zip
