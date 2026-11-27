"""Clips imagen→video (LTX, Space gratis de Hugging Face) y mapas de profundidad para Guineo Animación.

Uso: python3 clips.py <id> [escena1,escena2,...] [--sin-video] [--sin-depth]
- Imágenes: lotes/img/<id>/<escena>.png
- Movimiento de cada escena (opcional): lotes/img/<id>/movimientos.json  {"escena": "qué se mueve, en inglés o español"}
- Salida: lotes/img/<id>/video/<escena>.mp4 y lotes/img/<id>/depth/<escena>.png
"""
import glob, json, os, shutil, sys, time

ide = sys.argv[1]
pedidas = [a for a in sys.argv[2:] if not a.startswith("--")]
pedidas = [e.strip() for e in ",".join(pedidas).split(",") if e.strip()]
base = f"lotes/img/{ide}"
todas = sorted(glob.glob(f"{base}/*.png"))
imgs = [f"{base}/{e}.png" for e in pedidas if os.path.exists(f"{base}/{e}.png")] if pedidas else todas
print("clips de:", [os.path.basename(i)[:-4] for i in imgs] if pedidas else "ninguna (solo profundidad)")

# tramos del audio (para pegarlos en corto.json): lotes/audio/<id>.m4a o el que se pase con --audio=nombre.m4a
import re, subprocess
aud = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--audio=") and a.split("=", 1)[1]), f"{ide}.m4a")
ra = f"lotes/audio/{aud}"
if os.path.exists(ra):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", ra, "-af", "silencedetect=n=-35dB:d=0.4", "-f", "null", "-"], capture_output=True, text=True).stderr
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", o).group(3)) + 60 * int(re.search(r"Duration: (\d+):(\d+)", o).group(2))
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    cortes, t0 = [], 0.0
    if ini and ini[0] < 0.05:
        t0 = fin.pop(0); ini.pop(0)
    for a, b in zip(ini, fin + [dur]):
        if a - t0 > 0.3: cortes.append([round(max(0, t0 - 0.05), 2), round(a + 0.05, 2)])
        t0 = b
    if dur - t0 > 0.3: cortes.append([round(t0 - 0.05, 2), round(dur, 2)])
    txt = json.dumps(cortes)
    open(f"{base}/tramos.txt", "w").write(f"Audio: {ra}\nFrases detectadas: {len(cortes)}\n\"tramos\": {txt}\n")
    print("TRAMOS", len(cortes), txt)

if "--sin-depth" not in sys.argv:
    from PIL import Image
    from transformers import pipeline
    os.makedirs(f"{base}/depth", exist_ok=True)
    pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
    for f in todas:  # profundidad de TODAS las imágenes (las que ya tienen se saltan)
        if os.path.exists(f"{base}/depth/" + os.path.basename(f)):
            continue
        im = Image.open(f).convert("RGB")
        pipe(im)["depth"].resize(im.size).save(f"{base}/depth/" + os.path.basename(f)); print("depth ok", f)

if "--sin-video" not in sys.argv and pedidas:  # clips solo de las escenas pedidas (el cupo gratis es corto)
    from gradio_client import Client, handle_file
    mov = {}
    if os.path.exists(f"{base}/movimientos.json"):
        mov = json.load(open(f"{base}/movimientos.json", encoding="utf-8"))
    tok = (os.environ.get("HF_TOKEN") or "").strip() or None
    print("token HF:", "sí" if tok else "NO")
    try:
        c = Client("Lightricks/ltx-video-distilled", hf_token=tok)
    except TypeError:
        c = Client("Lightricks/ltx-video-distilled", token=tok)
    os.makedirs(f"{base}/video", exist_ok=True)
    E = "claymation stop-motion animation, plasticine figures, miniature set, smooth natural movement"
    for f in imgs:
        k = os.path.basename(f)[:-4]
        p = mov.get(k, "the plasticine characters move naturally, subtle camera push in")
        for intento in range(3):
            try:
                r = c.predict(prompt=E + ": " + p, negative_prompt="blurry, distorted, deformed faces, extra limbs, text, watermark, morphing",
                              input_image_filepath=handle_file(f), input_video_filepath=None, height_ui=832, width_ui=480,
                              mode="image-to-video", duration_ui=5, ui_frames_to_use=9, seed_ui=42, randomize_seed=False,
                              ui_guidance_scale=1, improve_texture_flag=True, api_name="/image_to_video")
                v = r[0]["video"] if isinstance(r[0], dict) else r[0]
                shutil.copy(v, f"{base}/video/{k}.mp4"); print("CLIP OK", k); break
            except Exception as e:
                msg = str(e)[:200]
                if tok: msg = msg.replace(tok, "***")
                print("ERR", k, intento, type(e).__name__, msg)
                if "quota" in msg.lower():
                    print("::warning::Se acabó el cupo gratis de GPU de Hugging Face por hoy; prueba mañana."); sys.exit(0)
                time.sleep(45)
