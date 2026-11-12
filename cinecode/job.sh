#!/usr/bin/env bash
# Job 17 (2026-11-12): Guineo short Jhonatan Narváez — clips por yt-dlp (solo Creative Commons) + Pixabay de respaldo + voz Andrea
set -u
O=cinecode/out; mkdir -p $O
echo "== deps"; pip install -q -U "yt-dlp[default]" 2>&1 | tail -1; curl -fsSL https://deno.land/install.sh | sh -s -- -y >/dev/null 2>&1; export PATH="$HOME/.deno/bin:$PATH"; yt-dlp --version; deno --version | head -1
echo "== narration"; EDGE_TRIES=8 timeout 600 uv run python cinecode/edge_take.py cinecode/narvaez/takes.json $O/vo || echo "edge fail $?"
echo "== youtube cc"; timeout 900 python3 cinecode/buscar_clips.py cinecode/narvaez/escenas.json --solo-cc --candidatos 8 --salida $O/yt_cc || echo "yt fail $?"
echo "== pixabay"; timeout 600 uv run python cinecode/costco_clips.py cinecode/narvaez/pixabay.json $O/pixabay || echo "pix fail $?"
ls -la $O/vo $O/yt_cc $O/pixabay
