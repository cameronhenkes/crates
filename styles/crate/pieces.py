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
DEPTH = 950      # deeper than the walls are tall, or a folded wall
                 # covers the whole floor and the crate reads bottomless
RIM = 54         # the base's upstanding perimeter, which the walls hinge into
WALL_T = 13      # wall thickness; the footprint is W + WALL_T wide because
                 # the sides sit outboard of the front
FOOT_W = None    # set in main() once the palette colour is known


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
    """A crate panel in the FRONT's vocabulary, at any aspect.

    An earlier version drew the walls with the piano-key slots seen in the
    reference photo. Truthful to the object, but the front of this crate is
    the icon -- rounded silhouette, rails down each edge, a double-framed
    panel, a slot grid, a bottom rail with feet -- and a side in a different
    language does not read as the same object. Consistency with the front
    wins, so this draws the icon's body at whatever width and height is asked.
    """
    from generate import G
    sw, sh, sr = G["SLOT_W"], G["SLOT_H"], G["SLOT_R"]
    bev = 3.2
    r = min(G["R_BR"], w * 0.09, h * 0.09)
    rail = max(46, w * 0.115)
    flange = max(18, h * 0.030)
    foot = max(40, h * 0.115)
    o = [f'<rect x="0" y="0" width="{w}" height="{h}" rx="{r:.0f}" fill="{c["base"]}"/>']

    px0, px1 = rail + 4, w - rail - 4
    py0, py1 = flange + 4, h - foot - 4

    # recessed floor, double-framed -- the front's defining border
    o.append(f'<rect x="{px0:.1f}" y="{py0:.1f}" width="{px1-px0:.1f}" '
             f'height="{py1-py0:.1f}" rx="12" fill="{c["edge"]}"/>')
    o.append(f'<rect x="{px0+1.5:.1f}" y="{py0+1.5:.1f}" width="{px1-px0-3:.1f}" '
             f'height="{py1-py0-3:.1f}" rx="11" fill="none" stroke="{c["cav"]}" '
             f'stroke-width="3" stroke-opacity=".5"/>')
    o.append(f'<rect x="{px0+12:.1f}" y="{py0+12:.1f}" width="{px1-px0-24:.1f}" '
             f'height="{py1-py0-24:.1f}" rx="7" fill="none" stroke="{c["hi"]}" '
             f'stroke-width="3" stroke-opacity=".6"/>')

    # the folded-wall ladder down each edge, as on the icon's rails
    n = max(3, int((py1 - py0) / 78))
    pitch = (py1 - py0) / n
    for i in range(n):
        ry, rh = py0 + i * pitch + 4, pitch - 12
        for rx in (10, w - rail + 8):
            o.append(f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rail-20:.1f}" '
                     f'height="{rh:.1f}" rx="5" fill="{c["edge"]}" fill-opacity=".55"/>')
            o.append(f'<rect x="{rx:.1f}" y="{ry-2:.1f}" width="{rail-20:.1f}" '
                     f'height="{rh:.1f}" rx="5" fill="none" stroke="{c["hi"]}" '
                     f'stroke-width="2" stroke-opacity=".45"/>')

    # centre divider
    dx, dw = w / 2, 18
    o.append(f'<rect x="{dx-dw/2:.1f}" y="{py0:.1f}" width="{dw}" '
             f'height="{py1-py0:.1f}" fill="{c["base"]}"/>')
    o.append(f'<rect x="{dx-dw/2:.1f}" y="{py0:.1f}" width="3" '
             f'height="{py1-py0:.1f}" fill="{c["hi"]}" fill-opacity=".85"/>')

    # the slot grid, front's slot size and bevel
    pad = 22
    for sx0, sx1 in ((px0+pad, dx-dw/2-pad), (dx+dw/2+pad, px1-pad)):
        nc = max(2, int((sx1-sx0) / 34))
        nr = max(2, int((py1-py0-2*pad) / 100))
        cp = (sx1-sx0) / nc
        rp = (py1-py0-2*pad-sh) / max(nr-1, 1)
        for ri in range(nr):
            y = py0 + pad + ri * rp
            for i in range(nc):
                x = sx0 + i * cp + (cp - sw) / 2
                wp = bev * 1.6
                o.append(f'<rect x="{x-wp:.1f}" y="{y-wp:.1f}" '
                         f'width="{sw+wp*2:.1f}" height="{sh+wp*2:.1f}" '
                         f'rx="{sr+wp:.1f}" fill="{c["hi"]}" fill-opacity=".5"/>')
                o.append(f'<rect x="{x-bev:.1f}" y="{y-bev:.1f}" width="{sw}" '
                         f'height="{sh}" rx="{sr}" fill="{c["hi"]}"/>')
                o.append(f'<rect x="{x+bev:.1f}" y="{y+bev*.8:.1f}" width="{sw}" '
                         f'height="{sh}" rx="{sr}" fill="{c["cav"]}"/>')
                o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sw}" '
                         f'height="{sh}" rx="{sr}" fill="{c["cav"]}" fill-opacity=".92"/>')

    # Latch grooves. On the real crate the end walls carry a catch that drops
    # into a recessed channel on the side wall -- Cameron: "it's a groove".
    # A vertical channel inboard of each corner post, with a lit near edge and
    # a shadowed far one so it reads as cut into the moulding rather than
    # drawn on it, plus the catch step partway down.
    for gx in (rail * 0.40, w - rail * 0.40 - 13):
        o.append(f'<rect x="{gx:.1f}" y="{flange+10:.1f}" width="13" '
                 f'height="{h-foot-flange-20:.1f}" rx="5" fill="{c["cav"]}" '
                 f'fill-opacity=".55"/>')
        o.append(f'<rect x="{gx:.1f}" y="{flange+10:.1f}" width="3" '
                 f'height="{h-foot-flange-20:.1f}" rx="1.5" fill="{c["deep"]}" '
                 f'fill-opacity=".6"/>')
        o.append(f'<rect x="{gx+10:.1f}" y="{flange+10:.1f}" width="3" '
                 f'height="{h-foot-flange-20:.1f}" rx="1.5" fill="{c["hi"]}" '
                 f'fill-opacity=".5"/>')
        # the catch itself, a step across the groove
        cy = flange + (h - foot - flange) * 0.34
        o.append(f'<rect x="{gx-4:.1f}" y="{cy:.1f}" width="21" height="22" '
                 f'rx="5" fill="{c["lit"]}" stroke="{c["deep"]}" '
                 f'stroke-width="2" stroke-opacity=".45"/>')

    # top rim and bottom rail with feet, as the front has
    o.append(f'<rect x="0" y="0" width="{w}" height="{flange:.1f}" fill="{c["lit"]}"/>')
    o.append(f'<rect x="0" y="0" width="{w}" height="3" fill="{c["hi"]}"/>')
    o.append(f'<rect x="0" y="{h-foot:.1f}" width="{w}" height="{foot:.1f}" fill="{c["base"]}"/>')
    o.append(f'<rect x="0" y="{h-foot:.1f}" width="{w}" height="3" fill="{c["hi"]}" fill-opacity=".8"/>')
    nf = max(2, int(w / 230))
    fw = w * 0.095
    for i in range(nf):
        fx = w * (i + 1) / (nf + 1) - fw / 2
        o.append(f'<rect x="{fx:.1f}" y="{h-foot+4:.1f}" width="{fw:.1f}" '
                 f'height="{foot*0.6:.1f}" rx="8" fill="{c["lit"]}" fill-opacity=".5" '
                 f'stroke="{c["deep"]}" stroke-width="2" stroke-opacity=".3"/>')

    # Hinge knuckles along the bottom edge. The wall does not hinge on a flat
    # plane -- it seats into sockets in the base's perimeter rim, and these
    # are the pins that do it. Without them a wall reads as a loose panel
    # standing near the base rather than attached to it.
    kn = max(3, int(w / 150))
    kw = w * 0.055
    for i in range(kn):
        kx = w * (i + 0.5) / kn - kw / 2
        o.append(f'<rect x="{kx:.1f}" y="{h-14:.1f}" width="{kw:.1f}" '
                 f'height="18" rx="7" fill="{c["lit"]}" stroke="{c["deep"]}" '
                 f'stroke-width="2" stroke-opacity=".5"/>')
        o.append(f'<rect x="{kx+kw*0.3:.1f}" y="{h-10:.1f}" width="{kw*0.4:.1f}" '
                 f'height="7" rx="3.5" fill="{c["cav"]}" fill-opacity=".5"/>')

    o.append(f'<rect x="0" y="0" width="{w}" height="{h}" rx="{r:.0f}" fill="none" '
             f'stroke="{c["edge"]}" stroke-width="2" stroke-opacity=".7"/>')
    return wrap(w, h, "".join(o))


