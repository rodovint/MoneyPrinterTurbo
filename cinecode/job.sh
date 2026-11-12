#!/usr/bin/env bash
# Job 18 (2026-11-12): diagnóstico yt-dlp desde GitHub Actions (Narváez)
set -u
O=cinecode/out; mkdir -p $O
pip install -q -U "yt-dlp[default]" 2>&1 | tail -1; curl -fsSL https://deno.land/install.sh | sh -s -- -y >/dev/null 2>&1; export PATH="$HOME/.deno/bin:$PATH"
echo "== test search"; yt-dlp --flat-playlist --print "%(id)s %(title)s" "ytsearch3:cycling Ecuador" 2>&1 | tail -5
echo "== test info"; yt-dlp --skip-download --print "%(title)s | %(license)s" "https://www.youtube.com/watch?v=jNQXAC9IVRw" 2>&1 | tail -5
echo "== test download"; yt-dlp -f "b[height<=480]" --download-sections "*5-10" -o "$O/test.%(ext)s" "https://www.youtube.com/watch?v=jNQXAC9IVRw" 2>&1 | tail -5
echo "== cc run"; timeout 700 python3 cinecode/buscar_clips.py cinecode/narvaez/escenas.json --solo-cc --candidatos 6 --salida $O/yt_cc || echo "yt fail $?"
ls -la $O $O/yt_cc
