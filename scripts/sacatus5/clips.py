"""Clips reales y tomas de voz para el anuncio de SacaTus5 (se arma luego con cinecode).

Busca en Pixabay videos de futbol amateur (gente jugando, cancha de noche, futsal), los recorta a 6 s
en 1280 px y escribe creditos.csv. Ademas graba la misma frase con varias voces de Edge para elegir de oido.
Uso: python scripts/sacatus5/clips.py sacatus5/out
"""
import asyncio, csv, json, os, shutil, subprocess, sys, urllib.parse, urllib.request
import edge_tts

OUT = sys.argv[1] if len(sys.argv) > 1 else "sacatus5/out"
CLAVE = os.environ.get("PIXABAY_API_KEY", "")
BUSQUEDAS = ["futsal", "soccer friends", "soccer night", "soccer training", "soccer kick", "soccer goal",
             "indoor soccer", "street soccer", "soccer ball grass", "soccer team celebration"]
SI = {"soccer", "football", "futsal", "futbol", "pitch", "goal", "stadium", "ball"}
NO = {"american", "rugby", "cartoon", "animation", "3d", "chroma", "green screen", "render", "gym", "basketball", "tennis"}
POR_BUSQUEDA = 3
VOCES = ["es-EC-LuisNeural", "es-EC-AndreaNeural", "es-MX-JorgeNeural", "es-CO-SalomeNeural"]
FRASE = "Martes, ocho de la noche. La cancha está lista... y faltan dos. Con SacaTus5, el partido se completa."


def abrir(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 SacaTus5Clips/1.0"}), timeout=timeout)


def clips():
    os.makedirs(f"{OUT}/clips", exist_ok=True)
    filas, vistos = [], set()
    for q in BUSQUEDAS:
        url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": CLAVE, "q": q, "per_page": 40, "safesearch": "true", "video_type": "film"})
        try:
            data = json.load(abrir(url, 30))
        except Exception as e:
            print(f"::warning::busqueda {q}: {e}"); continue
        n = 0
        for h in sorted(data.get("hits", []), key=lambda h: -h.get("downloads", 0)):
            tags = h.get("tags", "").lower()
            palabras = {p for t in tags.split(",") for p in t.strip().split()}
            if h["id"] in vistos or not (palabras & SI) or any(x in tags for x in NO):
                continue
            v = h["videos"].get("large") or h["videos"].get("medium")
            if not v or not v.get("url") or v.get("width", 0) < 1280:
                continue
            vistos.add(h["id"]); crudo = f"{OUT}/tmp_{h['id']}.mp4"; final = f"{OUT}/clips/{h['id']}.mp4"
            try:
                with abrir(v["url"], 180) as r, open(crudo, "wb") as f:
                    shutil.copyfileobj(r, f)
                subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-t", "6", "-i", crudo, "-an",
                                       "-vf", "scale=1280:-2,fps=24", "-c:v", "libx264", "-crf", "24", "-preset", "veryfast", final])
                os.remove(crudo)
            except Exception as e:
                print(f"::warning::clip {h['id']}: {e}"); continue
            filas.append([f"clips/{h['id']}.mp4", q, h.get("tags", ""), h.get("user", ""), h.get("pageURL", ""), "Pixabay Content License"])
            print("clip", h["id"], q, h.get("tags")); n += 1
            if n >= POR_BUSQUEDA:
                break
    with open(f"{OUT}/creditos.csv", "w", newline="") as f:
        csv.writer(f).writerows([["archivo", "busqueda", "etiquetas", "autor", "pagina", "licencia"]] + filas)
    print(f"::notice::{len(filas)} clips")


async def voces():
    os.makedirs(f"{OUT}/voces", exist_ok=True)
    for v in VOCES:
        try:
            await edge_tts.Communicate(FRASE, v, rate="+5%").save(f"{OUT}/voces/{v}.mp3")
            print("voz", v)
        except Exception as e:
            print(f"::warning::voz {v}: {e}")


if __name__ == "__main__":
    clips() if CLAVE else print("::warning::sin PIXABAY_API_KEY")
    asyncio.run(voces())
