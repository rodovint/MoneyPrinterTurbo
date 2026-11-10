#!/usr/bin/env bash
# Job 9 (2026-11-10): IDV bicampeón — narration, crests, Commons photos, football clips, epic music
set -u
O=cinecode/out; mkdir -p $O
uv run python cinecode/edge_take.py cinecode/takes-idv.json $O/vo
python3 cinecode/escudos.py $O/escudos '{"idv":["Independiente del Valle logo","Escudo Independiente del Valle"],"macara":["Macará escudo","Club Social y Deportivo Macará logo"],"catolica":["Universidad Católica Ecuador escudo","CD Universidad Católica del Ecuador logo"],"aucas":["Sociedad Deportiva Aucas escudo","Aucas logo"]}'
T=cinecode/tools/asset_search.py
for q in "Independiente del Valle" "Estadio Banco Guayaquil" "Junior Sornoza" "Estadio Gonzalo Pozo Ripalda"; do
  d=$O/img/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type image --sources wikimedia --n 8 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2,3,4 --dest $d/files --licenses $O/LICENSES.csv || true
  sleep 5
done
for q in "epic orchestral cinematic" "epic trailer drums"; do
  d=$O/music/$(echo $q | tr ' ' '-')
  python3 $T search --q "$q" --type music --n 6 --max-wait 25 --out $d
  python3 $T fetch --results $d/results.json --pick 1,2,3 --dest $d/files --licenses $O/LICENSES.csv || true
done
mkdir -p $O/bg/clips
uv run python - <<'PY'
import importlib.util, json, os
spec = importlib.util.spec_from_file_location("g", "scripts/guineo/generar.py"); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
clips = g.fondos(os.environ.get("PIXABAY_API_KEY", "").strip(), "cinecode/out/bg/clips", cuantos=12)
json.dump({"clips": [os.path.basename(c) for c in clips], "fotos": {}}, open("cinecode/out/bg/bg.json", "w"))
print("clips", len(clips))
PY
ls -R $O | head -120
