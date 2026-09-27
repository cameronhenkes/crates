#!/usr/bin/env python3
"""Schematic of the front-reveal concept, judged on the idea not the build."""
import pathlib
F, S, B, FL, E = "#C9765F", "#A85440", "#8E4534", "#7A3B2C", "#5E2C21"
W, H = 260, 210

def frame(inner, cap, note=""):
    return (f'<figure><svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{inner}</svg>'
            f'<figcaption>{cap}<span>{note}</span></figcaption></figure>')

def scene(front_deg, back_deg, side_deg, tilt):
    """front_deg 0=upright facing us, 90=fallen flat away."""
    import math
    cx, base_y = W/2, 150
    fw, fh = 150, 104          # front wall, face on
    d = 62 * (tilt/17)         # apparent depth once tilted
    o = []
    # floor, visible once the front tips
    if front_deg > 6:
        k = min(1,(front_deg-6)/84)
        o.append(f'<polygon points="{cx-fw/2},{base_y} {cx+fw/2},{base_y} '
                 f'{cx+fw/2*0.80},{base_y-d*k:.1f} {cx-fw/2*0.80},{base_y-d*k:.1f}" '
                 f'fill="{FL}"/>')
    # back wall, standing at the far edge, converging
    if front_deg > 18:
        k = min(1,(front_deg-18)/72); bw = fw*0.80
        bh = fh*(1-back_deg/90)*0.86
        o.append(f'<polygon points="{cx-bw/2},{base_y-d*k:.1f} {cx+bw/2},{base_y-d*k:.1f} '
                 f'{cx+bw/2},{base_y-d*k-bh:.1f} {cx-bw/2},{base_y-d*k-bh:.1f}" '
                 f'fill="{B}"/>')
    # side walls, foreshortened front to back
    if front_deg > 24:
        k = min(1,(front_deg-24)/66); sh = fh*(1-side_deg/90)
        for sgn in (-1, 1):
            x0 = cx + sgn*fw/2; x1 = cx + sgn*fw/2*0.80
            o.append(f'<polygon points="{x0},{base_y} {x1},{base_y-d*k:.1f} '
                     f'{x1},{base_y-d*k-sh*0.86:.1f} {x0},{base_y-sh:.1f}" fill="{S}"/>')
    # the front wall itself -- the icon
    fy = fh*math.cos(math.radians(front_deg))
    fd = fh*math.sin(math.radians(front_deg))*0.42
    o.append(f'<polygon points="{cx-fw/2},{base_y} {cx+fw/2},{base_y} '
             f'{cx+fw/2 - fd*0.10:.1f},{base_y-fy-fd*0.0:.1f} '
             f'{cx-fw/2 + fd*0.10:.1f},{base_y-fy:.1f}" fill="{F}"/>')
    if front_deg < 70:
        for r in range(3):
            for c in range(7):
                sx = cx-fw/2+22+c*16; sy = base_y-fy+14+r*(fy-30)/3
                if sy < base_y-6:
                    o.append(f'<rect x="{sx}" y="{sy:.1f}" width="5" '
                             f'height="{max(3,(fy-34)/4):.1f}" rx="2" fill="{E}" '
                             f'fill-opacity=".55"/>')
    return "".join(o)

rows = [(0,90,90,0,"1 &middot; rest","the icon, face on"),
        (34,90,90,17,"2 &middot; front tips back","floor appears"),
        (90,90,90,17,"3 &middot; front down","sides and back revealed"),
        (90,40,90,17,"4 &middot; back folds forward","toward you"),
        (90,0,20,17,"5 &middot; sides fold in","foreshortened front to back"),
        (90,0,0,17,"6 &middot; flat","")]
html = ['<!doctype html><meta charset="utf-8"><style>',
 'html,body{margin:0;background:#f6f4f0;color:#1b1d21;',
 'font:13px/1.5 -apple-system,BlinkMacSystemFont,sans-serif}',
 '.s{padding:26px 28px}h2{font-size:15px;margin:0 0 2px;font-weight:600}',
 'p.sub{margin:0 0 10px;color:#6f767f;font-size:12.5px;max-width:700px}',
 '.strip{display:flex;gap:4px}figure{margin:0;text-align:center}',
 'figcaption{font-size:11.5px;color:#1b1d21;margin-top:-4px;font-weight:500}',
 'figcaption span{display:block;color:#8a9099;font-weight:400;font-size:10.5px}',
 '</style><div class="s"><h2>The icon is the front of the crate</h2>',
 '<p class="sub">Click and the front falls back on its bottom hinge, revealing ',
 'there was a crate behind it all along. Then the back folds forward and the ',
 'sides fold in.</p><div class="strip">']
for fd, bd, sd, t, cap, note in rows:
    html.append(frame(scene(fd, bd, sd, t), cap, note))
html.append('</div></div>')
pathlib.Path("/tmp/fold/concept-board.html").write_text("".join(html))
