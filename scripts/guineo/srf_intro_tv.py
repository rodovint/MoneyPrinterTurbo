"""Intro "zapping" del Súper Resumen Futbolero (idea de Mui, 21/11).

Señal de ajuste → meme → corte → señal de ajuste → meme → corte → gráfica de Guineo → meme → ...
todo veloz, y al final la tele se apaga y aparece SÚPER RESUMEN FUTBOLERO (de srf_intro.py).

Uso: python scripts/guineo/srf_intro_tv.py salida.mp4 memes.json
memes.json: [{"archivo": "/ruta/meme.mp4", "desde": 31.0, "dur": 0.9, "texto": "¡TUCA, SACA TU CAÑÓN!",
              "audio": true, "recorte": [0.0, 0.0, 1.0, 0.8]}, ...]   (recorte = x0,y0,x1,y1 relativos)
Los memes NO van en el repo público: se pasan por ruta (material de terceros que manda Mui).
"""
import json, math, os, subprocess, sys, tempfile, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srf_intro as base  # noqa: E402

W, H, FPS, SR = 1920, 1080, 30, 44100
A, B, Y, BG, INK = base.A, base.B, base.Y, base.BG, base.INK
rng = np.random.default_rng(11)
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
NEG = lambda n: ImageFont.truetype(os.path.join(FD, "InterDisplay-Black.otf"), n)
NEGI = lambda n: ImageFont.truetype(os.path.join(FD, "InterDisplay-BlackItalic.otf"), n)
OSD = lambda n: ImageFont.truetype(os.path.join(FD, "DejaVuSansMono-Bold.ttf"), n)
ROJO, CIAN, BLANCO, NEGRO, VERDE = (232, 32, 42), (25, 195, 230), (245, 245, 245), (8, 8, 10), (90, 255, 120)
PLACA = None  # imagen "por favor espere" que manda Mui (opcional)


def canal(arr, n):
    """Texto OSD de tele vieja: CH 0n arriba a la derecha."""
    im = Image.fromarray(arr)
    d = ImageDraw.Draw(im)
    d.text((W - 90, 70), f"CH {n:02d}", font=OSD(64), fill=VERDE, anchor="ra", stroke_width=3, stroke_fill=NEGRO)
    return np.asarray(im)


