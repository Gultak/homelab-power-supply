"""Fill zones and run DRC on rack-power-board.kicad_pcb -> docs/drc-report.txt (shared tool: agent-tools/pcbtools/post.py)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools", "agent-tools"))   # git submodule Gultak/agent-tools
from pcbtools.post import post
print(post(os.path.join(HERE, "rack-power-board.kicad_pcb"), os.path.join(HERE, "docs", "drc-report.txt"))[:200])
