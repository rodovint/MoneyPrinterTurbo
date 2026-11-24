"""Generador de episodios del Súper Resumen Futbolero (16:9, 1920x1080, 25 fps).

Uso: python scripts/guineo/srf_episodio.py episodio.json salida.mp4
episodio.json:
{
 "voz": "lotes/audio/srf-001.m4a",
 "intro": "scripts/guineo/srf/intro-srf-oficial.mp4",          (opcional)
 "piezas": [                                                     línea de tiempo en orden
   {"voz": [3.2, 21.3]},                                         tramo de la grabación de Mui (s)
   {"meme": "/ruta/meme.mp4", "desde": 16.4, "dur": 2.2, "texto": "¡TUCA, SACA TU CAÑÓN!", "recorte": [0,0.33,0.82,0.65]}
 ],
 "planos": [ {"t": 3.2, "tipo": "texto", ...}, ... ]            t = segundo de la GRABACIÓN donde entra el plano
}
Tipos de plano: texto, duo, marcador, cifra, cita, tabla, cortinilla, srf. Campos comunes: sobre, titulo, sub,
color (acento "#RRGGBB"), zocalo (nombre del bloque), entrada (flash|barrido|glitch|corte).
Los memes (material de terceros que manda Mui) se pasan por ruta y no van al repo público.
"""
import json, math, os, subprocess, sys, tempfile, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(AQUI))
W, H, FPS, SR = 1920, 1080, 25, 44100
PAD = 48  # margen para el paneo lento
FD = os.path.join(AQUI, "fonts")
NEG = lambda n: ImageFont.truetype(os.path.join(FD, "InterDisplay-Black.otf"), n)
NEGI = lambda n: ImageFont.truetype(os.path.join(FD, "InterDisplay-BlackItalic.otf"), n)
MONO = lambda n: ImageFont.truetype(os.path.join(FD, "DejaVuSansMono-Bold.ttf"), n)
VERDE, VERDE2, ORO, CREMA, NEGRO = (22, 92, 48), (8, 40, 22), (222, 178, 52), (250, 242, 220), (8, 10, 9)
AVATAR = Image.open(os.path.join(AQUI, "srf", "srf-avatar.png")).convert("RGBA")
ESCUDO = Image.open(os.path.join(AQUI, "srf", "srf-logo.png")).convert("RGBA")
ESCUDOS = os.path.join(ROOT, "lotes", "img", "escudos")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def escudo(nombre, tam):
    if not nombre:
        return None
    p = os.path.join(ESCUDOS, nombre + ".png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGBA")
    bb = im.getbbox()
    if not bb:
        return None
    im = im.crop(bb)
    k = tam / max(im.size)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def ajustar(d, txt, fuente, ancho, tam, minimo=40):
    while tam > minimo and d.textlength(txt, font=fuente(tam)) > ancho:
        tam -= 6
    return fuente(tam)


def lineas(d, txt, fuente, ancho, tam, maxl=3):
    while True:
        f = fuente(tam)
        out, cur = [], ""
        for w_ in txt.split():
            t = (cur + " " + w_).strip()
            if d.textlength(t, font=f) <= ancho:
                cur = t
            else:
                out.append(cur)
                cur = w_
        out.append(cur)
        if len(out) <= maxl or tam < 50:
            return f, out
        tam -= 8


