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
DEPTH = 720      # must be >= wall height or the walls cannot fold flat


def shades(body):
    L = hex_to_oklab(body)[0]
    b = 0.0 if L > 0.62 else (0.62 - L) * 0.20
    return dict(base=body, lit=shade(body, .030 + b * .5), hi=shade(body, .062 + b),
                spec=shade(body, .090 + b, .85), edge=shade(body, -.050),
                deep=shade(body, -.095), cav=shade(body, -.150))


def wrap(w, h, inner, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{defs}{inner}</svg>')


def base_piece(c, colour):
    """The base is the ORIGINAL icon, unchanged.

    Earlier this redrew a simplified floor, which meant the resting state of
    the 3D scene was not the icon any more. The canonical artwork is the
    default state; the walls are extra planes that only matter once it folds.
    """
    from generate import build, G
    svg = build(colour, None, "Crate", "full")
    # The icon is authored on a 1024 square with the crate inset inside it --
    # right for an app icon, wrong for a pane in a 3D scene, where every other
    # piece is tight to its content. Crop the viewBox to the crate itself so
    # the front lines up with the walls instead of floating small inside them.
    return svg.replace(
        f'viewBox="0 0 {G["CANVAS"]} {G["CANVAS"]}" '
        f'width="{G["CANVAS"]}" height="{G["CANVAS"]}"',
        f'viewBox="{G["OX"]} {G["OY"]} {G["W"]} {G["H"]}" '
        f'width="{G["W"]}" height="{G["H"]}"')


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


def inner_panel(w, h, c):
    """A plain inner face -- what you see looking INTO the crate once the
    front has folded away. Quieter than the front, because it is background."""
    o = [f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="{c["edge"]}"/>']
    o.append(f'<rect x="5" y="4" width="{w-10}" height="10" rx="5" fill="{c["hi"]}"/>')
    n = max(5, int(w / 118))
    cw = (w - 26) / n - 11
    for i in range(n):
        x = 13 + i * (cw + 11)
        o.append(f'<rect x="{x:.1f}" y="26" width="{cw:.1f}" height="{h-50}" '
                 f'rx="6" fill="{c["base"]}"/>')
        o.append(f'<rect x="{x:.1f}" y="22" width="{cw:.1f}" height="{h-50}" '
                 f'rx="6" fill="none" stroke="{c["hi"]}" stroke-width="2.5" '
                 f'stroke-opacity=".45"/>')
    return wrap(w, h, "".join(o))


def floor_piece(w, d, c):
    """The crate floor, seen from inside."""
    o = [f'<rect x="0" y="0" width="{w}" height="{d}" rx="8" fill="{c["edge"]}"/>']
    n = max(6, int(w / 96))
    for i in range(1, n):
        x = w * i / n
        o.append(f'<rect x="{x:.1f}" y="10" width="4" height="{d-20}" '
                 f'fill="{c["deep"]}" fill-opacity=".3"/>')
    sw, sh = 15, 44
    cols = max(5, int(w / 88))
    for row in (0.32, 0.68):
        for i in range(cols):
            x = 24 + (w - 48 - sw) * i / max(1, cols - 1)
            o.append(f'<rect x="{x:.1f}" y="{d*row - sh/2:.1f}" width="{sw}" '
                     f'height="{sh}" rx="5" fill="{c["cav"]}" fill-opacity=".8"/>')
    return wrap(w, d, "".join(o))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("colour")
    ap.add_argument("-d", "--dir", default=".")
    a = ap.parse_args()
    c = shades(a.colour)
    out = pathlib.Path(a.dir); out.mkdir(parents=True, exist_ok=True)
    (out / "base.svg").write_text(base_piece(c, a.colour))
    (out / "back.svg").write_text(inner_panel(G["W"], G["H"], c))
    (out / "side.svg").write_text(inner_panel(DEPTH, G["H"], c))
    (out / "floor.svg").write_text(floor_piece(G["W"], DEPTH, c))
    for name, L in (("long", G["W"]), ("short", G["H"])):
        for face in ("out", "in"):
            (out / f"wall-{name}-{face}.svg").write_text(wall_piece(L, c, face))
    print(f"wrote base + 4 wall faces to {out}  (wall height {WALL_H})")


if __name__ == "__main__":
    main()
