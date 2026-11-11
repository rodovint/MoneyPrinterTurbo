#!/usr/bin/env bash
# Job 15 (2026-11-11): Costco narration scene 6 split in three (Edge kept failing on the long take)
set -u
O=cinecode/out; mkdir -p $O
echo "== narration"; EDGE_TRIES=8 timeout 1200 uv run python cinecode/edge_take.py cinecode/takes-costco-andrew-3.json $O/vo || echo "edge fail $?"
ls -la $O/vo
