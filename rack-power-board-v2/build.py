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

# --- outputs: 2-pin 5.08 mm screw terminals (Phoenix MKDS-1,5 footprint), wire entry at the board edge.
#     Bottom edge, left to right: 5V, 12V x4.  Left edge, as low as the corner hole allows: 54V 1, 54V 2.
TB2 = ("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal")
JY = 75.3                         # bottom row pin line: body front flush with the board edge
TP = 10.3                         # block pitch (bodies are 10.16 wide)
JX = {"J8": 26.8}
for i, ref in enumerate(("J4", "J5", "J6", "J7")):
    JX[ref] = 26.8 + TP * (i + 1)
C = {k: v + 2.54 for k, v in JX.items()}       # block centre
LX = 5.0                          # left-edge column: pin line (body front flush with the left edge)
LY = {"J2": 53.8, "J3": 64.1}     # pin 1 (top) of each left-edge block; pin 2 is 5.08 below
JNET = {"J2": ("OUT54_1", "GND54"), "J3": ("OUT54_2", "GND54"),
        "J4": ("OUT12_1", "GND"), "J5": ("OUT12_2", "GND"), "J6": ("OUT12_3", "GND"),
        "J7": ("OUT12_4", "GND"), "J8": ("+5V", "GND")}
JSHORT = {"J2": "54V1", "J3": "54V2", "J4": "12V1", "J5": "12V2", "J6": "12V3", "J7": "12V4", "J8": "5V"}
JVAL = {"J2": "54V OUT1", "J3": "54V OUT2", "J4": "12V OUT1", "J5": "12V OUT2",
        "J6": "12V OUT3", "J7": "12V OUT4", "J8": "5V OUT"}

def tight_courtyard(m):
    """Library courtyard is 11.2 mm wide; blocks sit side by side at 10.3 mm (bodies 10.16 mm),
    so replace it with one hugging the body."""
    for g in list(m.GraphicalItems()):
        if g.GetLayer() == pcbnew.F_CrtYd:
            m.Remove(g)
    pts = [(-2.6, -5.3), (7.68, -5.3), (7.68, 4.7), (-2.6, 4.7)]
    for i in range(4):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % 4]
        sh = pcbnew.FP_SHAPE(m); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.F_CrtYd)
        sh.SetWidth(MM(0.05)); sh.SetStart0(VECTOR2I(MM(x0), MM(y0))); sh.SetEnd0(VECTOR2I(MM(x1), MM(y1)))
        m.Add(sh); sh.SetDrawCoord()

J = {}
for ref, x in JX.items():
    m = place(*TB2, ref, x, JY, 0, "5.08mm screw terminal 2p")
    J[ref] = m
for ref, y in LY.items():
    m = place(*TB2, ref, LX, y, 270, "5.08mm screw terminal 2p")
    J[ref] = m
for ref, m in J.items():
    setnet(m, 1, JNET[ref][0]); setnet(m, 2, JNET[ref][1])
    m.Reference().SetVisible(False)
    tight_courtyard(m)

# --- inputs, JST VH 6-pin, pins 1-3 = +, 4-6 = -, pin 1 at the top:
#     J1 54 V on the left edge (top end, just below J9), J10 12 V on the right edge (top end)
J1X, J1Y = 6.1, 15.3
J10X, J10Y = W - 5.8, 10.0
J1 = place(*VH6, "J1", J1X, J1Y, 270, "JST B6P-VH")
J10 = place(*VH6, "J10", J10X, J10Y, 270, "JST B6P-VH")
for n in (1, 2, 3): setnet(J1, n, "+54V"); setnet(J10, n, "+12V")
for n in (4, 5, 6): setnet(J1, n, "GND54"); setnet(J10, n, "GND")
J1.Reference().SetVisible(False); J10.Reference().SetVisible(False)

# --- 54 V output fuses (5x20, vertical, centred over their connector)
Ft = 42.0
FX54 = {"F3": 16.5, "F2": 26.8}   # F3 (left) feeds J3 (lower), F2 (right) feeds J2 (upper)
F = {}
for ref, jref in (("F2", "J2"), ("F3", "J3")):
    m = place("Fuse", "Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open", ref, FX54[ref], Ft, 270, "5x20 T 2.5A")
    setnet(m, 1, "+54V"); setnet(m, 2, JNET[jref][0])
    F[ref] = m

