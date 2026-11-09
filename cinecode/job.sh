#!/usr/bin/env bash
# Job 5 (2026-11-09): football clips (Pixabay) and Bombonera photos (Commons) for the Guineo-style cut
set -u
O=cinecode/out; mkdir -p $O
uv run python cinecode/fetch_bg.py $O/bg
ls -la $O/bg/clips $O/bg/fotos
