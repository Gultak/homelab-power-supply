#!/usr/bin/env python3
"""Render top/bottom PNGs of a KiCad board on black, cropped to the outline.
usage: render.py <board.kicad_pcb> <outdir>  -> <outdir>/top.png, <outdir>/bottom.png
Bottom is mirrored (viewed from below) with B.Silkscreen composited in white.
Needs kicad-cli, rsvg-convert, Pillow."""
import subprocess, sys, tempfile, os
from PIL import Image, ImageChops
pcb, outdir = sys.argv[1], sys.argv[2]
T = tempfile.mkdtemp()
def svg(name, layers, mirror=False):
    cmd = ["kicad-cli","pcb","export","svg","-o",f"{T}/{name}.svg","--layers",layers,"--exclude-drawing-sheet","--page-size-mode","2"]
    if mirror: cmd.append("--mirror")
    subprocess.run(cmd+[pcb],check=True,capture_output=True)
    subprocess.run(["rsvg-convert","-z","4","-b","black",f"{T}/{name}.svg","-o",f"{T}/{name}.png"],check=True)
    return Image.open(f"{T}/{name}.png").convert("RGB")
def crop(im, ref):
    bb = ImageChops.difference(ref, Image.new("RGB", ref.size)).getbbox(); m = 20
    return im.crop((max(bb[0]-m,0), max(bb[1]-m,0), min(bb[2]+m,im.size[0]), min(bb[3]+m,im.size[1])))
top = svg("top","F.Cu,F.Silkscreen,Edge.Cuts"); edge = svg("edge","Edge.Cuts")
crop(top, edge).save(f"{outdir}/top.png")
bot = svg("bot","B.Cu,Edge.Cuts",True); bs = svg("bs","B.Silkscreen",True); edgeb = svg("edgeb","Edge.Cuts",True)
mask = bs.convert("L").point(lambda v: 255 if v > 40 else 0)
bot.paste(Image.new("RGB", bot.size, (255,255,255)), (0,0), mask)
crop(bot, edgeb).save(f"{outdir}/bottom.png")
