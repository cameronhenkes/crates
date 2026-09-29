#!/usr/bin/env python3
"""
Build the redline specs: docs/media/redline-dimensions.png and redline-detail.png.

    ./build-redlines.py

Every number is read from the generator's own geometry (styles/crate/generate.py), so a
redline cannot disagree with the icon it measures. Units are the generator's: the crate is
900 x 684 on a 1024 canvas.
"""
import pathlib, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "styles/crate"))
from generate import G as g

RED, PINK, INK, MUTE, BG = "#E5484D", "rgba(229,72,77,.20)", "#1F1D1B", "#77706A", "#DEDAD6"
FONT = "-apple-system, 'SF Pro Text', 'Helvetica Neue', sans-serif"
W, H, BT = g["W"], g["H"], g["BODY_TOP"]
RAIL, FL, FOOT = g["RAIL_W"], g["FLANGE_H"], g["FOOT_H"]
PX0, PX1, PY0, PY1 = RAIL + 4, W - RAIL - 4, BT + FL + 4, H - FOOT - 4
num = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")


class Sheet:
    def __init__(self, w, h, title, sub):
        self.w, self.h, self.o = w, h, []
        self.o.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
        self.o.append(f'<text x="80" y="104" font-size="40" font-weight="650" fill="{INK}">{title}</text>')
        self.o.append(f'<text x="80" y="148" font-size="22" fill="{MUTE}">{sub}</text>')

    def a(self, s): self.o.append(s)

    def band(self, x, y, w, h):
        self.a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PINK}"/>')

    def dashed(self, x, y, w, h, r=0):
        self.a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" '
               f'stroke="{RED}" stroke-width="2" stroke-dasharray="7 6"/>')

    def ext(self, x1, y1, x2, y2):
        self.a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{RED}" stroke-width="1" '
               f'stroke-opacity=".55"/>')

    def label(self, x, y, text, anchor="middle", size=24):
        self.a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="650" fill="{RED}" '
               f'text-anchor="{anchor}" dominant-baseline="central">{text}</text>')

    def dim_h(self, x1, x2, y, text, frm=None, side=-1):
        """A horizontal measure at y, with extension lines from the object at frm."""
        if frm is not None:
            self.ext(x1, frm, x1, y - side * 10); self.ext(x2, frm, x2, y - side * 10)
        self.a(f'<path d="M{x1},{y - 9}V{y + 9}M{x2},{y - 9}V{y + 9}M{x1},{y}H{x2}" '
               f'stroke="{RED}" stroke-width="2" fill="none"/>')
        self.label((x1 + x2) / 2, y + side * 24, text)

    def dim_v(self, x, y1, y2, text, frm=None, side=-1):
        if frm is not None:
            self.ext(frm, y1, x - side * 10, y1); self.ext(frm, y2, x - side * 10, y2)
        self.a(f'<path d="M{x - 9},{y1}H{x + 9}M{x - 9},{y2}H{x + 9}M{x},{y1}V{y2}" '
               f'stroke="{RED}" stroke-width="2" fill="none"/>')
        self.label(x + side * 18, (y1 + y2) / 2, text, "end" if side < 0 else "start")

    def lead(self, x1, y1, x2, y2, text, anchor="start"):
        self.a(f'<path d="M{x1},{y1}L{x2},{y2}" stroke="{RED}" stroke-width="2" fill="none"/>')
        self.a(f'<circle cx="{x1}" cy="{y1}" r="4.5" fill="{RED}"/>')
        self.label(x2 + (10 if anchor == "start" else -10), y2, text, anchor)

    def crate(self, x, y, scale=1.0, view=None):
        vx, vy, vw, vh = view or (0, 0, W, H)
        self.a(f'<svg x="{x}" y="{y}" width="{vw * scale}" height="{vh * scale}" '
               f'viewBox="{vx} {vy} {vw} {vh}"><image href="crate-sky.svg" width="{W}" height="{H}"/></svg>')

    def write(self, name):
        html = (f'<!doctype html><meta charset="utf-8"><body style="margin:0;background:{BG}">'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">' + "".join(self.o) + "</svg>")
        page = HERE / f"{name}.html"
        page.write_text(html)
        out = ROOT / "docs/media" / f"{name}.png"
        subprocess.run([str(ROOT / "lib/render.sh"), str(page), str(out), str(self.w), str(self.h), "2"],
                       check=True, stdout=subprocess.DEVNULL)
        print("built", out.relative_to(ROOT))


def dimensions():
    s = Sheet(1900, 1320, "Crate: dimensions",
              "A folder's silhouette, a crate's construction. Units are the generator's; the crate is 900 × 684.")
    X, Y = 520, 340
    # what is space, not object: beside the tab, and the three rails
    s.band(X + g["CURVE_END"], Y, W - g["CURVE_END"], BT)
    s.band(X, Y + BT + FL, RAIL, H - BT - FL - FOOT)
    s.band(X + W - RAIL, Y + BT + FL, RAIL, H - BT - FL - FOOT)
    s.band(X, Y + H - FOOT, W, FOOT)
    s.crate(X, Y)
    s.band(X, Y + BT, W, FL)
    s.dashed(X + PX0, Y + PY0, PX1 - PX0, PY1 - PY0, 12)
    # across the top: the tab
    s.dim_h(X, X + g["TAB_END"], Y - 70, num(g["TAB_END"]), frm=Y)
    s.dim_h(X + g["TAB_END"], X + g["CURVE_END"], Y - 70, num(g["CURVE_END"] - g["TAB_END"]), frm=Y + BT * 0.5)
    s.dim_h(X + g["CURVE_END"], X + W, Y - 70, num(W - g["CURVE_END"]), frm=Y + BT)
    # down the left: tab rise, flange, body, foot
    s.dim_v(X - 80, Y, Y + BT, num(BT), frm=X)
    s.dim_v(X - 80, Y + BT, Y + BT + FL, num(FL), frm=X)
    s.dim_v(X - 80, Y + BT + FL, Y + H - FOOT, num(H - BT - FL - FOOT), frm=X)
    s.dim_v(X - 80, Y + H - FOOT, Y + H, num(FOOT), frm=X)
    # down the right: the whole, and the body
    s.dim_v(X + W + 80, Y + BT, Y + H, num(H - BT), frm=X + W, side=1)
    s.dim_v(X + W + 190, Y, Y + H, num(H), side=1)
    s.ext(X + g["R_TL"], Y, X + W + 200, Y)
    s.ext(X + W, Y + H, X + W + 200, Y + H)
    # along the foot: rails, panel, the whole
    s.dim_h(X, X + RAIL, Y + H + 70, num(RAIL), frm=Y + H, side=1)
    s.dim_h(X + RAIL, X + W - RAIL, Y + H + 70, num(W - RAIL * 2), frm=Y + H, side=1)
    s.dim_h(X + W - RAIL, X + W, Y + H + 70, num(RAIL), frm=Y + H, side=1)
    s.dim_h(X, X + W, Y + H + 160, num(W), side=1)
    s.ext(X, Y + H, X, Y + H + 170); s.ext(X + W, Y + H, X + W, Y + H + 170)
    # corners
    k = 0.2929
    s.lead(X + g["R_TL"] * k, Y + g["R_TL"] * k, X - 150, Y - 120, f'r {num(g["R_TL"])}', "end")
    s.lead(X + W - g["R_TR"] * k, Y + BT + g["R_TR"] * k, X + W + 130, Y - 40, f'r {num(g["R_TR"])}')
    s.lead(X + g["R_BL"] * k, Y + H - g["R_BL"] * k, X - 150, Y + H + 110, f'r {num(g["R_BL"])}', "end")
    s.lead(X + W - g["R_BR"] * k, Y + H - g["R_BR"] * k, X + W + 130, Y + H + 110, f'r {num(g["R_BR"])}')
    s.label(X + (PX0 + PX1) / 2, Y + PY0 + 34, f"panel {num(PX1 - PX0)} × {num(PY1 - PY0)}", size=22)
    s.write("redline-dimensions")


def detail():
    s = Sheet(1900, 1420, "Crate: perforations",
              "Cut through, not painted on: the desktop shows through every one. 72 in the body, 7 in the tab.")
    sc = 2.7
    vx, vy, vw, vh = 96, 20, 380, 366
    X, Y = 330, 300
    T = lambda x, y: (X + (x - vx) * sc, Y + (y - vy) * sc)
    sw, sh, sr = g["SLOT_W"], g["SLOT_H"], g["SLOT_R"]
    pad, dx, dw = g["PANEL_PAD"], g["DIV_X"], g["DIV_W"]
    sx0, sx1 = PX0 + pad, dx - dw / 2 - pad
    cp = (sx1 - sx0) / g["COLS"]
    rp = (g["GRID_Y1"] - g["GRID_Y0"] - sh) / (g["ROWS"] - 1)
    col = lambda c: sx0 + c * cp + (cp - sw) / 2
    row = lambda r: g["GRID_Y0"] + r * rp
    bottom, right = Y + vh * sc, X + vw * sc
    s.crate(X, Y, sc, (vx, vy, vw, vh))
    # the gaps, as bands, over the artwork
    x, y = T(col(3) + sw, row(1)); s.band(x, y, (cp - sw) * sc, sh * sc)
    x, y = T(col(7), row(0) + sh); s.band(x, y, sw * sc, (rp - sh) * sc)
    x, y = T(PX0, row(1)); s.band(x, y, (col(0) - PX0) * sc, sh * sc)
    # one slot, outlined
    x, y = T(col(1), row(1)); s.dashed(x - 5, y - 5, sw * sc + 10, sh * sc + 10, sr * sc + 5)
    # along the foot, one line: inset, width, gap, pitch
    _, y1 = T(0, row(1) + sh)
    line = bottom + 70
    a, b = T(PX0, 0)[0], T(col(0), 0)[0];            s.dim_h(a, b, line, num(col(0) - PX0), frm=y1, side=1)
    a, b = T(col(1), 0)[0], T(col(1) + sw, 0)[0];    s.dim_h(a, b, line, num(sw), frm=y1, side=1)
    a, b = T(col(3) + sw, 0)[0], T(col(4), 0)[0];    s.dim_h(a, b, line, num(cp - sw), frm=y1, side=1)
    a, b = T(col(6), 0)[0], T(col(7), 0)[0];         s.dim_h(a, b, line, f"pitch {num(cp)}", frm=y1, side=1)
    # down the right: height, gap between rows, pitch
    ya, yb, yc = T(0, row(0))[1], T(0, row(0) + sh)[1], T(0, row(1))[1]
    s.dim_v(right + 70, ya, yb, num(sh), frm=T(col(8) + sw, 0)[0], side=1)
    s.dim_v(right + 70, yb, yc, num(rp - sh), frm=T(col(7) + sw, 0)[0], side=1)
    s.dim_v(right + 190, ya, yc, f"pitch {num(rp)}", side=1)
    s.ext(right, ya, right + 200, ya); s.ext(right, yc, right + 200, yc)
    # corner radius
    x, y = T(col(8) + sw - sr * 0.29, row(0) + sr * 0.29)
    s.lead(x, y, right + 60, Y + 250, f"r {num(sr)}")
    # the tab's slots, along the top
    tw, th = g["TAB_SLOT_W"], g["TAB_SLOT_H"]
    tp = (g["TAB_X1"] - g["TAB_X0"]) / g["TAB_COLS"]
    tcol = lambda c: g["TAB_X0"] + c * tp + (tp - tw) / 2
    x, y = T(tcol(1), g["TAB_Y"]); s.dashed(x - 5, y - 5, tw * sc + 10, th * sc + 10, sr * sc + 5)
    ya, yb = T(0, g["TAB_Y"])[1], T(0, g["TAB_Y"] + th)[1]
    s.dim_v(X - 70, ya, yb, num(th), frm=T(tcol(0), 0)[0])
    a, b = T(tcol(1), 0)[0], T(tcol(1) + tw, 0)[0];  s.dim_h(a, b, Y - 60, num(tw), frm=ya)
    a, b = T(tcol(4), 0)[0], T(tcol(5), 0)[0];       s.dim_h(a, b, Y - 60, f"pitch {num(tp)}", frm=ya)
    s.write("redline-detail")


dimensions(); detail()
