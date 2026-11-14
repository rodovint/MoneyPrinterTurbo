#!/usr/bin/env bash
# Guineo · Jordy Caicedo (2026-11-13): word-timed transcript of Mui's own narration (faster-whisper)
set -u
O=cinecode/out-tri; mkdir -p $O
pip install -q faster-whisper 2>&1 | tail -1
python3 - <<'PY'
import json
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = m.transcribe("cinecode/voz/jordy.m4a", language="es", word_timestamps=True, vad_filter=False)
out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "t": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
json.dump(out, open("cinecode/out-tri/jordy-transcript.json", "w"), ensure_ascii=False, indent=1)
PY
