import pcbnew, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
f = os.path.join(HERE, "rack-power-board.kicad_pcb")
b=pcbnew.LoadBoard(f)
b.BuildConnectivity()
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.BuildConnectivity()
pcbnew.SaveBoard(f,b)
pcbnew.WriteDRCReport(b,os.path.join(HERE, "docs", "drc-report.txt"),pcbnew.EDA_UNITS_MILLIMETRES,True)
print(open(os.path.join(HERE, "docs", "drc-report.txt")).read()[:200])
