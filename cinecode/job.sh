#!/usr/bin/env bash
# Job 12 (2026-11-11): Costco long video (business case channel) — voice auditions, music previews, stock clips
set -u
O=cinecode/out; mkdir -p $O
echo "== voices"; timeout 300 uv run python cinecode/edge_take.py cinecode/takes-costco-audicion.json $O/voces || echo "edge fail $?"
echo "== music"
cd cinecode
for q in "corporate documentary" "ambient piano" "lofi instrumental"; do
  d=out/music/$(echo $q | tr ' ' '-')
  timeout 120 python3 tools/asset_search.py search --q "$q" --type music --sources archive,openverse --licence cc0,pd,cc-by --n 6 --out $d --max-wait 40 || echo "music search fail $q"
  timeout 90 python3 tools/asset_search.py fetch --results $d/results.json --pick 1,2 --dest $d/preview --preview 30 --licenses out/music/LICENSES-preview.csv || echo "music fetch fail $q"
done
cd ..
echo "== clips"; timeout 840 uv run python cinecode/costco_clips.py cinecode/costco_queries.json $O/clips || echo "clips fail $?"
du -sh $O/*; ls -R $O | head -150
