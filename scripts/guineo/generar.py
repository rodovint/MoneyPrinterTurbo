"""Genera los reels de Guineo Comunicaciones a partir de lotes/actual.json.

Cada escena lleva una oracion narrada y un grafico de la noticia. Los clips de
Pixabay solo se usan de fondo, oscurecidos, y se filtran por etiquetas para que
sean de futbol. Uso: python scripts/guineo/generar.py lotes/actual.json salida
"""
import asyncio, json, os, random, re, shutil, subprocess, sys, tempfile, time, traceback, urllib.error, urllib.parse, urllib.request, wave

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pizarra  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H, FPS = 1080, 1920, 30
BG, INK, Y = (13, 20, 17), (248, 246, 238), (246, 201, 14)
VOICE = "es-EC-AndreaNeural"
VOCES = {"andrea": "es-EC-AndreaNeural", "luis": "es-EC-LuisNeural"}
GAP = 0.08
RITMO = "+10%"
MARCA = "GUINEO COMUNICACIONES"
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


ANIMADOS = {"pizarra", "pixel", "retro", "tv"}


_ESC = {}

# Nombres en español -> como los busca TheSportsDB (selecciones y clubes que no salen igual).
ESCUDO_EN = {"paises-bajos": "Netherlands", "holanda": "Netherlands", "alemania": "Germany", "espana": "Spain",
             "inglaterra": "England", "francia": "France", "italia": "Italy", "belgica": "Belgium",
             "brasil": "Brazil", "estados-unidos": "USA", "mexico": "Mexico", "canada": "Canada",
             "peru": "Peru", "japon": "Japan", "gales": "Wales", "escocia": "Scotland", "grecia": "Greece",
             "dinamarca": "Denmark", "noruega": "Norway", "suiza": "Switzerland", "croacia": "Croatia",
             "serbia": "Serbia", "turquia": "Turkey", "marruecos": "Morocco", "corea-del-sur": "South Korea",
             "republica-dominicana": "Dominican Republic", "haiti": "Haiti", "panama": "Panama"}


def slug(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def bajar_escudo(destino):
    """Si falta lotes/img/escudos/<slug>.png, lo baja de TheSportsDB (strBadge) por el nombre del archivo."""
    base = os.path.splitext(os.path.basename(destino))[0]
    for q in dict.fromkeys([ESCUDO_EN.get(base, ""), base.replace("-", " ")]):
        if not q:
            continue
        try:
            url = "https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t=" + urllib.parse.quote(q)
            with urllib.request.urlopen(url, timeout=20) as r:
                equipos = json.load(r).get("teams") or []
            equipos = [t for t in equipos if t.get("strSport") == "Soccer" and t.get("strBadge")]
            if not equipos:
                continue
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            urllib.request.urlretrieve(equipos[0]["strBadge"], destino)
            print(f"::notice::Escudo bajado de TheSportsDB: {equipos[0]['strTeam']} -> {destino}", flush=True)
            return True
        except Exception as e:
            print(f"::warning::No se pudo bajar el escudo de {q}: {e}", flush=True)
    return False


def escudo_auto(e):
    """Escudo de un equipo de partido/marcador: el que diga el JSON o, si falta, img/escudos/<slug del nombre>.png."""
    return e.get("escudo") or ("img/escudos/" + slug(e.get("nombre", "")) + ".png" if e.get("nombre") else None)


def todos_con_escudo(equipos):
    """Regla de Mui (17/11): o salen los escudos de TODOS los equipos o no sale ninguno."""
    ok = all(escudo_auto(e) and escudo_img(escudo_auto(e), 180) is not None for e in equipos)
    if not ok:
        print("::warning::Falta el escudo de algún equipo: la tarjeta sale SIN escudos (regla de Mui)", flush=True)
    return ok


def escudo_img(ruta, lado):
    """Escudo (PNG con transparencia) de lotes/<ruta>, escalado a un cuadrado de 'lado'."""
    if not ruta:
        return None
    clave = (ruta, lado)
    if clave not in _ESC:
        f = ruta if os.path.isabs(ruta) else os.path.join(ROOT, "lotes", ruta)
        if not os.path.exists(f):
            bajar_escudo(f)
        try:
            im = Image.open(f).convert("RGBA")
            im.thumbnail((lado, lado), Image.LANCZOS)
            _ESC[clave] = im
        except Exception as e:
            print(f"::warning::No se pudo abrir el escudo {ruta}: {e}")
            _ESC[clave] = None
    return _ESC[clave]


def pegar_escudo(im, ruta, cx, cy, lado):
    e = escudo_img(ruta, lado)
    if e is not None:
        im.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))
        return True
    return False


