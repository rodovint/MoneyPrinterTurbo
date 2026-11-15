#!/usr/bin/env bash
# Job 29 (2026-11-15): escudos de Orense, Mushuc Runa, Aucas, Cuenca, Manta, Delfín y Técnico desde Wikipedia (imagen principal del artículo)
set -u
O=cinecode/out/escudos2; mkdir -p $O
python3 - <<'PY'
import json, time, urllib.parse, urllib.request
UA = {"User-Agent": "GuineoReels/1.0 (rodovint; news reel crests)"}
clubs = {"orense": ["Orense S.C.", "Orense Sporting Club"], "mushuc": ["Mushuc Runa S.C.", "Mushuc Runa Sporting Club"],
         "aucas": ["S.D. Aucas", "Sociedad Deportiva Aucas"], "cuenca": ["C.D. Cuenca", "Club Deportivo Cuenca"],
         "manta": ["Manta F.C.", "Manta Fútbol Club"], "delfin": ["Delfín S.C.", "Delfín Sporting Club"],
         "tecnico": ["C.D. Técnico Universitario", "Club Técnico Universitario"]}
info = {}
for club, titles in clubs.items():
    for wiki in ["en", "es"]:
        for t in titles:
            u = f"https://{wiki}.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "format": "json", "titles": t, "redirects": 1,
                "prop": "pageimages", "piprop": "thumbnail|name", "pithumbsize": 600})
            try:
                d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
            except Exception as e:
                print("err", club, t, e); continue
            for p in d.get("query", {}).get("pages", {}).values():
                th = p.get("thumbnail", {}).get("source")
                if th:
                    time.sleep(4)
                    try:
                        open(f"cinecode/out/escudos2/{club}.png", "wb").write(urllib.request.urlopen(urllib.request.Request(th, headers=UA), timeout=30).read())
                        info[club] = {"wiki": wiki, "page": p.get("title"), "file": p.get("pageimage"), "url": th}
                        print("ok", club, wiki, p.get("title"), p.get("pageimage"), flush=True)
                    except Exception as e:
                        print("dl err", club, e)
            if club in info: break
        if club in info: break
    time.sleep(2)
json.dump(info, open("cinecode/out/escudos2/info.json", "w"), ensure_ascii=False, indent=1)
PY
ls -la $O
