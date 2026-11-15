#!/usr/bin/env bash
# Job 31 (2026-11-15): escudos Ravenna y Forlì, fotos libres del Stadio Benelli y transcripción de lotes/audio/08.m4a
set -u
O=cinecode/out/ronaldinho; mkdir -p $O
python3 - <<'PY'
import json, time, urllib.parse, urllib.request
UA = {"User-Agent": "GuineoReels/1.0 (https://github.com/rodovint/MoneyPrinterTurbo; news reels)"}
O = "cinecode/out/ronaldinho"
def get(u, binary=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
    return r if binary else json.loads(r)
info = {}
for club, q, wt in [("ravenna", "Ravenna", "Ravenna FC"), ("forli", "Forli", "Forlì FC")]:
    for key in ["123", "3"]:
        try:
            d = get(f"https://www.thesportsdb.com/api/v1/json/{key}/searchteams.php?t=" + urllib.parse.quote(q))
            for t in (d.get("teams") or []):
                if t.get("strCountry") == "Italy" and t.get("strSport") == "Soccer" and (t.get("strBadge") or t.get("strTeamBadge")):
                    b = t.get("strBadge") or t.get("strTeamBadge")
                    open(f"{O}/{club}.png", "wb").write(get(b, True))
                    info[club] = {"src": "thesportsdb", "team": t.get("strTeam"), "url": b}
                    print("ok", club, t.get("strTeam"), b, flush=True); break
        except Exception as e:
            print("tsdb err", club, key, e)
        if club in info: break
        time.sleep(3)
    if club in info: continue
    time.sleep(10)
    try:
        d = get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "format": "json", "titles": wt, "redirects": 1, "prop": "pageimages", "piprop": "thumbnail|name", "pithumbsize": 500}))
        for p in d["query"]["pages"].values():
            th = p.get("thumbnail", {}).get("source")
            if th:
                time.sleep(5)
                open(f"{O}/{club}.png", "wb").write(get(th, True))
                info[club] = {"src": "wikipedia", "file": p.get("pageimage"), "url": th}
                print("ok", club, "wikipedia", p.get("pageimage"), flush=True)
    except Exception as e:
        print("wiki err", club, e)
# Fotos libres del estadio en Wikimedia Commons
try:
    time.sleep(5)
    d = get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrsearch": "Stadio Bruno Benelli Ravenna", "gsrnamespace": 6, "gsrlimit": 15, "prop": "imageinfo", "iiprop": "extmetadata|size", "iiextmetadatafilter": "LicenseShortName|Artist"}))
    info["commons"] = [{"title": p["title"], "lic": p["imageinfo"][0]["extmetadata"].get("LicenseShortName", {}).get("value"), "w": p["imageinfo"][0].get("width"), "h": p["imageinfo"][0].get("height")} for p in d.get("query", {}).get("pages", {}).values()]
    print(json.dumps(info["commons"], ensure_ascii=False, indent=1))
except Exception as e:
    print("commons err", e)
json.dump(info, open(f"{O}/info.json", "w"), ensure_ascii=False, indent=1)
PY
pip install -q faster-whisper >/dev/null 2>&1
python3 - <<'PY'
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe("lotes/audio/08.m4a", language="es", word_timestamps=True)
with open("cinecode/out/ronaldinho/transcripcion.txt", "w") as f:
    for s in segs:
        line = f"{s.start:.2f}-{s.end:.2f} {s.text.strip()}"
        print(line); f.write(line + "\n")
        for w in s.words:
            f.write(f"   {w.start:.2f}-{w.end:.2f} {w.word}\n")
PY
ls -la cinecode/out/ronaldinho
