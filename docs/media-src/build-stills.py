#!/usr/bin/env python3
"""
Build the stills in docs/media that sit on a desktop.

    ./build-stills.py

Needs, in docs/media-src/local/ (ignored by git, because none of it is ours to publish as
a file):
    wallpaper.png        the system's default desktop picture, converted with sips
    finder-window.png    a real Finder window, captured with `screencapture -l`
    icons/<colour>.png   each crate icon at 1024, rendered from the generator

Every image here is the real thing over the real desktop: the Finder window is a capture,
not a drawing, and the icons are the icons. Nothing is mocked.
"""
import json, pathlib
from PIL import Image, ImageFilter, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
L = HERE / "local"
OUT = HERE.parent / "media"
PAL = json.load(open(HERE.parents[1] / "styles/crate/palette.json"))
WALL = Image.open(L / "wallpaper.png").convert("RGB")


def desk(w, h, focus=(0.5, 0.5), zoom=1.0, dim=0.0, blur=0):
    """The wallpaper, cropped to w x h about a point of interest."""
    s = max(w / WALL.width, h / WALL.height) * zoom
    im = WALL.resize((round(WALL.width * s), round(WALL.height * s)), Image.LANCZOS)
    x = round((im.width - w) * focus[0]); y = round((im.height - h) * focus[1])
    im = im.crop((x, y, x + w, y + h))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if dim:
        im = Image.blend(im, Image.new("RGB", im.size, (12, 14, 20)), dim)
    return im.convert("RGBA")


def icon(name, size):
    im = Image.open(L / "icons" / f"{name}.png").convert("RGBA")
    box = im.getbbox()
    im = im.crop(box)
    s = size / im.width
    return im.resize((size, round(im.height * s)), Image.LANCZOS)


def place(bg, im, x, y, shadow=(0, 26, 40, 0.42)):
    """Paste with a soft shadow cast from the image's own shape, holes and all."""
    dx, dy, r, a = shadow
    sh = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    mask = im.split()[3].point(lambda v: round(v * a))
    sh.paste((0, 0, 0, 255), (x + dx, y + dy), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(r))
    bg.alpha_composite(sh)
    bg.alpha_composite(im, (x, y))


def font(size, bold=False):
    for p in ("/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            f = ImageFont.truetype(p, size)
            if bold:
                try: f.set_variation_by_name("Semibold")
                except Exception: pass
            return f
        except Exception:
            continue
    return ImageFont.load_default()


def in_finder():
    W, H = 2560, 1600
    bg = desk(W, H, focus=(0.5, 0.35))
    win = Image.open(L / "finder-window.png").convert("RGBA")
    # the capture is at the screen's own 2x; it goes in at its own size, untouched
    bg.alpha_composite(win, ((W - win.width) // 2, (H - win.height) // 2 + 10))
    bg.convert("RGB").save(OUT / "in-finder.png", optimize=True)


def hero():
    W, H = 2400, 1350
    bg = desk(W, H, focus=(0.62, 0.30), zoom=1.0)
    a, b, c = icon("sage", 560), icon("butter", 700), icon("rust", 960)
    place(bg, a, 250, 560, (0, 30, 46, 0.40))
    place(bg, b, 640, 470, (0, 36, 54, 0.42))
    place(bg, c, 1180, 300, (0, 46, 66, 0.46))
    bg.convert("RGB").save(OUT / "hero.png", optimize=True)


def transparency():
    W, H = 2000, 680
    # over the bridge and the rocks: the busiest part of the picture, on purpose
    bg = desk(W, H, focus=(0.86, 0.34), zoom=1.55)
    place(bg, icon("sky", 520), 200, 150, (0, 24, 36, 0.40))
    place(bg, icon("butter", 520), 800, 150, (0, 24, 36, 0.40))
    place(bg, icon("chalk", 300), 1440, 250, (0, 18, 28, 0.40))
    bg.convert("RGB").save(OUT / "transparency.png", optimize=True)


def palette():
    W, H = 2720, 2100
    bg = desk(W, H, focus=(0.30, 0.20), zoom=1.2, dim=0.34, blur=22)
    d = ImageDraw.Draw(bg)
    names = list(PAL)
    cw, ch, x0, y0 = 620, 640, 170, 130
    for i, k in enumerate(names):
        cx, cy = x0 + (i % 4) * cw, y0 + (i // 4) * ch
        im = icon(k, 440)
        place(bg, im, cx + (cw - 440) // 2 - 50, cy, (0, 22, 34, 0.42))
        tx = cx + cw // 2 - 50
        d.text((tx, cy + 400), PAL[k]["label"], font=font(44, True), fill=(255, 255, 255, 245), anchor="ma")
        d.text((tx, cy + 462), PAL[k]["hex"].upper(), font=font(32), fill=(255, 255, 255, 170), anchor="ma")
    bg.convert("RGB").save(OUT / "palette.png", optimize=True)


for f in (in_finder, hero, transparency, palette):
    f(); print("built", f.__name__)
