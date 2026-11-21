#!/usr/bin/env bash
# Job 40 (2026-11-21): final Sudamericana Boca vs Mineiro — transcripción con tomas, escudos y fotos libres
set -u
O=cinecode/out/finalsud; mkdir -p $O
pip install -q faster-whisper >/dev/null 2>&1
ffmpeg -loglevel error -y -i lotes/audio/final-sud.m4a -ar 16000 -ac 1 -f f32le /tmp/a.raw
python3 - <<'PY'
import numpy as np
from faster_whisper import WhisperModel
a = np.fromfile("/tmp/a.raw", dtype=np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="es", word_timestamps=True, vad_filter=False)
with open("cinecode/out/finalsud/transcripcion.txt", "w") as f:
    for s in segs:
        f.write(f"{s.start:.2f}-{s.end:.2f} {s.text.strip()}\n")
        for w in s.words:
            f.write(f"   {w.start:.2f}-{w.end:.2f} {w.word}\n")
PY
python3 cinecode/escudos.py $O/escudos '{"boca":["Boca Juniors logo","CABJ escudo"],"mineiro":["Atlético Mineiro logo","Clube Atlético Mineiro crest"],"lanus":["Club Atlético Lanús logo"],"sudamericana":["Copa Sudamericana logo"]}'
python3 - <<'PY'
import json, urllib.parse, urllib.request
UA = {"User-Agent": "GuineoReels/1.0 (rodovint; news reel photos)"}
Q = {"enner":["Enner Valencia"],"preciado":["Ángelo Preciado","Angelo Preciado"],"minda":["Alan Minda"],"franco":["Alan Franco Ecuador"],
     "estadio":["Estadio Metropolitano Roberto Meléndez"],"trofeo":["Copa Sudamericana trofeo"]}
res = {}
for k, qs in Q.items():
    out = []
    for q in qs:
        u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action":"query","format":"json","generator":"search",
            "gsrsearch":q,"gsrnamespace":6,"gsrlimit":10,"prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":400})
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
        except Exception as e:
            print("err", q, e); continue
        for p in (d.get("query", {}).get("pages", {}) or {}).values():
            ii = p.get("imageinfo", [{}])[0]; md = ii.get("extmetadata", {})
            out.append({"title": p["title"], "lic": md.get("LicenseShortName", {}).get("value"), "license": md.get("License", {}).get("value"),
                        "w": ii.get("width"), "h": ii.get("height"), "date": md.get("DateTimeOriginal", {}).get("value", "")[:40],
                        "desc": md.get("ImageDescription", {}).get("value", "")[:160]})
    res[k] = out
json.dump(res, open("cinecode/out/finalsud/fotos.json", "w"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k); [print("  ", x["title"], x["lic"], x["w"], x["h"], x["date"]) for x in v[:8]]
PY
ls -laR $O | head -60
