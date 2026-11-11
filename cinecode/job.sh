#!/usr/bin/env bash
# Job 16 (2026-11-11): Costco new scene 7b (gas stations and returns) — narration and clips
set -u
O=cinecode/out; mkdir -p $O
echo "== narration"; EDGE_TRIES=8 timeout 600 uv run python cinecode/edge_take.py cinecode/takes-costco-andrew-4.json $O/vo || echo "edge fail $?"
echo "== clips"; timeout 600 uv run python cinecode/costco_clips.py cinecode/costco_queries3.json $O/clips || echo "clips fail $?"
ls -la $O/vo; ls $O/clips | wc -l
