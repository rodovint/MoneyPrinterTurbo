#!/usr/bin/env bash
# Job 1 (2026-11-09): voice audition + music and crowd candidates for "El golpe de Enner"
set -u
O=cinecode/out; mkdir -p $O
cat > $O/takes.json <<'J'
{"takes": [
 {"id": "voz-luis", "voice": "es-EC-LuisNeural", "rate": "+12%", "text": "El plan era simple: que alguien se equivoque. Y alguien se equivocó."},
 {"id": "voz-andrea", "voice": "es-EC-AndreaNeural", "rate": "+12%", "text": "El plan era simple: que alguien se equivoque. Y alguien se equivocó."}
]}
J
uv run python cinecode/edge_take.py $O/takes.json $O/voz
T=cinecode/tools/asset_search.py
for q in "suspense heist tension" "dark electronic action" "cinematic drums tension"; do
  d=$O/music/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type music --n 8 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2 --dest $d/files --preview 45 --licenses $O/LICENSES.csv || true
done
for q in "stadium crowd cheering" "football crowd goal"; do
  d=$O/sound/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type sound --n 8 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2 --dest $d/files --licenses $O/LICENSES.csv || true
done
ls -R $O | head -80
