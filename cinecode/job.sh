#!/usr/bin/env bash
# Job 42 (2026-11-23): imágenes libres (Commons) de Emelec + escudo de Emelec, Bragantino, Cruzeiro
set -u
O=cinecode/out/emelec; mkdir -p $O
python3 cinecode/escudos.py $O/escudos '{"emelec":["Club Sport Emelec logo","Emelec escudo"],"bragantino":["Red Bull Bragantino logo"],"cruzeiro":["Cruzeiro Esporte Clube logo"]}'
python3 - <<'PY'
import json, urllib.parse, urllib.request
UA = {"User-Agent": "GuineoReels/1.0 (rodovint; news reel photos)"}
Q = {"capwell":["Estadio George Capwell","Estadio Banco del Pacífico Capwell"],"emelec_equipo":["Club Sport Emelec","Emelec players"],
     "emelec_hinchas":["Emelec fans","Boca del Pozo Emelec"],"saya":["Reixon Saya"],"emelec_jugador":["Emelec footballer"],
     "enner":["Enner Valencia"],"jordy":["Jordy Caicedo"],"plata":["Gonzalo Plata"],"moises":["Moisés Caicedo"]}
res = {}
for k, qs in Q.items():
    out = []
    for q in qs:
        u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action":"query","format":"json","generator":"search",
            "gsrsearch":q,"gsrnamespace":6,"gsrlimit":12,"prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":400})
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
        except Exception as e:
            print("err", q, e); continue
        for p in (d.get("query", {}).get("pages", {}) or {}).values():
            ii = p.get("imageinfo", [{}])[0]; md = ii.get("extmetadata", {})
            out.append({"title": p["title"], "lic": md.get("LicenseShortName", {}).get("value"), "w": ii.get("width"), "h": ii.get("height"),
                        "date": md.get("DateTimeOriginal", {}).get("value", "")[:20], "thumb": ii.get("thumburl"),
                        "desc": md.get("ImageDescription", {}).get("value", "")[:140]})
    res[k] = out
json.dump(res, open("cinecode/out/emelec/fotos.json", "w"), ensure_ascii=False, indent=1)
# miniaturas para revisar
import os
os.makedirs("cinecode/out/emelec/mini", exist_ok=True)
for k, lst in res.items():
    for i, f in enumerate(lst[:8]):
        if f.get("thumb"):
            try:
                open(f"cinecode/out/emelec/mini/{k}-{i}.jpg", "wb").write(urllib.request.urlopen(urllib.request.Request(f["thumb"], headers=UA), timeout=30).read())
            except Exception as e:
                print("thumb err", e)
PY
