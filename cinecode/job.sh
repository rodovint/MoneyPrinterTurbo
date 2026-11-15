#!/usr/bin/env bash
# Job 24 (2026-11-15): bajar música (Megis - Epic Celestial Choir 2, CC BY) e hinchada (paulw2k, CC BY) para los reels
set -u
O=cinecode/out; mkdir -p $O; cd $O
T=../../cinecode/tools/asset_search.py
python3 $T search --q "epic choir" --type music --licence cc0,pd,cc-by --out m 2>&1 | tail -3
python3 $T fetch --results m/results.json --pick 3 --dest musica 2>&1 | tail -5
python3 $T search --q "stadium crowd cheer" --type sound --licence cc0,pd,cc-by --out s 2>&1 | tail -3
python3 $T fetch --results s/results.json --pick 1 --dest hinchada 2>&1 | tail -5
ls -la musica hinchada; cat LICENSES.csv 2>/dev/null; find . -name LICENSES.csv -exec cat {} \;
