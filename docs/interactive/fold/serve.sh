#!/usr/bin/env bash
# serve.sh [page]   Serve this folder and open the playground (or another page).
# Modules and textures are refused from file://, so it has to be http.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PORT=8741
curl -s -o /dev/null "http://127.0.0.1:$PORT/playground.html" || {
  (cd "$HERE" && nohup python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &)
  sleep 1
}
open "http://127.0.0.1:$PORT/${1:-playground.html}"
echo "serving $HERE at http://127.0.0.1:$PORT/  (stop: pkill -f 'http.server $PORT')"
