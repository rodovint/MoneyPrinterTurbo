#!/usr/bin/env bash
# Job 11c (2026-11-11): Messi narration — Edge TTS capped at 6 min, Piper backup
set -u
O=cinecode/out; mkdir -p $O
echo "== edge"; timeout 360 uv run python cinecode/edge_take.py cinecode/takes-messi.json $O/vo || echo "edge timeout/fail $?"
echo "== piper"
pip install -q piper-tts 2>&1 | tail -2
mkdir -p /tmp/pv && for f in es_MX-claude-high es_ES-sharvard-medium; do
  L=${f%%-*}; base=https://huggingface.co/rhasspy/piper-voices/resolve/main/es/$L/$(echo $f | cut -d- -f2)/$(echo $f | cut -d- -f3)
  curl -sSL -o /tmp/pv/$f.onnx "$base/$f.onnx" && curl -sSL -o /tmp/pv/$f.onnx.json "$base/$f.onnx.json"
  timeout 240 python3 cinecode/piper_take.py cinecode/takes-messi.json $O/piper-$f /tmp/pv/$f.onnx || echo "piper $f fail"
done
ls -R $O | head -80
