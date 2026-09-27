#!/usr/bin/env python3
"""
Folding-crate folder icon generator.

Draws the crate-as-macOS-folder silhouette as a parametric SVG. Every surface
shade is derived in OKLab from one body colour, so recolouring is one argument.

    ./crate.py "#C3D2E1" -o sky.svg          # holes punched through
    ./crate.py --void "#0B0B0C" "#C3D2E1"    # holes filled solid instead
    ./crate.py --detail simple "#C3D2E1"     # art for the 16/32px icon slots

By default the perforations are real holes: they are cut out of the artwork
with a mask, so the desktop shows through them. Pass --void with a colour to
fill them instead.
"""
import argparse
import math
import sys

# ---------------------------------------------------------------- colour ----

_M1 = ((0.4122214708, 0.5363325363, 0.0514459929),
       (0.2119034982, 0.6806995451, 0.1073969566),
       (0.0883024619, 0.2817188376, 0.6299787005))
_M2 = ((0.2104542553, 0.7936177850, -0.0040720468),
       (1.9779984951, -2.4285922050, 0.4505937099),
       (0.0259040371, 0.7827717662, -0.8086757660))


def _to_linear(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _to_srgb(c):
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (abs(c) ** (1 / 2.4)) - 0.055
    return max(0, min(255, round(v * 255)))


def hex_to_oklab(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    rgb = tuple(_to_linear(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    lms = [sum(m * v for m, v in zip(row, rgb)) for row in _M1]
    lms = [math.copysign(abs(v) ** (1 / 3), v) for v in lms]
    return [sum(m * v for m, v in zip(row, lms)) for row in _M2]


def oklab_to_hex(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (v ** 3 for v in (l_, m_, s_))
    return "#%02X%02X%02X" % (
        _to_srgb(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
        _to_srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
        _to_srgb(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s),
    )


def shade(base_hex, dL, chroma=1.0):
    """Shift OKLab lightness by dL and scale chroma."""
    L, a, b = hex_to_oklab(base_hex)
    return oklab_to_hex(max(0.0, min(1.0, L + dL)), a * chroma, b * chroma)


# -------------------------------------------------------------- geometry ----
# Measured off ref/source.png. The crate is a 900x684 box inside a 1024 canvas.

G = dict(
    CANVAS=1024,
    W=900, H=684, OX=62, OY=170,
    BODY_TOP=96,                         # top edge of the main body
    TAB_END=330,                         # x where the tab's flat top ends
    CURVE_END=437,                       # x where the step lands on BODY_TOP
    R_TL=44, R_TR=54, R_BR=62, R_BL=62,  # corner radii
    WALL=12,                             # outer rim thickness
    RAIL_W=108,                          # folded side-wall width
    RAIL_BAND=30,                        # outer wall strip inside the rail
    RAIL_CELLS=9,                        # recesses stacked down the rail
    FLANGE_H=20, FOOT_H=80,              # top and bottom rail depths
    DIV_X=450, DIV_W=20,                 # centre divider
    ROWS=4, COLS=9,                      # slots: rows x cols per sub-panel
    SLOT_W=15, SLOT_H=66, SLOT_R=4.5,
    GRID_Y0=199, GRID_Y1=570,            # band the slot rows are laid into
    PANEL_PAD=14,
    TAB_COLS=7, TAB_SLOT_W=19, TAB_SLOT_H=60,
    TAB_X0=105, TAB_X1=299, TAB_Y=42,
    FEET=5, FOOT_W=76,
    LUG_AT=0.20, LUG_H=62, LUG_OUT=9,   # stacking lugs on the side walls
)

SIMPLE = dict(
    ROWS=3, COLS=5, SLOT_W=38, SLOT_H=92, SLOT_R=11,
    GRID_Y0=192, GRID_Y1=584, PANEL_PAD=18,
    TAB_COLS=4, TAB_SLOT_W=32, TAB_SLOT_H=56, TAB_X0=98, TAB_X1=306, TAB_Y=28,
    RAIL_CELLS=3, RAIL_BAND=46, DIV_W=28, WALL=16, FLANGE_H=26, FOOT_H=74,
)


def silhouette(g):
    W, H = g["W"], g["H"]
    bt, tl, tr, br, bl = g["BODY_TOP"], g["R_TL"], g["R_TR"], g["R_BR"], g["R_BL"]
    te, ce = g["TAB_END"], g["CURVE_END"]
    return (
        f"M 0,{H - bl} "
        f"L 0,{tl} A {tl},{tl} 0 0 1 {tl},0 "
        f"L {te},0 "
        f"C {te + 42},0 {ce - 42},{bt} {ce},{bt} "
        f"L {W - tr},{bt} A {tr},{tr} 0 0 1 {W},{bt + tr} "
        f"L {W},{H - br} A {br},{br} 0 0 1 {W - br},{H} "
        f"L {bl},{H} A {bl},{bl} 0 0 1 0,{H - bl} Z"
    )


# ----------------------------------------------------------------- build ----

def build(body, void_col=None, title="Crate", detail="full", parts=False):
    """void_col None punches the perforations through; a hex fills them.

    parts=True wraps each structural section in a class-bearing <g> so the
    piece can be animated independently."""
    g = dict(G)
    full = detail == "full"
    if not full:
        g.update(SIMPLE)

    W, H, OX, OY, C = g["W"], g["H"], g["OX"], g["OY"], g["CANVAS"]
    base = body
    # Dark crates need a stronger lit edge or the perforations vanish into the
    # body: there is no room left below them to darken the void further.
    body_L = hex_to_oklab(base)[0]
    boost = 0.0 if body_L > 0.62 else (0.62 - body_L) * 0.20
    lit = shade(base, +0.030 + boost * 0.5)
    hi = shade(base, +0.062 + boost)
    spec = shade(base, +0.090 + boost, 0.85)
    edge = shade(base, -0.050)
    deep = shade(base, -0.095)
    cavity = shade(base, -0.150)
    bevel = 3.2 if full else 4.2

    rail, band = g["RAIL_W"], g["RAIL_BAND"]
    flange, foot, bt = g["FLANGE_H"], g["FOOT_H"], g["BODY_TOP"]
    px0, px1 = rail + 4, W - rail - 4
    py0, py1 = bt + flange + 4, H - foot - 4
    sil = silhouette(g)

    holes = []   # geometry of every perforation, for the cut-out mask
    p = []
    a = p.append

    def g_open(cls):
        if parts: a(f'<g class="{cls}">')

    def g_close():
        if parts: a('</g>')

    def slot(x, y, w, h, r):
        holes.append((x, y, w, h, r))
        # the well the hole is sunk into: the most legible cue that these are
        # mouldings through a thick wall rather than painted-on marks
        wp = bevel * 1.6
        a(f'<rect x="{x - wp:.1f}" y="{y - wp:.1f}" width="{w + wp * 2:.1f}" '
          f'height="{h + wp * 2:.1f}" rx="{r + wp:.1f}" fill="{hi}" '
          f'fill-opacity="0.55"/>')
        a(f'<rect x="{x - bevel:.1f}" y="{y - bevel:.1f}" width="{w}" '
          f'height="{h}" rx="{r}" fill="{hi}"/>')
        a(f'<rect x="{x + bevel:.1f}" y="{y + bevel * 0.8:.1f}" width="{w}" '
          f'height="{h}" rx="{r}" fill="{cavity}"/>')
        if void_col:
            a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
              f'fill="{void_col}"/>')

    # stacking lugs, behind the shell so they read as one moulding
    lug_out, lug_h = g["LUG_OUT"], g["LUG_H"]
    if full:
        for side in (0, 1):
            lx = -lug_out if side == 0 else W - 24
            ly = bt + (H - bt) * g["LUG_AT"]
            a(f'<rect x="{lx}" y="{ly:.1f}" width="{lug_out + 24}" '
              f'height="{lug_h}" rx="11" fill="{edge}"/>')

    a(f'<path d="{sil}" fill="url(#body)"/>')
    a('<g clip-path="url(#shell)">')

    g_open('c-floor')
    # recessed floor, double-framed
    a(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" '
      f'rx="12" fill="url(#floor)"/>')
    a(f'<rect x="{px0 + 1.5}" y="{py0 + 1.5}" width="{px1 - px0 - 3}" '
      f'height="{py1 - py0 - 3}" rx="11" fill="none" stroke="{cavity}" '
      f'stroke-width="3" stroke-opacity="0.5"/>')
    a(f'<rect x="{px0 + 12}" y="{py0 + 12}" width="{px1 - px0 - 24}" '
      f'height="{py1 - py0 - 24}" rx="7" fill="none" stroke="{hi}" '
      f'stroke-width="{3 if full else 5}" stroke-opacity="0.6"/>')
    if full:
        a(f'<rect x="{px0 + 12}" y="{py0 + 15}" width="{px1 - px0 - 24}" '
          f'height="{py1 - py0 - 24}" rx="7" fill="none" stroke="{cavity}" '
          f'stroke-width="1.5" stroke-opacity="0.35"/>')

    g_close()

    # folded side walls
    for side in (0, 1):
        g_open('c-wall c-wall-left' if side == 0 else 'c-wall c-wall-right')
        x0 = 0 if side == 0 else W - rail
        a(f'<rect x="{x0}" y="{bt}" width="{rail}" height="{H - bt}" '
          f'fill="{base}"/>')
        bx = x0 if side == 0 else x0 + rail - band
        a(f'<rect x="{bx}" y="{bt}" width="{band}" height="{H - bt}" '
          f'fill="{lit}"/>')
        seam = bx + band - 2.5 if side == 0 else bx
        a(f'<rect x="{seam}" y="{bt}" width="{2.5 if full else 3.5}" '
          f'height="{H - bt}" fill="{deep}" fill-opacity="0.55"/>')
        cx0 = x0 + band + 9 if side == 0 else x0 + 9
        cw = rail - band - 18
        top, bot = bt + flange + 4, H - foot - 4
        n = g["RAIL_CELLS"]
        pitch = (bot - top) / n
        for i in range(n):
            ry, rh = top + i * pitch + 4, pitch - 10
            a(f'<rect x="{cx0}" y="{ry:.1f}" width="{cw}" height="{rh:.1f}" '
              f'rx="4" fill="{edge}" fill-opacity="0.55"/>')
            a(f'<rect x="{cx0}" y="{ry - 2:.1f}" width="{cw}" '
              f'height="{rh:.1f}" rx="4" fill="none" stroke="{hi}" '
              f'stroke-width="2" stroke-opacity="0.45"/>')
        if full:
            for i in range(1, n):
                a(f'<rect x="{bx + 5}" y="{top + i * pitch - 2:.1f}" '
                  f'width="{band - 10}" height="3" rx="1.5" fill="{deep}" '
                  f'fill-opacity="0.35"/>')
        g_close()

    g_open('c-divider')
    # centre divider
    dx, dw = g["DIV_X"], g["DIV_W"]
    a(f'<rect x="{dx - dw / 2}" y="{py0}" width="{dw}" height="{py1 - py0}" '
      f'fill="{base}"/>')
    a(f'<rect x="{dx - dw / 2}" y="{py0}" width="3" height="{py1 - py0}" '
      f'fill="{hi}" fill-opacity="0.9"/>')
    a(f'<rect x="{dx + dw / 2 - 3}" y="{py0}" width="3" height="{py1 - py0}" '
      f'fill="{cavity}" fill-opacity="0.4"/>')

    g_close()

    g_open('c-grid')
    # perforation grid
    pad = g["PANEL_PAD"]
    sw, sh, sr = g["SLOT_W"], g["SLOT_H"], g["SLOT_R"]
    rows, cols = g["ROWS"], g["COLS"]
    gy0, gy1 = g["GRID_Y0"], g["GRID_Y1"]
    row_pitch = (gy1 - gy0 - sh) / max(rows - 1, 1)
    spans = ((px0 + pad, dx - dw / 2 - pad), (dx + dw / 2 + pad, px1 - pad))
    for sx0, sx1 in spans:
        col_pitch = (sx1 - sx0) / cols
        for r in range(rows):
            y = gy0 + r * row_pitch
            for c in range(cols):
                x = sx0 + c * col_pitch + (col_pitch - sw) / 2
                slot(round(x, 1), round(y, 1), sw, sh, sr)

    g_close()

    g_open('c-tab')
    # top flange, then the tab repainted over it
    a(f'<rect x="0" y="{bt}" width="{W}" height="{flange}" fill="{lit}"/>')
    a(f'<rect x="0" y="{bt}" width="{W}" height="3" fill="{hi}"/>')
    a(f'<rect x="0" y="{bt + flange - 3}" width="{W}" height="3" '
      f'fill="{deep}" fill-opacity="0.5"/>')
    a(f'<path d="M 0,{bt + flange} L 0,{g["R_TL"]} '
      f'A {g["R_TL"]},{g["R_TL"]} 0 0 1 {g["R_TL"]},0 L {g["TAB_END"]},0 '
      f'C {g["TAB_END"] + 42},0 {g["CURVE_END"] - 42},{bt} '
      f'{g["CURVE_END"]},{bt} L {g["CURVE_END"]},{bt + flange} Z" '
      f'fill="url(#body)"/>')
    if full:
        a(f'<path d="M {g["TAB_END"]},2 C {g["TAB_END"] + 42},2 '
          f'{g["CURVE_END"] - 42},{bt + 2} {g["CURVE_END"]},{bt + 2}" '
          f'fill="none" stroke="{deep}" stroke-width="2" '
          f'stroke-opacity="0.3"/>')
    tsw, tsh = g["TAB_SLOT_W"], g["TAB_SLOT_H"]
    tpitch = (g["TAB_X1"] - g["TAB_X0"]) / g["TAB_COLS"]
    for i in range(g["TAB_COLS"]):
        x = g["TAB_X0"] + i * tpitch + (tpitch - tsw) / 2
        slot(round(x, 1), g["TAB_Y"], tsw, tsh, sr)

    g_close()

    g_open('c-foot')
    # bottom rail and fold-down feet
    a(f'<rect x="0" y="{H - foot}" width="{W}" height="{foot}" fill="{base}"/>')
    a(f'<rect x="0" y="{H - foot}" width="{W}" height="3" fill="{hi}" '
      f'fill-opacity="0.8"/>')
    if full:
        fw, n = g["FOOT_W"], g["FEET"]
        a(f'<rect x="0" y="{H - foot + 40}" width="{W}" height="2.5" '
          f'fill="{deep}" fill-opacity="0.3"/>')
        for i in range(n):
            fx = W * (i + 1) / (n + 1) - fw / 2
            a(f'<rect x="{fx:.1f}" y="{H - foot + 4}" width="{fw}" '
              f'height="44" rx="7" fill="{lit}" fill-opacity="0.4" '
              f'stroke="{deep}" stroke-width="2" stroke-opacity="0.25"/>')

    g_close()

    a(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#sheen)"/>')
    a('</g>')

    # outer rim: an inside stroke, faked by clipping a fat stroke to the shell
    a(f'<g clip-path="url(#shell)">'
      f'<path d="{sil}" fill="none" stroke="{spec}" '
      f'stroke-width="{g["WALL"] * 2}"/>'
      f'<path d="{sil}" fill="none" stroke="{deep}" stroke-width="4" '
      f'stroke-opacity="0.22" transform="translate(0,5)"/></g>')
    a(f'<path d="{sil}" fill="none" stroke="{edge}" stroke-width="2" '
      f'stroke-opacity="0.7"/>')

    # ------------------------------------------------------------ assemble --
    d = []
    d.append(f'<linearGradient id="body" x1="0.1" y1="0" x2="0.4" y2="1">'
             f'<stop offset="0" stop-color="{lit}"/>'
             f'<stop offset="0.6" stop-color="{base}"/>'
             f'<stop offset="1" stop-color="{shade(base, -0.030)}"/>'
             f'</linearGradient>')
    d.append(f'<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{shade(base, -0.040)}"/>'
             f'<stop offset="1" stop-color="{shade(base, -0.012)}"/>'
             f'</linearGradient>')
    d.append(f'<linearGradient id="sheen" x1="0.15" y1="0" x2="0.65" y2="1">'
             f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.055"/>'
             f'<stop offset="0.45" stop-color="#FFFFFF" stop-opacity="0.02"/>'
             f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>'
             f'</linearGradient>')
    d.append(f'<clipPath id="shell"><path d="{sil}"/></clipPath>')

    mask_attr = ""
    if not void_col:
        cuts = "".join(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="#000"/>' for x, y, w, h, r in holes)
        d.append(f'<mask id="holes" maskUnits="userSpaceOnUse" x="-30" '
                 f'y="-30" width="{W + 60}" height="{H + 60}">'
                 f'<rect x="-30" y="-30" width="{W + 60}" height="{H + 60}" '
                 f'fill="#FFF"/>{cuts}</mask>')
        mask_attr = ' mask="url(#holes)"'

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {C} {C}" '
        f'width="{C}" height="{C}" role="img" '
        f'aria-label="{title} crate folder">'
        f'<title>{title}</title>'
        f'<defs>{"".join(d)}</defs>'
        f'<g transform="translate({OX},{OY})"><g{mask_attr}>'
        f'{"".join(p)}'
        f'</g></g></svg>'
    )


def main():
    ap = argparse.ArgumentParser(
        description="Generate a folding-crate folder icon as SVG.")
    ap.add_argument("colour", help="crate body colour, e.g. '#C3D2E1'")
    ap.add_argument("--void", default=None,
                    help="fill the perforations with this colour instead of "
                         "cutting them through")
    ap.add_argument("--name", default="Crate", help="title / aria label")
    ap.add_argument("--detail", choices=("full", "simple"), default="full",
                    help="'simple' for the 16/32px iconset slots")
    ap.add_argument("--parts", action="store_true",
                    help="wrap structural sections in class-bearing groups, "
                         "for animation")
    ap.add_argument("-o", "--out", help="write here instead of stdout")
    args = ap.parse_args()

    svg = build(args.colour, args.void, args.name, args.detail, args.parts)
    if args.out:
        with open(args.out, "w") as f:
            f.write(svg)
    else:
        sys.stdout.write(svg)


if __name__ == "__main__":
    main()
