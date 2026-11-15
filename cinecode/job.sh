#!/usr/bin/env bash
# Job 30 (2026-11-15): escudos que faltan (TheSportsDB y, si no, Wikipedia con pausas largas)
set -u
O=cinecode/out/escudos2; mkdir -p $O
python3 - <<'PY'
import json, time, urllib.parse, urllib.request
UA = {"User-Agent": "GuineoReels/1.0 (https://github.com/rodovint/MoneyPrinterTurbo; news reels)"}
def get(u, binary=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
    return r if binary else json.loads(r)
clubs = {"orense": ("Orense", "Orense S.C."), "mushuc": ("Mushuc Runa", "Mushuc Runa S.C."), "aucas": ("Aucas", "S.D. Aucas"),
         "cuenca": ("Deportivo Cuenca", "C.D. Cuenca"), "manta": ("Manta", "Manta F.C."), "delfin": ("Delfin", "Delfín S.C."),
         "tecnico": ("Tecnico Universitario", "C.D. Técnico Universitario")}
info = {}
for club, (q, wt) in clubs.items():
    for key in ["123", "3"]:
        try:
            d = get(f"https://www.thesportsdb.com/api/v1/json/{key}/searchteams.php?t=" + urllib.parse.quote(q))
            for t in (d.get("teams") or []):
                if t.get("strCountry") == "Ecuador" and t.get("strSport") == "Soccer" and (t.get("strBadge") or t.get("strTeamBadge")):
                    b = t.get("strBadge") or t.get("strTeamBadge")
                    open(f"cinecode/out/escudos2/{club}.png", "wb").write(get(b, True))
                    info[club] = {"src": "thesportsdb", "team": t.get("strTeam"), "url": b}
                    print("ok", club, "thesportsdb", t.get("strTeam"), b, flush=True)
                    break
        except Exception as e:
            print("tsdb err", club, key, e)
        if club in info: break
        time.sleep(3)
    if club in info: continue
    time.sleep(15)
    try:
        d = get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "format": "json", "titles": wt, "redirects": 1, "prop": "pageimages", "piprop": "thumbnail|name", "pithumbsize": 500}))
        for p in d["query"]["pages"].values():
            th = p.get("thumbnail", {}).get("source")
            if th:
                time.sleep(10)
                open(f"cinecode/out/escudos2/{club}.png", "wb").write(get(th, True))
                info[club] = {"src": "wikipedia", "file": p.get("pageimage"), "url": th}
                print("ok", club, "wikipedia", p.get("pageimage"), flush=True)
    except Exception as e:
        print("wiki err", club, e)
json.dump(info, open("cinecode/out/escudos2/info.json", "w"), ensure_ascii=False, indent=1)
PY
ls -la $O
