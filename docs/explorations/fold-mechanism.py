#!/usr/bin/env python3
"""Schematic storyboard: the real fold, then each digital option."""
import pathlib

BASE, SHORT, LONG, EDGE = "#C9765F", "#8E4534", "#B35C45", "#5E2C21"
W, H = 200, 150            # frame box
CW, CH = 132, 92           # crate footprint in plan

def frame(inner, cap):
    return (f'<figure><svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{inner}</svg>'
            f'<figcaption>{cap}</figcaption></figure>')

# ---------------------------------------------------------- side elevation --
def elev(t):
    """t: 0 upright, 1 flat. Side view, walls hinged at the base."""
    import math
    x0, y0 = (W - CW) / 2, 104
    wall_h = 44
    latch = "#F2C14E" if t == 0.15 else EDGE
    parts = [f'<rect x="{x0}" y="{y0}" width="{CW}" height="9" rx="2" fill="{BASE}"/>']
    # short walls (drawn as the near/far ends -> vertical sticks at each end)
    a_s = math.radians(90 * (1 - min(1, max(0, (t - 0.15) / 0.35))))
    for sx, d in ((x0 + 4, 1), (x0 + CW - 4, -1)):
        ex, ey = sx + d * wall_h * math.cos(a_s), y0 - wall_h * math.sin(a_s)
        parts.append(f'<line x1="{sx}" y1="{y0}" x2="{ex:.1f}" y2="{ey:.1f}" '
                     f'stroke="{SHORT}" stroke-width="7" stroke-linecap="round"/>')
    # long walls fold after
    a_l = math.radians(90 * (1 - min(1, max(0, (t - 0.5) / 0.4))))
    for sx, d in ((x0 + 16, 1), (x0 + CW - 16, -1)):
        ex, ey = sx + d * wall_h * 1.15 * math.cos(a_l), y0 - 6 - wall_h * 1.15 * math.sin(a_l)
        parts.append(f'<line x1="{sx}" y1="{y0 - 6}" x2="{ex:.1f}" y2="{ey:.1f}" '
                     f'stroke="{LONG}" stroke-width="7" stroke-linecap="round"/>')
    if t == 0.15:
        for cx in (x0 + 10, x0 + CW - 10):
            parts.append(f'<circle cx="{cx}" cy="{y0 - 30}" r="5" fill="none" '
                         f'stroke="{latch}" stroke-width="2.5"/>')
    return "".join(parts)

# --------------------------------------------------------------- option A ---
def plan(t):
    """Plan view. Short walls lay inward, then long walls over them."""
    x0, y0 = (W - CW) / 2, (H - CH) / 2
    band = 15
    s = min(1, max(0, (t - 0.12) / 0.4))     # short walls
    l = min(1, max(0, (t - 0.48) / 0.45))    # long walls
    sw = band + (CW * 0.30 - band) * s
    lw = band + (CH * 0.42 - band) * l
    p = [f'<rect x="{x0}" y="{y0}" width="{CW}" height="{CH}" rx="6" fill="{BASE}"/>']
    p.append(f'<rect x="{x0+band+2}" y="{y0+band+2}" width="{CW-2*band-4}" '
             f'height="{CH-2*band-4}" rx="3" fill="none" stroke="{EDGE}" '
             f'stroke-opacity=".28" stroke-width="1.5"/>')
    p.append(f'<rect x="{x0}" y="{y0}" width="{sw:.1f}" height="{CH}" rx="4" fill="{SHORT}"/>')
    p.append(f'<rect x="{x0+CW-sw:.1f}" y="{y0}" width="{sw:.1f}" height="{CH}" rx="4" fill="{SHORT}"/>')
    p.append(f'<rect x="{x0}" y="{y0}" width="{CW}" height="{lw:.1f}" rx="4" fill="{LONG}"/>')
    p.append(f'<rect x="{x0}" y="{y0+CH-lw:.1f}" width="{CW}" height="{lw:.1f}" rx="4" fill="{LONG}"/>')
    if t == 0.12:
        for cx in (x0 + 7, x0 + CW - 7):
            p.append(f'<circle cx="{cx}" cy="{y0+CH/2}" r="6" fill="none" stroke="#F2C14E" stroke-width="2.5"/>')
    return "".join(p)

