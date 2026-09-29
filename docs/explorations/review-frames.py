#!/usr/bin/env python3
"""
Render the fold at named moments and stitch them, plus a latch close-up.

    ./review-frames.py [out-dir]

Replaces review-frames.sh, which rendered a 440px viewport against a 460px
canvas and so cropped the right-hand side of the crate out of every frame.
Moments are given in milliseconds, because the timing is authored that way.
"""
import os, subprocess, sys, pathlib
from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
RENDER = HERE.parent.parent / "lib" / "render.sh"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/crate-review")
OUT.mkdir(parents=True, exist_ok=True)
TOTAL = 1890
MOMENTS = [(0, "rest"), (20, "first frame"), (40, "squeeze begins"),
           (80, "squeezing"), (130, "front: squeezed"), (180, "front: releasing"),
           (240, "front: popped free"), (500, "front: lowering"),
           (760, "front down"), (770, "back: squeezed"),
           (880, "back: popped free"), (1150, "back: lowering"),
           (1400, "back down"), (1510, "left folding"), (1720, "right folding"),
           (1890, "flat")]
# Unfolding plays the same positions in reverse, so these frames are also
# every frame of the unfold; the first row is its last quarter second.

def shot(ms, scale):
    out = OUT / f"f-{ms:04d}-{scale}x.png"
    env = dict(os.environ, WEBGL="1")
    subprocess.run([str(RENDER), f"fold-three.html?t={ms / TOTAL:.5f}", str(out),
                    "580", "640", str(scale)], cwd=HERE, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(out).convert("RGBA")
    bg = Image.new("RGBA", im.size, (20, 22, 26, 255))
    return Image.alpha_composite(bg, im).convert("RGB")

def crate_box(im):
    small = im.resize((im.width // 4, im.height // 4))
    px = small.load()
    xs, ys = [], []
    for y in range(small.height):
        for x in range(small.width):
            r, g, b = px[x, y]
            if r > 70 and r > g + 22 and r > b + 22:
                xs.append(x); ys.append(y)
    return (min(xs) * 4, min(ys) * 4, max(xs) * 4 + 4, max(ys) * 4 + 4)

frames = [(ms, label, shot(ms, 1)) for ms, label in MOMENTS]
# one crop window for every frame, so motion reads as motion
boxes = [crate_box(f) for _, _, f in frames]
x0 = max(0, min(b[0] for b in boxes) - 14); y0 = max(0, min(b[1] for b in boxes) - 14)
x1 = max(b[2] for b in boxes) + 14;          y1 = max(b[3] for b in boxes) + 14
cw, ch = x1 - x0, y1 - y0
cols = 6
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw, rows * (ch + 30)), (16, 18, 22))
d = ImageDraw.Draw(sheet)
for i, (ms, label, f) in enumerate(frames):
    cx, cy = (i % cols) * cw, (i // cols) * (ch + 30)
    sheet.paste(f.crop((x0, y0, x1, y1)), (cx, cy))
    d.text((cx + 10, cy + ch + 8), f"{ms} ms  {label}", fill=(233, 236, 241))
sheet.save(OUT / "sequence.png")

# latch close-up: the right-hand tongue, at rest and squeezed
tiles = []
for ms, label in ((0, "rest: tongue out, catch engaged"), (130, "squeezed: tongue in, catch clear")):
    f = shot(ms, 3)
    bx = crate_box(f)
    w = bx[2] - bx[0]
    box = (bx[2] - int(w * 0.20), bx[1] + int((bx[3] - bx[1]) * 0.24),
           bx[2] + int(w * 0.06), bx[1] + int((bx[3] - bx[1]) * 0.62))
    tiles.append((label, f.crop(box)))
tw = max(t.width for _, t in tiles); th = max(t.height for _, t in tiles)
lz = Image.new("RGB", (tw * 2 + 30, th + 34), (16, 18, 22))
d = ImageDraw.Draw(lz)
for i, (label, t) in enumerate(tiles):
    lz.paste(t, (10 + i * (tw + 10), 6))
    d.text((10 + i * (tw + 10), th + 14), label, fill=(233, 236, 241))
lz.save(OUT / "latch.png")
# the four corners at every moment, enlarged: what the eye goes to
f2 = {ms: shot(ms, 2) for ms, _ in MOMENTS[:8]}
bx = crate_box(f2[0])
cw2, ch2 = (bx[2] - bx[0]) // 4, (bx[3] - bx[1]) // 3
spots = [(bx[0] - 20, bx[1] - 20), (bx[2] - cw2 + 20, bx[1] + ch2 // 3),
         (bx[0] - 20, bx[3] - ch2 + 20), (bx[2] - cw2 + 20, bx[3] - ch2 + 20)]
cs = Image.new("RGB", (len(f2) * (cw2 + 4), 4 * (ch2 + 4) + 24), (16, 18, 22))
d = ImageDraw.Draw(cs)
for i, (ms, f) in enumerate(f2.items()):
    for j, (x, y) in enumerate(spots):
        cs.paste(f.crop((x, y, x + cw2, y + ch2)), (i * (cw2 + 4), j * (ch2 + 4)))
    d.text((i * (cw2 + 4) + 6, 4 * (ch2 + 4) + 6), f"{ms} ms", fill=(233, 236, 241))
cs.save(OUT / "corners.png")
print("corners :", OUT / "corners.png", cs.size)
print("sequence:", OUT / "sequence.png", sheet.size)
print("latch   :", OUT / "latch.png", lz.size)
