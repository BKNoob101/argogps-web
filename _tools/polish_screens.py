#!/usr/bin/env python3
"""Polish ArgoGPS screenshots: remove Android system nav bar (bottom ~90px),
sharpen, normalize. Keeps original layout intact."""
from PIL import Image, ImageFilter, ImageEnhance
import os

SRC = "/opt/data/argogps-web/assets/screens"
# each 572x1280. System nav bar is the bottom ~90px (3 buttons: menu/home/back)
CROP_BOTTOM = 92  # px to remove from bottom (system nav)

def polish(name):
    p = os.path.join(SRC, name)
    im = Image.open(p).convert("RGB")
    w, h = im.size
    # crop bottom system nav
    im = im.crop((0, 0, w, h - CROP_BOTTOM))
    # slight sharpen + subtle contrast to look crisper on web
    im = ImageEnhance.Sharpness(im).enhance(1.25)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    # upscale 1.5x with LANCZOS for crispness on high-dpi
    nw, nh = int(w*1.5), int((h-CROP_BOTTOM)*1.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    base = os.path.splitext(name)[0]
    out = os.path.join(SRC, base + "-polished.png")
    im.save(out, "PNG", optimize=True)
    print(base, "->", im.size, os.path.getsize(out)//1024, "KB")

for n in ["home.jpg","tagihan.jpg","riwayat.jpg","setelan.jpg"]:
    polish(n)
