#!/usr/bin/env python3
"""Generate rack-power-board.kicad_pcb (KiCad 7) - 54V -> 54V/12V/5V distribution board."""
import pcbnew
from pcbnew import VECTOR2I, FromMM as MM

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rack-power-board.kicad_pcb")
LIB = "/usr/share/kicad/footprints/"
OX, OY = 30.0, 30.0          # sheet offset
W, H = 134.0, 78.5           # board size (mm)

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
# --- connectors: Phoenix MSTBA 5.08mm horizontal, opening facing the board edge (y=H)
JY = H - 5.8            # JST VH: body edge 0.5 mm inside the board edge
JX = {"J1": 12, "J2": 26, "J3": 40, "J4": 56, "J5": 70, "J6": 84, "J7": 98, "J8": 116}
JNET = {"J1": ("VIN_RAW", "GND"), "J2": ("OUT54_1", "GND"), "J3": ("OUT54_2", "GND"),
        "J4": ("OUT12_1", "GND"), "J5": ("OUT12_2", "GND"), "J6": ("OUT12_3", "GND"),
        "J7": ("OUT12_4", "GND"), "J8": ("+5V", "GND")}
JSHORT = {"J1": "54V IN", "J2": "54V 1", "J3": "54V 2", "J4": "12V 1", "J5": "12V 2", "J6": "12V 3", "J7": "12V 4", "J8": "5V"}
JVAL = {"J1": "54V IN", "J2": "54V OUT1", "J3": "54V OUT2", "J4": "12V OUT1", "J5": "12V OUT2",
        "J6": "12V OUT3", "J7": "12V OUT4", "J8": "5V OUT"}
J = {}
for ref, x in JX.items():
    m = place("Connector_JST", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
              ref, x, JY, 0, "JST B2P-VH")
    setnet(m, 1, JNET[ref][0]); setnet(m, 2, JNET[ref][1])
    m.Reference().SetVisible(False)
    J[ref] = m

# --- 54V fuses (5x20 holders, vertical): upper pad = bus side
F = {}
for ref, jref, low in (("F1", "J1", "VIN_RAW"), ("F2", "J2", "OUT54_1"), ("F3", "J3", "OUT54_2")):
    x = JX[jref]
    m = place("Fuse", "Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open", ref, x, 42.5, 270,
              "5x20 T 8A" if ref == "F1" else "5x20 T 2.5A")
    # pad1 at rotation origin (52), pad2 at 52+22.5
    setnet(m, 1, "+54V"); setnet(m, 2, low)
    F[ref] = m

# --- 12V fuses (Keystone 3568 mini-blade holders, vertical)
for ref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    x = JX[jref]
    m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", ref, x, 53.3, 270, "ATM 5A")
    setnet(m, 1, "+12V"); setnet(m, 2, "OUT12_" + jref[1:] if False else JNET[jref][0])
    F[ref] = m
# Pololu feed fuse, horizontal
m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", "F8", 99.5, 8.0, 0, "ATM 5A")
setnet(m, 1, "+12V"); setnet(m, 2, "12V_PL"); F["F8"] = m

# --- Eighth-brick DC-DC (DOSA), centre (64, 26)
BX, BY = 64.0, 26.0
brick_pads = [
    (1, BX - 25.4, BY - 7.62, 2.6, 1.5), (2, BX - 25.4, BY, 2.6, 1.5), (3, BX - 25.4, BY + 7.62, 2.6, 1.5),
    (4, BX + 25.4, BY + 7.62, 3.6, 2.1), (5, BX + 25.4, BY + 3.81, 2.6, 1.5), (6, BX + 25.4, BY, 2.6, 1.5),
    (7, BX + 25.4, BY - 3.81, 2.6, 1.5), (8, BX + 25.4, BY - 7.62, 3.6, 2.1)]
U1 = custom_fp("U1", "DOSA_EighthBrick_THT", brick_pads,
               outline=(BX - 29.2, BY - 11.45, BX + 29.2, BY + 11.45), silk_label=(BX, BY - 9))
for num, nm in ((1, "+54V"), (2, "RC"), (3, "GND"), (4, "GND"), (5, "GND"), (7, "+12V"), (8, "+12V")):
    setnet(U1, num, nm)
text("54-12V 1/8 BRICK", BX, BY - 3, 1.5, bold=True)
text("DVE0125 / PKB4313D / E48SC12025", BX, BY, 1.0)
text("pin1", BX - 21.5, BY - 7.62, 0.9)

# --- input caps (54V)
C1 = place("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C1", 18.0, 8.5, 0, "68uF 100V")
C2 = place("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C2", 31.0, 8.5, 0, "68uF 100V")
for c in (C1, C2):
    setnet(c, 1, "+54V"); setnet(c, 2, "GND")
