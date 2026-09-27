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


def panel_art(w, h, c, cols, rows, rim="top"):
    """A crate WALL, drawn from the reference photo rather than from the floor.

    The floor and the walls do not share a pattern, which is what the earlier
    version got wrong. A wall is: a rim along the top, a band of tall slots
    with tapered ribs between them running up into that rim, then a smooth
    rail across the bottom carrying small raised feet, and a corner post at
    each end.
    """
    post = max(18, w * 0.035)
    rim_h = h * 0.050
    # slots run up INTO the rim with no gap, as they do on the real crate,
    # and they run deeper than the first attempt allowed
    slot_top, slot_bot = rim_h, h * 0.72
    rail_y = h * 0.735
    # Only the top edge of a wall is a free edge. Its vertical edges butt
    # against the neighbouring walls, so a radius there opens a notch at
    # every corner -- which is what made the corners look unjoined.
    o = [f'<path d="M 0,{h} L 0,10 A 10,10 0 0 1 10,0 L {w-10},0 '
         f'A 10,10 0 0 1 {w},10 L {w},{h} Z" fill="{c["base"]}"/>']

    # the slot band: tall openings separated by ribs that taper toward the rim,
    # which is what gives the real crate its piano-key look
    n = max(7, int(w / 58))
    pitch = (w - post * 2) / n
    sw = pitch * 0.62
    for i in range(n):
        x = post + i * pitch + (pitch - sw) / 2
        o.append(f'<path d="M {x:.1f},{slot_top:.1f} '
                 f'L {x + sw:.1f},{slot_top:.1f} '
                 f'L {x + sw:.1f},{slot_bot - sw/2:.1f} '
                 f'A {sw/2:.1f},{sw/2:.1f} 0 0 1 {x:.1f},{slot_bot - sw/2:.1f} Z" '
                 f'fill="{c["cav"]}"/>')
        # ribs catch light on their left edge and fall away to the right
        rx = x + sw
        o.append(f'<path d="M {rx:.1f},{slot_top:.1f} '
                 f'L {rx + pitch - sw:.1f},{slot_top:.1f} '
                 f'L {rx + pitch - sw - 2:.1f},{slot_bot:.1f} '
                 f'L {rx + 2:.1f},{slot_bot:.1f} Z" fill="{c["lit"]}"/>')
        o.append(f'<rect x="{rx + 1:.1f}" y="{slot_top:.1f}" width="2.5" '
                 f'height="{slot_bot - slot_top:.1f}" fill="{c["hi"]}" '
                 f'fill-opacity=".55"/>')

    # the rim the slots run up into
    o.append(f'<rect x="0" y="0" width="{w}" height="{rim_h:.1f}" rx="6" fill="{c["lit"]}"/>')
    o.append(f'<rect x="0" y="{rim_h - 3:.1f}" width="{w}" height="3" '
             f'fill="{c["deep"]}" fill-opacity=".4"/>')
    o.append(f'<rect x="4" y="2" width="{w - 8}" height="4" rx="2" fill="{c["hi"]}"/>')

    # the smooth rail across the bottom, with its raised feet
    o.append(f'<rect x="0" y="{rail_y:.1f}" width="{w}" height="{h - rail_y:.1f}" '
             f'rx="10" fill="{c["base"]}"/>')
    o.append(f'<rect x="0" y="{rail_y:.1f}" width="{w}" height="3.5" '
             f'fill="{c["hi"]}" fill-opacity=".7"/>')
    feet = max(3, int(w / 230))
    fw = w * 0.105
    for i in range(feet):
        fx = w * (i + 1) / (feet + 1) - fw / 2
        o.append(f'<rect x="{fx:.1f}" y="{rail_y - 12:.1f}" width="{fw:.1f}" '
                 f'height="{34:.0f}" rx="7" fill="{c["lit"]}" stroke="{c["deep"]}" '
                 f'stroke-width="2" stroke-opacity=".35"/>')

    # corner posts
    for px in (0, w - post):
        o.append(f'<rect x="{px:.1f}" y="{rim_h:.1f}" width="{post:.1f}" '
                 f'height="{rail_y - rim_h:.1f}" fill="{c["base"]}"/>')
        o.append(f'<rect x="{px + (post-4 if px == 0 else 0):.1f}" y="{rim_h:.1f}" '
                 f'width="4" height="{rail_y - rim_h:.1f}" fill="{c["deep"]}" '
                 f'fill-opacity=".35"/>')

    o.append(f'<path d="M 0,{h} L 0,10 A 10,10 0 0 1 10,0 L {w-10},0 '
             f'A 10,10 0 0 1 {w},10 L {w},{h} Z" fill="none" '
             f'stroke="{c["edge"]}" stroke-width="2" stroke-opacity=".7"/>')
    return wrap(w, h, "".join(o))


def floor_piece(w, d, c):
    """The crate floor, seen from inside."""
    from generate import G
    r = G["R_BR"]          # the crate's own corner radius
    o = [f'<rect x="0" y="0" width="{w}" height="{d}" rx="{r}" fill="{c["edge"]}"/>']
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
    # The back is the same moulding as the front, but cropped to the body:
    # a tab is a FOLDER affordance and belongs on the front only. Leaving it
    # on the back put a second tab in the resting silhouette, mirrored to the
    # wrong side, which no amount of texture flipping fixed cleanly.
    from generate import build as _build
    _front = _build(a.colour, None, "Crate", "full")
    (out / "back.svg").write_text(_front.replace(
        f'viewBox="0 0 {G["CANVAS"]} {G["CANVAS"]}" '
        f'width="{G["CANVAS"]}" height="{G["CANVAS"]}"',
        f'viewBox="{G["OX"]} {G["OY"] + G["BODY_TOP"]} {G["W"]} {G["H"] - G["BODY_TOP"]}" '
        f'width="{G["W"]}" height="{G["H"] - G["BODY_TOP"]}"'))
    # the side walls span the crate BODY, not the folder tab above it
    (out / "side.svg").write_text(
        panel_art(DEPTH, G["H"] - G["BODY_TOP"], c, 7, 4))
    (out / "floor.svg").write_text(floor_piece(G["W"], DEPTH, c))
    for name, L in (("long", G["W"]), ("short", G["H"])):
        for face in ("out", "in"):
            (out / f"wall-{name}-{face}.svg").write_text(wall_piece(L, c, face))
    print(f"wrote base + 4 wall faces to {out}  (wall height {WALL_H})")


if __name__ == "__main__":
    main()
