"""Intro animada del Súper Resumen Futbolero (SRF) de Guineo Comunicaciones.

Uso: python scripts/guineo/srf_intro.py salida.mp4 [--vertical]
Genera ~7 s a 30 fps: luces de estadio, balón que entra con estela, golpe y destello,
SÚPER / RESUMEN / FUTBOLERO con temblor, franjas amarillas y el logo de Guineo.
Audio: whoosh y golpe sintetizados + música e hinchada CC BY del repo (créditos en audio/LICENSES.csv).
"""
import math, os, subprocess, sys, tempfile, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERT = "--vertical" in sys.argv
W, H = (1080, 1920) if VERT else (1920, 1080)
FPS, DUR = 30, 7.2
SR = 44100
Y, BG, INK, AZ = (246, 201, 14), (10, 14, 12), (248, 246, 238), (18, 40, 30)
A = lambda s: ImageFont.truetype(os.path.join(ROOT, "scripts/guineo/fonts/Anton.ttf"), s)
B = lambda s: ImageFont.truetype(os.path.join(ROOT, "resource/fonts/BeVietnamPro-Bold.ttf"), s)
LOGO = Image.open(os.path.join(ROOT, "scripts/guineo/logo-guineo.png")).convert("RGBA")
S = min(W, H) / 1080  # escala


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def back_out(t, s=1.7):
    t = max(0.0, min(1.0, t)) - 1
    return t * t * ((s + 1) * t + s) + 1


_BASE = None


def _base():
    """Parte fija del fondo: cielo oscuro, tribuna con hinchas y césped con franjas."""
    global _BASE
    if _BASE is not None:
        return _BASE
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = yy / H
    base = np.zeros((H, W, 3), np.float32)
    base[:] = np.stack([6 + 10 * g, 10 + 18 * g, 22 + 10 * g], -1)  # cielo azul noche
    rng = np.random.default_rng(3)
    t0, t1 = int(H * 0.40), int(H * 0.56)  # tribuna
    base[t0:t1] = (14, 16, 24)
    pal = np.array([(246, 201, 14), (20, 70, 160), (200, 30, 40), (240, 240, 235)], np.float32)
    n = int(W * (t1 - t0) / (60 * S * S))
    ys, xs = rng.integers(t0, t1, n), rng.integers(0, W, n)
    cols = pal[rng.integers(0, 4, n)] * rng.uniform(0.35, 0.8, (n, 1))
    r = max(2, int(5 * S))
    for y, x, c in zip(ys, xs, cols):
        base[max(0, y - r):y + r, max(0, x - r):x + r] = c
    cesped = yy >= t1
    franja = ((xx / (160 * S)).astype(int) % 2)[cesped]
    base[cesped] = np.stack([10 + 4 * franja, 52 + 14 * franja, 26 + 6 * franja], -1)
    base[t1:t1 + max(2, int(4 * S))] = (220, 220, 210)  # línea
    _BASE = (base, yy, xx, (ys, xs))
    return _BASE


def fondo(t):
    """Estadio de noche: reflectores que se encienden, haces de luz y flashes en la tribuna."""
    base, yy, xx, (ys, xs) = _base()
    out = base.copy()
    for i, (cx, cy) in enumerate([(0.10, 0.10), (0.90, 0.10), (0.33, 0.05), (0.67, 0.05)]):
        on = 1.0 if t > 0.15 + i * 0.15 else (0.25 if int(t * 20) % 2 else 0.0)
        if not on:
            continue
        d = np.sqrt((xx - cx * W) ** 2 + (yy - cy * H) ** 2) / (230 * S)
        out += on * np.exp(-d * d * 3)[..., None] * np.array([150, 150, 135], np.float32)
        # haz suave hacia la cancha
        ang = np.abs(np.arctan2(xx - cx * W, yy - cy * H + 1) - (0.5 if cx < 0.5 else -0.5))
        out += on * (np.exp(-ang * 9) * np.exp(-((yy - cy * H) / H) * 1.5) * 28)[..., None]
    # flashes de cámaras en la tribuna
    rng = np.random.default_rng(int(t * 30))
    for k in rng.integers(0, len(ys), 6):
        y, x = ys[k], xs[k]
        r = int(10 * S)
        out[max(0, y - r):y + r, max(0, x - r):x + r] += 140
    return np.clip(out, 0, 255)


