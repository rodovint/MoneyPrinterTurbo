#!/usr/bin/env bash
# Job 45 (2026-11-24): mapas de profundidad (Depth Anything V2 small) de las ilustraciones de Berna para animación 2.5D
set -u
O=cinecode/out/berna-depth; mkdir -p $O
pip install -q torch --index-url https://download.pytorch.org/whl/cpu >/dev/null 2>&1
pip install -q transformers pillow >/dev/null 2>&1
python3 - <<'PY'
import glob, os
from PIL import Image
from transformers import pipeline
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
for f in sorted(glob.glob("lotes/img/berna/*.png")):
    im = Image.open(f).convert("RGB")
    d = pipe(im)["depth"].resize(im.size)
    d.save("cinecode/out/berna-depth/" + os.path.basename(f))
    print("ok", f)
PY
