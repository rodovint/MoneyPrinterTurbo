"""Genera ilustraciones con Cloudflare Workers AI (FLUX.2 klein 9B) usando imágenes de referencia.

Uso: python scripts/guineo/dibujar.py escenas.json carpeta_salida
Necesita las variables CF_ACCOUNT_ID y CF_API_TOKEN (secretos de GitHub).

escenas.json:
{
  "referencias": ["scripts/guineo/ref/enner-cara.jpg", "scripts/guineo/ref/estilo1.jpg"],
  "estilo": "texto con el estilo de dibujo, se agrega a cada escena",
  "ancho": 1080, "alto": 1920,
  "escenas": [{"id": "centro", "prompt": "...", "seed": 7, "referencias": [0, 1]}]
}
Las referencias se reducen a menos de 512x512 como pide el modelo.
"""
import io, json, os, sys, time
import requests
from PIL import Image

MODEL = "@cf/black-forest-labs/flux-2-klein-9b"


def ref_bytes(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((510, 510), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=92)
    return b.getvalue()


def main(spec_path, out_dir):
    acc, tok = os.environ["CF_ACCOUNT_ID"], os.environ["CF_API_TOKEN"]
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{MODEL}"
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    refs = [ref_bytes(p) for p in spec.get("referencias", [])]
    w, h = spec.get("ancho", 1080), spec.get("alto", 1920)
    for esc in spec["escenas"]:
        prompt = esc["prompt"] + (" " + spec["estilo"] if spec.get("estilo") else "")
        files = {"prompt": (None, prompt), "width": (None, str(min(w, 1920))), "height": (None, str(min(h, 1920)))}
        if "seed" in esc:
            files["seed"] = (None, str(esc["seed"]))
        for n, i in enumerate(esc.get("referencias", range(len(refs)))):
            files[f"input_image_{n}"] = (f"ref{n}.jpg", refs[i], "image/jpeg")
        for intento in range(4):
            r = requests.post(url, headers={"Authorization": f"Bearer {tok}"}, files=files, timeout=180)
            if r.ok:
                break
            print(f"[{esc['id']}] intento {intento + 1}: HTTP {r.status_code} {r.text[:300]}", flush=True)
            time.sleep(10 * (intento + 1))
        else:
            print(f"[{esc['id']}] FALLÓ", flush=True); continue
        import base64
        img = base64.b64decode(r.json()["result"]["image"])
        dest = os.path.join(out_dir, f"{esc['id']}.png")
        Image.open(io.BytesIO(img)).save(dest)
        print(f"[{esc['id']}] ok -> {dest}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