# --------------------------------------------------------------- option D ---
def peel(t):
    """Walls slide under the base -- footprint constant, floor stays clean."""
    x0, y0 = (W - CW) / 2, (H - CH) / 2
    band = 15
    s = min(1, max(0, (t - 0.12) / 0.4)); l = min(1, max(0, (t - 0.48) / 0.45))
    p = [f'<rect x="{x0}" y="{y0}" width="{CW}" height="{CH}" rx="6" fill="{BASE}"/>']
    p.append(f'<rect x="{x0}" y="{y0}" width="{band*(1-s):.1f}" height="{CH}" rx="4" fill="{SHORT}"/>')
    p.append(f'<rect x="{x0+CW-band*(1-s):.1f}" y="{y0}" width="{band*(1-s):.1f}" height="{CH}" rx="4" fill="{SHORT}"/>')
    p.append(f'<rect x="{x0}" y="{y0}" width="{CW}" height="{band*(1-l):.1f}" rx="4" fill="{LONG}"/>')
    p.append(f'<rect x="{x0}" y="{y0+CH-band*(1-l):.1f}" width="{CW}" height="{band*(1-l):.1f}" rx="4" fill="{LONG}"/>')
    # stacked slab emerges at the base
    if l > 0:
        p.append(f'<rect x="{x0+6}" y="{y0+CH/2-7}" width="{CW-12}" height="{14*l:.1f}" '
                 f'rx="3" fill="{EDGE}" fill-opacity=".45"/>')
    return "".join(p)

rows = [
 ("How the real crate folds",
  "Side elevation. Latches release, short end walls fall inward onto the base, "
  "long side walls fold down over them.",
  [(elev, v, c) for v, c in ((0.0,"upright"),(0.15,"latch release"),
                             (0.42,"short walls in"),(0.72,"long walls over"),(1.0,"flat"))]),
 ("A &middot; Plan fold &mdash; walls lay inward across the floor",
  "Same order, seen from above. The walls sweep in and cover the perforated floor. "
  "Footprint never changes.",
  [(plan, v, f"{int(v*360)}ms") for v in (0.0,0.12,0.4,0.66,1.0)]),
 ("D &middot; Walls retract, slab builds",
  "Walls shrink to nothing at the rim while a stacked slab grows at the centre. "
  "Reads as collapsing without stretching any artwork.",
  [(peel, v, f"{int(v*360)}ms") for v in (0.0,0.12,0.4,0.66,1.0)]),
]

html = ['<!doctype html><meta charset="utf-8"><style>',
 'html,body{margin:0;background:#f6f4f0;color:#1b1d21;',
 'font:13px/1.5 -apple-system,BlinkMacSystemFont,sans-serif}',
 '.sheet{padding:28px 32px}',
 'h2{font-size:15px;margin:26px 0 2px;font-weight:600}',
 'p.sub{margin:0 0 6px;color:#6f767f;font-size:12.5px;max-width:720px}',
 '.strip{display:flex;gap:6px}',
 'figure{margin:0;text-align:center}',
 'figcaption{font-size:11px;color:#8a9099;margin-top:-6px}',
 'svg{display:block}',
 '.key{display:flex;gap:18px;margin:4px 0 0;font-size:11.5px;color:#6f767f;align-items:center}',
 '.key i{width:11px;height:11px;border-radius:3px;display:inline-block;margin-right:5px;vertical-align:-1px}',
 '</style><div class="sheet">']
html.append('<div class="key"><span><i style="background:%s"></i>base</span>'
            '<span><i style="background:%s"></i>short end walls (fold first)</span>'
            '<span><i style="background:%s"></i>long side walls (fold over)</span>'
            '<span><i style="background:#F2C14E"></i>latch</span></div>' % (BASE, SHORT, LONG))
for title, sub, frames in rows:
    html.append(f'<h2>{title}</h2><p class="sub">{sub}</p><div class="strip">')
    for fn, v, cap in frames:
        html.append(frame(fn(v), cap))
    html.append('</div>')
html.append('</div>')
pathlib.Path("/tmp/fold/story.html").write_text("".join(html))
print("storyboard written")
