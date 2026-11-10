#!/usr/bin/env bash
# Job 7 (2026-11-09): new narration (epic night, no heist) + breathing and stadium-explosion recordings
set -u
O=cinecode/out; mkdir -p $O
uv run python cinecode/edge_take.py cinecode/takes-enner-v2.json $O/vo
T=cinecode/tools/asset_search.py
for q in "heavy breathing man" "breathing slow" "heartbeat" "stadium crowd goal celebration" "crowd cheering roar"; do
  d=$O/rec/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type sound --n 6 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2 --dest $d/files --licenses $O/LICENSES.csv || true
done
ls -R $O | head -80
