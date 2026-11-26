#!/usr/bin/env bash
# Job 50 (2026-11-25): transcripción con tiempos por palabra de la voz NUEVA de Rattín
set -u
mkdir -p cinecode/out/rattin
pip install -q faster-whisper numpy >/dev/null 2>&1
ffmpeg -loglevel error -y -i lotes/audio/rattin.m4a -ac 1 -ar 16000 -f f32le /tmp/v.raw
python3 - <<'PY'
import json, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", compute_type="int8")
segs, _ = m.transcribe(np.fromfile("/tmp/v.raw", dtype=np.float32), language="es", word_timestamps=True)
out = []
for s in segs:
    out.append({"a": round(s.start,2), "b": round(s.end,2), "t": s.text.strip(), "w": [[round(w.start,2), round(w.end,2), w.word] for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
json.dump(out, open("cinecode/out/rattin/whisper.json","w"), ensure_ascii=False, indent=1)
PY
