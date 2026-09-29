#!/usr/bin/env bash
# render.sh <input.svg|input.html> <output.png> [width] [height] [scale]
# scale is the device pixel ratio: 2 renders a retina-density PNG at twice
# the CSS dimensions, which is what you want for anything shown on the web.
set -uo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
IN="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
W="${3:-1024}"; H="${4:-$W}"; S="${5:-1}"
TMP="$(mktemp -d)"
rm -f "$2"
# WEBGL=1 swaps --disable-gpu for software GL. Headless Chrome will not run
# WebGL at all without it, and it is slow, so it stays opt-in.
GPU="--disable-gpu"
BUDGET=2000
if [ "${WEBGL:-0}" = "1" ]; then
  GPU="--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader"
  BUDGET=6000
fi
"$CHROME" --headless $GPU --no-sandbox --hide-scrollbars \
  --force-device-scale-factor="$S" --default-background-color=00000000 \
  --user-data-dir="$TMP" --window-size="${W},${H}" \
  --virtual-time-budget="$BUDGET" \
  --screenshot="$2" "file://$IN" >/dev/null 2>&1 &
CPID=$!
for _ in $(seq 1 70); do [ -s "$2" ] && break; sleep 0.5; done
sleep 0.5; kill "$CPID" 2>/dev/null; wait "$CPID" 2>/dev/null
rm -rf "$TMP"
[ -s "$2" ] && echo "rendered $2" || { echo "render failed"; exit 1; }
