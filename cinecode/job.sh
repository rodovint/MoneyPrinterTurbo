#!/usr/bin/env bash
# Job 44 (2026-11-23): ilustraciones de plastilina de Berna vía Pollinations (gratis, sin clave) mientras Cloudflare no tiene cupo
set -u
O=cinecode/out/berna-img; mkdir -p $O
python3 - <<'PY'
import json, urllib.parse, urllib.request, time
spec = json.load(open("lotes/dibujos/berna.json"))
estilo = "claymation, plasticine stop-motion miniature figures with fingerprint texture, handmade miniature stadium set, soft studio lighting, shallow depth of field, Aardman-like craft look"
for e in spec["escenas"]:
    p = e["prompt"].replace("Vertical illustration: ", "") + " " + estilo + ". No text, no logos, no real people faces."
    u = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(p) + "?width=1080&height=1920&seed=54&nologo=true&model=flux"
    for intento in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "GuineoReels/1.0"}), timeout=180).read()
            open(f"cinecode/out/berna-img/{e['id']}.jpg", "wb").write(data); print("ok", e["id"], len(data)); break
        except Exception as ex:
            print("err", e["id"], ex); time.sleep(10)
PY