C3 = place("Capacitor_SMD", "C_1210_3225Metric", "C3", 30.0, 19.5, 0, "2.2uF 100V X7R")
C4 = place("Capacitor_SMD", "C_1210_3225Metric", "C4", 30.0, 24.0, 0, "2.2uF 100V X7R")
for c in (C3, C4):
    setnet(c, 1, "+54V"); setnet(c, 2, "GND")
# TVS
D1 = place("Diode_SMD", "D_SMB", "D1", 22.5, 30.0, 0, "SMBJ58A")
setnet(D1, 1, "+54V"); setnet(D1, 2, "GND")
# RC jumper (pin2 -> pin3)
JP1 = place("Jumper", "SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "JP1", 31.5, 30.5, 90, "RC_NEG")
setnet(JP1, 1, "RC"); setnet(JP1, 2, "GND")

# --- output caps (12V)
C5 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C5", 70.0, 7.5, 0, "470uF 16V polymer")
C6 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C6", 80.5, 7.5, 0, "470uF 16V polymer")
for c in (C5, C6):
    setnet(c, 1, "+12V"); setnet(c, 2, "GND")
C7 = place("Capacitor_SMD", "C_1210_3225Metric", "C7", 96.5, 24.0, 90, "22uF 25V X5R")
C8 = place("Capacitor_SMD", "C_1210_3225Metric", "C8", 99.8, 24.0, 90, "22uF 25V X5R")
for c in (C7, C8):
    setnet(c, 1, "+12V"); setnet(c, 2, "GND")

# --- Pololu D24V90F5 (on M2 standoffs), vertical, x 103..123.3, y 30..70.6
PX0, PY0 = 103.0, 20.0
pcx, pcy = PX0 + 10.15, PY0 + 20.3
M2H = []
for i, (dx, dy) in enumerate(((-7.62, -17.78), (7.62, -17.78), (-7.62, 17.78), (7.62, 17.78))):
    M2H.append((pcx + dx, pcy + dy))
    place("MountingHole", "MountingHole_2.2mm_M2", "H%d" % (5 + i), pcx + dx, pcy + dy, 0, "M2 standoff")
U2 = custom_fp("U2", "Pololu_D24V90F5_outline", [], outline=(PX0, PY0, PX0 + 20.3, PY0 + 40.6), silk_label=(pcx, pcy - 4), crtyd=False)
U2.Reference().SetPosition(P(pcx, pcy - 4))
text("POLOLU", pcx, pcy - 1, 1.2, rot=90)
text("D24V90F5", pcx + 2, pcy - 1, 1.0, rot=90)
text("on M2 x10mm", pcx + 4, pcy - 1, 0.9, rot=90)
# wire pads for the Pololu (1.0 mm2 wires)
WP = 3.6; WD = 1.8
P1 = custom_fp("P1", "WIREPAD", [(1, 109.92, 17.0, WP, WD)], silk_label=(109.92, 14.4))
P2 = custom_fp("P2", "WIREPAD", [(1, 116.5, 17.0, WP, WD)], silk_label=(116.5, 14.4))
P3 = custom_fp("P3", "WIREPAD", [(1, 118.5, 64.0, WP, WD)], silk_label=(121.8, 64.0))
P4 = custom_fp("P4", "WIREPAD", [(1, 110.5, 64.0, WP, WD)], silk_label=(107.2, 64.0))
setnet(P1, 1, "12V_PL"); setnet(P2, 1, "GND"); setnet(P3, 1, "+5V"); setnet(P4, 1, "GND")
text("VIN", 105.4, 17.0, 1.0); text("GND", 121.0, 17.0, 1.0)
for _p in (P1, P2, P3, P4): _p.Reference().SetVisible(False)
text("VOUT", 123.3, 64.0, 1.0); text("GND", 106.6, 64.0, 1.0)

# --- LEDs
R1 = place("Resistor_SMD", "R_1206_3216Metric", "R1", 17.0, 35.5, 0, "47k")
D2 = place("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical", "D2", 21.6, 35.5, 90, "LED 54V header")
setnet(R1, 1, "+54V"); setnet(R1, 2, "LED54"); setnet(D2, 1, "LED54"); setnet(D2, 2, "GND")
R2 = place("Resistor_SMD", "R_1206_3216Metric", "R2", 60.0, 46.0, 0, "4.7k")
D3 = place("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical", "D3", 64.6, 46.0, 90, "LED 12V header")
setnet(R2, 1, "+12V"); setnet(R2, 2, "LED12"); setnet(D3, 1, "LED12"); setnet(D3, 2, "GND")
R3 = place("Resistor_SMD", "R_1206_3216Metric", "R3", 129.5, 41.5, 90, "1k")
D4 = place("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical", "D4", 129.5, 36.8, 180, "LED 5V header")
setnet(R3, 1, "+5V"); setnet(R3, 2, "LED5"); setnet(D4, 1, "LED5"); setnet(D4, 2, "GND")

# --- M3 mounting holes
for i, (x, y) in enumerate(((4, 4), (W - 4, 4), (4, H - 4.5), (W - 4, H - 4.5))):
    place("MountingHole", "MountingHole_3.2mm_M3", "H%d" % (1 + i), x, y, 0, "M3").Reference().SetVisible(False)

# --- J9: 4-pin Molex 8981 "disk drive" header, right angle, plug enters from the left edge
MX, MY = 8.0, 16.5
J9 = custom_fp("J9", "Molex_8981_1x04_P5.08mm_Horizontal",
               [(i + 1, MX, MY + 5.08 * i, 3.0, 1.7) for i in range(4)]
               # mounting tabs of the right-angle variant: one pitch beyond each end pin,
               # one pitch towards the board edge (unused when a straight header is fitted)
               + [("MP", MX - 5.08, MY - 5.08, 3.0, 1.7), ("MP", MX - 5.08, MY + 15.24 + 5.08, 3.0, 1.7)],
               outline=(0.4, MY - 6.6, MX + 4.5, MY + 15.24 + 6.6), silk_label=(MX + 5, MY - 5))
for i, nm in enumerate(("+5V", "GND", "GND", "+5V")):
    setnet(J9, i + 1, nm)
    text(("+5V", "GND", "GND", "+5V")[i], MX + 8.0, MY + 5.08 * i, 1.0)
setnet(J9, "MP", "GND")
text("5V AUX", MX + 5.6, MY + 7.6, 1.1, rot=90, bold=True)

# ======================= ROUTING =======================
def near(m, num, target_x=None):
    ps = [padpos(m, num, i) for i in range(len(pads(m, num)))]
    if target_x is None:
        return ps[0]
    return min(ps, key=lambda q: abs(q[0] - target_x))

# fuse -> connector (vertical) tracks
for fref, jref, nm in (("F1", "J1", "VIN_RAW"), ("F2", "J2", "OUT54_1"), ("F3", "J3", "OUT54_2")):
    a = near(F[fref], 2); c = padpos(J[jref], 1)
    track([a, (c[0], a[1]), c] if abs(a[0] - c[0]) > 0.01 else [a, c], nm, 3.0)
for fref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    a = near(F[fref], 2, JX[jref]); c = padpos(J[jref], 1)
    track([a, (c[0], a[1]), c] if abs(a[0] - c[0]) > 0.01 else [a, c], JNET[jref][0], 3.0)
# blade holders: both pins of each clip are one contact -> tie them
for fref in ("F4", "F5", "F6", "F7", "F8"):
    for num in (1, 2):
        ps = [padpos(F[fref], num, i) for i in range(len(pads(F[fref], num)))]
        track(ps, F[fref].FindPadByNumber(str(num)).GetNetname(), 2.0)
# F8 -> P1
a = near(F["F8"], 2, 109.92)
track([a, (109.92, a[1]), (109.92, 17.0)], "12V_PL", 2.0)
# P3 (+5V) -> J8 pin1, and to R3
c = padpos(J["J8"], 1)
track([(118.5, 64.0), (118.5, 66.0), (c[0], 68.5), c], "+5V", 3.0)
q = padpos(R3, 1); track([q, (126.0, q[1])], "+5V", 0.6); via(126.0, q[1], "+5V")
# LED nets
track([padpos(R1, 2), padpos(D2, 1)], "LED54", 0.4)
track([padpos(R2, 2), padpos(D3, 1)], "LED12", 0.4)
track([padpos(R3, 2), padpos(D4, 1)], "LED5", 0.4)
def away_via(m, num, other, nm, dist=1.9, w=0.5, d=0.8, dr=0.4):
    q = padpos(m, num); o = padpos(m, other)
    dx, dy = q[0] - o[0], q[1] - o[1]; L = (dx * dx + dy * dy) ** 0.5
    v = (q[0] + dx / L * dist, q[1] + dy / L * dist)
    track([q, v], nm, w); via(v[0], v[1], nm, d, dr)
# LED cathodes -> vias to bottom ground planes
# LED headers: pin 1 = anode (+, via resistor), pin 2 = cathode (GND, through-hole into the bottom pour)
for _d in (D2, D3, D4):
    _q = padpos(_d, 1); text("+", _q[0] + (1.6 if _d is D4 else 0), _q[1] + (0 if _d is D4 else -1.9), 1.0, bold=True)
# RC jumper
track([padpos(U1, 2), (33.5, BY), (33.5, padpos(JP1, 1)[1]), padpos(JP1, 1)], "RC", 0.5)
away_via(JP1, 2, 1, "GND", 1.9, 0.6)
# ceramic cap GND vias
for c, nm in ((C3, "GND"), (C4, "GND"), (D1, "GND")):
    q = padpos(c, 2); track([q, (q[0] + 1.6, q[1])], nm, 0.8); via(q[0] + 1.6, q[1], nm, 1.0, 0.5)
for c in (C7, C8):
    away_via(c, 2, 1, "GND", 2.0, 0.8, 1.0, 0.5)

# 5V bus to J9 on the bottom layer: P3 -> right edge -> top edge -> down to J9
BC = pcbnew.B_Cu
track([(118.5, 64.0), (126.0, 64.0), (126.0, 12.0), (121.0, 12.0), (121.0, 2.2),
       (27.0, 2.2), (27.0, 14.0), (12.0, 14.0), (12.0, MY + 15.24)], "+5V", 3.0, BC)
track([(12.0, MY), (MX, MY)], "+5V", 3.0, BC)
track([(12.0, MY + 15.24), (MX, MY + 15.24)], "+5V", 3.0, BC)
# extra stitching vias for ground planes near connectors (help current spread on 2 layers)
# (connector pin2 pads are through-hole, so they already join bottom plane)

# ======================= ZONES =======================
def zone(netname, layer, poly, prio=0, name=None):
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
# top: +54V region (left)
zone("+54V", pcbnew.F_Cu, [(e, e), (45.5, e), (45.5, 50.0), (e, 50.0)])
# top: +12V region (middle/right), notched around the Pololu
zone("+12V", pcbnew.F_Cu, [(48.0, e), (104.0, e), (104.0, 14.0), (101.8, 14.0), (101.8, 58.0), (48.0, 58.0)])
# bottom: one common GND pour
zone("GND", pcbnew.B_Cu, [(e, e), (W - e, e), (W - e, H - e), (e, H - e)])

# keep-out: no top copper under the open-frame brick body (between the pin rows)
ko = pcbnew.ZONE(b)
ko.SetIsRuleArea(True); ko.SetDoNotAllowCopperPour(True); ko.SetDoNotAllowTracks(False)
ko.SetDoNotAllowVias(False); ko.SetDoNotAllowPads(False); ko.SetDoNotAllowFootprints(False)
ko.SetLayer(pcbnew.F_Cu)
o = ko.Outline(); o.NewOutline()
for x, y in ((BX - 21.5, BY - 11.0), (BX + 21.5, BY - 11.0), (BX + 21.5, BY + 11.0), (BX - 21.5, BY + 11.0)):
    o.Append(MM(OX + x), MM(OY + y))
b.Add(ko)

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
for ref, x in JX.items():
    text(JSHORT[ref], x + 6.9, JY - 6.0, 1.0, bold=True)
    text("+", x - 2.4, JY, 1.0, bold=True)
    text("+", x - 2.4, JY, 1.0, layer=pcbnew.B_SilkS, bold=True)
    text("-", x + 3.96 + 2.4, JY, 1.0, layer=pcbnew.B_SilkS, bold=True)
    text(JVAL[ref], x + 1.98, JY + 3.6, 1.0, layer=pcbnew.B_SilkS, bold=True)
B = pcbnew.B_SilkS
text("RACK POWER BOARD", 72, 39.5, 2.5, layer=B, bold=True)
text("54V -> 54V x2 / 12V x4 / 5V", 72, 43, 1.6, layer=B)
text("2 layers, 2oz Cu, 1.6mm", 72, 45.6, 1.2, layer=B)
text("F1 8A T, F2/F3 2.5A T (5x20, 250V)", 72, 47.8, 1.2, layer=B)
text("F4-F8 ATM mini blade 5A", 72, 50, 1.2, layer=B)
for ref, lab in (("J1", "8A"), ("J2", "2.5A"), ("J3", "2.5A")):
    text(lab, JX[ref] - 4.2, 54.0, 1.0, rot=90)
for ref in ("J4", "J5", "J6", "J7"):
    text("5A", JX[ref] + 5.6, 58.3, 1.0, rot=90)
text("5A", 95.0, 12.8, 1.0)
text("JP1: bridge = brick ON", BX, BY + 5.0, 0.9)
text("for NEG-logic RC", BX, BY + 6.5, 0.9)
text("54V", 28.2, 35.5, 0.9); text("12V", 71.5, 46.0, 0.9); text("5V", 132.2, 38.8, 0.9, rot=90)

#FILL
b.Save(OUT)
print("saved", OUT)
