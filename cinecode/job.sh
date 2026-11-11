#!/usr/bin/env bash
# Job 11 (2026-11-11): Messi 18 FIFPRO World 11 — narration
set -u
O=cinecode/out; mkdir -p $O
uv run python cinecode/edge_take.py cinecode/takes-messi.json $O/vo
ls -R $O | head -40
