#!/usr/bin/env bash
# Job 3 (2026-11-09): recorded effects (Kenney CC0 packs + open recordings) for "El golpe de Enner"
set -u
O=cinecode/out; mkdir -p $O/sfx
S=cinecode/tools/sounds.py
for q in "metal heavy" "metal latch" "click" "footstep grass" "impact soft heavy" "impact punch" "door open" "switch" "chips stack"; do
  echo "== $q" >> $O/sfx/search.txt
  python3 $S search "$q" --n 5 >> $O/sfx/search.txt 2>&1
  id=$(python3 $S search "$q" --n 2 2>/dev/null | grep " · " | head -2 | cut -d' ' -f1)
  for i in $id; do python3 $S get "$i" --dest $O/sfx >> $O/sfx/get.txt 2>&1; done
done
T=cinecode/tools/asset_search.py
for q in "referee whistle" "football kick ball" "crowd gasp"; do
  d=$O/rec/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type sound --n 6 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2 --dest $d/files --licenses $O/LICENSES.csv || true
done
ls -R $O | head -80
