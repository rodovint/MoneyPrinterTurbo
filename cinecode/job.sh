#!/usr/bin/env bash
# Job 27 (2026-11-15): transcribir la grabación de Mui (tarde), buscar escudos y fotos libres en Commons
set -u
O=cinecode/out; mkdir -p $O
uv venv -q --python 3.11 /tmp/fw && uv pip install -q --python /tmp/fw/bin/python faster-whisper 2>&1 | tail -2
/tmp/fw/bin/python - <<'PY'
import json
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe("lotes/audio/tarde-mui.m4a", language="es", word_timestamps=True, vad_filter=False)
out = []
for s in segs:
    out.append({"ini": s.start, "fin": s.end, "texto": s.text, "palabras": [[w.start, w.end, w.word] for w in s.words]})
    print(f"{s.start:6.2f} {s.end:6.2f} {s.text}", flush=True)
json.dump(out, open("cinecode/out/tarde-mui.json", "w"), ensure_ascii=False, indent=1)
PY
python3 cinecode/escudos.py $O/escudos '{
 "barcelona": ["Barcelona Sporting Club logo", "Barcelona SC escudo"],
 "catolica": ["Universidad Católica Quito logo", "CD Universidad Católica Ecuador escudo"],
 "idv": ["Independiente del Valle logo"],
 "macara": ["Club Social y Deportivo Macará logo"],
 "orense": ["Orense Sporting Club logo"],
 "mushuc": ["Mushuc Runa Sporting Club logo"],
 "liga": ["Liga Deportiva Universitaria Quito logo"],
 "aucas": ["Sociedad Deportiva Aucas logo"],
 "tecnico": ["Técnico Universitario logo"],
 "cuenca": ["Club Deportivo Cuenca logo"],
 "manta": ["Manta Fútbol Club logo"],
 "delfin": ["Delfín Sporting Club logo"],
 "fef": ["Federación Ecuatoriana de Fútbol logo", "Ecuador national football team logo"]
}' 2>&1 | tail -80
python3 cinecode/escudos.py $O/fotos '{
 "bsc-jugadores": ["Barcelona Sporting Club players", "Barcelona SC Guayaquil match"],
 "monumental": ["Estadio Monumental Banco Pichincha", "Estadio Monumental Isidro Romero Carbo"],
 "atahualpa": ["Estadio Olímpico Atahualpa"],
 "ecuador-sub17": ["Ecuador national under-17 football team"],
 "ecuador-tri": ["Ecuador national football team match"],
 "rodrigo-paz": ["Estadio Rodrigo Paz Delgado"],
 "nueve-mayo": ["Estadio 9 de Mayo Machala"],
 "idv-estadio": ["Estadio Banco Guayaquil Sangolquí"],
 "ligapro": ["LigaPro Ecuador match"]
}' 2>&1 | tail -80
