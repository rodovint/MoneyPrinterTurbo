"""Arma el corto vertical de Guineo con clips por escena + voz Edge con tiempos por palabra.
Uso: ensamblar.py <escenas.json> <out_dir_del_job> <salida.mp4>"""
import glob, json, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "guineo"))
import generar as G  # noqa: E402

W, H, FPS = G.W, G.H, G.FPS
TAG = "HISTORIAS QUE INSPIRAN"


def clip_de(out, n):
    sel = os.path.join(out, "elegidos.json")
    if os.path.exists(sel):
        f = json.load(open(sel)).get(str(n))
        if f:
            return os.path.join(out, f), f.split("/")[0]
    yt = os.path.join(out, "yt_cc", f"escena_{n:02d}.mp4")
    if os.path.exists(yt):
        return yt, "yt"
    px = sorted(glob.glob(os.path.join(out, "pixabay", f"px_s{n}_*.mp4")))
    return (px[0], "px") if px else (None, None)


def lector(clip, n):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
    return subprocess.Popen(["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-i", clip, "-an", "-vf", vf,
                             "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)


def a_wav(mp3, wav):
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", "24000", wav])
    with wave.open(wav) as w:
        return w.getnframes() / w.getframerate()


def cierre():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 760, W, 1040], fill=(*G.BG, 225))
    d.text((W / 2, 850), "SÍGUENOS EN", font=G.B(48), fill=G.INK, anchor="mm")
    d.text((W / 2, 950), "GUINEO COMUNICACIONES", font=G.A(92), fill=G.Y, anchor="mm")
    return im


def main(esc_path, out, salida):
    cfg = json.load(open(esc_path, encoding="utf-8"))
    work = os.path.join(out, "_work"); os.makedirs(work, exist_ok=True)
    datos = []
    for e in cfg["escenas"]:
        n = e["id"]
        sid = f"S{n:02d}"
        dur = a_wav(os.path.join(out, "vo", sid + ".mp3"), os.path.join(work, sid + ".wav"))
        words = json.load(open(os.path.join(out, "vo", sid + ".words.json"), encoding="utf-8"))
        datos.append((e, dur + 0.25 + (1.8 if n == cfg["escenas"][-1]["id"] else 0), [w["t"] for w in words]))
    total = sum(d for _, d, _ in datos)
    marca, fin = G.marca(TAG), cierre()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                          "-pix_fmt", "yuv420p", os.path.join(work, "v.mp4")], stdin=subprocess.PIPE)
    inicio, usados = 0.0, []
    for e, dur, marcas in datos:
        n = round(dur * FPS)
        clip, fuente = clip_de(out, e["id"])
        usados.append((e["id"], fuente, os.path.basename(clip) if clip else None))
        rd = lector(clip, n) if clip else None
        caps = G.trozos(e["texto"], marcas, dur)
        capa = {}
        ultimo = e is datos[-1][0]
        for f in range(n):
            t = f / FPS
            arr = np.full((H, W, 3), G.BG, np.uint8)
            if rd:
                raw = rd.stdout.read(W * H * 3)
                if len(raw) == W * H * 3:
                    arr = (np.frombuffer(raw, np.uint8).reshape(H, W, 3) * 0.62).astype(np.uint8)
            im = Image.fromarray(arr).convert("RGBA")
            im.alpha_composite(marca)
            cur = caps[0][1]
            for ini, txt in caps:
                if t >= ini:
                    cur = txt
            capa.setdefault(cur, G.caption_layer(cur))
            im.alpha_composite(capa[cur], (0, 1300))
            if ultimo and t > dur - 2.2:
                im.alpha_composite(fin)
            ImageDraw.Draw(im).rectangle([0, H - 14, int(W * min(1, (inicio + t) / total)), H], fill=G.Y)
            p.stdin.write(im.convert("RGB").tobytes())
        if rd:
            rd.stdout.close(); rd.wait()
        inicio += n / FPS
    p.stdin.close(); p.wait()
    pistas = []
    for e, dur, _ in datos:
        with wave.open(os.path.join(work, f"S{e['id']:02d}.wav")) as w:
            sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        m = round(round(dur * FPS) / FPS * sr)
        pistas.append(np.concatenate([a, np.zeros(max(0, m - len(a)), np.int16)])[:m])
    with wave.open(os.path.join(work, "a.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.concatenate(pistas).tobytes())
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(work, "v.mp4"), "-i", os.path.join(work, "a.wav"),
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                           "-shortest", "-movflags", "+faststart", salida])
    print(json.dumps(usados, ensure_ascii=False))
    print("total", round(inicio, 1), "s")


if __name__ == "__main__":
    main(*sys.argv[1:4])
