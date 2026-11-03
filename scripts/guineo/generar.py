"""Genera los reels de Guineo Deportes a partir de lotes/actual.json.

Cada escena lleva una oracion narrada y un grafico de la noticia. Los clips de
Pixabay solo se usan de fondo, oscurecidos, y se filtran por etiquetas para que
sean de futbol. Uso: python scripts/guineo/generar.py lotes/actual.json salida
"""
import asyncio, json, os, random, re, shutil, subprocess, sys, tempfile, time, traceback, urllib.parse, urllib.request, wave

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H, FPS = 1080, 1920, 30
BG, INK, Y = (13, 20, 17), (248, 246, 238), (246, 201, 14)
VOICE = "es-EC-LuisNeural"
GAP = 0.08
RITMO = "+18%"
BUSQUEDAS = ["soccer stadium", "football stadium", "soccer match", "soccer field", "soccer fans"]
ETIQUETAS = {"soccer", "football", "stadium", "futbol", "pitch"}
EXCLUIR = {"woman", "women", "man", "men", "girl", "boy", "person", "model", "portrait", "freestyle",
           "ball", "animation", "3d", "cartoon", "screen", "chroma", "american", "rugby", "gym"}

A = lambda s: ImageFont.truetype(os.path.join(ROOT, "scripts/guineo/fonts/Anton.ttf"), s)
B = lambda s: ImageFont.truetype(os.path.join(ROOT, "resource/fonts/BeVietnamPro-Bold.ttf"), s)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def ease(t):
    t = max(0, min(1, t))
    return 1 - (1 - t) ** 3


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit(d, text, maxw, maxlines, sizes, F=A):
    for s in sizes:
        f = F(s)
        l = wrap(d, text, f, maxw)
        if len(l) <= maxlines and all(d.textlength(x, font=f) <= maxw for x in l):
            return f, l
    return f, l