# --- 12 V output fuses (ATM mini blade, vertical, centred over their connector)
Fy = 56.0
for ref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", ref, C[jref] + 1.7, Fy, 270, "ATM 5A")
    setnet(m, 1, "+12V"); setnet(m, 2, JNET[jref][0])
    F[ref] = m
# Pololu feed fuse, top edge next to J10 (pad 1 right = +12V, pad 2 left -> P1)
F8X, F8Y = 67.5, 9.5
m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", "F8", F8X, F8Y, 180, "ATM 5A")
setnet(m, 1, "+12V"); setnet(m, 2, "12V_PL"); F["F8"] = m

# --- 12 V bulk caps below J10
C5 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C5", 75.0, 38.0, 0, "470uF 16V polymer")
C6 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C6", 75.0, 47.0, 0, "470uF 16V polymer")
for c in (C5, C6):
    setnet(c, 1, "+12V"); setnet(c, 2, "GND")

# --- Pololu D24V90F5, horizontal between the two inputs, soldered flat on 0.1" header pins
#     (end rows of 4 small holes) plus solid wire links through the large terminal-block holes.
#     Positions from Pololu's D24VxF5 dimension drawing (top view: u across 0..20.3, v along 0..40.6).
#     The FB/PG/EN column is at u = 19.03, v = 12.7..20.3, i.e. nearer the VIN end, so v = 0 is the
#     VIN end; GND is the large hole on the column side (u = 12.70) at both ends.
#     Rotated so the VOUT end is on the left and the FB/PG/EN column faces the front edge:
#     board x = PX0 + 40.6 - v, board y = PY0 + u.
PX0, PY0 = 31.0, 14.5
pcx, pcy = PX0 + 20.3, PY0 + 10.15
M2H = []                       # no standoffs any more
def pol(u, v):
    return (PX0 + 40.6 - v, PY0 + u)
POL = []                       # (net, u, v, pad, drill)
for vend, small_v, live in ((2.54, 5.08, "12V_PL"), (38.06, 35.52, "+5V")):
    POL += [(live, 7.62, vend, 2.8, 1.6), ("GND", 12.70, vend, 2.8, 1.6)]
    POL += [(live, 6.35, small_v, 1.8, 1.0), (live, 8.89, small_v, 1.8, 1.0),
            ("GND", 11.43, small_v, 1.8, 1.0), ("GND", 13.97, small_v, 1.8, 1.0)]
U2 = custom_fp("U2", "Pololu_D24V90F5_headers",
               [(i + 1, *pol(u, v), pd, dr) for i, (nm, u, v, pd, dr) in enumerate(POL)],
               outline=(PX0, PY0, PX0 + 40.6, PY0 + 20.3), silk_label=(pcx, pcy - 3), crtyd=False)
for i, (nm, u, v, pd, dr) in enumerate(POL):
    setnet(U2, i + 1, nm)
text("POLOLU D24V90F5", pcx, pcy, 1.2)
text("on 0.1in headers + wire links", pcx, pcy + 2, 0.9)
VOUT_L = pol(7.62, 38.06); VIN_L = pol(7.62, 2.54)
text("VOUT", VOUT_L[0] + 5.0, VOUT_L[1] - 3.2, 0.8); text("VIN", VIN_L[0] - 5.0, VIN_L[1] - 3.2, 0.8)
_c = pol(19.03, 16.5); text("FB PG EN pins this side", _c[0], _c[1] - 2.0, 0.8)
PY = PY0 + 20.3 + 3.7

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
R1 = place("Resistor_SMD", "R_2512_6332Metric", "R1", 5.5, 40.5, 0, "5.1k 1W")
D2 = place(*HDR, "D2", 4.5, 44.6, 0, "LED 54V header")
setnet(R1, 1, "+54V"); setnet(R1, 2, "LED54"); setnet(D2, 1, "LED54"); setnet(D2, 2, "GND54")
R2 = place("Resistor_SMD", "R_1206_3216Metric", "R2", 50.0, 47.0, 0, "1k")
D3 = place(*HDR, "D3", 54.5, 47.0, 90, "LED 12V header")
setnet(R2, 1, "+12V"); setnet(R2, 2, "LED12"); setnet(D3, 1, "LED12"); setnet(D3, 2, "GND")
R3 = place("Resistor_SMD", "R_1206_3216Metric", "R3", 35.3, 43.0, 270, "300R")
D4 = place(*HDR, "D4", 35.3, 47.6, 0, "LED 5V header")
setnet(R3, 1, "+5V"); setnet(R3, 2, "LED5"); setnet(D4, 1, "LED5"); setnet(D4, 2, "GND")

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
for fref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    a = near(F[fref], 2, JX[jref]); c = padpos(J[jref], 1)
    track([a, c], JNET[jref][0], 3.0)
