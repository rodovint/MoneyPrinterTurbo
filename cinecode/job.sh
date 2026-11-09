#!/usr/bin/env bash
# Job 2 (2026-11-09): narration lines in the chosen voice (Andrea) + full music track A
set -u
O=cinecode/out; mkdir -p $O
uv run python cinecode/edge_take.py cinecode/takes-enner.json $O/vo
T=cinecode/tools/asset_search.py
d=$O/music/suspense-heist-tension
python3 $T search --q "suspense heist tension" --type music --n 8 --max-wait 25 --out $d
python3 $T fetch --results $d/results.json --pick 2 --dest $d/full --licenses $O/LICENSES.csv || true
ls -R $O | head -40