def ajustar(im):
    """Imagen cualquiera a 16:9 con fondo borroso."""
    fondo = im.resize((W, H)).filter(ImageFilter.GaussianBlur(30))
    fondo = Image.eval(fondo, lambda v: int(v * 0.45))
    k = H / im.height
    fg = im.resize((int(im.width * k), H))
    fondo.paste(fg, ((W - fg.width) // 2, 0))
    return fondo


def crt(arr, fuerza=1.0):
    """Líneas de barrido, leve corrimiento RGB y viñeta: look de tele."""
    out = arr.astype(np.float32)
    out[::3] *= 1 - 0.18 * fuerza
    sh = int(4 * fuerza)
    if sh:
        out[:, sh:, 0] = out[:, :-sh, 0]
        out[:, :-sh, 2] = out[:, sh:, 2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.5 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
    return np.clip(out * vig[..., None], 0, 255).astype(np.uint8)


def barras(variante):
    """Señal de ajuste (barras de color) con identificación de Guineo."""
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    cols = [(192, 192, 192), (192, 192, 0), (0, 192, 192), (0, 192, 0), (192, 0, 192), (192, 0, 0), (0, 0, 192)]
    if variante:
        cols = cols[::-1]
    bw = W / 7
    for i, c in enumerate(cols):
        d.rectangle([i * bw, 0, (i + 1) * bw, H * 0.67], fill=c)
    for i, c in enumerate([(0, 0, 192), BG, (192, 0, 192), BG, (0, 192, 192), BG, (192, 192, 192)]):
        d.rectangle([i * bw, H * 0.67, (i + 1) * bw, H * 0.75], fill=c)
    for i, c in enumerate([(0, 33, 76), (255, 255, 255), (50, 0, 106), (19, 19, 19), (9, 9, 9), (19, 19, 19), (29, 29, 29)]):
        d.rectangle([i * W / 7, H * 0.75, (i + 1) * W / 7, H], fill=c)
    r = 230
    d.ellipse([W / 2 - r, H * 0.36 - r, W / 2 + r, H * 0.36 + r], fill=NEGRO, outline=BLANCO, width=10)
    lg = base.LOGO.resize((380, 380))
    im.paste(lg, (int(W / 2 - 190), int(H * 0.36 - 190)), lg)
    return np.asarray(im)


def estatica():
    n = rng.integers(0, 255, (H // 4, W // 4), dtype=np.uint8)
    a = np.repeat(np.repeat(n, 4, 0), 4, 1)
    out = np.stack([a, a, a], -1)
    for _ in range(3):  # bandas de glitch
        y = int(rng.integers(0, H - 80)); h = int(rng.integers(10, 80))
        out[y:y + h] = np.roll(out[y:y + h], int(rng.integers(-200, 200)), 1)
    return out.astype(np.uint8)


def grafica(k, t):
    """Gráficas propias entre memes: placa 'por favor espere' y los segmentos."""
    if k == 0 and PLACA is not None:
        im = ajustar(PLACA)
        z = 1 + 0.04 * t
        im = im.resize((int(W * z), int(H * z))).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
        return np.asarray(im)
    im = Image.new("RGB", (W, H), NEGRO)
    d = ImageDraw.Draw(im)
    for i, (s_, c) in enumerate([("VILLANO", ROJO), ("WINNER", (222, 178, 52)), ("CABALLERO", (250, 242, 220))]):
        ee = base.ease_out((t - i * 0.08) / 0.2)
        cy = H * (0.27 + i * 0.23)
        x = W / 2 + (1 - ee) * W * (1 if i % 2 else -1)
        d.text((x, cy), s_, font=NEGI(170), fill=c, anchor="mm")
    d.text((W / 2, H * 0.92), "DE LA SEMANA", font=OSD(48), fill=BLANCO, anchor="mm")
    return np.asarray(im)


ESCUDO = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "srf", "srf-logo.png")).convert("RGBA")
ORO, CREMA, VERDE_SRF = (222, 178, 52), (250, 242, 220), (22, 92, 48)


def titulo(t):
    """Tras apagarse la tele: el escudo oficial del SRF aparece sobre negro (verde y dorado)."""
    im = Image.new("RGB", (W, H), NEGRO)
    d = ImageDraw.Draw(im)
    # resplandor verde detrás
    e = base.ease_out(t / 0.35)
    if e > 0:
        r = int(520 * e)
        glow = Image.new("L", (W, H), 0)
        ImageDraw.Draw(glow).ellipse([W / 2 - r, H / 2 - 40 - r, W / 2 + r, H / 2 - 40 + r], fill=110)
        glow = glow.filter(ImageFilter.GaussianBlur(90))
        im.paste(Image.new("RGB", (W, H), VERDE_SRF), (0, 0), glow)
        # escudo: entra grande con rebote y destello
        z = 1.35 - 0.35 * e + 0.05 * math.sin(min(t, 0.6) * 18) * (1 - e)
        tam = int(820 * z)
        lg = ESCUDO.resize((tam, tam), Image.LANCZOS)
        im.paste(lg, (W // 2 - tam // 2, H // 2 - 40 - tam // 2), lg)
    if 0.25 < t < 0.45:  # destello al asentarse
        k = 1 - abs(t - 0.35) / 0.1
        im = Image.blend(im, Image.new("RGB", (W, H), CREMA), max(0, k) * 0.55)
        d = ImageDraw.Draw(im)
    if t > 0.8:
        d.text((W / 2, H * 0.93), "VILLANO  ·  WINNER  ·  CABALLERO", font=NEG(44), fill=ORO, anchor="mm")
    if t > 1.1:
        d.text((90, 70), "▶ PLAY", font=OSD(56), fill=VERDE, anchor="la")
    if t > 3.3:  # parpadeo de salida
        return crt(np.asarray(im) // 3 if int(t * 30) % 2 else np.asarray(im), 0.5)
    return crt(np.asarray(im), 0.5)


def cargar_meme(m):
    """Frames del meme (vertical) sobre un fondo borroso del mismo clip, en 16:9."""
    n = int(round(m["dur"] * FPS))
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(m["desde"]), "-i", m["archivo"], "-frames:v", str(n),
                          "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    w0, h0 = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                      "-of", "csv=p=0", m["archivo"]], capture_output=True, text=True).stdout.split(",")[:2])
    fr = np.frombuffer(raw, np.uint8)[: (len(raw) // (w0 * h0 * 3)) * w0 * h0 * 3].reshape(-1, h0, w0, 3)
    x0, y0, x1, y1 = m.get("recorte", [0, 0, 1, 1])
    out = []
    for f in fr:
        im = Image.fromarray(f).crop((int(x0 * w0), int(y0 * h0), int(x1 * w0), int(y1 * h0)))
        fondo = ajustar(im)
        d = ImageDraw.Draw(fondo)
        f = NEGI(92)
        x0_, y0_, x1_, y1_ = d.textbbox((W / 2, H * 0.86), m["texto"], font=f, anchor="mm")
        d.rectangle([x0_ - 34, y0_ - 22, x1_ + 34, y1_ + 22], fill=ROJO)
        d.text((W / 2, H * 0.86), m["texto"], font=f, fill=BLANCO, anchor="mm")
        out.append(np.asarray(fondo))
    while len(out) < n:
        out.append(out[-1])
    return out


def audio_meme(m, path):
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(m["desde"]), "-t", str(m["dur"]), "-i", m["archivo"],
                           "-ac", "1", "-ar", str(SR), path])


def main(out, memes_json, placa=None):
    global PLACA
    if placa:
        PLACA = Image.open(placa).convert("RGB")
    memes = json.load(open(memes_json, encoding="utf-8"))
    tmp = tempfile.mkdtemp()
    # guion de planos: (tipo, duracion, dato)
    plan = []
    g = 0
    for i, m in enumerate(memes):
        if i % 2 == 0:
            plan.append(("barras", 0.5, i // 2 % 2))
        else:
            plan.append(("grafica", 0.6, g % 2)); g += 1
        plan.append(("meme", m["dur"], m))
        plan.append(("corte", 0.2, None))
    plan.append(("apagado", 0.7, None))
    plan.append(("final", 3.6, None))
    frames_v = os.path.join(tmp, "v.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", frames_v], stdin=subprocess.PIPE)
    n_total = sum(int(round(d * FPS)) for _, d, _ in plan)
    mix = np.zeros(int(n_total / FPS * SR) + SR, np.float32)
    pos = 0  # frame actual
    ultimo = None
    ch = 0
    for tipo, dur, dato in plan:
        n = int(round(dur * FPS))
        a0 = int(pos / FPS * SR)
        if tipo == "barras":
            ch += 1
            fr = crt(canal(barras(dato), ch))
            for _ in range(n):
                p.stdin.write(fr.tobytes())
            tt = np.arange(int(dur * SR)) / SR
            mix[a0:a0 + len(tt)] += np.sin(2 * math.pi * 1000 * tt) * 0.18
            ultimo = fr
        elif tipo == "grafica":
            for f in range(n):
                fr = crt(grafica(dato, f / FPS), 0.6)
                p.stdin.write(fr.tobytes())
            ultimo = fr
            tt = np.arange(int(0.25 * SR)) / SR
            mix[a0:a0 + len(tt)] += np.sin(2 * math.pi * (80 + 200 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 8) * 0.8
        elif tipo == "meme":
            ch += 1
            for fr in cargar_meme(dato):
                fr = crt(canal(fr, ch), 0.7)
                p.stdin.write(fr.tobytes())
                ultimo = fr
            if dato.get("audio", True):
                w = os.path.join(tmp, f"m{pos}.wav")
                audio_meme(dato, w)
                with wave.open(w) as wf:
                    s = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
                mix[a0:a0 + len(s)] += s * 0.9
            else:  # sin audio original: pitido de censura
                tt = np.arange(int(dur * 0.6 * SR)) / SR
                k = a0 + int(dur * 0.2 * SR)
                mix[k:k + len(tt)] += np.sin(2 * math.pi * 1000 * tt) * 0.3
        elif tipo == "corte":
            for _ in range(n):
                p.stdin.write(crt(estatica()).tobytes())
            mix[a0:a0 + int(dur * SR)] += rng.standard_normal(int(dur * SR)).astype(np.float32) * 0.25
        elif tipo == "apagado":
            src = ultimo.astype(np.float32)
            for f in range(n):
                q = f / max(n - 1, 1)
                fr = np.zeros((H, W, 3), np.float32)
                if q < 0.5:  # se aplasta a una línea blanca
                    hh = max(4, int(H * (1 - q * 2) ** 2))
                    img = Image.fromarray(src.astype(np.uint8)).resize((W, hh))
                    a = np.asarray(img).astype(np.float32) * (1 - q) + 255 * q * 1.6
                    fr[(H - hh) // 2:(H - hh) // 2 + hh] = np.clip(a, 0, 255)
                else:  # la línea se encoge a un punto y se apaga
                    r = 1 - (q - 0.5) * 2
                    ww = max(6, int(W * r * r))
                    fr[H // 2 - 3:H // 2 + 3, (W - ww) // 2:(W + ww) // 2] = 255 * r + 60
                p.stdin.write(fr.astype(np.uint8).tobytes())
            tt = np.arange(int(dur * SR)) / SR
            mix[a0:a0 + len(tt)] += np.sin(2 * math.pi * (900 * np.exp(-tt * 6) + 60) * tt) * np.exp(-tt * 3) * 0.35
        elif tipo == "final":
            for f in range(n):
                p.stdin.write(titulo(f / FPS).tobytes())
        pos += n
    p.stdin.close(); p.wait()
    # audio del final: el de srf_intro desde 1.85 s
    fin_wav = os.path.join(tmp, "fin.wav")
    base.audio(fin_wav)
    a_fin = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", "1.85", "-t", "3.6", "-i", fin_wav, "-ac", "1", "-ar", str(SR),
                            "-f", "s16le", "-"], capture_output=True).stdout
    s = np.frombuffer(a_fin, np.int16).astype(np.float32) / 32768
    k0 = int((pos / FPS - 3.6) * SR)
    mix[k0:k0 + len(s)] += s
    sfx = os.path.join(tmp, "a.wav")
    with wave.open(sfx, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix[: int(pos / FPS * SR)], -1, 1) * 30000).astype(np.int16).tobytes())
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", frames_v, "-i", sfx, "-af", "loudnorm=I=-14:TP=-1.5",
                           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", out])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
