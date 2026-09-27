#!/usr/bin/env python3
"""Emit the three fold options: interactive demo, or a static frame at t."""
import pathlib, re, sys

RAW = pathlib.Path("/tmp/crate-parts.svg").read_text()

def svg(ns):
    s = RAW.replace('<svg xmlns', '<svg class="crate" xmlns')
    s = re.sub(r'\swidth="1024"\sheight="1024"', '', s)
    for i in ("body", "floor", "sheen", "shell", "holes"):
        s = s.replace(f'id="{i}"', f'id="{ns}-{i}"').replace(f'url(#{i})', f'url(#{ns}-{i})')
    return s

def lerp(a, b, t): return a + (b - a) * max(0.0, min(1.0, t))
def seg(t, a, b):  return 0.0 if t <= a else 1.0 if t >= b else (t - a) / (b - a)

# Walls hinge on the base perimeter, so the transform origin is the OUTER edge
# and the wall grows inward across the floor. No zero crossing, no flicker --
# the wall's apparent width goes from its top edge to its full height.
SHORT_IN, LONG_IN = 3.40, 3.00

def frame_css(opt, t):
    s = seg(t, 0.12, 0.55)          # short end walls
    l = seg(t, 0.48, 1.00)          # long side walls, overlapping the short
    latch = seg(t, 0.00, 0.12)
    pop = 9 * (1 - abs(latch * 2 - 1))
    # A laid-down wall is a separate panel resting ON the floor. Same fill as
    # the floor means the fold is invisible, so the panels carry a contact
    # shadow and a brightness shift that ramp in as they fall.
    shade = max(s, l)
    base = f'''
    .c-wall,.c-tab,.c-foot{{transform-box:fill-box;
      filter:drop-shadow(0 {lerp(0,3,shade):.1f}px {lerp(0,5,shade):.1f}px
        rgba(0,0,0,{lerp(0,.45,shade):.2f})) brightness({lerp(1,1.09,shade):.3f})}}
    .c-wall-left {{transform-origin:0% 50%;   transform:scaleX({lerp(1,SHORT_IN,s):.3f})}}
    .c-wall-right{{transform-origin:100% 50%; transform:scaleX({lerp(1,SHORT_IN,s):.3f})}}
    .c-tab {{transform-origin:50% 0%;   transform:scaleY({lerp(1,LONG_IN,l):.3f})}}
    .c-foot{{transform-origin:50% 100%; transform:scaleY({lerp(1,LONG_IN,l):.3f})}}'''
    if opt == "A":
        return base + f'.lugs{{transform:translateX({-pop:.1f}px)}}'
    if opt == "B":
        dip = 1 - abs(seg(t, 0, 1) * 2 - 1)
        return (f'.scene{{perspective:1500px}}'
                f'.tilt{{transform:rotateX({lerp(0,58,dip):.1f}deg) scale({lerp(1,.93,dip):.3f})}}'
                + base)
    if opt == "D":
        r = seg(t, 0.10, 0.55); r2 = seg(t, 0.45, 1.0)
        return f'''
    .c-wall,.c-tab,.c-foot{{transform-box:fill-box}}
    .c-wall-left {{transform-origin:0% 50%;   transform:scaleX({lerp(1,.06,r):.3f})}}
    .c-wall-right{{transform-origin:100% 50%; transform:scaleX({lerp(1,.06,r):.3f})}}
    .c-tab {{transform-origin:50% 0%;   transform:scaleY({lerp(1,.06,r2):.3f})}}
    .c-foot{{transform-origin:50% 100%; transform:scaleY({lerp(1,.06,r2):.3f})}}
    .c-floor,.c-grid,.c-divider{{transform-box:fill-box;transform-origin:50% 50%;
      transform:scaleY({lerp(1,.16,r2):.3f})}}'''
    return ""

if sys.argv[1] == "frame":
    opt, t, out = sys.argv[2], float(sys.argv[3]), sys.argv[4]
    pathlib.Path(out).write_text(f'''<!doctype html><meta charset="utf-8"><style>
 html,body{{margin:0;height:100%;background:#101216;display:grid;place-items:center}}
 .scene{{width:230px;height:230px}} .tilt,.fold{{width:100%;height:100%}}
 .crate{{width:100%;height:100%;display:block;overflow:visible;
   filter:drop-shadow(0 12px 18px rgba(0,0,0,.42))}}
 {frame_css(opt, t)}
</style><div class="scene"><div class="tilt"><div class="fold">{svg("f")}</div></div></div>''')
