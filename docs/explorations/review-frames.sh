#!/usr/bin/env bash
# review-frames.sh -- render the Three.js fold frame by frame and stitch it.
# The ?t= hook renders one instant and stops, so motion can be read from
# stills: pacing, ordering, pops and stacking all show up in a strip.
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-/tmp/crate-motion.png}"
for t in 0 0.14 0.28 0.42 0.56 0.70 0.84 1.0; do
  n="${t//./}"
  WEBGL=1 ../../lib/render.sh "fold-three.html?t=$t" "/tmp/cf-$n.png" 440 520 >/dev/null
done
{ printf '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#101216;color:#8b93a1;font:11px -apple-system,sans-serif}.r{display:flex}.r div{text-align:center;width:215px}img{width:215px;display:block;margin-bottom:-86px}b{color:#e9ecf1}</style><div class="r">'
  for t in 0 0.14 0.28 0.42 0.56 0.70 0.84 1.0; do
    printf '<div><img src="/tmp/cf-%s.png"><b>%s</b></div>' "${t//./}" "$t"
  done
  printf '</div>'
} > /tmp/cf-strip.html
../../lib/render.sh /tmp/cf-strip.html "$OUT" 1740 400 >/dev/null
echo "strip: $OUT"
