"""Download landscape Pixabay clips per scene query, trimmed and downscaled for a 16:9 long video.
Usage: costco_clips.py <queries.json> <outdir>
queries.json: {"scenes": {"s1": ["hot dog", ...], ...}, "per_query": 3, "seconds": 7}"""
import json, os, subprocess, sys, urllib.parse, urllib.request

KEY = os.environ.get("PIXABAY_API_KEY", "").strip()
EXCLUDE = {"cartoon", "animation", "3d", "render", "illustration", "ai", "generated"}


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "cinecode/1.0"})
    return urllib.request.urlopen(req, timeout=timeout)


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    per, secs = cfg.get("per_query", 3), cfg.get("seconds", 7)
    pre = cfg.get("prefix", "")
    seen, manifest = set(), []
    for scene, queries in cfg["scenes"].items():
        for q in queries:
            url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
                {"key": KEY, "q": q, "per_page": 20, "safesearch": "true", "video_type": "film"})
            try:
                hits = json.load(get(url, 30)).get("hits", [])
            except Exception as e:
                print("search fail", q, type(e).__name__, flush=True)
                continue
            got = 0
            for h in hits:
                if got >= per:
                    break
                tags = {w for t in h.get("tags", "").lower().split(",") for w in t.split()}
                need = {w for w in q.lower().split() if len(w) > 2}
                if h["id"] in seen or tags & EXCLUDE or (cfg.get("strict") and not need & tags):
                    continue
                v = h["videos"].get("medium") or h["videos"].get("small")
                if not v or not v.get("url") or v.get("width", 0) < v.get("height", 1):
                    continue
                raw = f"/tmp/raw{h['id']}.mp4"
                name = f"{pre}{scene}_{len([m for m in manifest if m['scene'] == scene]):02d}_{h['id']}.mp4"
                try:
                    with get(v["url"], 120) as r, open(raw, "wb") as fh:
                        fh.write(r.read())
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-t", str(secs), "-an",
                                    "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30",
                                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", os.path.join(out, name)],
                                   check=True)
                    os.remove(raw)
                except Exception as e:
                    print("clip fail", h["id"], type(e).__name__, flush=True)
                    continue
                seen.add(h["id"])
                got += 1
                manifest.append({"scene": scene, "query": q, "file": name, "id": h["id"], "tags": h.get("tags"),
                                 "user": h.get("user"), "page": h.get("pageURL"), "duration": h.get("duration")})
                print("ok", name, h.get("tags"), flush=True)
    json.dump(manifest, open(os.path.join(out, "clips.json"), "w"), ensure_ascii=False, indent=1)
    print("clips:", len(manifest))


if __name__ == "__main__":
    main()