def rim_piece(length, height, c):
    """A run of the base's perimeter rim, with the hinge sockets in it."""
    o = [f'<rect x="0" y="0" width="{length}" height="{height}" fill="{c["base"]}"/>']
    o.append(f'<rect x="0" y="0" width="{length}" height="4" fill="{c["hi"]}"/>')
    o.append(f'<rect x="0" y="{height-5}" width="{length}" height="5" '
             f'fill="{c["deep"]}" fill-opacity=".45"/>')
    n = max(3, int(length / 150))
    sw = length * 0.055 + 8
    for i in range(n):
        sx = length * (i + 0.5) / n - sw / 2
        o.append(f'<rect x="{sx:.1f}" y="3" width="{sw:.1f}" '
                 f'height="{height-8:.1f}" rx="6" fill="{c["cav"]}" fill-opacity=".5"/>')
        o.append(f'<rect x="{sx:.1f}" y="3" width="3" height="{height-8:.1f}" '
                 f'rx="1.5" fill="{c["deep"]}" fill-opacity=".5"/>')
    return wrap(length, height, "".join(o))


def floor_piece(w, d, c):
    """The crate floor, in the same grid vocabulary as the front.

    The first version drew tiny slots that rendered as specks and read as
    nothing at all -- which is why the crate looked bottomless. This is the
    front's own language: a double-framed panel, a centre rib, and the same
    slot size and bevels.
    """
    from generate import G
    sw, sh, sr = G["SLOT_W"], G["SLOT_H"], G["SLOT_R"]
    bev = 3.2
    rail = 52
    o = [f'<rect x="0" y="0" width="{w}" height="{d}" rx="36" '
         f'fill="{c["base"]}"/>']
    px0, px1, py0, py1 = rail, w - rail, rail, d - rail
    o.append(f'<rect x="{px0}" y="{py0}" width="{px1-px0}" height="{py1-py0}" '
             f'rx="12" fill="{c["edge"]}"/>')
    o.append(f'<rect x="{px0+1.5}" y="{py0+1.5}" width="{px1-px0-3}" '
             f'height="{py1-py0-3}" rx="11" fill="none" stroke="{c["cav"]}" '
             f'stroke-width="3" stroke-opacity=".45"/>')
    o.append(f'<rect x="{px0+12}" y="{py0+12}" width="{px1-px0-24}" '
             f'height="{py1-py0-24}" rx="7" fill="none" stroke="{c["hi"]}" '
             f'stroke-width="3" stroke-opacity=".55"/>')
    # centre rib, as on the crate base
    dx, dw = w / 2, 20
    o.append(f'<rect x="{dx-dw/2}" y="{py0}" width="{dw}" height="{py1-py0}" '
             f'fill="{c["base"]}"/>')
    o.append(f'<rect x="{dx-dw/2}" y="{py0}" width="3" height="{py1-py0}" '
             f'fill="{c["hi"]}" fill-opacity=".8"/>')
    # the slot grid, front's slot size and bevel
    pad = 26
    for sx0, sx1 in ((px0+pad, dx-dw/2-pad), (dx+dw/2+pad, px1-pad)):
        cols = max(4, int((sx1-sx0) / 34))
        rows = max(3, int((py1-py0-2*pad) / 96))
        cp = (sx1-sx0) / cols
        rp = (py1-py0-2*pad-sh) / max(rows-1, 1)
        for r in range(rows):
            y = py0 + pad + r * rp
            for i in range(cols):
                x = sx0 + i * cp + (cp - sw) / 2
                wp = bev * 1.6
                o.append(f'<rect x="{x-wp:.1f}" y="{y-wp:.1f}" '
                         f'width="{sw+wp*2:.1f}" height="{sh+wp*2:.1f}" '
                         f'rx="{sr+wp:.1f}" fill="{c["hi"]}" fill-opacity=".5"/>')
                o.append(f'<rect x="{x-bev:.1f}" y="{y-bev:.1f}" width="{sw}" '
                         f'height="{sh}" rx="{sr}" fill="{c["hi"]}"/>')
                o.append(f'<rect x="{x+bev:.1f}" y="{y+bev*.8:.1f}" width="{sw}" '
                         f'height="{sh}" rx="{sr}" fill="{c["cav"]}"/>')
                o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sw}" '
                         f'height="{sh}" rx="{sr}" fill="{c["cav"]}" '
                         f'fill-opacity=".9"/>')
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
    # The sides sit OUTBOARD of the front, so wherever the front's silhouette
    # curves in at a corner the side is left exposed as a nub. Dropping their
    # top below where that curve starts hides it, and side walls slightly
    # lower than the end walls is normal on a real crate anyway.
    SIDE_H = G["H"] - G["BODY_TOP"] - G["R_TR"] - 39
    # the side spans the base between the front and back walls
    (out / "side.svg").write_text(panel_art(DEPTH - 38, SIDE_H, c, 7, 4))
    # the floor and the long rim span the FOOTPRINT, not the front's
    # width -- the sides sit outboard, so it is W + WALL_T
    foot = G["W"] + 39
    (out / "floor.svg").write_text(floor_piece(foot, DEPTH, c))
    for name, L in (("long", G["W"]), ("short", G["H"])):
        for face in ("out", "in"):
            (out / f"wall-{name}-{face}.svg").write_text(wall_piece(L, c, face))
    print(f"wrote base + 4 wall faces to {out}  (wall height {WALL_H})")


if __name__ == "__main__":
    main()
