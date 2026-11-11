#!/usr/bin/env bash
# Job 13 (2026-11-11): Costco long video — full narration (Andrew, per scene), full music track, stricter stock clips
set -u
O=cinecode/out; mkdir -p $O
echo "== narration"; timeout 420 uv run python cinecode/edge_take.py cinecode/takes-costco-andrew.json $O/vo || echo "edge fail $?"
echo "== music"
cd cinecode; mkdir -p out/music
timeout 120 python3 tools/asset_search.py fetch --results costco_music_results.json --pick 2 --dest out/music --licenses out/music/LICENSES.csv || echo "music fetch fail"
cd ..
echo "== clips"; timeout 840 uv run python cinecode/costco_clips.py cinecode/costco_queries2.json $O/clips || echo "clips fail $?"
du -sh $O/*; ls $O/vo $O/music
