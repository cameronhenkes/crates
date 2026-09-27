#!/usr/bin/env python3
"""
Inline the crate textures into the Three.js page so it runs from file://.

WebGL treats textures fetched over file:// as cross-origin and refuses them,
which is silent apart from the loader's error callback. Data URIs sidestep it
entirely and make the page self-contained -- no server, no CORS, portable.

    ./build-three.py <dir with fold-three.html and tex/>
"""
import base64, pathlib, re, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
page = root / "fold-three.html"
html = page.read_text()

tex = {}
for p in sorted((root / "tex").glob("*.png")):
    tex[p.name] = ("data:image/png;base64,"
                   + base64.b64encode(p.read_bytes()).decode())

block = ("const TEX = {\n"
         + "".join(f'  "{k}": "{v}",\n' for k, v in tex.items())
         + "};\n")

# replace any previous block, then point the loader at it
html = re.sub(r"const TEX = \{.*?\n\};\n", "", html, flags=re.S)
html = html.replace("const manager = new THREE.LoadingManager();",
                    block + "const manager = new THREE.LoadingManager();")
# every "tex/x.png" string, wherever it appears -- some are passed
# through helpers rather than straight into mat()
html = re.sub(r'"tex/([a-z]+)\.png"', r'TEX["\1.png"]', html)
html = html.replace('diag("TEXTURE FAILED: " + u)',
                    'diag("TEXTURE FAILED: " + String(u).slice(0, 60))')

page.write_text(html)
kb = sum(len(v) for v in tex.values()) // 1024
print(f"inlined {len(tex)} textures ({kb}k base64) into {page}")
