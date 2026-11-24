"""Guineo Animación: anima ilustraciones (plastilina) sobre la voz de Mui. Vertical 1080x1920, 25 fps.

Uso: python scripts/guineo/animacion/animar.py corto.json salida.mp4
corto.json:
{
 "voz": "lotes/audio/berna.m4a",
 "tramos": [[3.99, 10.07], [11.4, 16.74], ...],            tramos de la grabación, en orden (s)
 "silencios": {"46.93": 1.0},                              silencio extra a insertar DESPUÉS de ese segundo de la grabación
 "escenas": [ {"t": 3.99, "img": "ruta.png", "mov": "zoom_in|zoom_out|pan_izq|pan_der|sacudon", "lluvia": true,
               "texto": "BERNA · 1954", "marcador": ["HUN", 2, "BRA", 0], "efecto": "apagon|flash|camara_lenta|sangre",
               "titulo": "LA BATALLA DE BERNA", "sfx": ["trueno","silbato","golpe","redoble","sirena","zumbido","click","whoosh","patada"]} ],
 "subtitulos": [[3.99, 10.07, "En 1954…"], ...],          opcional (tiempos de la grabación)
 "color": "#F6C90E"
}
"""
import json, math, os, subprocess, sys, tempfile, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(AQUI)))
FD = os.path.join(os.path.dirname(AQUI), "fonts")
W, H, FPS, SR = 1080, 1920, 25, 44100
ANTON = lambda n: ImageFont.truetype(os.path.join(FD, "Anton.ttf"), n)
NEG = lambda n: ImageFont.truetype(os.path.join(FD, "InterDisplay-Black.otf"), n)
rng = np.random.default_rng(54)


def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def leer(ruta):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


# ---------- efectos de sonido sintetizados (sin derechos) ----------
def sfx(nombre):
    t = np.arange(int(SR * 1.6)) / SR
    n = lambda: rng.standard_normal(len(t)).astype(np.float32)
    if nombre == "trueno":
        s = np.convolve(n(), np.ones(400) / 400, "same") * np.exp(-t * 1.6) * 3.5
    elif nombre == "silbato":
        t = t[: int(SR * 0.9)]; s = np.sin(2 * np.pi * (2900 + 120 * np.sin(2 * np.pi * 38 * t)) * t) * 0.35 * np.minimum(1, t * 30) * np.minimum(1, (0.9 - t) * 10)
    elif nombre == "golpe":
        t = t[: int(SR * 0.7)]; s = np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 18)) * t) * np.exp(-t * 6) * 1.2
    elif nombre == "patada":
        t = t[: int(SR * 0.25)]; s = (np.sin(2 * np.pi * 140 * t) * 0.8 + rng.standard_normal(len(t)) * 0.4) * np.exp(-t * 28)
    elif nombre == "redoble":
        t = t[: int(SR * 1.4)]; s = rng.standard_normal(len(t)) * (0.5 + 0.5 * (np.sin(2 * np.pi * 22 * t) > 0)) * np.minimum(1, t / 1.2) * 0.35
    elif nombre == "sirena":
        s = np.sin(2 * np.pi * (650 + 250 * np.sin(2 * np.pi * 1.2 * t)) * t) * 0.18 * np.minimum(1, t * 4) * np.minimum(1, (1.6 - t) * 4)
    elif nombre == "zumbido":
        s = (np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)) * 0.18 * (0.6 + 0.4 * (rng.random(len(t)) > 0.02))
    elif nombre == "click":
        t = t[: int(SR * 0.08)]; s = rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.9
    elif nombre == "patadas":
        s = sum(np.roll(np.pad(sfx("patada"), (0, len(t))), int(SR * k))[: len(t)] for k in (0.0, 0.35, 0.6, 1.0))
    else:  # whoosh
        t = t[: int(SR * 0.5)]; s = np.convolve(rng.standard_normal(len(t)), np.ones(30) / 30, "same") * np.sin(np.pi * t / 0.5) ** 2 * 0.9
    return np.asarray(s, np.float32)


