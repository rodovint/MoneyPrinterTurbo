"""Busca escudos de clubes en Wikimedia Commons y baja una vista PNG de cada candidato con su licencia."""
import json, os, sys, urllib.parse, urllib.request
UA = {"User-Agent": "GuineoReels/1.0 (rodovint; news reel crests)"}
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
QUERIES = {"boca": ["Boca Juniors logo", "Escudo Boca Juniors", "CABJ escudo"],
           "central": ["Rosario Central logo", "Escudo Rosario Central"],
           "defensa": ["Defensa y Justicia logo", "Escudo Defensa y Justicia"]}
idx = {}
for club, qs in QUERIES.items():
    seen = []
    for q in qs:
        u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": 8,
            "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": 600})
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
        except Exception as e:
            print("err", q, e); continue
        for p in (d.get("query", {}).get("pages", {}) or {}).values():
            ii = p.get("imageinfo", [{}])[0]; md = ii.get("extmetadata", {})
            if p["title"] in [s["title"] for s in seen]:
                continue
            seen.append({"title": p["title"], "thumb": ii.get("thumburl"), "page": ii.get("descriptionurl"), "mime": ii.get("mime"),
                         "license": md.get("LicenseShortName", {}).get("value"), "artist": md.get("Artist", {}).get("value", "")[:120]})
    for i, s in enumerate(seen[:10]):
        if not s["thumb"]:
            continue
        f = os.path.join(out, f"{club}-{i}.png")
        try:
            open(f, "wb").write(urllib.request.urlopen(urllib.request.Request(s["thumb"], headers=UA), timeout=30).read()); s["file"] = f
        except Exception as e:
            print("dl err", s["title"], e)
    idx[club] = seen[:10]
json.dump(idx, open(os.path.join(out, "escudos.json"), "w"), ensure_ascii=False, indent=1)
for c, l in idx.items():
    for i, s in enumerate(l):
        print(c, i, s["license"], s["title"])
