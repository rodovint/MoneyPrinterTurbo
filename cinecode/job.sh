#!/usr/bin/env bash
# Job 51 (2026-11-27): Hazaña de La Plata — whisper de la voz + profundidad 2.5D de las ilustraciones
set -u
mkdir -p cinecode/out/laplata/depth
pip install -q torch --index-url https://download.pytorch.org/whl/cpu >/dev/null 2>&1
pip install -q faster-whisper numpy transformers pillow >/dev/null 2>&1
ffmpeg -loglevel error -y -i lotes/audio/laplata.m4a -ac 1 -ar 16000 -f f32le /tmp/v.raw
python3 - <<'PY'
import json, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", compute_type="int8")
segs, _ = m.transcribe(np.fromfile("/tmp/v.raw", dtype=np.float32), language="es", word_timestamps=True)
out = []
for s in segs:
    out.append({"a": round(s.start,2), "b": round(s.end,2), "t": s.text.strip(), "w": [[round(w.start,2), round(w.end,2), w.word] for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
json.dump(out, open("cinecode/out/laplata/whisper.json","w"), ensure_ascii=False, indent=1)
PY
python3 - <<'PY'
import glob, os
from PIL import Image
from transformers import pipeline
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
for f in sorted(glob.glob("lotes/img/laplata/*.png")):
    im = Image.open(f).convert("RGB")
    pipe(im)["depth"].resize(im.size).save("cinecode/out/laplata/depth/" + os.path.basename(f)); print("depth ok", f)
PY