def lluvia_capa(k):
    """Capa de lluvia animada (RGBA)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = np.random.default_rng(k % 25)
    for _ in range(170):
        x = r.integers(0, W); y = (r.integers(0, H) + k * 55) % H
        d.line([x, y, x - 8, y + 46], fill=(220, 230, 255, 120), width=2)
    return im


def cuadro(base, mov, q):
    """Paneo / zoom de la ilustración (base ya escalada a 1.18x)."""
    bw, bh = base.size
    z = {"zoom_in": 1 + 0.12 * q, "zoom_out": 1.12 - 0.12 * q}.get(mov, 1.06)
    cw, ch = int(W * 1.18 / z), int(H * 1.18 / z)
    cx = bw / 2 + {"pan_izq": (0.5 - q), "pan_der": (q - 0.5)}.get(mov, 0) * (bw - cw) * 0.9
    cy = bh / 2
    if mov == "sacudon":
        cx += math.sin(q * 90) * 14 * (1 - q); cy += math.cos(q * 70) * 10 * (1 - q)
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))
    return base.crop(box).resize((W, H), Image.BILINEAR)


def main(cfg_path, out):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    acento = rgb(cfg.get("color", "#F6C90E"))
    voz = leer(cfg["voz"] if os.path.isabs(cfg["voz"]) else os.path.join(ROOT, cfg["voz"]))
    extra = {float(k): v for k, v in cfg.get("silencios", {}).items()}
    # línea de tiempo: tramos con pausa corta + silencios extra
    tl, t = [], 0.4
    for a, b in cfg["tramos"]:
        tl.append((t, a, b)); t += (b - a) + 0.25
        for k, v in extra.items():
            if a <= k <= b + 0.3:
                t += v
    total = t + 1.2

    def m(tg):
        for t0, a, b in tl:
            if a - 0.3 <= tg <= b + 0.3:
                return t0 + max(0.0, tg - a)
        for t0, a, b in tl:
            if a > tg:
                return t0
        return total
    # audio
    mix = np.zeros(int((total + 2) * SR), np.float32)
    for t0, a, b in tl:
        s = voz[int(a * SR):int(b * SR)].copy()
        f = int(0.03 * SR); s[:f] *= np.linspace(0, 1, f); s[-f:] *= np.linspace(1, 0, f)
        k = int(t0 * SR); mix[k:k + len(s)] += s * 1.1
    escenas = sorted(cfg["escenas"], key=lambda e: e["t"])
    for e in escenas:
        for i, nombre in enumerate(e.get("sfx", [])):
            s = sfx(nombre) * 0.6
            k = int(max(0, m(e["t"]) - (0.15 if nombre == "whoosh" else 0)) * SR) + int(i * 0.05 * SR)
            mix[k:k + len(s)] += s[: max(0, len(mix) - k)]
    lluvia_audio = np.convolve(rng.standard_normal(len(mix)), np.ones(6) / 6, "same").astype(np.float32) * 0.05
    mix += lluvia_audio
    mus = os.path.join(os.path.dirname(AQUI), "audio", "musica.mp3")
    if os.path.exists(mus):
        mu = leer(mus); mix += np.tile(mu, int(len(mix) / len(mu)) + 1)[: len(mix)] * 0.05
    # silencio absoluto (salvo voz) durante el apagón
    for e in escenas:
        if e.get("efecto") == "apagon":
            k0 = int((m(e["apagon_en"]) + 0.05) * SR); k1 = k0 + int(extra.get(e["apagon_en"], 1.0) * SR + 0.3 * SR)
            mix[k0:k1] *= 0.0
            z = sfx("click") * 0.8; mix[k0:k0 + len(z)] += z
    tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "a.wav")
    with wave.open(wav, "wb") as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR)
        w_.writeframes((np.clip(mix[: int(total * SR)], -1, 1) * 30000).astype(np.int16).tobytes())
    # video
    subs = [(m(a), m(b), txt) for a, b, txt in cfg.get("subtitulos", [])]
    vid = os.path.join(tmp, "v.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    n_total = int(total * FPS)
    cortes = [m(e["t"]) if i else 0.0 for i, e in enumerate(escenas)]
    cache = {}
    for i, e in enumerate(escenas):
        f0, f1 = int(cortes[i] * FPS), int((cortes[i + 1] if i + 1 < len(escenas) else total) * FPS)
        if e["img"] not in cache:
            im = Image.open(e["img"] if os.path.isabs(e["img"]) else os.path.join(ROOT, e["img"])).convert("RGB")
            k = max(W * 1.18 / im.width, H * 1.18 / im.height)
            cache[e["img"]] = im.resize((int(im.width * k) + 2, int(im.height * k) + 2), Image.LANCZOS)
        base = cache[e["img"]]
        n = max(1, f1 - f0)
        t_ap = m(e["apagon_en"]) if e.get("efecto") == "apagon" else None
        for kk in range(n):
            tg = (f0 + kk) / FPS; q = kk / n
            fr = cuadro(base, e.get("mov", "zoom_in"), q if e.get("efecto") != "camara_lenta" else q * 0.35).convert("RGBA")
            if e.get("lluvia", True):
                fr.alpha_composite(lluvia_capa(f0 + kk))
            d = ImageDraw.Draw(fr)
            if e.get("texto") and kk / FPS > 0.3:
                d.rectangle([0, 230, W, 360], fill=(0, 0, 0, 150))
                fz = 96
                while d.textlength(e["texto"], font=ANTON(fz)) > W - 80:
                    fz -= 6
                d.text((W / 2, 295), e["texto"], font=ANTON(fz), fill=acento, anchor="mm")
            if e.get("marcador"):
                a1, g1, a2, g2 = e["marcador"]
                vis = min(1, kk / FPS / 0.6)
                if e.get("marcador_pos") == "centro":  # tapa el tablero de la ilustración
                    d.rounded_rectangle([110, 560, W - 110, 1200], 40, fill=(70, 45, 25, 245), outline=(30, 18, 8), width=14)
                    d.text((W / 2 - 230, 700), a1, font=ANTON(110), fill=(250, 240, 220), anchor="mm")
                    d.text((W / 2 + 230, 700), a2, font=ANTON(110), fill=(250, 240, 220), anchor="mm")
                    d.text((W / 2 - 230, 960), str(int(round(g1 * vis))), font=ANTON(300), fill=acento, anchor="mm")
                    d.text((W / 2 + 230, 960), str(int(round(g2 * vis))), font=ANTON(300), fill=acento, anchor="mm")
                else:
                    d.rounded_rectangle([W / 2 - 330, 220, W / 2 + 330, 420], 30, fill=(70, 45, 25, 235), outline=(30, 18, 8), width=10)
                    d.text((W / 2 - 180, 320), a1, font=ANTON(90), fill=(250, 240, 220), anchor="mm")
                    d.text((W / 2 + 180, 320), a2, font=ANTON(90), fill=(250, 240, 220), anchor="mm")
                    d.text((W / 2, 320), f"{int(round(g1 * vis))}-{int(round(g2 * vis))}", font=ANTON(120), fill=acento, anchor="mm")
            if e.get("titulo") and tg >= m(e.get("titulo_en", e["t"])):
                d.rectangle([0, H / 2 - 170, W, H / 2 + 170], fill=(0, 0, 0, 170))
                d.text((W / 2, H / 2 - 60), "LA BATALLA", font=ANTON(150), fill=acento, anchor="mm")
                d.text((W / 2, H / 2 + 80), "DE BERNA", font=ANTON(150), fill=(250, 240, 220), anchor="mm")
            for a, b, txt in subs:
                if a <= tg < b:
                    f = NEG(56); lines, cur = [], ""
                    for w_ in txt.split():
                        if d.textlength(cur + " " + w_, font=f) > W - 160:
                            lines.append(cur); cur = w_
                        else:
                            cur = (cur + " " + w_).strip()
                    lines.append(cur)
                    y = H - 470 - (len(lines) - 1) * 34
                    for l in lines:
                        d.text((W / 2, y), l, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0)); y += 68
            arr = np.asarray(fr.convert("RGB")).astype(np.float32)
            if e.get("efecto") == "flash" and kk < 5:
                arr += (255 - arr) * (1 - kk / 5)
            if t_ap is not None:
                dt = tg - t_ap
                hueco = extra.get(e["apagon_en"], 1.0) + 0.3
                if 0 <= dt < hueco:
                    parp = dt < 0.25 and int(dt * 30) % 2 == 0
                    arr = arr * (0.6 if parp else 0.0)
                elif dt >= hueco:
                    arr *= 0.75  # luz vuelve más tenue
                    if not hasattr(main, "_salp"):
                        sp = Image.new("L", (W, H), 0); ds = ImageDraw.Draw(sp)
                        for _ in range(40):
                            x, y, r = rng.integers(0, W), rng.integers(300, H - 300), rng.integers(10, 70)
                            ds.ellipse([x - r, y - r, x + r, y + r], fill=200)
                        main._salp = np.asarray(sp.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)[..., None] / 255
                    a_ = main._salp * min(1, (dt - hueco) / 0.4)
                    arr = arr * (1 - a_) + np.array([150, 10, 15], np.float32) * a_
            if e.get("efecto") == "camara_lenta":
                g = arr.mean(2, keepdims=True); arr = arr * 0.55 + g * 0.45
            if (f0 + kk) >= n_total - 12:  # fundido final
                arr *= max(0, (n_total - (f0 + kk)) / 12)
            p.stdin.write(np.clip(arr, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-af", "loudnorm=I=-14:TP=-1.5", "-c:v", "copy",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out])
    print(f"listo {out} {total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