def ctext(d, y, lines, font, fill, gap=1.12, cx=W // 2):
    a, de = font.getmetrics()
    for l in lines:
        d.text((cx, y), l, font=font, fill=fill, anchor="ma")
        y += int((a + de) * gap)


def titular(d, lines, f, y, cx, fill=INK):
    for t in lines:
        d.text((cx, y + f.size * .58), t, font=f, fill=fill, anchor="mm")
        y += f.size * 1.16


def card(c):
    im = Image.new("RGBA", (W, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    kind = c["tipo"]
    if kind == "titular":
        kf = B(40)
        kw = d.textlength(c["sobre"], font=kf) + 56
        d.rectangle([(W - kw) / 2, 110, (W + kw) / 2, 186], fill=Y)
        d.text((W / 2, 148), c["sobre"], font=kf, fill=BG, anchor="mm")
        for sz in [190, 170, 150, 130, 112, 100, 90]:
            f, l = fit(d, c["texto"], 900, 4, [sz])
            if len(l) * sz * 1.16 <= 650:
                break
        titular(d, l, f, 215 + (660 - len(l) * f.size * 1.16) / 2, W // 2)
    elif kind == "cifra":
        f, l = fit(d, c["valor"], 920, 1, [430, 380, 320, 280, 240])
        ctext(d, 60, l, f, Y, 1.0)
        f2, l2 = fit(d, c["texto"], 880, 3, [72, 64, 56, 50], B)
        ctext(d, 650 - (len(l2) - 1) * 28, l2, f2, INK, 1.1)
    elif kind == "marcador":
        for i, e in enumerate(c["equipos"]):
            y = 90 + i * 300
            d.rectangle([60, y, W - 60, y + 280], fill=rgb(e["color"]))
            f, l = fit(d, e["nombre"], 620, 1, [130, 112, 96, 84, 72])
            d.text((105, y + 140), l[0], font=f, fill=INK, anchor="lm")
            d.rectangle([W - 300, y, W - 60, y + 280], fill=INK)
            d.text((W - 180, y + 140), str(e["goles"]), font=A(210), fill=BG, anchor="mm")
        f, l = fit(d, c["pie"], 900, 2, [52, 46, 40], B)
        ctext(d, 710, l, f, Y)
    elif kind == "cita":
        d.rectangle([60, 130, 76, 720], fill=Y)
        f, l = fit(d, c["texto"], 860, 3, [180, 160, 140, 120])
        titular(d, l, f, 130 + (450 - len(l) * f.size * 1.16) / 2, W // 2 + 15)
        f2, l2 = fit(d, c["autor"], 860, 2, [48, 42], B)
        ctext(d, 610, l2, f2, Y, cx=W // 2 + 15)
    elif kind == "duo":
        for i, (n, lb) in enumerate(((c["a"], c["a_texto"]), (c["b"], c["b_texto"]))):
            x0 = 60 + i * 490
            d.rectangle([x0, 90, x0 + 470, 620], fill=(30, 42, 36))
            d.rectangle([x0, 90, x0 + 470, 104], fill=Y)
            f, ls = fit(d, n, 420, 1, [260, 220, 180])
            d.text((x0 + 235, 300), ls[0], font=f, fill=Y, anchor="mm")
            f2, ls2 = fit(d, lb, 420, 2, [52, 46, 40], B)
            ctext(d, 490, ls2, f2, INK, cx=x0 + 235)
        f, l = fit(d, c["pie"], 900, 2, [56, 50, 44], B)
        ctext(d, 680, l, f, INK)
    elif kind == "partido":
        for i, e in enumerate(c["equipos"]):
            y = 90 + i * 300
            d.rectangle([60, y, W - 60, y + 280], fill=rgb(e["color"]))
            f, l = fit(d, e["nombre"], 880, 1, [130, 112, 96, 84, 72])
            d.text((W / 2, y + 140), l[0], font=f, fill=INK, anchor="mm")
        w = d.textlength(c["hora"], font=A(84)) + 70
        d.rectangle([(W - w) / 2, 325, (W + w) / 2, 435], fill=Y)
        d.text((W / 2, 380), c["hora"], font=A(84), fill=BG, anchor="mm")
        f, l = fit(d, c["pie"], 900, 2, [52, 46, 40], B)
        ctext(d, 710, l, f, Y)
    elif kind == "protagonista":
        d.rectangle([60, 110, W - 60, 760], fill=(*rgb(c["color"]), 235))
        d.rectangle([60, 110, W - 60, 124], fill=Y)
        f0, l0 = fit(d, c["rol"], 860, 1, [46, 40, 34], B)
        ctext(d, 165, l0, f0, INK)
        for sz in [170, 150, 130, 112, 96]:
            f, l = fit(d, c["nombre"], 860, 2, [sz])
            if len(l) * sz * 1.16 <= 340:
                break
        titular(d, l, f, 245 + (330 - len(l) * f.size * 1.16) / 2, W // 2)
        f2, l2 = fit(d, c["dato"], 840, 2, [80, 70, 60, 50])
        titular(d, l2, f2, 600 + (130 - len(l2) * f2.size * 1.16) / 2, W // 2, Y)
    elif kind == "cierre":
        ctext(d, 170, [c["texto"]], fit(d, c["texto"], 900, 1, [120, 100, 84])[0], INK)
        d.rectangle([60, 360, W - 60, 660], fill=Y)
        f, l = fit(d, c.get("marca", "GUINEO DEPORTES"), 880, 2, [170, 150, 130, 110, 96])
        titular(d, l, f, 510 - len(l) * f.size * 1.16 / 2, W // 2, BG)
    else:
        raise ValueError(f"tipo de escena desconocido: {kind}")
    return im


def marca(tag):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([60, 120, 500, 200], fill=Y)
    d.text((280, 160), "GUINEO DEPORTES", font=A(52), fill=BG, anchor="mm")
    d.text((525, 160), tag, font=B(36), fill=INK, anchor="lm", stroke_width=3, stroke_fill=BG)
    return im


def caption_layer(text):
    im = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f, l = fit(d, text, 800, 2, [66, 60, 54], B)
    ls = sum(f.getmetrics()) * 1.15
    y = 150 - ls * len(l) / 2
    for t in l:
        d.text((W / 2, y), t, font=f, fill=INK, anchor="ma", stroke_width=6, stroke_fill=BG)
        y += ls
    return im


def trozos(text, marcas, dur):
    """Agrupa palabras en subtitulos y les da tiempos (reales si la voz los entrega)."""
    words = text.split()
    grupos, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if len(cur) >= 5 or (len(cur) >= 3 and w[-1] in ",:;."):
            grupos.append(cur)
            cur = []
    if cur:
        if len(cur) == 1 and grupos:
            grupos[-1] += cur
        else:
            grupos.append(cur)
    total = sum(len(w) + 1 for w in words)
    out = []
    for g in grupos:
        i = g[0]
        if len(marcas) == len(words):
            ini = marcas[i]
        else:
            ini = dur * sum(len(w) + 1 for w in words[:i]) / total
        out.append((ini, " ".join(words[j] for j in g)))
    return out


async def _voz(text, mp3):
    try:
        com = edge_tts.Communicate(text, VOICE, rate=RITMO, boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(text, VOICE, rate=RITMO)
    marcas = []
    with open(mp3, "wb") as fh:
        async for ch in com.stream():
            if ch["type"] == "audio":
                fh.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                marcas.append(ch["offset"] / 1e7)
    return marcas


def voz(text, base):
    """Devuelve (wav, duracion, tiempos de palabra)."""
    mp3, wav = base + ".mp3", base + ".wav"
    for intento in range(1, 5):
        try:
            marcas = asyncio.run(_voz(text, mp3))
            break
        except Exception as e:
            print(f"Voz fallo (intento {intento}): {type(e).__name__}: {e}", flush=True)
            if intento == 4:
                raise
            time.sleep(5 * intento)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", wav])
    with wave.open(wav) as w:
        return wav, w.getnframes() / w.getframerate(), marcas


def abrir(url, timeout=60):
    pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) GuineoDeportes/1.0", "Accept": "*/*"})
    return urllib.request.urlopen(pedido, timeout=timeout)


def tramo(origen, ini, fin, base):
    """Recorta un tramo de la narracion grabada por una persona."""
    wav = base + ".wav"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ini), "-to", str(fin), "-i", origen,
                           "-af", "highpass=f=70", "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", wav])
    with wave.open(wav) as w:
        return wav, w.getnframes() / w.getframerate(), []


def fondos(clave, carpeta, cuantos=6):
    """Descarga clips verticales o recortables, solo si sus etiquetas son de futbol."""
    if not clave:
        print("Sin clave de Pixabay: fondo liso")
        return []
    vistos, hits = set(), []
    for q in BUSQUEDAS:
        url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
            {"key": clave, "q": q, "per_page": 30, "safesearch": "true", "video_type": "film", "category": "sports"})
        try:
            with abrir(url, 30) as r:
                data = json.load(r)
        except Exception as e:
            print(f"::warning::Pixabay fallo en la busqueda {q}: {type(e).__name__} {getattr(e, 'code', '')}")
            continue
        for h in data.get("hits", []):
            tags = {t.strip().lower() for t in h.get("tags", "").split(",")}
            palabras = {p for t in tags for p in t.split()}
            if h["id"] in vistos or not (palabras & ETIQUETAS) or palabras & EXCLUIR:
                continue
            vistos.add(h["id"])
            hits.append(h)
    random.shuffle(hits)
    out = []
    for h in hits:
        if len(out) >= cuantos:
            break
        v = h["videos"].get("medium") or h["videos"].get("small")
        if not v or not v.get("url"):
            continue
        p = os.path.join(carpeta, f"bg{h['id']}.mp4")
        try:
            with abrir(v["url"], 120) as r, open(p, "wb") as fh:
                shutil.copyfileobj(r, fh)
            print("Clip", h["id"], h.get("tags"))
            out.append(p)
        except Exception as e:
            print(f"::warning::No se pudo bajar el clip {h['id']}: {type(e).__name__} {getattr(e, 'code', '')}")
    print(f"::notice::Clips de fondo: {len(out)} de {len(hits)} candidatos")
    return out


def foto_commons(titulo, carpeta):
    """Baja una foto de Wikimedia Commons solo si su licencia es libre. Devuelve (ruta, credito)."""
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "format": "json", "prop": "imageinfo", "titles": "File:" + titulo,
         "iiprop": "url|extmetadata", "iiurlwidth": 1800})
    try:
        with abrir(url, 30) as r:
            pag = next(iter(json.load(r)["query"]["pages"].values()))
        info = pag["imageinfo"][0]
        meta = info["extmetadata"]
        lic = meta.get("License", {}).get("value", "").lower()
        nombre = meta.get("LicenseShortName", {}).get("value", "")
        if not (lic.startswith(("cc-by", "cc0", "pd"))):
            print(f"::warning::Foto descartada por licencia: {titulo} ({nombre})")
            return None, None
        autor = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()[:50]
        destino = os.path.join(carpeta, "c" + str(abs(hash(titulo))) + ".jpg")
        with abrir(info.get("thumburl") or info["url"], 120) as r, open(destino, "wb") as fh:
            shutil.copyfileobj(r, fh)
        credito = f"Foto: {autor} / {nombre} / Wikimedia Commons"
        print(f"::notice::Foto usada: {titulo} | {credito}")
        return destino, credito
    except Exception as e:
        print(f"::warning::No se pudo usar la foto {titulo}: {type(e).__name__} {getattr(e, 'code', '')}")
        return None, None


def lector_fondo(clip, n):
    if not clip:
        return None
    return subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-i", clip, "-an",
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
         "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)


def teñir(arr, color):
    """Pasa el clip a los colores del equipo para que el fondo se asocie con el club."""
    lum = arr.mean(axis=2, keepdims=True) / 255.0
    return (lum * np.array(color, np.float32) * 0.85 + lum * 40).clip(0, 255).astype(np.uint8)


def foto_cuadro(foto, t, dur):
    """Encuadre con zoom lento de una foto propia."""
    z = 1.0 + 0.08 * (t / max(dur, .1))
    w, h = foto.size
    cw, ch = w / z, h / z
    x, y = (w - cw) / 2, (h - ch) / 2
    return foto.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))


def cargar_foto(ruta, lote):
    im = Image.open(os.path.join(os.path.dirname(os.path.abspath(lote)), ruta)).convert("RGB")
    esc = max(W * 1.1 / im.width, H * 1.1 / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x, y = (im.width - round(W * 1.1)) // 2, (im.height - round(H * 1.1)) // 2
    return im.crop((x, y, x + round(W * 1.1), y + round(H * 1.1)))


def render_escena(esc, wav_dur, marcas, clip, tag, dest, inicio, total, extra, color, lote, gap=GAP):
    dur = wav_dur + gap + extra
    n = round(dur * FPS)
    tmp = dest[:-4] + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    foto = None
    if esc.get("foto_commons"):
        ruta, cred = foto_commons(esc["foto_commons"], os.path.dirname(dest))
        if ruta:
            foto = cargar_foto(ruta, lote)
            esc = {**esc, "credito": cred}
    if esc.get("foto"):
        foto = cargar_foto(esc["foto"], lote)
    fondo = None if foto else lector_fondo(clip, n)
    credito = None
    if esc.get("credito"):
        credito = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
        ImageDraw.Draw(credito).text((W / 2, 30), esc["credito"], font=B(26), fill=INK, anchor="mm", stroke_width=3, stroke_fill=BG)
    c, ch = card(esc["grafico"]), marca(tag)
    caps = trozos(esc["texto"], marcas, wav_dur)
    capa = {}
    plano = np.full((H, W, 3), BG, np.uint8)
    for f in range(n):
        t = f / FPS
        arr = plano
        if foto:
            arr = (np.asarray(foto_cuadro(foto, t, dur)) * 0.45).astype(np.uint8)
        elif fondo:
            raw = fondo.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                arr = (teñir(np.frombuffer(raw, np.uint8).reshape(H, W, 3), color) * 0.55).astype(np.uint8)
        im = Image.fromarray(arr).convert("RGBA")
        im.alpha_composite(ch)
        e = ease(t / 0.4)
        layer = c
        if e < 1:
            layer = c.copy()
            layer.putalpha(c.getchannel("A").point(lambda v: int(v * e)))
        im.alpha_composite(layer, (0, 240 + int((1 - e) * 70)))
        cur = caps[0][1]
        for ini, txt in caps:
            if t >= ini:
                cur = txt
        capa.setdefault(cur, caption_layer(cur))
        im.alpha_composite(capa[cur], (0, 1170))
        if credito:
            im.alpha_composite(credito, (0, H - 90))
        ImageDraw.Draw(im).rectangle([0, H - 14, int(W * min(1, (inicio + t) / total)), H], fill=Y)
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg fallo al renderizar")
    if fondo:
        fondo.stdout.close()
        fondo.wait()
    os.replace(tmp, dest)
    return n / FPS


def generar_reel(reel, idx, salida, clips, work, lote):
    pref = os.path.join(work, f"r{idx}")
    gap = 0.0 if reel.get("audio") else GAP
    if reel.get("audio"):
        origen = os.path.join(os.path.dirname(os.path.abspath(lote)), reel["audio"])
        vozes = [tramo(origen, e["inicio"], e["fin"], f"{pref}_{i}") for i, e in enumerate(reel["escenas"])]
    else:
        vozes = [voz(e["texto"], f"{pref}_{i}") for i, e in enumerate(reel["escenas"])]
    total = sum(v[1] + gap for v in vozes) + 1.0
    partes, pistas, inicio = [], [], 0.0
    orden = clips[:]
    random.shuffle(orden)
    for i, (esc, (wav, dur, marcas)) in enumerate(zip(reel["escenas"], vozes)):
        extra = 1.0 if i == len(vozes) - 1 else 0.0
        clip = orden[i % len(orden)] if orden else None
        dest = f"{pref}_{i}.mp4"
        real = render_escena(esc, dur, marcas, clip, reel["etiqueta"], dest, inicio, total, extra, rgb(reel.get("color", "#2E7D4F")), lote, gap)
        with wave.open(wav) as w:
            sr = w.getframerate()
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        m = round(real * sr)
        pistas.append(np.concatenate([a, np.zeros(max(0, m - len(a)), np.int16)])[:m])
        partes.append(dest)
        inicio += real
    lista = f"{pref}.txt"
    with open(lista, "w") as fh:
        fh.writelines(f"file '{os.path.abspath(x)}'\n" for x in partes)
    mix = f"{pref}_mix.wav"
    with wave.open(mix, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(np.concatenate(pistas).tobytes())
    out = os.path.join(salida, f"reel-{idx:02d}.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", mix,
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                           "-shortest", "-movflags", "+faststart", out])
    print("Listo", out, round(inicio, 1), "s")


def main(lote, salida):
    os.makedirs(salida, exist_ok=True)
    reels = json.load(open(lote, encoding="utf-8"))
    with tempfile.TemporaryDirectory() as work:
        clips = fondos(os.environ.get("PIXABAY_API_KEY", "").strip(), work)
        for i, r in enumerate(reels, 1):
            generar_reel(r, i, salida, clips, work, lote)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except Exception as e:
        traceback.print_exc()
        donde = traceback.extract_tb(e.__traceback__)[-1]
        msg = f"{type(e).__name__}: {e} ({os.path.basename(donde.filename)}:{donde.lineno} {donde.name})"
        print("::error::" + msg.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A"), flush=True)
        sys.exit(1)
