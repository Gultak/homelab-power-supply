#!/usr/bin/env python3
"""Generate rack-power-board-v2.kicad_pcb (KiCad 7): 12V from a separate PSU -> 4x fused 12V + 5V (Pololu), plus fused 54V passthrough."""
import pcbnew
from pcbnew import VECTOR2I, FromMM as MM

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rack-power-board-v2.kicad_pcb")
LIB = "/usr/share/kicad/footprints/"
OX, OY = 30.0, 30.0          # sheet offset
W, H = 108.6, 80.0          # board size (mm): v1 width minus 1"

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

# --- output connector row along the front edge (y = H), JST VH 2-pin
JY = H - 5.8
P_ = 11.8
JX = {"J8": 10.0, "J4": 10.0 + P_, "J5": 10.0 + 2 * P_, "J6": 10.0 + 3 * P_, "J7": 10.0 + 4 * P_,
      "J1": 10.0 + 5 * P_, "J2": 10.0 + 6 * P_, "J3": 10.0 + 7 * P_}
JNET = {"J1": ("+54V", "GND54"), "J2": ("OUT54_1", "GND54"), "J3": ("OUT54_2", "GND54"),
        "J4": ("OUT12_1", "GND"), "J5": ("OUT12_2", "GND"), "J6": ("OUT12_3", "GND"),
        "J7": ("OUT12_4", "GND"), "J8": ("+5V", "GND")}
JSHORT = {"J1": "54V IN", "J2": "54V 1", "J3": "54V 2", "J4": "12V 1", "J5": "12V 2", "J6": "12V 3",
          "J7": "12V 4", "J8": "5V"}
JVAL = {"J1": "54V IN", "J2": "54V OUT1", "J3": "54V OUT2", "J4": "12V OUT1", "J5": "12V OUT2",
        "J6": "12V OUT3", "J7": "12V OUT4", "J8": "5V OUT"}
J = {}
for ref, x in JX.items():
    m = place(*VH2, ref, x, JY, 0, "JST B2P-VH")
    setnet(m, 1, JNET[ref][0]); setnet(m, 2, JNET[ref][1])
    m.Reference().SetVisible(False)
    J[ref] = m

# --- J10: 12 V input from the LOP PSU, JST VH 6-pin on the right edge (pins 1-3 +12V, 4-6 GND)
J10X, J10Y = W - 5.8, 10.0
J10 = place(*VH6, "J10", J10X, J10Y, 270, "JST B6P-VH")
for n in (1, 2, 3): setnet(J10, n, "+12V")
for n in (4, 5, 6): setnet(J10, n, "GND")
J10.Reference().SetVisible(False)

# --- 54 V fuses (5x20) for the two 54 V outputs; top pad = +54V bus
Ft = JY - 30.2
F = {}
for ref, jref in (("F2", "J2"), ("F3", "J3")):
    m = place("Fuse", "Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open", ref, JX[jref], Ft, 270, "5x20 T 2.5A")
    setnet(m, 1, "+54V"); setnet(m, 2, JNET[jref][0])
    F[ref] = m

# --- 12 V output fuses (ATM mini blade)
Fy = JY - 19.4
for ref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", ref, JX[jref], Fy, 270, "ATM 5A")
    setnet(m, 1, "+12V"); setnet(m, 2, JNET[jref][0])
    F[ref] = m
# Pololu feed fuse
m = place("Fuse", "Fuseholder_Blade_Mini_Keystone_3568", "F8", 60.0, 27.0, 0, "ATM 5A")
setnet(m, 1, "+12V"); setnet(m, 2, "12V_PL"); F["F8"] = m

# --- 12 V bulk caps near the input
C5 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C5", 88.0, 13.0, 0, "470uF 16V polymer")
C6 = place("Capacitor_THT", "CP_Radial_D8.0mm_P3.50mm", "C6", 88.0, 25.0, 0, "470uF 16V polymer")
for c in (C5, C6):
    setnet(c, 1, "+12V"); setnet(c, 2, "GND")

# --- Pololu D24V90F5 on M2 standoffs, horizontal, top-left
PX0, PY0 = 15.0, 2.0
pcx, pcy = PX0 + 20.3, PY0 + 10.15
for i, (dx, dy) in enumerate(((-17.78, -7.62), (17.78, -7.62), (-17.78, 7.62), (17.78, 7.62))):
    place("MountingHole", "MountingHole_2.2mm_M2", "H%d" % (5 + i), pcx + dx, pcy + dy, 0, "M2 standoff").Reference().SetVisible(False)
