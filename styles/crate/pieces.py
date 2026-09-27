#!/usr/bin/env python3
"""
Emit the crate as separate pieces, so a 3D scene can hinge each wall.

A fold happens in the axis a flat icon discards, so the only honest way to
show it is to stop faking: build the base and four walls as real planes and
let perspective do the foreshortening. This writes:

    base.svg          the floor, seen from above
    wall-long-out.svg / wall-long-in.svg    900 x WALL_H
    wall-short-out.svg / wall-short-in.svg  684 x WALL_H

Outer and inner faces are separate because you see different ones: looking
into an open crate you see the near wall's outside and the far walls' insides.
"""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate import G, shade, hex_to_oklab, silhouette

WALL_H = 232


def shades(body):
    L = hex_to_oklab(body)[0]
    b = 0.0 if L > 0.62 else (0.62 - L) * 0.20
    return dict(base=body, lit=shade(body, .030 + b * .5), hi=shade(body, .062 + b),
                spec=shade(body, .090 + b, .85), edge=shade(body, -.050),
                deep=shade(body, -.095), cav=shade(body, -.150))


def wrap(w, h, inner, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{defs}{inner}</svg>')


def base_piece(c):
    g = G
    W, H, bt = g["W"], g["H"], g["BODY_TOP"]
    sw, sh, sr = g["SLOT_W"], g["SLOT_H"], g["SLOT_R"]
    rows, cols = g["ROWS"], g["COLS"]
    gy0, gy1 = g["GRID_Y0"], g["GRID_Y1"]
    dx, dw, pad = g["DIV_X"], g["DIV_W"], g["PANEL_PAD"]
    px0, px1 = 30, W - 30
    holes, art = [], []
    art.append(f'<path d="{silhouette(g)}" fill="{c["base"]}"/>')
    art.append(f'<rect x="{px0}" y="{bt + 24}" width="{px1 - px0}" '
               f'height="{H - bt - 72}" rx="12" fill="{c["edge"]}"/>')
    art.append(f'<rect x="{dx - dw/2}" y="{bt + 24}" width="{dw}" '
               f'height="{H - bt - 72}" fill="{c["base"]}"/>')
    row_pitch = (gy1 - gy0 - sh) / max(rows - 1, 1)
    for sx0, sx1 in ((px0 + pad, dx - dw/2 - pad), (dx + dw/2 + pad, px1 - pad)):
        cp = (sx1 - sx0) / cols
        for r in range(rows):
            y = gy0 + r * row_pitch
            for i in range(cols):
                x = sx0 + i * cp + (cp - sw) / 2
                holes.append((round(x, 1), round(y, 1)))
                art.append(f'<rect x="{x-2.2:.1f}" y="{y-2.2:.1f}" width="{sw}" '
                           f'height="{sh}" rx="{sr}" fill="{c["hi"]}"/>')
                art.append(f'<rect x="{x+2.2:.1f}" y="{y+1.8:.1f}" width="{sw}" '
                           f'height="{sh}" rx="{sr}" fill="{c["cav"]}"/>')
    cuts = "".join(f'<rect x="{x}" y="{y}" width="{sw}" height="{sh}" '
                   f'rx="{sr}" fill="#000"/>' for x, y in holes)
    defs = (f'<defs><clipPath id="bs"><path d="{silhouette(g)}"/></clipPath>'
            f'<mask id="bh" maskUnits="userSpaceOnUse" x="-20" y="-20" '
            f'width="{W+40}" height="{H+40}">'
            f'<rect x="-20" y="-20" width="{W+40}" height="{H+40}" fill="#FFF"/>'
            f'{cuts}</mask></defs>')
    body = (f'<g mask="url(#bh)"><g clip-path="url(#bs)">{"".join(art)}'
            f'<path d="{silhouette(g)}" fill="none" stroke="{c["spec"]}" '
            f'stroke-width="18"/></g>'
            f'<path d="{silhouette(g)}" fill="none" stroke="{c["edge"]}" '
            f'stroke-width="2" stroke-opacity=".7"/></g>')
    return wrap(W, H, body, defs)


def wall_piece(length, c, face):
    """One wall. face 'out' is smoother; 'in' carries the recess ladder."""
    h = WALL_H
    o = [f'<rect x="0" y="0" width="{length}" height="{h}" rx="9" '
         f'fill="{c["lit"] if face == "out" else c["base"]}"/>']
    # the rim: the crate's top edge, which is the free edge of the wall
    o.append(f'<rect x="4" y="3" width="{length-8}" height="9" rx="4" fill="{c["hi"]}"/>')
    # the hinge crease at the base edge
    o.append(f'<rect x="0" y="{h-5}" width="{length}" height="5" '
             f'fill="{c["deep"]}" fill-opacity=".5"/>')
    n = max(5, int(length / 96))
    for i in range(1, n):
        x = length * i / n
        o.append(f'<rect x="{x:.1f}" y="14" width="{5 if face=="out" else 3}" '
                 f'height="{h-24}" fill="{c["deep"]}" '
                 f'fill-opacity="{.30 if face=="out" else .20}"/>')
    if face == "in":
        # inner face carries the stacked recesses you see looking into the crate
        cells = max(4, int(length / 118))
        cw = (length - 22) / cells - 9
        for i in range(cells):
            x = 11 + i * (cw + 9)
            o.append(f'<rect x="{x:.1f}" y="26" width="{cw:.1f}" height="{h-52}" '
                     f'rx="5" fill="{c["edge"]}"/>')
            o.append(f'<rect x="{x:.1f}" y="23" width="{cw:.1f}" height="{h-52}" '
                     f'rx="5" fill="none" stroke="{c["hi"]}" stroke-width="2.5" '
                     f'stroke-opacity=".6"/>')
    else:
        sw, sh = 14, 56
        cols = max(4, int(length / 84))
        for i in range(cols):
            x = 20 + (length - 40 - sw) * i / max(1, cols - 1)
            o.append(f'<rect x="{x:.1f}" y="{(h-sh)/2:.0f}" width="{sw}" '
                     f'height="{sh}" rx="5" fill="{c["cav"]}" fill-opacity=".75"/>')
    return wrap(length, h, "".join(o))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("colour")
    ap.add_argument("-d", "--dir", default=".")
    a = ap.parse_args()
    c = shades(a.colour)
    out = pathlib.Path(a.dir); out.mkdir(parents=True, exist_ok=True)
    (out / "base.svg").write_text(base_piece(c))
    for name, L in (("long", G["W"]), ("short", G["H"])):
        for face in ("out", "in"):
            (out / f"wall-{name}-{face}.svg").write_text(wall_piece(L, c, face))
    print(f"wrote base + 4 wall faces to {out}  (wall height {WALL_H})")


if __name__ == "__main__":
    main()
