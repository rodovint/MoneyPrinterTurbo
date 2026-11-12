#!/usr/bin/env bash
# Job 19 (2026-11-12): Narváez — rehacer voz escena 7 pronunciando "Yonatan"
set -u
O=cinecode/out; mkdir -p $O
EDGE_TRIES=8 timeout 600 uv run python cinecode/edge_take.py cinecode/narvaez/takes-s07.json $O/vo || echo "edge fail $?"
ls -la $O/vo