U2 = custom_fp("U2", "Pololu_D24V90F5_outline", [], outline=(PX0, PY0, PX0 + 40.6, PY0 + 20.3), silk_label=(pcx, pcy - 3), crtyd=False)
text("POLOLU D24V90F5", pcx, pcy, 1.2)
text("on M2 x10mm", pcx, pcy + 2, 0.9)
WP = 3.6; WD = 1.8
P1 = custom_fp("P1", "WIREPAD", [(1, 74.0, 33.3, WP, WD)], silk_label=(74.0, 36.4))
P2 = custom_fp("P2", "WIREPAD", [(1, 66.5, 33.3, WP, WD)], silk_label=(66.5, 36.4))
P3 = custom_fp("P3", "WIREPAD", [(1, 10.0, 12.0, WP, WD)], silk_label=(10.0, 8.8))
P4 = custom_fp("P4", "WIREPAD", [(1, 6.0, 19.0, WP, WD)], silk_label=(6.0, 15.7))
setnet(P1, 1, "12V_PL"); setnet(P2, 1, "GND"); setnet(P3, 1, "+5V"); setnet(P4, 1, "GND")
for _p in (P1, P2, P3, P4): _p.Reference().SetVisible(False)
text("VIN", 77.6, 33.3, 1.0); text("GND", 62.6, 33.3, 1.0)
text("VOUT", 10.0, 8.8, 1.0); text("GND", 6.0, 15.7, 1.0)

# --- J9: 4-pin Molex 8981 header on the left edge (straight or right-angle; tab holes for R/A)
MX, MY = 8.0, 30.0
J9 = custom_fp("J9", "Molex_8981_1x04_P5.08mm_Horizontal",
               [(i + 1, MX, MY + 5.08 * i, 3.0, 1.7) for i in range(4)]
               + [("MP", MX - 5.08, MY - 5.08, 3.0, 1.7), ("MP", MX - 5.08, MY + 15.24 + 5.08, 3.0, 1.7)],
               outline=(0.4, MY - 6.6, MX + 4.5, MY + 15.24 + 6.6), silk_label=(MX + 4.5, MY - 8.0))
for i, nm in enumerate(("+5V", "GND", "GND", "+5V")):
    setnet(J9, i + 1, nm)
setnet(J9, "MP", "GND")
text("5V AUX", MX - 1.0, MY + 7.6, 1.1, rot=90, bold=True)

# --- LED headers (Dupont 2.54 mm): pin 1 = LED anode via resistor, pin 2 = cathode
R1 = place("Resistor_SMD", "R_1206_3216Metric", "R1", 65.5, 45.5, 270, "47k")
D2 = place(*HDR, "D2", 65.5, 50.5, 0, "LED 54V header")
setnet(R1, 1, "+54V"); setnet(R1, 2, "LED54"); setnet(D2, 1, "LED54"); setnet(D2, 2, "GND54")
R2 = place("Resistor_SMD", "R_1206_3216Metric", "R2", 40.0, 31.0, 0, "4.7k")
D3 = place(*HDR, "D3", 44.6, 31.0, 90, "LED 12V header")
setnet(R2, 1, "+12V"); setnet(R2, 2, "LED12"); setnet(D3, 1, "LED12"); setnet(D3, 2, "GND")
R3 = place("Resistor_SMD", "R_1206_3216Metric", "R3", 7.0, 56.0, 180, "1k")
D4 = place(*HDR, "D4", 5.54, 59.5, 0, "LED 5V header")
setnet(R3, 1, "+5V"); setnet(R3, 2, "LED5"); setnet(D4, 1, "LED5"); setnet(D4, 2, "GND")

