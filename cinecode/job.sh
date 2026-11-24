#!/usr/bin/env bash
# Job 41 (2026-11-23): transcripción con tiempos por palabra de la grabación del SRF 001 (Mui)
set -u
O=cinecode/out/srf001; mkdir -p $O
pip install -q faster-whisper >/dev/null 2>&1
ffmpeg -loglevel error -y -i lotes/audio/srf-001.m4a -ar 16000 -ac 1 -f f32le /tmp/a.raw
python3 - <<'PY'
import numpy as np
from faster_whisper import WhisperModel
a = np.fromfile("/tmp/a.raw", dtype=np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="es", word_timestamps=True, vad_filter=False)
with open("cinecode/out/srf001/transcripcion.txt", "w") as f:
    for s in segs:
        f.write(f"{s.start:.2f}-{s.end:.2f} {s.text.strip()}\n")
        for w in s.words:
            f.write(f"   {w.start:.2f}-{w.end:.2f} {w.word}\n")
PY
