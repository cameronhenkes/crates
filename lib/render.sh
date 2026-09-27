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
"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor="$S" --default-background-color=00000000 \
  --user-data-dir="$TMP" --window-size="${W},${H}" \
  --virtual-time-budget=2000 \
  --screenshot="$2" "file://$IN" >/dev/null 2>&1 &
CPID=$!
for _ in $(seq 1 40); do [ -s "$2" ] && break; sleep 0.5; done
sleep 0.5; kill "$CPID" 2>/dev/null; wait "$CPID" 2>/dev/null
rm -rf "$TMP"
[ -s "$2" ] && echo "rendered $2" || { echo "render failed"; exit 1; }
