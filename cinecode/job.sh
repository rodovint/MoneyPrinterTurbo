#!/usr/bin/env bash
# Job 8 (2026-11-09): less robotic takes for the Rosario Central lines + club crests from Wikimedia Commons
set -u
O=cinecode/out; mkdir -p $O
uv run python cinecode/edge_take.py cinecode/takes-central.json $O/vo
python3 cinecode/escudos.py $O/escudos
ls -R $O | head -80
