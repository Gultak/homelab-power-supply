#!/usr/bin/env python3
"""Generate rack-power-board-v2.kicad_pcb (KiCad 7): 12V and 54V from separate PSUs -> 4x fused 12V + 5V (Pololu), plus fused 54V passthrough."""
import pcbnew
from pcbnew import VECTOR2I, FromMM as MM

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rack-power-board-v2.kicad_pcb")
LIB = "/usr/share/kicad/footprints/"
OX, OY = 30.0, 30.0          # sheet offset
W, H = 83.2, 80.0           # board size (mm): v1 width minus 2"

b = pcbnew.BOARD()
b.SetCopperLayerCount(2)
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = MM(0.25)
ds.m_MinClearance = MM(0.3)
ds.m_CopperEdgeClearance = MM(0.5)

def P(x, y):
    return VECTOR2I(MM(OX + x), MM(OY + y))

# ---------- nets ----------
nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(b, name)
        b.Add(n)
        nets[name] = n
    return nets[name]

# netclasses: power default wide
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(MM(0.3))
nc.SetTrackWidth(MM(0.5))

# ---------- outline ----------
def seg(layer, a, c, w=0.15):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(a); s.SetEnd(c); s.SetLayer(layer); s.SetWidth(MM(w))
    b.Add(s)

corners = [(0, 0), (W, 0), (W, H), (0, H)]
for i in range(4):
    seg(pcbnew.Edge_Cuts, P(*corners[i]), P(*corners[(i + 1) % 4]), 0.1)

# ---------- footprints ----------
def place(lib, name, ref, x, y, rot=0, val="", layer_back=False):
    m = pcbnew.FootprintLoad(LIB + lib + ".pretty", name)
    assert m is not None, name
    m.SetReference(ref)
    m.SetValue(val or name)
    b.Add(m)
    m.SetPosition(P(x, y))
    if rot:
        m.SetOrientationDegrees(rot)
    if layer_back:
        m.Flip(m.GetPosition(), False)
    return m

def pads(m, num):
    return [p for p in m.Pads() if p.GetNumber() == str(num)]

def setnet(m, num, name):
    for p in pads(m, num):
        p.SetNet(net(name))

def padpos(m, num, idx=0):
    p = pads(m, num)[idx].GetPosition()
    return (pcbnew.ToMM(p.x) - OX, pcbnew.ToMM(p.y) - OY)

def track(pts, netname, w, layer=pcbnew.F_Cu):
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(P(*a)); t.SetEnd(P(*c))
        t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(net(netname))
        b.Add(t)

def via(x, y, netname, d=0.8, dr=0.4):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(P(x, y)); v.SetWidth(MM(d)); v.SetDrill(MM(dr))
    v.SetNet(net(netname)); b.Add(v)

def stitch(x, y, netname, n=3, step=1.4, horiz=True):
    for i in range(n):
        via(x + (i * step if horiz else 0), y + (0 if horiz else i * step), netname)

def text(s, x, y, size=1.2, layer=pcbnew.F_SilkS, rot=0, bold=False):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(MM(size), MM(size))); t.SetTextThickness(MM(size * (0.2 if bold else 0.15)))
    if rot: t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS: t.SetMirrored(True)
    b.Add(t)

def custom_fp(ref, value, padlist, outline=None, silk_label=None, crtyd=True):
    """padlist: (num, x, y, pad_d, drill_d)"""
    m = pcbnew.FOOTPRINT(b)
    m.SetReference(ref); m.SetValue(value)
    m.SetFPID(pcbnew.LIB_ID("rack_power", value))
    b.Add(m)
    for num, x, y, pd, dr in padlist:
        p = pcbnew.PAD(m)
        p.SetNumber(str(num))
        p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetLayerSet(p.PTHMask())
        p.SetSize(VECTOR2I(MM(pd), MM(pd)))
        p.SetDrillSize(VECTOR2I(MM(dr), MM(dr)))
        m.Add(p)
        p.SetPos0(P(x, y))
        p.SetPosition(P(x, y))
    if outline:
        (x0, y0, x1, y1) = outline
        for lay, w in ((pcbnew.F_Fab, 0.1), (pcbnew.F_SilkS, 0.15)) + (((pcbnew.F_CrtYd, 0.05),) if crtyd else ()):
            e = 0.25 if lay == pcbnew.F_CrtYd else 0
            pts = [(x0 - e, y0 - e), (x1 + e, y0 - e), (x1 + e, y1 + e), (x0 - e, y1 + e)]
            for i in range(4):
                s = pcbnew.FP_SHAPE(m)
                s.SetShape(pcbnew.SHAPE_T_SEGMENT)
                s.SetLayer(lay); s.SetWidth(MM(w))
                m.Add(s)
                s.SetStart0(P(*pts[i])); s.SetEnd0(P(*pts[(i + 1) % 4])); s.SetDrawCoord()
    m.Reference().SetPosition(P(*(silk_label or (padlist[0][1], padlist[0][2] - 3))))
    m.Value().SetVisible(False)
    return m


