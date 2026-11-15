#!/usr/bin/env bash
# Job 32 (2026-11-15): transcripción de lotes/audio/08.m4a (para alinear las frases de Mui)
set -u
O=cinecode/out/ronaldinho; mkdir -p $O
pip install -q faster-whisper >/dev/null 2>&1
ffmpeg -loglevel error -y -i lotes/audio/08.m4a -ar 16000 -ac 1 -f f32le /tmp/a.raw
python3 - <<'PY'
import numpy as np
from faster_whisper import WhisperModel
a = np.fromfile("/tmp/a.raw", dtype=np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="es", word_timestamps=True)
with open("cinecode/out/ronaldinho/transcripcion.txt", "w") as f:
    for s in segs:
        line = f"{s.start:.2f}-{s.end:.2f} {s.text.strip()}"
        print(line); f.write(line + "\n")
        for w in s.words:
            f.write(f"   {w.start:.2f}-{w.end:.2f} {w.word}\n")
PY
ls -la $O
