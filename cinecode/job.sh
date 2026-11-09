#!/usr/bin/env bash
# Job 4 (2026-11-09): new closing line (Guineo Comunicaciones), voice Andrea
set -u
O=cinecode/out; mkdir -p $O
uv run python cinecode/edge_take.py cinecode/takes-enner.json $O/vo
ls -R $O