# 54 V: F3 (left) straight across to J3; F2 (right) up between the two holders and over to J2
track([padpos(F["F3"], 2), padpos(J["J3"], 1)], "OUT54_2", 2.0)
_a = padpos(F["F2"], 2); _x = (FX54["F3"] + FX54["F2"]) / 2
track([_a, (_x, _a[1] - (FX54["F2"] - _x)), (_x, 50.5), (7.5, 50.5), padpos(J["J2"], 1)], "OUT54_1", 2.0)
# blade holders: both pins of each clip are one contact
for fref in ("F4", "F5", "F6", "F7", "F8"):
    for num in (1, 2):
        ps = [padpos(F[fref], num, i) for i in range(len(pads(F[fref], num)))]
        track(ps, F[fref].FindPadByNumber(str(num)).GetNetname(), 2.0)
# F8 pad 2 -> Pololu VIN (large hole + two header pins), under the Pololu
f2 = (F8X - 9.92, F8Y)
_vs1, _vs2 = pol(6.35, 5.08), pol(8.89, 5.08)
track([f2, (f2[0], 12.5), (63.0, 17.9), (63.0, VIN_L[1]), VIN_L], "12V_PL", 2.0)
track([_vs1, _vs2], "12V_PL", 1.2)
# 5 V: Pololu VOUT large hole down to J8 pin 1 (inside the +5V pour)
track([(32.0, 42.0), (32.0, 68.5), (JX["J8"], JY)], "+5V", 3.0)   # VOUT reaches this through the +5V pour

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
X54 = 28.8          # the 54 V block is x < X54, y > Y54 (left column, below J9)
Y54 = 14.1
XB = 46.0           # +5V / +12V split under the Pololu
# top: +54V (J1 -> F2/F3 tops), +5V (J9, Pololu output side, J8 column), +12V (J10 -> F8, fuses, caps)
zone("+54V", pcbnew.F_Cu, [(e, Y54), (X54, Y54), (X54, Ft + 2.0), (e, Ft + 2.0)])
zone("+5V", pcbnew.F_Cu, [(e, e), (XB, e), (XB, 40.0), (37.2, 40.0), (37.2, H - e), (X54 + 1.5, H - e),
                         (X54 + 1.5, Y54 - 1.5), (e, Y54 - 1.5)])
zone("+12V", pcbnew.F_Cu, [(XB + 1.5, e), (W - e, e), (W - e, Fy + 3.0), (38.7, Fy + 3.0), (38.7, 41.5),
                          (XB + 1.5, 41.5)])
# bottom: GND54 under the 54 V block, GND everywhere else (1.5 mm gap)
zone("GND54", pcbnew.B_Cu, [(e, Y54), (X54, Y54), (X54, 71.5), (e, 71.5)])
zone("GND", pcbnew.B_Cu, [(e, e), (W - e, e), (W - e, H - e), (e, H - e), (e, 73.0), (X54 + 1.5, 73.0), (X54 + 1.5, Y54 - 1.5),
                         (e, Y54 - 1.5)])