def balon(d, x, y, r, rot):
    d.ellipse([x - r, y - r, x + r, y + r], fill=INK, outline=BG, width=max(2, int(r * 0.08)))
    for k in range(5):
        a = rot + k * 2 * math.pi / 5
        px, py = x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55
        pts = [(px + math.cos(a + j * 2 * math.pi / 5) * r * 0.22, py + math.sin(a + j * 2 * math.pi / 5) * r * 0.22) for j in range(5)]
        d.polygon(pts, fill=BG)


def texto_slam(im, txt, font, cy, t0, t, color, desde):
    """Palabra que entra rebotando desde arriba (-1) o abajo (+1)."""
    p = (t - t0) / 0.35
    if p <= 0:
        return
    e = back_out(p)
    d = ImageDraw.Draw(im)
    y = cy + desde * (1 - e) * H * 0.6
    d.text((W / 2 + 6 * S, y + 6 * S), txt, font=font, fill=(0, 0, 0, 200), anchor="mm")
    d.text((W / 2, y), txt, font=font, fill=color, anchor="mm", stroke_width=int(4 * S), stroke_fill=BG)


def cuadro(t):
    arr = fondo(t)
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    # franjas diagonales amarillas que barren (2.0–3.0 s)
    if t > 1.9:
        p = ease_out((t - 1.9) / 0.8)
        for k in range(5):
            off = (p * 2.4 - 1.2) * W + k * 160 * S
            d.polygon([(off, 0), (off + 70 * S, 0), (off - 0.6 * H + 70 * S, H), (off - 0.6 * H, H)], fill=(*Y, 70))
    # balón con estela (0.7–1.9 s)
    if 0.7 < t < 2.05:
        p = ease_out((t - 0.7) / 1.1)
        x0, y0, x1, y1 = -150 * S, H * 0.75, W / 2, H * 0.48
        for k in range(8, 0, -1):
            pk = max(0.0, p - k * 0.035)
            xk, yk = x0 + (x1 - x0) * pk, y0 + (y1 - y0) * pk - math.sin(pk * math.pi) * H * 0.25
            d.ellipse([xk - 60 * S * (1 - k / 10), yk - 60 * S * (1 - k / 10), xk + 60 * S * (1 - k / 10), yk + 60 * S * (1 - k / 10)], fill=(*Y, int(120 * (1 - k / 9))))
        x, y = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p - math.sin(p * math.pi) * H * 0.25
        balon(d, x, y, 75 * S, t * 12)
    im.alpha_composite(capa)
    # textos (desde el golpe en 1.9 s)
    sh = 0
    if 1.9 < t < 2.4:
        sh = int(14 * S * math.sin(t * 90) * (2.4 - t) * 2)
    tx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    big = 0.9 if VERT else 1.0
    texto_slam(tx, "SÚPER", A(int(150 * S * big)), H * (0.30 if VERT else 0.25), 1.95, t, INK, -1)
    texto_slam(tx, "RESUMEN", A(int(150 * S * big)), H * (0.39 if VERT else 0.42), 2.15, t, INK, 1)
    texto_slam(tx, "FUTBOLERO", A(int(230 * S * big)), H * (0.50 if VERT else 0.64), 2.35, t, Y, -1)
    im.alpha_composite(tx, (sh, 0))
    # logo y firma (3.6 s)
    if t > 3.6:
        e = back_out((t - 3.6) / 0.45)
        tam = int(230 * S * max(0.01, e))
        lg = LOGO.resize((tam, tam), Image.LANCZOS)
        cy = int(H * (0.66 if VERT else 0.86))
        im.alpha_composite(lg, (int(W / 2 - tam / 2 - (0 if VERT else 360 * S)), int(cy - tam / 2)))
        d2 = ImageDraw.Draw(im)
        if t > 3.9:
            a = int(255 * ease_out((t - 3.9) / 0.4))
            pos = (W / 2, cy + 170 * S) if VERT else (W / 2 + 140 * S, cy)
            d2.text(pos, "por GUINEO COMUNICACIONES", font=B(int(46 * S)), fill=(*INK, a), anchor="mm")
    # segmentos (4.4–6.6 s)
    if t > 4.4:
        segs = ["VILLANO", "WINNER", "CABALLERO"]
        d3 = ImageDraw.Draw(im)
        for i, s in enumerate(segs):
            ti = 4.4 + i * 0.25
            if t < ti:
                continue
            e = ease_out((t - ti) / 0.3)
            f = B(int(40 * S))
            w = d3.textlength(s, font=f) + 50 * S
            cx = W / 2 + (i - 1) * (300 * S if VERT else 360 * S)
            cy = H * (0.78 if VERT else 0.08) + (1 - e) * 40 * S
            d3.rectangle([cx - w / 2, cy - 34 * S, cx + w / 2, cy + 34 * S], fill=(*Y, int(255 * e)))
            d3.text((cx, cy), s, font=f, fill=(*BG, int(255 * e)), anchor="mm")
    # destellos: golpe del balón (1.9 s) y salida (6.9 s)
    out = np.asarray(im.convert("RGB")).astype(np.float32)
    for tf, dur in ((1.9, 0.25), (6.85, 0.35)):
        if tf <= t < tf + dur:
            k = 1 - (t - tf) / dur if tf < 5 else (t - tf) / dur
            out = out * (1 - k) + 255 * k
    # viñeta
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
    return np.clip(out * vig[..., None], 0, 255).astype(np.uint8)


