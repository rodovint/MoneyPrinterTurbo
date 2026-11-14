#!/usr/bin/env bash
# Guineo · IDV mejor ataque (2026-11-14): Mui's narration transcript + Andrea takes
set -u
O=cinecode/out-tri; mkdir -p $O
timeout 420 uv run python cinecode/edge_take.py cinecode/takes-idv-ataque.json $O/vo || echo "edge timeout/fail"
pip install -q faster-whisper 2>&1 | tail -1
python3 - <<'PY'
import json, subprocess
import numpy as np
from faster_whisper import WhisperModel
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "cinecode/voz/idv-ataque.m4a", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
audio = np.frombuffer(raw, np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = m.transcribe(audio, language="es", word_timestamps=True, vad_filter=False)
out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "t": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
json.dump(out, open("cinecode/out-tri/idv-transcript.json", "w"), ensure_ascii=False, indent=1)
PY
