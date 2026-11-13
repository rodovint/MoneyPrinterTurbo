#!/usr/bin/env bash
# Job 12 (2026-11-12): La Tri vuelve al Atahualpa — narration + Commons photos of the stadium
set -u
O=cinecode/out; mkdir -p $O
timeout 360 uv run python cinecode/edge_take.py cinecode/takes-tri.json $O/vo || echo "edge timeout/fail"
T=cinecode/tools/asset_search.py
for q in "Estadio Olímpico Atahualpa" "Atahualpa stadium Quito"; do
  d=$O/img/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type image --sources wikimedia --n 8 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2,3,4 --dest $d/files --licenses $O/LICENSES.csv || true
  sleep 5
done
ls -R $O | head -60