def audio(path):
    n = int(DUR * SR)
    t = np.arange(n) / SR
    mix = np.zeros(n, np.float32)
    rng = np.random.default_rng(7)
    # whoosh del balón (0.7–1.9 s): ruido filtrado con barrido
    a, b = int(0.7 * SR), int(1.9 * SR)
    ruido = rng.standard_normal(b - a).astype(np.float32)
    ruido = np.convolve(ruido, np.ones(40) / 40, mode="same")
    env = np.sin(np.linspace(0, math.pi, b - a)) ** 2
    mix[a:b] += ruido * env * 0.9
    # golpe grave en 1.9 s y en el logo (3.6 s)
    for tg, amp in ((1.9, 1.0), (3.6, 0.6)):
        i = int(tg * SR)
        tt = np.arange(int(0.8 * SR)) / SR
        boom = np.sin(2 * math.pi * (55 + 60 * np.exp(-tt * 18)) * tt) * np.exp(-tt * 5) * amp
        mix[i:i + len(boom)] += boom[: n - i]
    # pequeños "tic" de los segmentos
    for i in range(3):
        k = int((4.4 + i * 0.25) * SR)
        tt = np.arange(int(0.08 * SR)) / SR
        mix[k:k + len(tt)] += np.sin(2 * math.pi * 1400 * tt) * np.exp(-tt * 60) * 0.25
    tmp = tempfile.mkdtemp()
    sfx = os.path.join(tmp, "sfx.wav")
    with wave.open(sfx, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 30000).astype(np.int16).tobytes())
    musica = os.path.join(ROOT, "scripts/guineo/audio/musica.mp3")
    hincha = os.path.join(ROOT, "scripts/guineo/audio/hinchada.mp3")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", sfx, "-i", musica, "-i", hincha, "-filter_complex",
                           f"[1:a]atrim=0:{DUR},afade=t=in:d=0.6,afade=t=out:st={DUR - 0.8}:d=0.8,volume=0.55[m];"
                           f"[2:a]atrim=0:{DUR},adelay=1900|1900,afade=t=in:st=1.9:d=0.8,afade=t=out:st={DUR - 1}:d=1,volume=0.5[h];"
                           "[0:a][m][h]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                           "-map", "[a]", "-ar", "44100", "-ac", "2", path])


def main(out):
    tmp = tempfile.mkdtemp()
    v = os.path.join(tmp, "v.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", v], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        p.stdin.write(cuadro(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    a = os.path.join(tmp, "a.wav")
    audio(a)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", "-movflags", "+faststart", out])


if __name__ == "__main__":
    main(sys.argv[1])
