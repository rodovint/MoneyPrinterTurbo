#!/usr/bin/env bash
# Job 20 (2026-11-12): Narváez — Pixabay más específico para escenas 1, 2, 4 y 5
set -u
O=cinecode/out; mkdir -p $O
timeout 900 uv run python cinecode/costco_clips.py cinecode/narvaez/pixabay2.json $O/pixabay2 || echo "pix fail $?"
ls $O/pixabay2 | wc -l
