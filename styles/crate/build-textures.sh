#!/usr/bin/env bash
# build-textures.sh <explorations-dir>
# Render every piece SVG to a texture AT ITS OWN viewBox SIZE.
#
# Dimensions used to be passed by hand on each render call, so a stale or
# mistyped invocation could silently produce a texture with the wrong aspect
# -- which then stretches across its plane in the 3D scene and looks like a
# modelling fault rather than a build one. Reading the viewBox removes the
# chance entirely.
set -euo pipefail
DIR="${1:-.}"
HERE="$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p "$DIR/tex"
declare -A MAP=( [base]=front [back]=back [side]=side [floor]=floor
                 [rim-long]=rimlong [rim-short]=rimshort )
for src in base back side floor rim-long rim-short; do
  svg="$DIR/pieces/$src.svg"
  [ -f "$svg" ] || { echo "missing $svg" >&2; exit 1; }
  read -r w h < <(python3 -c "
import re,sys
vb = re.search(r'viewBox=\"([^\"]+)\"', open('$svg').read()).group(1).split()
print(int(float(vb[2])), int(float(vb[3])))")
  "$HERE/lib/render.sh" "$svg" "$DIR/tex/${MAP[$src]}.png" "$w" "$h" >/dev/null
  printf '  %-10s %sx%s\n' "${MAP[$src]}.png" "$w" "$h"
done
