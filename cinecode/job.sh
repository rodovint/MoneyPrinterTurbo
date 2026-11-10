#!/usr/bin/env bash
# Job 10 (2026-11-10): Elvira Espinosa — narration, free swimming clips (Pixabay), water/heartbeat sounds
set -u
O=cinecode/out; mkdir -p $O/bg/clips
uv run python cinecode/edge_take.py cinecode/takes-elvira.json $O/vo
uv run python - <<'PY'
import importlib.util, json, os
spec = importlib.util.spec_from_file_location("g", "scripts/guineo/generar.py"); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
g.BUSQUEDAS = ["swimming race", "swimmer", "swimming pool", "underwater swimming", "freestyle swimming", "swimming competition"]
g.ETIQUETAS = {"swimming", "swimmer", "swim", "pool", "freestyle", "underwater"}
g.EXCLUIR = {"animation", "3d", "cartoon", "chroma", "dog", "baby", "child", "kids", "bikini", "sexy", "model", "fashion"}
clips = g.fondos(os.environ.get("PIXABAY_API_KEY", "").strip(), "cinecode/out/bg/clips", cuantos=14)
json.dump({"clips": [os.path.basename(c) for c in clips], "fotos": {}}, open("cinecode/out/bg/bg.json", "w"))
print("clips", len(clips))
PY
T=cinecode/tools/asset_search.py
for q in "heartbeat" "water splash dive" "underwater ambience" "swimming pool crowd cheering"; do
  d=$O/rec/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type sound --n 6 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2 --dest $d/files --licenses $O/LICENSES.csv || true
done
ls -R $O | head -120