def card(c):
    if not c or c.get("tipo") in ANIMADOS or c.get("tipo") == "ninguno":
        return None
    im = Image.new("RGBA", (W, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    kind = c["tipo"]
    if kind == "titular":
        kf = B(40)
        kw = d.textlength(c["sobre"], font=kf) + 56
        d.rectangle([(W - kw) / 2, 110, (W + kw) / 2, 186], fill=Y)
        d.text((W / 2, 148), c["sobre"], font=kf, fill=BG, anchor="mm")
        for sz in [190, 170, 150, 130, 112, 100, 90, 80, 70]:
            f, l = fit(d, c["texto"], 900, 4, [sz])
            if len(l) * sz * 1.16 <= 650 and all(d.textlength(x, font=f) <= 900 for x in l):
                break
        titular(d, l, f, 215 + (660 - len(l) * f.size * 1.16) / 2, W // 2)
    elif kind == "cifra":
        f, l = fit(d, c["valor"], 920, 1, [430, 380, 320, 280, 240])
        ctext(d, 60, l, f, Y, 1.0)
        f2, l2 = fit(d, c["texto"], 880, 3, [72, 64, 56, 50], B)
        ctext(d, 650 - (len(l2) - 1) * 28, l2, f2, INK, 1.1)
    elif kind == "marcador":
        con_escudo = todos_con_escudo(c["equipos"])
        for i, e in enumerate(c["equipos"]):
            y = 90 + i * 300
            d.rectangle([60, y, W - 60, y + 280], fill=rgb(e["color"]))
            x0 = 105
            if con_escudo and pegar_escudo(im, escudo_auto(e), 170, y + 140, 180):
                x0 = 280
            f, l = fit(d, e["nombre"], W - 300 - x0 - 20, 1, [130, 112, 96, 84, 72, 62])
            d.text((x0, y + 140), l[0], font=f, fill=INK, anchor="lm")
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
        con_escudo = todos_con_escudo(c["equipos"])
        for i, e in enumerate(c["equipos"]):
            y = 90 + i * 300
            d.rectangle([60, y, W - 60, y + 280], fill=rgb(e["color"]))
            if con_escudo and pegar_escudo(im, escudo_auto(e), 175, y + 140 + (-20 if i == 0 else 20), 190):
                f, l = fit(d, e["nombre"], 680, 1, [120, 104, 92, 80, 70])
                d.text(((290 + W - 60) / 2, y + 140), l[0], font=f, fill=INK, anchor="mm")
            else:
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
    elif kind == "escudo":
        pegar_escudo(im, c["escudo"], W / 2, 250, 380)
        if c.get("sobre"):
            kf = B(40)
            kw = d.textlength(c["sobre"], font=kf) + 56
            d.rectangle([(W - kw) / 2, 470, (W + kw) / 2, 546], fill=Y)
            d.text((W / 2, 508), c["sobre"], font=kf, fill=BG, anchor="mm")
        f, l = fit(d, c["texto"], 900, 2, [130, 112, 96, 84])
        titular(d, l, f, 570, W // 2)
    elif kind == "cierre":
        marca_txt = c.get("marca", MARCA)
        logo = os.path.join(ROOT, "scripts/guineo/logo-guineo.png")
        if os.path.exists(logo):
            ctext(d, 40, [c["texto"]], fit(d, c["texto"], 900, 1, [110, 96, 84])[0], INK)
            lg = Image.open(logo).convert("RGBA").resize((330, 330), Image.LANCZOS)
            im.alpha_composite(lg, ((W - 330) // 2, 185))
            d.rectangle([60, 545, W - 60, 805], fill=Y)
            f, l = fit(d, marca_txt, 880, 2, [120, 110, 96, 84])
            titular(d, l, f, 675 - len(l) * f.size * 1.16 / 2, W // 2, BG)
        else:
            ctext(d, 170, [c["texto"]], fit(d, c["texto"], 900, 1, [120, 100, 84])[0], INK)
            d.rectangle([60, 360, W - 60, 660], fill=Y)
            f, l = fit(d, marca_txt, 880, 2, [120, 110, 96, 84])
            titular(d, l, f, 510 - len(l) * f.size * 1.16 / 2, W // 2, BG)
    else:
        raise ValueError(f"tipo de escena desconocido: {kind}")
    return im


def marca(tag):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = A(46)
    w = d.textlength(MARCA, font=f) + 48
    d.rectangle([60, 120, 60 + w, 200], fill=Y)
    d.text((60 + w / 2, 160), MARCA, font=f, fill=BG, anchor="mm")
    d.text((60, 225), tag, font=B(34), fill=INK, anchor="lm", stroke_width=3, stroke_fill=BG)
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


async def _voz(text, mp3, voice=None):
    voice = voice or VOICE
    try:
        com = edge_tts.Communicate(text, voice, rate=RITMO, boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(text, voice, rate=RITMO)
    marcas = []
    with open(mp3, "wb") as fh:
        async for ch in com.stream():
            if ch["type"] == "audio":
                fh.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                marcas.append(ch["offset"] / 1e7)
    return marcas


def voz(text, base, voice=None):
    """Devuelve (wav, duracion, tiempos de palabra)."""
    mp3, wav = base + ".mp3", base + ".wav"
    for intento in range(1, 5):
        try:
            marcas = asyncio.run(_voz(text, mp3, voice))
            break
        except Exception as e:
            print(f"Voz fallo (intento {intento}): {type(e).__name__}: {e}", flush=True)
            if intento == 4:
                raise
            time.sleep(5 * intento)
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", "volume=-3dB", "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", wav])
    with wave.open(wav) as w:
        return wav, w.getnframes() / w.getframerate(), marcas


def abrir(url, timeout=60):
    agente = "Mozilla/5.0 (X11; Linux x86_64) GuineoComunicaciones/1.0"
    if "wikimedia.org" in url:
        agente = "GuineoComunicacionesReels/1.0 (https://github.com/rodovint/MoneyPrinterTurbo)"
    pedido = urllib.request.Request(url, headers={"User-Agent": agente, "Accept": "*/*"})
    for intento in range(4):
        try:
            return urllib.request.urlopen(pedido, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429 or intento == 3:
                raise
            time.sleep(10 * (intento + 1))


def tramo(origen, ini, fin, base):
    """Recorta un tramo de la narracion grabada por una persona."""
    wav = base + ".wav"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ini), "-to", str(fin), "-i", origen,
                           "-af", LIMPIEZA, "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", wav])
    with wave.open(wav) as w:
        return wav, w.getnframes() / w.getframerate(), []


LIMPIEZA = ("highpass=f=80,afftdn=nf=-25,deesser,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
            "equalizer=f=3000:t=q:w=1.2:g=3,volume=3dB")


EXT_AUDIO = (".m4a", ".mp3", ".wav", ".ogg", ".opus", ".aac", ".mp4")


def buscar_audio(base):
    """Acepta 'audio/01' con cualquier extension comun de audio."""
    if os.path.splitext(base)[1].lower() in EXT_AUDIO and os.path.exists(base):
        return base
    for ext in EXT_AUDIO:
        if os.path.exists(base + ext):
            return base + ext
    return None


def silencios(origen, umbral=-35, minimo=0.3):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", origen, "-af", f"silencedetect=n={umbral}dB:d={minimo}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    fin = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    dur = float(re.search(r"Duration: (\d+):(\d+):([0-9.]+)", out).group(3)) + \
        60 * float(re.search(r"Duration: (\d+):(\d+)", out).group(2)) + \
        3600 * float(re.search(r"Duration: (\d+)", out).group(1))
    pares = list(zip(ini, fin + [dur] * (len(ini) - len(fin))))
    return pares, dur


def repartir(origen, textos):
    """Divide una grabacion en escenas usando las pausas entre frases."""
    pares, dur = silencios(origen)
    voz_ini = pares[0][1] if pares and pares[0][0] <= 0.05 else 0.0
    voz_fin = pares[-1][0] if pares and pares[-1][1] >= dur - 0.05 else dur
    huecos = [(a, b) for a, b in pares if a > voz_ini + 0.2 and b < voz_fin - 0.2]
    pesos = [max(len(t), 1) for t in textos]
    total, acum, cortes, desde = sum(pesos), 0, [], voz_ini
    for p in pesos[:-1]:
        acum += p
        esperado = voz_ini + (voz_fin - voz_ini) * acum / total
        candidatos = [(abs((a + b) / 2 - esperado) / (0.4 + (b - a)), (a + b) / 2) for a, b in huecos if (a + b) / 2 > desde + 0.4]
        corte = min(candidatos)[1] if candidatos and min(candidatos)[0] < 6 else esperado
        cortes.append(corte)
        desde = corte
    bordes = [max(0.0, voz_ini - 0.1)] + cortes + [min(dur, voz_fin + 0.15)]
    tramos = list(zip(bordes[:-1], bordes[1:]))
    print("Escenas detectadas:", ", ".join(f"{a:.1f}-{b:.1f}" for a, b in tramos), flush=True)
    return tramos


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
         "iiprop": "url|extmetadata", "iiurlwidth": 1920})
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


def lector_fondo(clip, n, desde=0.0):
    if not clip:
        return None
    return subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-ss", str(desde), "-i", clip, "-an",
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
         "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)


def teñir(arr, color):
    """Pasa el clip a los colores del equipo para que el fondo se asocie con el club."""
    lum = arr.mean(axis=2, keepdims=True) / 255.0
    return (lum * np.array(color, np.float32) * 0.85 + lum * 40).clip(0, 255).astype(np.uint8)


MOVIMIENTOS = {"zoom_in", "zoom_out", "paneo_izq", "paneo_der", "subir", "bajar", "quieto"}


def foto_cuadro(foto, t, dur, mov="zoom_in"):
    """Encuadre con movimiento lento (efecto Ken Burns) de una foto o dibujo."""
    p = min(1.0, t / max(dur, .1))
    p = p * p * (3 - 2 * p)
    w, h = foto.size
    if mov == "zoom_out":
        z = 1.08 - 0.08 * p
    elif mov in ("paneo_izq", "paneo_der", "subir", "bajar"):
        z = 1.06
    elif mov == "quieto":
        z = 1.0
    else:
        z = 1.0 + 0.08 * p
    cw, ch = w / z, h / z
    x, y = (w - cw) / 2, (h - ch) / 2
    if mov == "paneo_der":
        x = (w - cw) * p
    elif mov == "paneo_izq":
        x = (w - cw) * (1 - p)
    elif mov == "subir":
        y = (h - ch) * (1 - p)
    elif mov == "bajar":
        y = (h - ch) * p
    return foto.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))


def cargar_foto(ruta, lote):
    im = Image.open(os.path.join(os.path.dirname(os.path.abspath(lote)), ruta)).convert("RGB")
    esc = max(W * 1.1 / im.width, H * 1.1 / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x, y = (im.width - round(W * 1.1)) // 2, (im.height - round(H * 1.1)) // 2
    return im.crop((x, y, x + round(W * 1.1), y + round(H * 1.1)))


_FX = None


def fx():
    """guineo_fx (transiciones, numeros animados, franja, paletas), cargado al usarlo."""
    global _FX
    if _FX is None:
        import importlib.util as iu
        sp = iu.spec_from_file_location("guineo_fx", os.path.join(os.path.dirname(os.path.abspath(__file__)), "guineo_fx.py"))
        _FX = iu.module_from_spec(sp)
        sp.loader.exec_module(_FX)
    return _FX


LOGO = os.path.join(ROOT, "scripts/guineo/logo-guineo.png")


def render_escena(esc, wav_dur, marcas, clip, tag, dest, inicio, total, extra, color, lote, gap=GAP, efectos=None):
    efectos = efectos or {}
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
    propio = esc.get("video")
    if propio:
        propio = os.path.join(os.path.dirname(os.path.abspath(lote)), propio)
        if not os.path.exists(propio):
            print(f"::warning::No existe el video propio {esc['video']}, se usa el fondo normal", flush=True)
            propio = None
    mov = esc.get("movimiento", "zoom_in")
    if mov not in MOVIMIENTOS:
        mov = "zoom_in"
    fondo = None if foto else lector_fondo(propio or clip, n, float(esc.get("video_inicio", 0)) if propio else 0.0)
    credito = None
    if esc.get("credito"):
        credito = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
        ImageDraw.Draw(credito).text((W / 2, 30), esc["credito"], font=B(26), fill=INK, anchor="mm", stroke_width=3, stroke_fill=BG)
    g = esc.get("grafico")
    animado = bool(g) and g.get("tipo") in ANIMADOS
    numero = g.get("valor") if g and g.get("tipo") == "cifra" and esc.get("animar", True) else None
    if numero and (efectos.get("primera") or re.fullmatch(r"(19|20)\d\d", str(numero).strip())):
        numero = None  # el gancho se ve completo desde el fotograma 0 y los años no "cuentan"
    c, ch = card({**g, "valor": ""} if numero else g), marca(tag)
    F = fx() if (efectos.get("entrada") or efectos.get("franja") or efectos.get("tono") or numero) else None
    logo = Image.open(LOGO).convert("RGBA") if efectos.get("franja") and os.path.exists(LOGO) else None
    n_tr = 7
    limpio = c is None and not animado  # sin grafico: la imagen se ve con brillo completo
    luz_foto, luz_video = (0.92, 0.9) if limpio else (0.45, 0.5)
    fuentes = (A(56), B(30), A(70))
    caps = trozos(esc["texto"], marcas, wav_dur)
    capa = {}
    plano = np.full((H, W, 3), BG, np.uint8)
    for f in range(n):
        t = f / FPS
        arr = plano
        if foto:
            arr = (np.asarray(foto_cuadro(foto, t, dur, mov)) * luz_foto).astype(np.uint8)
        elif fondo:
            raw = fondo.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                cuadro = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
                if propio:
                    arr = (cuadro * luz_video).astype(np.uint8)
                else:
                    arr = (teñir(cuadro, color) * 0.55).astype(np.uint8)
        im = Image.fromarray(arr).convert("RGBA")
        im.alpha_composite(ch)
        e = 1.0 if efectos.get("primera") else ease(t / 0.4)
        layer = pizarra.capa(g, t, dur, *fuentes) if animado else c
        if layer is not None:
            if e < 1:
                base = layer
                layer = base.copy()
                layer.putalpha(base.getchannel("A").point(lambda v: int(v * e)))
            im.alpha_composite(layer, (0, 240 + int((1 - e) * 70)))
        if numero:
            nl = F.numero_layer(str(numero), t, size=300 if len(str(numero)) <= 5 else 220)
            im.alpha_composite(nl, (0, 240 + 60 + 210 - nl.height // 2 + int((1 - e) * 70)))
        cur = caps[0][1]
        for ini, txt in caps:
            if t >= ini:
                cur = txt
        capa.setdefault(cur, caption_layer(cur))
        im.alpha_composite(capa[cur], (0, 1170))
        if credito:
            im.alpha_composite(credito, (0, H - 90))
        if efectos.get("franja"):
            im.alpha_composite(F.band_layer(inicio + t, efectos["franja"], logo), (0, F.BAND_Y))
        ImageDraw.Draw(im).rectangle([0, H - 14, int(W * min(1, (inicio + t) / total)), H], fill=Y)
        out = im.convert("RGB")
        if efectos.get("tono"):
            out = F.tone(out, efectos["tono"], f)
        if efectos.get("entrada") and f < n_tr:
            out = F.transition(out, efectos["entrada"], 1 - f / n_tr, "in", f)
        p.stdin.write(out.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg fallo al renderizar")
    if fondo:
        fondo.stdout.close()
        fondo.wait()
    os.replace(tmp, dest)
    return n / FPS


def es_auto(esc):
    return str(esc.get("voz", "")).lower() in VOCES or str(esc.get("voz", "")).lower() == "mui"


def voz_clonada(texto, base, lote):
    """Frase de Mui ya generada por voz_clon.py (Chatterbox). Devuelve None si no esta."""
    import hashlib
    ref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voz", "mui-ref.wav")
    h = hashlib.sha1()
    h.update(texto.strip().encode("utf-8"))
    h.update(open(ref, "rb").read() if os.path.exists(ref) else b"")
    src = os.path.join(os.path.dirname(os.path.abspath(lote)), "audio", "clon", h.hexdigest()[:16] + ".wav")
    if not os.path.exists(src):
        return None
    wav = base + ".wav"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af",
                           "silenceremove=start_periods=1:start_threshold=-38dB,areverse,silenceremove=start_periods=1:start_threshold=-38dB,areverse,"
                           "afade=t=in:d=0.02,areverse,afade=t=in:d=0.08,areverse,highpass=f=80,lowpass=f=9000,"
                           "equalizer=f=3000:t=q:w=1.2:g=2,alimiter=limit=0.9",
                           "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", wav])
    with wave.open(wav) as w:
        return wav, w.getnframes() / w.getframerate(), []


def voces_reel(reel, pref, lote):
    """Voz de cada escena: tramos de la grabacion humana (Mui o Andrea) y Edge TTS en las escenas con "voz": "andrea"/"luis"."""
    escenas = reel["escenas"]
    humanas = [i for i, e in enumerate(escenas) if not es_auto(e)]
    out = [None] * len(escenas)
    if reel.get("audio") and humanas:
        origen = buscar_audio(os.path.join(os.path.dirname(os.path.abspath(lote)), reel["audio"]))
        if not origen:
            return None
        if all("inicio" in escenas[i] and "fin" in escenas[i] for i in humanas):
            tramos = [(escenas[i]["inicio"], escenas[i]["fin"]) for i in humanas]
        else:
            tramos = repartir(origen, [escenas[i]["texto"] for i in humanas])
        for i, (a, b) in zip(humanas, tramos):
            out[i] = tramo(origen, a, b, f"{pref}_{i}")
    for i, e in enumerate(escenas):
        if out[i] is None and str(e.get("voz", "")).lower() == "mui":
            out[i] = voz_clonada(e.get("dicho", e["texto"]), f"{pref}_{i}", lote)
            if out[i] is None:
                print(f"::warning::Sin voz clonada para: {e['texto'][:40]}... (va con Andrea)", flush=True)
        if out[i] is None:
            out[i] = voz(e.get("dicho", e["texto"]), f"{pref}_{i}", VOCES.get(str(e.get("voz", "")).lower(), reel.get("voz_tts", VOICE)))
    return out


SR = 44100
MUSICA = os.path.join(ROOT, "scripts/guineo/audio/musica.mp3")
HINCHADA = os.path.join(ROOT, "scripts/guineo/audio/hinchada.mp3")


def leer_audio(ruta, n):
    """Decodifica un audio a mono 44.1 kHz en float, repetido o cortado a n muestras."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    if not len(a):
        return np.zeros(n, np.float32)
    return np.tile(a, n // len(a) + 1)[:n]


def whoosh(sr=SR, dur=0.45, seed=0):
    """Swoosh grave y suave (sin siseo): ruido limitado a 80-1000 Hz con barrido de tono."""
    rng = np.random.default_rng(seed)
    n = int(sr * dur)
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / sr)
    spec[(f < 80) | (f > 1000)] = 0
    ruido = np.fft.irfft(spec, n).astype(np.float32)
    k = np.linspace(0, 1, n)
    env = np.sin(np.pi * k) ** 3
    out = ruido * env
    return (out / (np.abs(out).max() + 1e-6) * 0.6).astype(np.float32)


def golpe(sr=SR, dur=0.6):
    t = np.arange(int(sr * dur)) / sr
    f = 55 + 40 * np.exp(-t * 18)
    return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 6) * 0.8).astype(np.float32)


def latido(sr=SR, dur=0.9):
    t = np.arange(int(sr * dur)) / sr
    def bum(t0):
        tt = np.clip(t - t0, 0, None)
        return np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 22) * (t >= t0)
    return ((bum(0) + 0.7 * bum(0.28)) * 0.7).astype(np.float32)


def pegar(pista, sonido, ini, gan=1.0):
    i = max(0, int(ini * SR))
    j = min(len(pista), i + len(sonido))
    if j > i:
        pista[i:j] += sonido[:j - i] * gan


def hoja_contacto(video, dest, n=12):
    """12 fotogramas en una hoja para revisar textos, cortes y superposiciones."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout.strip() or 0)
    if not dur:
        return
    hoja = Image.new("RGB", (6 * 270, 2 * 480 + 40), BG)
    d = ImageDraw.Draw(hoja)
    for k in range(n):
        t = dur * (k + 0.5) / n if k else 0.0
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                              "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) == 270 * 480 * 3:
            hoja.paste(Image.frombuffer("RGB", (270, 480), raw), ((k % 6) * 270, (k // 6) * 500 + 20))
        d.text(((k % 6) * 270 + 6, (k // 6) * 500 + 2), f"{t:.1f}s", font=B(16), fill=Y)
    hoja.save(dest, quality=85)


def generar_reel(reel, idx, salida, clips, work, lote):
    pref = os.path.join(work, f"r{idx}")
    vozes = voces_reel(reel, pref, lote)
    if vozes is None:
        print(f"::notice::Reel {idx:02d} ({reel.get('titulo', '')}): falta la voz {reel['audio']}, se salta", flush=True)
        return False
    gap = GAP if not reel.get("audio") else 0.0
    total = sum(v[1] + gap for v in vozes) + 1.0
    partes, pistas, cortes, inicio = [], [], [], 0.0
    orden = clips[:]
    random.shuffle(orden)
    franja = reel.get("franja") or [reel.get("titulo", "").upper(), reel.get("etiqueta", "")]
    franja = [x for x in franja if x]
    trans = ["barrido", "zoom", "glitch", "barrido", "flash", "zoom"]
    n_esc = len(vozes)
    for i, (esc, (wav, dur, marcas)) in enumerate(zip(reel["escenas"], vozes)):
        extra = 1.0 if i == n_esc - 1 else 0.0
        clip = orden[i % len(orden)] if orden else None
        dest = f"{pref}_{i}.mp4"
        efectos = {
            "entrada": None if i == 0 else esc.get("transicion", "flash" if esc.get("destello") else trans[(i + idx) % len(trans)]),
            "salida": None if i == n_esc - 1 else "fade",
            "primera": i == 0,
            "franja": None if (esc.get("grafico") or {}).get("tipo") == "cierre" else franja,
            "tono": esc.get("tono"),
        }
        real = render_escena(esc, dur, marcas, clip, reel["etiqueta"], dest, inicio, total, extra, rgb(reel.get("color", "#2E7D4F")), lote, gap, efectos)
        with wave.open(wav) as w:
            sr = w.getframerate()
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        m = round(real * sr)
        pistas.append(np.concatenate([a, np.zeros(max(0, m - len(a)), np.int16)])[:m])
        partes.append(dest)
        cortes.append((inicio, esc))
        inicio += real
    lista = f"{pref}.txt"
    with open(lista, "w") as fh:
        fh.writelines(f"file '{os.path.abspath(x)}'\n" for x in partes)
    voz_pista = np.concatenate(pistas).astype(np.float32) / 32768
    if sr != SR:
        voz_pista = np.interp(np.linspace(0, len(voz_pista) - 1, int(len(voz_pista) * SR / sr)), np.arange(len(voz_pista)), voz_pista).astype(np.float32)
    n = len(voz_pista)
    fx = np.zeros(n, np.float32)
    if reel.get("musica", True) and os.path.exists(MUSICA):
        mus = leer_audio(MUSICA, n)
        env = np.ones(n, np.float32)
        fin = min(n, int(1.5 * SR))
        env[-fin:] = np.linspace(1, 0, fin)
        env[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
        fx += mus * env * float(reel.get("volumen_musica", 0.15))
    for k, (t0, esc) in enumerate(cortes):
        if k:
            pegar(fx, whoosh(seed=k), t0 - 0.22, 0.12)
        if esc.get("destello"):
            pegar(fx, golpe(), t0, 0.6)
        if esc.get("suspenso"):
            pegar(fx, latido(), t0, 0.5)
        if esc.get("hinchada") and os.path.exists(HINCHADA):
            pegar(fx, leer_audio(HINCHADA, int(3 * SR)) * np.linspace(1, 0, int(3 * SR)), t0, 0.15)
    mezcla = voz_pista + fx
    cola = min(n, int(0.6 * SR))
    mezcla[-cola:] *= np.linspace(1, 0, cola)
    mezcla = np.clip(mezcla, -1, 1)
    mix = f"{pref}_mix.wav"
    with wave.open(mix, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mezcla * 32767).astype(np.int16).tobytes())
    out = os.path.join(salida, f"reel-{idx:02d}.mp4")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", mix,
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                           "-shortest", "-movflags", "+faststart", out])
    try:
        hoja_contacto(out, os.path.join(salida, f"contacto-{idx:02d}.jpg"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", out, "-frames:v", "1", "-q:v", "2",
                        os.path.join(salida, f"portada-{idx:02d}.jpg")])
    except Exception as e:
        print(f"::warning::Sin hoja de contacto/portada para reel-{idx:02d}: {e}")
    if inicio > 36:
        print(f"::warning::reel-{idx:02d} dura {round(inicio, 1)} s (ideal 25-35 s)")
    print(f"::notice::Listo reel-{idx:02d} ({reel.get('titulo', '')}): {round(inicio, 1)} s", flush=True)
    return True


def main(lote, salida):
    os.makedirs(salida, exist_ok=True)
    reels = json.load(open(lote, encoding="utf-8"))
    with tempfile.TemporaryDirectory() as work:
        clips = None
        hechos = 0
        for i, r in enumerate(reels, 1):
            if r.get("audio") and any(not es_auto(e) for e in r["escenas"]) and not buscar_audio(os.path.join(os.path.dirname(os.path.abspath(lote)), r["audio"])):
                print(f"::notice::Reel {i:02d} ({r.get('titulo', '')}): falta la voz {r['audio']}, se salta", flush=True)
                continue
            if clips is None:
                clips = fondos(os.environ.get("PIXABAY_API_KEY", "").strip(), work)
            hechos += bool(generar_reel(r, i, salida, clips, work, lote))
        print(f"::notice::Reels generados: {hechos} de {len(reels)}", flush=True)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except Exception as e:
        traceback.print_exc()
        donde = traceback.extract_tb(e.__traceback__)[-1]
        msg = f"{type(e).__name__}: {e} ({os.path.basename(donde.filename)}:{donde.lineno} {donde.name})"
        print("::error::" + msg.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A"), flush=True)
        sys.exit(1)