# ======================= PLACEMENT =======================
VH2 = ("Connector_JST", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical")
VH6 = ("Connector_JST", "JST_VH_B6P-VH_1x06_P3.96mm_Vertical")
HDR = ("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical")

# --- output row along the front edge (y = H), JST VH 2-pin.  Left to right: 5V, 54V x2, 12V x4.
#     C = connector centre; pin 1 = C - 1.98, pin 2 = C + 1.98
JY = H - 5.8
C = {"J8": 11.98, "J2": 21.0, "J3": 31.3, "J4": 40.5, "J5": 49.8, "J6": 59.1, "J7": 68.3}
JX = {k: v - 1.98 for k, v in C.items()}
JNET = {"J2": ("OUT54_1", "GND54"), "J3": ("OUT54_2", "GND54"),
        "J4": ("OUT12_1", "GND"), "J5": ("OUT12_2", "GND"), "J6": ("OUT12_3", "GND"),
        "J7": ("OUT12_4", "GND"), "J8": ("+5V", "GND")}
JSHORT = {"J2": "54V 1", "J3": "54V 2", "J4": "12V 1", "J5": "12V 2", "J6": "12V 3", "J7": "12V 4", "J8": "5V"}
JVAL = {"J2": "54V OUT1", "J3": "54V OUT2", "J4": "12V OUT1", "J5": "12V OUT2",
        "J6": "12V OUT3", "J7": "12V OUT4", "J8": "5V OUT"}
J = {}
for ref, x in JX.items():
    m = place(*VH2, ref, x, JY, 0, "JST B2P-VH")
    setnet(m, 1, JNET[ref][0]); setnet(m, 2, JNET[ref][1])
    m.Reference().SetVisible(False)
    J[ref] = m

# --- right edge: J1 54 V input (top) and J10 12 V input (below), JST VH 6-pin, pins 1-3 = +, 4-6 = -
RX = W - 5.8
J1Y, J10Y = 10.0, 35.0
J1 = place(*VH6, "J1", RX, J1Y, 270, "JST B6P-VH")
J10 = place(*VH6, "J10", RX, J10Y, 270, "JST B6P-VH")
for n in (1, 2, 3): setnet(J1, n, "+54V"); setnet(J10, n, "+12V")
for n in (4, 5, 6): setnet(J1, n, "GND54"); setnet(J10, n, "GND")
J1.Reference().SetVisible(False); J10.Reference().SetVisible(False)

# --- 54 V output fuses (5x20, vertical, centred over their connector)
Ft = 45.5
F = {}
for ref, jref in (("F2", "J2"), ("F3", "J3")):
    m = place("Fuse", "Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open", ref, C[jref], Ft, 270, "5x20 T 2.5A")
    setnet(m, 1, "+54V"); setnet(m, 2, JNET[jref][0])
    F[ref] = m

# --- 12 V output fuses (ATM mini blade, vertical, centred over their connector)
Fy = 56.5
for ref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", ref, C[jref] + 1.7, Fy, 270, "ATM 5A")
    setnet(m, 1, "+12V"); setnet(m, 2, JNET[jref][0])
    F[ref] = m
# Pololu feed fuse, top edge (pad 1 = 12 V from J10 on the bottom layer, pad 2 -> P1)
F8X, F8Y = 67.5, 9.5
m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", "F8", F8X, F8Y, 180, "ATM 5A")
setnet(m, 1, "+12V"); setnet(m, 2, "12V_PL"); F["F8"] = m

# --- 12 V bulk caps
C5 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C5", 74.5, 63.5, 0, "470uF 16V polymer")
C6 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C6", 42.5, 48.5, 0, "470uF 16V polymer")
for c in (C5, C6):
    setnet(c, 1, "+12V"); setnet(c, 2, "GND")

# --- Pololu D24V90F5 on M2 standoffs, horizontal, under the Molex
PX0, PY0 = 8.0, 13.5
pcx, pcy = PX0 + 20.3, PY0 + 10.15
for i, (dx, dy) in enumerate(((-17.78, -7.62), (17.78, -7.62), (-17.78, 7.62), (17.78, 7.62))):
    place("MountingHole", "MountingHole_2.2mm_M2", "H%d" % (5 + i), pcx + dx, pcy + dy, 0, "M2 standoff").Reference().SetVisible(False)
U2 = custom_fp("U2", "Pololu_D24V90F5_outline", [], outline=(PX0, PY0, PX0 + 40.6, PY0 + 20.3), silk_label=(pcx, pcy - 3), crtyd=False)
text("POLOLU D24V90F5", pcx, pcy, 1.2)
text("on M2 x10mm", pcx, pcy + 2, 0.9)
WP = 3.6; WD = 1.8
PADS = {"P1": (52.0, 19.0, "12V_PL", "VIN"), "P2": (52.0, 26.0, "GND", "GND"),
        "P3": (4.5, 19.0, "+5V", "VOUT"), "P4": (4.5, 26.0, "GND", "GND")}
for ref, (x, y, nm, lab) in PADS.items():
    p = custom_fp(ref, "WIREPAD", [(1, x, y, WP, WD)], silk_label=(x, y + 3.0))
    setnet(p, 1, nm); p.Reference().SetVisible(False)
    text(lab, x, y + 3.0, 0.9)

# --- J9: 4-pin Molex 8981 on the top edge, far left (right-angle tab holes towards the edge)
MX, MY = 15.28, 8.0
J9 = custom_fp("J9", "Molex_8981_1x04_P5.08mm_Horizontal",
               [(i + 1, MX + 5.08 * i, MY, 3.0, 1.7) for i in range(4)]
               + [("MP", MX - 5.08, MY - 5.08, 3.0, 1.7), ("MP", MX + 15.24 + 5.08, MY - 5.08, 3.0, 1.7)],
               outline=(MX - 6.6, 0.4, MX + 15.24 + 6.6, MY + 4.5), silk_label=(MX + 15.24 + 8.4, 2.0))
for i, nm in enumerate(("+5V", "GND", "GND", "+5V")):
    setnet(J9, i + 1, nm)
setnet(J9, "MP", "GND")
text("5V AUX", MX + 7.62, MY + 3.0, 1.1, bold=True)

# --- LED headers (Dupont 2.54 mm): pin 1 = LED anode via resistor, pin 2 = cathode
R1 = place("Resistor_SMD", "R_1206_3216Metric", "R1", 19.5, 40.0, 0, "47k")
D2 = place(*HDR, "D2", 23.6, 40.0, 90, "LED 54V header")
setnet(R1, 1, "+54V"); setnet(R1, 2, "LED54"); setnet(D2, 1, "LED54"); setnet(D2, 2, "GND54")
R2 = place("Resistor_SMD", "R_1206_3216Metric", "R2", 54.0, 48.5, 0, "4.7k")
D3 = place(*HDR, "D3", 58.5, 48.5, 90, "LED 12V header")
setnet(R2, 1, "+12V"); setnet(R2, 2, "LED12"); setnet(D3, 1, "LED12"); setnet(D3, 2, "GND")
R3 = place("Resistor_SMD", "R_1206_3216Metric", "R3", 7.0, 40.0, 270, "1k")
D4 = place(*HDR, "D4", 7.0, 45.0, 0, "LED 5V header")
setnet(R3, 1, "+5V"); setnet(R3, 2, "LED5"); setnet(D4, 1, "LED5"); setnet(D4, 2, "GND")

# --- optional ground tie GND54 <-> GND (bottom, open = isolated)
JP2 = place("Jumper", "SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "JP2", 37.75, 50.0, 0, "GND_TIE", layer_back=True)
_p = sorted(JP2.Pads(), key=lambda p: p.GetPosition().x)
_p[0].SetNet(net("GND54")); _p[1].SetNet(net("GND"))

# --- M3 mounting holes
HOLES = ((4, 4), (W - 4, 4), (4, H - 4.5), (W - 4, H - 4.5))
for i, (x, y) in enumerate(HOLES):
    place("MountingHole", "MountingHole_3.2mm_M3", "H%d" % (1 + i), x, y, 0, "M3").Reference().SetVisible(False)

# ======================= ROUTING =======================
def near(m, num, target_x=None):
    ps = [padpos(m, num, i) for i in range(len(pads(m, num)))]
    if target_x is None:
        return ps[0]
    return min(ps, key=lambda q: abs(q[0] - target_x))

# fuse -> connector
for fref, jref in (("F2", "J2"), ("F3", "J3"), ("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    a = near(F[fref], 2, JX[jref]); c = padpos(J[jref], 1)
    track([a, c], JNET[jref][0], 3.0)
# blade holders: both pins of each clip are one contact
for fref in ("F4", "F5", "F6", "F7", "F8"):
    for num in (1, 2):
        ps = [padpos(F[fref], num, i) for i in range(len(pads(F[fref], num)))]
        track(ps, F[fref].FindPadByNumber(str(num)).GetNetname(), 2.0)

# 54 V passthrough: two parallel top-layer tracks from J1 to the 54 V block.
# The bottom layer stays GND underneath, so the 12 V feed of F8 can cross on the bottom.
TW = 3.0
track([padpos(J1, 1), padpos(J1, 3)], "+54V", TW)
track([padpos(J1, 4), padpos(J1, 6)], "GND54", TW)
YB54 = 37.0                      # +54V run below the Pololu
track([padpos(J1, 3), (57.0, padpos(J1, 3)[1]), (57.0, YB54), (31.0, YB54)], "+54V", TW)
YG54 = 41.0
track([padpos(J1, 6), (63.0, padpos(J1, 6)[1]), (63.0, YG54), (35.5, YG54), (35.5, 46.0)], "GND54", TW)
for vy in (41.0, 42.6, 44.2, 45.8):
    via(35.5, vy, "GND54", 1.0, 0.5)

# 12 V feed for the Pololu: J10 pin 1 -> bottom layer -> F8 pad 1 (crosses under the 54 V tracks)
a = padpos(J10, 1); f1 = near(F["F8"], 1)
track([a, (70.0, a[1]), (70.0, f1[1] + 2.5), f1], "+12V", 2.0, pcbnew.B_Cu)
# F8 pad 2 -> P1 (VIN)
f2 = (F8X - 9.92, F8Y)
track([f2, (52.0, 15.08), (52.0, 19.0)], "12V_PL", 2.0)

# LED nets
track([padpos(R1, 2), padpos(D2, 1)], "LED54", 0.4)
track([padpos(R2, 2), padpos(D3, 1)], "LED12", 0.4)
track([padpos(R3, 2), padpos(D4, 1)], "LED5", 0.4)

# ======================= ZONES =======================
def zone(netname, layer, poly, prio=0):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    if netname: z.SetNet(net(netname))
    o = z.Outline(); o.NewOutline()
    for x, y in poly:
        o.Append(MM(OX + x), MM(OY + y))
    z.SetLocalClearance(MM(0.5))
    z.SetMinThickness(MM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetAssignedPriority(prio)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
    return z

e = 0.6
# top: +5V everywhere on the Pololu/Molex side (top strip, under the Pololu, left column down to J8)
zone("+5V", pcbnew.F_Cu, [(e, e), (74.0, e), (74.0, 15.4), (54.5, 15.4), (54.5, 34.5),
                         (13.5, 34.5), (13.5, H - e), (e, H - e)])
# top: +12V from J10 to the 12 V fuses, F8 feed, C5/C6
zone("+12V", pcbnew.F_Cu, [(38.5, 43.0), (65.0, 43.0), (65.0, 31.8), (W - e, 31.8), (W - e, 70.5),
                          (72.3, 70.5), (72.3, 59.5), (38.5, 59.5)])
# top: +54V around the 54 V fuse tops
zone("+54V", pcbnew.F_Cu, [(15.0, 36.0), (33.5, 36.0), (33.5, 47.5), (15.0, 47.5)])
# bottom: GND everywhere except the 54 V block (GND54), 1.5 mm gap
zone("GND", pcbnew.B_Cu, [(e, e), (W - e, e), (W - e, H - e), (38.5, H - e), (38.5, 36.5),
                         (15.0, 36.5), (15.0, H - e), (e, H - e)])
zone("GND54", pcbnew.B_Cu, [(16.5, 38.0), (37.0, 38.0), (37.0, H - e), (16.5, H - e)])

# copper keep-out rings around the M3 mounting holes
import math
for (hx, hy) in HOLES:
    k = pcbnew.ZONE(b)
    k.SetIsRuleArea(True); k.SetDoNotAllowCopperPour(True); k.SetDoNotAllowTracks(True)
    k.SetDoNotAllowVias(True); k.SetDoNotAllowPads(False); k.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); k.SetLayerSet(ls)
    o = k.Outline(); o.NewOutline()
    for i in range(24):
        t = 2 * math.pi * i / 24
        o.Append(MM(OX + hx + 4.5 * math.cos(t)), MM(OY + hy + 4.5 * math.sin(t)))
    b.Add(k)

# ======================= SILKSCREEN =======================
B = pcbnew.B_SilkS
for ref, x in JX.items():
    text(JSHORT[ref], C[ref], JY + 3.1, 0.8, bold=True)
    text("+", x - 2.0, JY - 2.9, 0.9, bold=True)
    text("+", x - 2.2, JY, 1.0, layer=B, bold=True)
    text("-", x + 3.96 + 2.2, JY, 1.0, layer=B, bold=True)
    text(JVAL[ref], C[ref], JY + 3.4, 0.9, layer=B, bold=True)
for conn, labs in ((J1, ("+54V", "+54V", "+54V", "GND", "GND", "GND")),
                   (J10, ("+12V", "+12V", "+12V", "GND", "GND", "GND"))):
    for i, lab in enumerate(labs):
        q = padpos(conn, i + 1); text(lab, q[0] - 4.4, q[1], 0.8)
text("54V IN", 70.0, 24.0, 1.1, rot=90, bold=True)
text("12V IN", 69.5, 47.0, 1.1, rot=90, bold=True)
def refat(m, x, y, rot=0, size=0.8):
    r = m.Reference(); r.SetPosition(P(x, y)); r.SetTextAngleDegrees(rot)
    r.SetTextSize(VECTOR2I(MM(size), MM(size))); r.SetTextThickness(MM(size * 0.15))
refat(R1, 19.5, 42.2); refat(D2, 26.6, 42.2)
text("+", 23.6, 38.2, 1.0, bold=True); text("54V", 26.9, 38.2, 0.8)
refat(R2, 54.0, 46.6); refat(D3, 59.8, 50.5)
text("+", 58.5, 46.6, 1.0, bold=True); text("12V", 63.6, 48.5, 0.8)
refat(R3, 9.2, 40.0, 90); refat(D4, 9.2, 46.3, 90)
text("+", 5.1, 45.0, 1.0, bold=True); text("5V", 7.0, 49.4, 0.8)
for ref, jref in (("F2", "J2"), ("F3", "J3")):
    text("2.5A", C[jref], Ft + 5.8, 1.0, rot=90); refat(F[ref], C[jref], Ft + 16.5, 90, 1.0)
for ref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    text("5A", C[jref], Fy + 4.2, 0.9); refat(F[ref], C[jref], Fy + 6.4, 90, 0.8)
refat(C5, 76.25, 58.4); refat(C6, 44.25, 53.4 - 9.9)
text("5A", F8X - 5.0, 13.2, 0.9)
text("RACK POWER BOARD v2", 30.0, 22.0, 1.6, layer=B, bold=True)
text("12V + 54V in -> 12V x4 / 5V / 54V x2", 30.0, 24.6, 1.0, layer=B)
text("2 layers, 2oz Cu, 1.6mm", 30.0, 26.6, 1.0, layer=B)
text("F2/F3 2.5A T 5x20, F4-F8 ATM 5A", 30.0, 28.6, 1.0, layer=B)
text("JP2: bridge to tie GND54 to GND", 37.75, 55.0, 0.8, layer=B)

b.Save(OUT)
print("saved", OUT)
