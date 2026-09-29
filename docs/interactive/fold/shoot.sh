#!/usr/bin/env bash
# shoot.sh <out.png> '<query string>' [width] [height] [scale]
# Render demo.html at one instant. Starts a local server on 8741 if none is up.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
curl -s -o /dev/null "http://127.0.0.1:8741/demo.html" || {
  (cd "$HERE" && nohup python3 -m http.server 8741 --bind 127.0.0.1 >/dev/null 2>&1 &)
  sleep 1
}
T="$(mktemp -d)"
"$CHROME" --headless --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader \
  --no-sandbox --hide-scrollbars --user-data-dir="$T" \
  --force-device-scale-factor="${5:-1}" --window-size="${3:-620},${4:-680}" \
  --virtual-time-budget=8000 --screenshot="$1" \
  "http://127.0.0.1:8741/demo.html?$2" >/dev/null 2>&1 &
C=$!
for _ in $(seq 1 60); do [ -s "$1" ] && break; sleep 0.5; done
sleep 0.5; kill "$C" 2>/dev/null; wait "$C" 2>/dev/null
[ -s "$1" ] || { echo "render failed: $2" >&2; exit 1; }