# copper keep-out rings around the mounting holes
import math
# M3: 9 mm dia (screw head / washer); M2 Pololu standoffs: 6 mm dia, so the metal
# standoff (top) and screw head (bottom) can't bridge the pours on the two layers
for (hx, hy, kr) in [(x, y, 4.5) for (x, y) in ((4, 4), (W - 4, 4), (4, H - 4.5), (W - 4, H - 4.5))] + [(x, y, 3.0) for (x, y) in M2H]:
    k = pcbnew.ZONE(b)
    k.SetIsRuleArea(True); k.SetDoNotAllowCopperPour(True); k.SetDoNotAllowTracks(True)
    k.SetDoNotAllowVias(True); k.SetDoNotAllowPads(False); k.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); k.SetLayerSet(ls)
    o = k.Outline(); o.NewOutline()
    for i in range(24):
        t = 2 * math.pi * i / 24
        o.Append(MM(OX + hx + kr * math.cos(t)), MM(OY + hy + kr * math.sin(t)))
    b.Add(k)

# ======================= SILKSCREEN =======================
B = pcbnew.B_SilkS
# terminal labels go in the strip just behind the blocks (bodies hide anything under them)
for ref, x in JX.items():
    ly = JY - 6.2
    text("+", x, ly, 0.9, bold=True); text("-", x + 5.08, ly, 0.9, bold=True)
    text(JSHORT[ref], C[ref], ly, 0.8, bold=True)
    text("+", x, JY - 6.2, 1.0, layer=B, bold=True); text("-", x + 5.08, JY - 6.2, 1.0, layer=B, bold=True)
    text(JVAL[ref], C[ref], JY + 2.4, 0.9, layer=B, bold=True)
for ref, y in LY.items():
    lx = LX + 6.0
    text("+", lx, y, 0.9, bold=True); text("-", lx, y + 5.08, 0.9, bold=True)
    text(JSHORT[ref], lx, y + 2.54, 0.8, rot=90, bold=True)
    text("+", lx, y, 1.0, layer=B, bold=True); text("-", lx, y + 5.08, 1.0, layer=B, bold=True)
    text(JVAL[ref], lx + 1.6, y + 2.54, 0.9, rot=90, layer=B, bold=True)
for conn, labs, dx in ((J1, ("+54V", "+54V", "+54V", "GND", "GND", "GND"), 4.4),
                       (J10, ("+12V", "+12V", "+12V", "GND", "GND", "GND"), -4.4)):
    for i, lab in enumerate(labs):
        q = padpos(conn, i + 1); text(lab, q[0] + dx, q[1], 0.8)
text("54V IN", 14.0, 25.2, 1.1, rot=90, bold=True)
text("12V IN", 76.6, 33.0, 0.9, bold=True)

def refat(m, x, y, rot=0, size=0.8):
    r = m.Reference(); r.SetPosition(P(x, y)); r.SetTextAngleDegrees(rot)
    r.SetTextSize(VECTOR2I(MM(size), MM(size))); r.SetTextThickness(MM(size * 0.15))
refat(R1, 10.6, 40.5, 90); refat(D2, 6.6, 46.0, 90)
text("+", 2.6, 44.6, 1.0, bold=True); text("54V", 2.4, 47.4, 0.8, rot=90)
refat(R2, 50.0, 45.1); refat(D3, 55.8, 49.0)
text("+", 54.5, 45.1, 1.0, bold=True); text("12V", 59.6, 47.0, 0.8)
refat(R3, 37.5, 43.0, 90); refat(D4, 37.5, 48.9, 90)
text("+", 33.6, 47.6, 1.0, bold=True); text("5V", 35.3, 51.7, 0.8)
for ref in ("F2", "F3"):
    text("2.5A", FX54[ref], Ft + 5.8, 1.0, rot=90); refat(F[ref], FX54[ref], Ft + 16.5, 90, 1.0)
for ref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    text("5A", C[jref], Fy + 4.2, 0.9); refat(F[ref], C[jref], Fy + 6.4, 90, 0.8)
text("5A", F8X - 5.0, 13.0, 0.9)
refat(C5, 80.9, 34.6 + 0.0); refat(C6, 80.9, 52.6)
text("RACK POWER BOARD v2", 51.0, 20.0, 1.6, layer=B, bold=True)
text("12V + 54V in -> 12V x4 / 5V / 54V x2", 51.0, 22.6, 1.0, layer=B)
text("2 layers, 2oz Cu, 1.6mm", 51.0, 24.6, 1.0, layer=B)
text("F2/F3 2.5A T 5x20, F4-F8 ATM 5A", 51.0, 26.6, 1.0, layer=B)

b.Save(OUT)
print("saved", OUT)
