#!/usr/bin/env python3
"""
Rebuild docs/interactive/fold/ from the exploration page.

    ./build-component.py        (run from anywhere)

The exploration (docs/explorations/fold-three.html) is where the fold is
authored and reviewed frame by frame. This lifts its scene into
crate-fold.js and copies the textures beside it, so the shipped component
cannot drift from the thing that was reviewed.
"""
import pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "docs/explorations/fold-three.html"
OUT = ROOT / "docs/interactive/fold"
mod = OUT / "crate-fold.js"

src = SRC.read_text()
body = src[src.index("const W = 900"):src.index("let t = 0, target = 0")]
body, n = re.subn(r"const TEX = \{.*?\n\};\n", "const TEX = textures;\n", body, flags=re.S)
assert n == 1, "texture block not found"
for a, b in (
    ("const SIZE = 460;", "const SIZE = size;"),
    ('document.getElementById("wrap").appendChild(renderer.domElement);',
     'mount.appendChild(renderer.domElement);\n'
     'renderer.domElement.style.cssText = "display:block;width:100%;height:auto";'),
):
    assert body.count(a) == 1, a
    body = body.replace(a, b)
body = "\n".join(l for l in body.splitlines()
                 if not l.strip().startswith("diag(")) + "\n"

old = mod.read_text()
head = old[:old.index("const W = 900")]
tail = old[old.index("\nlet t = 0, target = 0"):]
mod.write_text(head + body + tail)
(OUT / "tex").mkdir(exist_ok=True)
for name in ("front", "back", "side", "floor"):
    shutil.copy(ROOT / f"docs/explorations/tex/{name}.png", OUT / "tex" / f"{name}.png")
print(f"rebuilt {mod.relative_to(ROOT)} ({len((head + body + tail).splitlines())} lines) and 4 textures")
