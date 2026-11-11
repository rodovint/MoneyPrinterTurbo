#!/usr/bin/env bash
# Job 14 (2026-11-11): Costco narration scenes 6-9 (Andrew), job 13 timed out after s5
set -u
O=cinecode/out; mkdir -p $O
echo "== narration"; timeout 1200 uv run python cinecode/edge_take.py cinecode/takes-costco-andrew-2.json $O/vo || echo "edge fail $?"
ls -la $O/vo