def fondo(acento):
    """Fondo oscuro con degradado del color del plano, rayas diagonales suaves y viñeta."""
    a = np.array(acento, np.float32)
    yy, xx = np.mgrid[0:H + 2 * PAD, 0:W + 2 * PAD].astype(np.float32)
    g = np.clip(1 - np.hypot((xx - (W + 2 * PAD) * 0.5) / (W * 0.75), (yy - (H + 2 * PAD) * 0.45) / (H * 0.9)), 0, 1)
    base = np.array(NEGRO, np.float32) + (a * 0.32 - np.array(NEGRO) * 0.3) * g[..., None]
    rayas = ((xx + yy) // 60 % 2 == 0)[..., None] * 6
    return Image.fromarray(np.clip(base + rayas, 0, 255).astype(np.uint8))


def comunes(im, p):
    d = ImageDraw.Draw(im)
    # avatar SRF arriba a la derecha (60 %)
    av = AVATAR.resize((130, 130), Image.LANCZOS)
    av.putalpha(av.getchannel("A").point(lambda v: int(v * 0.6)))
    im.alpha_composite(av, (W + PAD - 70 - 130, PAD + 50))
    if p.get("zocalo"):
        f = NEG(36)
        tw = d.textlength(p["zocalo"].upper(), font=f)
        x0, y0 = PAD + 70, H + PAD - 150
        d.rectangle([x0, y0, x0 + 14, y0 + 64], fill=ORO)
        d.rectangle([x0 + 14, y0, x0 + 48 + tw, y0 + 64], fill=(*VERDE2, 230))
        d.text((x0 + 32, y0 + 32), p["zocalo"].upper(), font=f, fill=CREMA, anchor="lm")
    return im


def sobre_pill(d, cx, y, txt, color):
    f = NEG(40)
    tw = d.textlength(txt, font=f)
    d.rectangle([cx - tw / 2 - 28, y - 34, cx + tw / 2 + 28, y + 34], fill=color)
    d.text((cx, y), txt, font=f, fill=NEGRO if sum(color) > 380 else CREMA, anchor="mm")


def tarjeta(p):
    acento = rgb(p["color"]) if p.get("color") else ORO
    im = fondo(acento if p.get("tipo") != "cortinilla" else NEGRO).convert("RGBA")
    d = ImageDraw.Draw(im)
    cx, cy = W / 2 + PAD, H / 2 + PAD
    t = p["tipo"]
    if p.get("sobre") and t not in ("cortinilla", "srf"):
        sobre_pill(d, cx, PAD + 150, p["sobre"].upper(), acento)
    if t == "texto":
        f, ls = lineas(d, p["titulo"].upper(), NEGI, 1550, 170)
        y = cy - (len(ls) - 1) * f.size * 0.55 - (40 if p.get("sub") else 0)
        for l in ls:
            d.text((cx, y), l, font=f, fill=CREMA, anchor="mm", stroke_width=4, stroke_fill=NEGRO)
            y += f.size * 1.1
        if p.get("sub"):
            d.text((cx, y + 30), p["sub"], font=ajustar(d, p["sub"], NEG, 1500, 60), fill=acento if (0.299 * acento[0] + 0.587 * acento[1] + 0.114 * acento[2]) > 140 else ORO, anchor="mm")
    elif t in ("duo", "marcador"):
        eq = p["equipos"]
        escs = [escudo(e.get("escudo"), 260) for e in eq]
        con = all(escs)  # regla de Mui: o todos los escudos o ninguno
        for i, e in enumerate(eq):
            x = cx + (-1 if i == 0 else 1) * 470
            if con:
                im.alpha_composite(escs[i], (int(x - escs[i].width / 2), int(cy - 150 - escs[i].height / 2)))
            fn = ajustar(d, e["nombre"].upper(), NEG, 640, 76)
            d.text((x, cy + (40 if con else -40)), e["nombre"].upper(), font=fn, fill=CREMA, anchor="mm")
            if t == "marcador":
                d.text((x, cy + 200 - (0 if con else 60)), str(e["goles"]), font=NEGI(220), fill=rgb(e.get("color", "#DEB234")) if e.get("color") else ORO, anchor="mm",
                       stroke_width=6, stroke_fill=NEGRO)
        d.text((cx, cy + (40 if con else -40)), "VS" if t == "duo" else "–", font=NEGI(90), fill=ORO, anchor="mm")
        if p.get("titulo"):
            d.text((cx, H + PAD - 230), p["titulo"].upper(), font=ajustar(d, p["titulo"].upper(), NEGI, 1500, 70), fill=ORO, anchor="mm")
    elif t == "cifra":
        d.text((cx, cy - 90), p["valor"], font=NEGI(380), fill=ORO, anchor="mm", stroke_width=8, stroke_fill=NEGRO)
        f, ls = lineas(d, p["titulo"].upper(), NEG, 1500, 72, 2)
        for i, l in enumerate(ls):
            d.text((cx, cy + 180 + i * 84), l, font=f, fill=CREMA, anchor="mm")
    elif t == "cita":
        d.rectangle([PAD + 230, cy - 260, PAD + 246, cy + 200], fill=acento)
        f, ls = lineas(d, "«" + p["titulo"] + "»", NEGI, 1300, 110, 4)
        y = cy - (len(ls) - 1) * f.size * 0.55 - 30
        for l in ls:
            d.text((PAD + 300, y), l, font=f, fill=CREMA, anchor="lm")
            y += f.size * 1.12
        if p.get("sub"):
            d.text((PAD + 300, y + 30), "— " + p["sub"], font=NEG(52), fill=ORO, anchor="lm")
    elif t == "tabla":
        filas = p["filas"]
        y = cy - (len(filas) - 1) * 70
        for i, (n, pts) in enumerate(filas):
            dest = n.upper() == p.get("destacar", "").upper()
            col = rgb(p["color"]) if dest and p.get("color") else (VERDE if not dest else ORO)
            d.rectangle([cx - 620, y - 58, cx + 620, y + 58], fill=(*col, 235))
            es = escudo(p.get("escudos", {}).get(n), 90)
            if es:
                im.alpha_composite(es, (int(cx - 590), int(y - es.height / 2)))
            d.text((cx - 470, y), n.upper(), font=NEG(64), fill=CREMA if not dest else NEGRO, anchor="lm")
            d.text((cx + 580, y), str(pts), font=NEGI(80), fill=CREMA if not dest else NEGRO, anchor="rm")
            y += 140
    elif t == "cortinilla":
        f, ls = lineas(d, p["titulo"].upper(), NEGI, 1600, 190, 2)
        y = cy - (len(ls) - 1) * f.size * 0.55
        for l in ls:
            d.text((cx, y), l, font=f, fill=ORO, anchor="mm")
            y += f.size * 1.1
    elif t == "srf":
        tam = 640
        lg = ESCUDO.resize((tam, tam), Image.LANCZOS)
        im.alpha_composite(lg, (int(cx - tam / 2), int(cy - tam / 2 - 60)))
        if p.get("titulo"):
            d.text((cx, H + PAD - 120), p["titulo"].upper(), font=NEGI(70), fill=ORO, anchor="mm")
    if t not in ("cortinilla", "srf"):
        comunes(im, p)
    return im.convert("RGB")


def meme_frames(m, n):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(m["desde"]), "-i", m["archivo"], "-frames:v", str(n),
                          "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    w0, h0 = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                      "-of", "csv=p=0", m["archivo"]], capture_output=True, text=True).stdout.split(",")[:2])
    fr = np.frombuffer(raw, np.uint8)[: (len(raw) // (w0 * h0 * 3)) * w0 * h0 * 3].reshape(-1, h0, w0, 3)
    x0, y0, x1, y1 = m.get("recorte", [0, 0, 1, 1])
    out = []
    for f in fr:
        im = Image.fromarray(f).crop((int(x0 * w0), int(y0 * h0), int(x1 * w0), int(y1 * h0)))
        bg = im.resize((W, H)).filter(ImageFilter.GaussianBlur(30))
        bg = Image.eval(bg, lambda v: int(v * 0.4))
        fg = im.resize((int(im.width * H / im.height), H))
        bg.paste(fg, ((W - fg.width) // 2, 0))
        d = ImageDraw.Draw(bg)
        if m.get("texto"):
            f_ = NEGI(84)
            bb = d.textbbox((W / 2, H * 0.86), m["texto"], font=f_, anchor="mm")
            d.rectangle([bb[0] - 30, bb[1] - 18, bb[2] + 30, bb[3] + 18], fill=VERDE)
            d.text((W / 2, H * 0.86), m["texto"], font=f_, fill=CREMA, anchor="mm")
        if m.get("credito"):
            d.text((W - 40, H - 30), m["credito"], font=MONO(24), fill=(200, 200, 200), anchor="rm")
        out.append(np.asarray(bg))
    while len(out) < n:
        out.append(out[-1] if out else np.zeros((H, W, 3), np.uint8))
    return out


def leer_audio(ruta, ss=None, dur=None):
    cmd = ["ffmpeg", "-loglevel", "error"] + (["-ss", str(ss)] if ss is not None else []) + (["-t", str(dur)] if dur else []) + \
          ["-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.int16).astype(np.float32) / 32768


def main(cfg_path, out):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    voz_full = leer_audio(os.path.join(ROOT, cfg["voz"]) if not os.path.isabs(cfg["voz"]) else cfg["voz"])
    # 1) línea de tiempo maestra: (inicio_master, pieza)
    tl, t = [], 0.0
    for pz in cfg["piezas"]:
        dur = (pz["voz"][1] - pz["voz"][0]) if "voz" in pz else pz["dur"]
        dur += pz.get("pausa", 0.2)
        tl.append((t, dur, pz))
        t += dur
    total = t

    def a_master(tg):
        for t0, dur, pz in tl:
            if "voz" in pz and pz["voz"][0] - 0.05 <= tg <= pz["voz"][1] + 0.05:
                return t0 + max(0, tg - pz["voz"][0])
        # si cae en un corte, va al inicio del siguiente tramo
        for t0, dur, pz in tl:
            if "voz" in pz and pz["voz"][0] > tg:
                return t0
        return total

    planos = sorted(cfg["planos"], key=lambda p: p["t"])
    cortes = [(a_master(p["t"]), p) for p in planos]
    # memes como planos propios
    for t0, dur, pz in tl:
        if "meme" in pz:
            cortes.append((t0, {"tipo": "meme", **pz}))
    cortes.sort(key=lambda c: c[0])
    # 2) audio
    mix = np.zeros(int((total + 2) * SR), np.float32)
    for t0, dur, pz in tl:
        k = int(t0 * SR)
        if "voz" in pz:
            a, b = pz["voz"]
            s = voz_full[int(a * SR):int(b * SR)].copy()
            n = min(len(s), int(0.03 * SR)); s[:n] *= np.linspace(0, 1, n); s[-int(0.06 * SR):] *= np.linspace(1, 0, int(0.06 * SR))
            mix[k:k + len(s)] += s
        else:
            s = leer_audio(pz["meme"], pz["desde"], pz["dur"]) * (0 if pz.get("mudo") else 0.8)
            mix[k:k + len(s)] += s[: len(mix) - k]
    rng = np.random.default_rng(3)
    for tc, p in cortes:  # whoosh en cada cambio de plano
        k = int(max(0, tc - 0.12) * SR)
        n = int(0.28 * SR)
        env = np.sin(np.linspace(0, math.pi, n)) ** 2
        ruido = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same")
        mix[k:k + n] += (ruido * env * (0.5 if p.get("tipo") != "cortinilla" else 0.9)).astype(np.float32)[: len(mix) - k]
    musica = leer_audio(os.path.join(AQUI, "audio", "musica.mp3"))
    if len(musica):
        reps = int(math.ceil(len(mix) / len(musica)))
        mix += np.tile(musica, reps)[: len(mix)] * 0.07
    mix = mix[: int(total * SR)]
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, "a.wav")
    with wave.open(wav, "wb") as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR)
        w_.writeframes((np.clip(mix, -1, 1) * 30000).astype(np.int16).tobytes())
    # 3) video
    body = os.path.join(tmp, "v.mp4")
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", body], stdin=subprocess.PIPE)
    nframes = int(round(total * FPS))
    for i, (tc, p) in enumerate(cortes):
        f0 = int(round(tc * FPS))
        f1 = int(round((cortes[i + 1][0] if i + 1 < len(cortes) else total) * FPS))
        n = max(0, min(f1, nframes) - f0)
        if n == 0:
            continue
        if p["tipo"] == "meme":
            frames = meme_frames({"archivo": p["meme"], **p}, n)
            for fr in frames[:n]:
                pr.stdin.write(fr.tobytes())
            continue
        card = np.asarray(tarjeta(p))
        dx, dy = (1, 0) if i % 2 else (-1, 0)
        entrada = p.get("entrada", "barrido" if p["tipo"] not in ("cortinilla",) else "glitch")
        ultimo = i == len(cortes) - 1
        for k in range(n):
            q = k / max(n - 1, 1)
            ox = int(PAD + dx * PAD * (q - 0.5) * 1.6)
            oy = int(PAD + dy * PAD * (q - 0.5))
            fr = card[oy:oy + H, ox:ox + W].astype(np.float32)
            tt = k / FPS
            if entrada == "flash" and tt < 0.16:
                fr = fr + (255 - fr) * (1 - tt / 0.16)
            elif entrada == "barrido" and tt < 0.28:
                cut = int(W * (1 - (tt / 0.28) ** 0.6))
                fr[:, W - cut:] = fr[:, W - cut:] * 0.15 + np.array(ORO, np.float32) * 0.85 * (cut > 0)
            elif entrada == "glitch" and tt < 0.24:
                s_ = int(30 * (1 - tt / 0.24))
                fr[:, s_:, 0] = fr[:, :W - s_, 0]
                fr[:, :W - s_, 2] = fr[:, s_:, 2]
            if ultimo and (n - k) <= 20:  # la tele se apaga
                qq = 1 - (n - k) / 20
                hh = max(4, int(H * (1 - qq) ** 2))
                small = np.asarray(Image.fromarray(fr.astype(np.uint8)).resize((W, hh)))
                fr = np.zeros((H, W, 3), np.float32)
                fr[(H - hh) // 2:(H - hh) // 2 + hh] = np.clip(small.astype(np.float32) + 255 * qq, 0, 255)
            pr.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait()
    cuerpo = os.path.join(tmp, "cuerpo.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", body, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", cuerpo])
    intro = cfg.get("intro")
    if intro:
        intro = intro if os.path.isabs(intro) else os.path.join(ROOT, intro)
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", intro, "-i", cuerpo, "-filter_complex",
                               f"[0:v]fps={FPS},scale={W}:{H},setsar=1[v0];[1:v]setsar=1[v1];[0:a]aresample={SR},aformat=channel_layouts=stereo[a0];"
                               f"[1:a]aresample={SR},aformat=channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1.5[an]",
                               "-map", "[v]", "-map", "[an]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    else:
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", cuerpo, "-af", "loudnorm=I=-14:TP=-1.5", "-c:v", "copy",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print(f"listo: {out} · {total + 13.6:.1f} s aprox.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