# --- optional ground tie 54V- <-> GND (bottom, open = isolated)
JP2 = place("Jumper", "SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "JP2", 62.75, 56.0, 0, "GND_TIE", layer_back=True)
setnet(JP2, 1, "GND"); setnet(JP2, 2, "GND54")

# --- M3 mounting holes
for i, (x, y) in enumerate(((4, 4), (W - 4, 4), (4, H - 4.5), (W - 4, H - 4.5))):
    place("MountingHole", "MountingHole_3.2mm_M3", "H%d" % (1 + i), x, y, 0, "M3").Reference().SetVisible(False)

# ======================= ROUTING =======================
def near(m, num, target_x=None):
    ps = [padpos(m, num, i) for i in range(len(pads(m, num)))]
    if target_x is None:
        return ps[0]
    return min(ps, key=lambda q: abs(q[0] - target_x))

# fuse -> connector
for fref, jref in (("F2", "J2"), ("F3", "J3")):
    a = near(F[fref], 2); c = padpos(J[jref], 1)
    track([a, (c[0], a[1]), c] if abs(a[0] - c[0]) > 0.01 else [a, c], JNET[jref][0], 3.0)
for fref, jref in (("F4", "J4"), ("F5", "J5"), ("F6", "J6"), ("F7", "J7")):
    a = near(F[fref], 2, JX[jref]); c = padpos(J[jref], 1)
    track([a, (c[0], a[1]), c] if abs(a[0] - c[0]) > 0.01 else [a, c], JNET[jref][0], 3.0)
# blade holders: both pins of each clip are one contact
for fref in ("F4", "F5", "F6", "F7", "F8"):
    for num in (1, 2):
        ps = [padpos(F[fref], num, i) for i in range(len(pads(F[fref], num)))]
        track(ps, F[fref].FindPadByNumber(str(num)).GetNetname(), 2.0)
# 54 V input: J1 pin 1 up into the +54V pour
c = padpos(J["J1"], 1); track([c, (c[0], Ft + 4.0)], "+54V", 3.0)
# F8 -> P1 (Pololu VIN)
a = near(F["F8"], 2, 74.0); track([a, (74.0, a[1]), (74.0, 33.3)], "12V_PL", 2.0)
# 5 V trunk on the top layer, left column: P3 -> J9 pins 1/4 -> J8 pin 1
c8 = padpos(J["J8"], 1)
track([(10.0, 12.0), (12.0, 14.0), (12.0, MY), (12.0, MY + 15.24), (12.0, 66.0), (c8[0], 68.5), c8], "+5V", 3.0)
track([(12.0, MY), (MX, MY)], "+5V", 3.0)
track([(12.0, MY + 15.24), (MX, MY + 15.24)], "+5V", 3.0)
track([padpos(R3, 1), (12.0, padpos(R3, 1)[1])], "+5V", 0.6)
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
X54 = 63.5          # 54 V section starts here (right/bottom block)
Y54 = 38.0
# top: +12V (from J10 across the top, down to the 12V fuses)
zone("+12V", pcbnew.F_Cu, [(15.5, e), (W - e, e), (W - e, Y54 - 2.5), (X54 - 2.0, Y54 - 2.5),
                          (X54 - 2.0, Fy + 3.0), (15.5, Fy + 3.0)])
# top: +54V bus around the fuse tops
zone("+54V", pcbnew.F_Cu, [(X54, Y54), (W - e, Y54), (W - e, Ft + 4.0), (X54, Ft + 4.0)])
# bottom: GND (12 V / 5 V) everywhere except the 54 V block; GND54 in the 54 V block (1.5 mm gap)
zone("GND", pcbnew.B_Cu, [(e, e), (W - e, e), (W - e, Y54 - 1.5), (X54 - 1.5, Y54 - 1.5),
                         (X54 - 1.5, H - e), (e, H - e)])
zone("GND54", pcbnew.B_Cu, [(X54, Y54), (W - e, Y54), (W - e, H - e), (X54, H - e)])

# copper keep-out rings around the M3 mounting holes
import math
for (hx, hy) in ((4, 4), (W - 4, 4), (4, H - 4.5), (W - 4, H - 4.5)):
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
for ref, x in JX.items():
    text(JSHORT[ref], x + 7.5, JY - 6.6, 0.9, rot=90, bold=True)
    text("+", x - 2.4, JY, 1.0, bold=True)
    text("+", x - 2.4, JY, 1.0, layer=pcbnew.B_SilkS, bold=True)
    text("-", x + 3.96 + 2.4, JY, 1.0, layer=pcbnew.B_SilkS, bold=True)
    text(JVAL[ref], x + 1.98, JY + 3.6, 1.0, layer=pcbnew.B_SilkS, bold=True)
for i, lab in enumerate(("+12V", "+12V", "+12V", "GND", "GND", "GND")):
    q = padpos(J10, i + 1); text(lab, q[0] - 4.6, q[1], 0.9)
text("12V IN", J10X - 4.6, J10Y - 3.6, 1.0, bold=True)
for _d in (D2, D3, D4):
    _q = padpos(_d, 1); text("+", _q[0] + (-1.9 if _d in (D2, D4) else 0), _q[1] + (0 if _d in (D2, D4) else -1.9), 1.0, bold=True)
text("54V", 65.5, 55.6, 0.9); text("12V", 49.0, 31.0, 0.9); text("5V", 9.0, 61.0, 0.9)
for ref in ("J2", "J3"):
    text("2.5A", JX[ref] - 4.2, Ft + 11.0, 1.0, rot=90)
for ref in ("J4", "J5", "J6", "J7"):
    text("5A", JX[ref] + 5.6, Fy + 5.0, 1.0, rot=90)
text("5A", 60.0, 23.6, 1.0)
B = pcbnew.B_SilkS
text("RACK POWER BOARD v2", 38, 38.0, 2.0, layer=B, bold=True)
text("12V in -> 12V x4 / 5V, 54V passthrough", 38, 41.2, 1.2, layer=B)
text("2 layers, 2oz Cu, 1.6mm", 38, 43.4, 1.1, layer=B)
text("F2/F3 2.5A T 5x20, F4-F8 ATM 5A", 38, 45.6, 1.1, layer=B)
text("JP2: bridge to tie 54V- to GND", 62.75, 60.0, 0.9, layer=B)

b.Save(OUT)
print("saved", OUT)
