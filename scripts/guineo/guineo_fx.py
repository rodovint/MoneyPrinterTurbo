"""Guineo FX: efectos y plantillas para variar los cortos sin perder el estilo Guineo Comunicaciones.

Todo trabaja a 1080x1920, 30 fps, con las fuentes y colores del generador (generar.py).

Cambios pequeños
  tone(im, mood)                 paleta por tono: "recuerdo" (blanco y negro sepia con grano), "urgente" (rojo),
                                 "celebracion" (dorado), "presente" (sin cambio)
  apply_edges(src, dest, ...)    transición de entrada/salida de un plano y su paleta:
                                 "barrido", "zoom", "rota", "flash", "glitch"
  numero_layer(valor, t)         número que cuenta hacia arriba (3.321) o letras que rebotan (6.º, 4:22.87)
  apply_band(src, dest, ticker)  franja fija de noticiero Guineo con texto corrido sobre todo el video

Plantillas de formato (cada una escribe un plano .mp4)
  render_cifra(...)              tarjeta de cifra con número animado sobre clip teñido
  render_top(...)                paso de cuenta regresiva "Top 5"
  render_sabias(...)             tarjeta "¿Sabías que…?" con el dato escribiéndose
  render_split(...)              pantalla dividida "Antes / Ahora"
  render_mapa(...)               mapa estilo radar con ruta animada entre ciudades
  render_portada(...)            portada de serie (PREVIA / RESULTADO) para videos encadenados
"""
import importlib.util, json, math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("g_fx", os.path.join(HERE, "generar.py"))
g = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(g)
W, H, FPS, Y, BG, INK = g.W, g.H, g.FPS, g.Y, g.BG, g.INK
ease = g.ease


def marca(tag):
    """Cabecera Guineo Comunicaciones (la del generador dice GUINEO DEPORTES)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = g.A(46)
    w = d.textlength("GUINEO COMUNICACIONES", font=f) + 48
    d.rectangle([60, 120, 60 + w, 200], fill=Y); d.text((60 + w / 2, 160), "GUINEO COMUNICACIONES", font=f, fill=BG, anchor="mm")
    if tag:
        d.text((60, 222), tag, font=g.B(34), fill=INK, anchor="lm", stroke_width=3, stroke_fill=BG)
    return im


# ---------------------------------------------------------------- I/O
def count_frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_packets", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return int(out.strip() or 0)


def stream(path):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    while True:
        raw = p.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            break
        yield Image.frombuffer("RGB", (W, H), raw)
    p.wait()


def writer(dest, crf=19):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p", dest], stdin=subprocess.PIPE)


def fade_layer(layer, a):
    if a >= 1:
        return layer
    l2 = layer.copy(); l2.putalpha(layer.getchannel("A").point(lambda v: int(v * max(0, a)))); return l2


def progress(im, start, t, total):
    if total:
        ImageDraw.Draw(im).rectangle([0, H - 14, int(W * min(1, (start + t) / total)), H], fill=Y)


# ---------------------------------------------------------------- paletas
_GRAIN = None


def tone(im, mood, f=0):
    global _GRAIN
    if not mood or mood == "presente":
        return im
    if mood == "recuerdo":
        gr = ImageOps.grayscale(im)
        im2 = ImageOps.colorize(gr, (18, 14, 10), (240, 226, 200))
        if _GRAIN is None:
            rng = np.random.default_rng(3); _GRAIN = [Image.fromarray(rng.integers(0, 40, (H // 2, W // 2), dtype=np.uint8)).resize((W, H)) for _ in range(4)]
        noise = _GRAIN[f % 4]
        im2 = Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im2, noise.point(lambda v: v // 2))
        vg = Image.radial_gradient("L").resize((W, H)).point(lambda v: min(255, int(max(0, v - 90) * 1.6)))
        return Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im2, vg)
    if mood == "urgente":
        return Image.blend(im, Image.new("RGB", im.size, (200, 16, 46)), 0.28)
    if mood == "celebracion":
        im2 = ImageEnhance.Color(im).enhance(1.25)
        return Image.blend(im2, Image.new("RGB", im.size, (230, 170, 20)), 0.16)
    return im


# ---------------------------------------------------------------- transiciones
def fx_barrido(im, k, color=Y, side="out"):
    """Panel de color en diagonal que cubre la imagen (k=1 la cubre entera)."""
    if k <= 0:
        return im
    im = im.copy(); d = ImageDraw.Draw(im); x = (W + 700) * k - 350
    pts = [(-400, 0), (x + 350, 0), (x - 350, H), (-400, H)] if side == "out" else [(W + 400, 0), (W - x - 350 + 700, 0), (W - x - 350, H), (W + 400, H)]
    d.polygon(pts, fill=color)
    d.polygon([(p[0] + (30 if side == "out" else -30), p[1]) for p in pts], outline=BG)
    return im


def fx_zoom(im, k):
    if k <= 0:
        return im
    z = 1 + 0.35 * k; w, h = int(W * z), int(H * z)
    big = im.resize((w, h), Image.BILINEAR).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    return big.filter(ImageFilter.GaussianBlur(6 * k))


def fx_rota(im, k, seed=7):
    """Pantalla rota: fragmentos desplazados y grietas blancas desde un punto de impacto."""
    if k <= 0:
        return im
    rng = np.random.default_rng(seed); cx, cy = W * 0.56, H * 0.42
    angs = sorted(rng.uniform(0, 2 * math.pi, 12)); cracks = []
    for a in angs:
        pts = [(cx, cy)]; r = 0
        while r < 1600:
            r += rng.uniform(80, 200); a2 = a + rng.uniform(-0.22, 0.22); pts.append((cx + math.cos(a2) * r, cy + math.sin(a2) * r))
        cracks.append(pts)
    base = im.copy()
    for i in range(0, len(cracks) - 1, 2):
        poly = [(cx, cy)] + cracks[i][1:] + cracks[i + 1][::-1][:-1]
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
        a = angs[i]; sh = Image.new("RGB", im.size); sh.paste(im, (int(22 * k * math.cos(a)), int(22 * k * math.sin(a))))
        base = Image.composite(ImageEnhance.Brightness(sh).enhance(1 + 0.25 * k), base, m)
    d = ImageDraw.Draw(base)
    for pts in cracks:
        d.line(pts, fill=(255, 255, 255), width=int(3 + 5 * k))
    d.ellipse([cx - 40 * k, cy - 40 * k, cx + 40 * k, cy + 40 * k], fill=(255, 255, 255))
    return Image.blend(im, base, min(1, k * 1.5))


def fx_flash(im, k):
    if k <= 0:
        return im
    glow = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(14))).enhance(1 + 2.5 * k)
    return Image.blend(Image.blend(im, glow, 0.6 * k), Image.new("RGB", im.size, (255, 255, 255)), 0.75 * k)


def fx_glitch(im, k, seed=1):
    if k <= 0:
        return im
    rng = np.random.default_rng(seed); a = np.asarray(im).copy(); sh = int(40 * k); out = a.copy()
    out[:, :, 0] = np.roll(a[:, :, 0], sh, axis=1); out[:, :, 2] = np.roll(a[:, :, 2], -sh, axis=1)
    for _ in range(int(14 * k)):
        y = int(rng.integers(0, H - 60)); hh = int(rng.integers(8, 90))
        out[y:y + hh] = np.roll(out[y:y + hh], int(rng.integers(-120, 120) * k), axis=1)
    return Image.fromarray(out)


def transition(im, kind, k, side, seed=0, color=Y):
    if kind == "barrido":
        return fx_barrido(im, k, color, side)
    if kind == "zoom":
        return fx_zoom(im, k)
    if kind == "rota":
        return fx_rota(im, k, seed)
    if kind == "flash":
        return fx_flash(im, k)
    if kind == "glitch":
        return fx_glitch(im, k, seed)
    return im


def apply_edges(src, dest, t_in=None, t_out=None, mood=None, frames=7, color=Y):
    """Repinta un plano: paleta y transiciones de entrada/salida (sin cambiar su duración)."""
    n = count_frames(src); p = writer(dest + ".tmp.mp4")
    for i, im in enumerate(stream(src)):
        im = tone(im, mood, i)
        if t_in:
            im = transition(im, t_in, max(0.0, 1 - i / frames), "in", i, color)
        if t_out:
            im = transition(im, t_out, max(0.0, 1 - (n - 1 - i) / frames), "out", i, color)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); os.replace(dest + ".tmp.mp4", dest)


# ---------------------------------------------------------------- números animados
def _fmt(v, dec_sep=None):
    s = f"{int(round(v)):,}".replace(",", ".")
    return s


def numero_layer(valor, t, color=Y, size=300, dur_count=0.9):
    """Si el valor es un entero (con o sin puntos de miles) cuenta hacia arriba; si no, sus caracteres rebotan."""
    im = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = g.A(size)
    plain = valor.replace(".", "")
    cy = im.height // 2
    if plain.isdigit() and len(plain) > 1:
        v = int(plain) * ease(t / dur_count)
        txt = _fmt(v) if "." in valor else str(int(round(v)))
        sc = 1 + 0.12 * max(0, 1 - abs(t - dur_count) / 0.15)
        f2 = g.A(int(size * sc))
        d.text((W / 2, cy), txt, font=f2, fill=color, anchor="mm", stroke_width=8, stroke_fill=BG)
        return im
    widths = [d.textlength(c, font=f) for c in valor]; x = W / 2 - sum(widths) / 2
    for i, (c, w) in enumerate(zip(valor, widths)):
        tt = t - i * 0.07
        if tt <= 0:
            x += w; continue
        e = min(1, tt / 0.28); bounce = 1 + 0.35 * math.sin(e * math.pi) * (1 - e)
        dy = -90 * (1 - e) ** 2
        ch = Image.new("RGBA", (int(w * 1.6) + 20, int(size * 1.4)), (0, 0, 0, 0))
        ImageDraw.Draw(ch).text((ch.width / 2, ch.height / 2), c, font=g.A(int(size * bounce)), fill=color, anchor="mm", stroke_width=8, stroke_fill=BG)
        im.alpha_composite(ch, (int(x + w / 2 - ch.width / 2), int(dy)))
        x += w
    return im


# ---------------------------------------------------------------- franja de noticiero
BAND_Y = 1690


def band_layer(t, ticker, logo=None, tag="GUINEO"):
    lay = Image.new("RGBA", (W, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, W, 100], fill=(13, 20, 17, 235)); d.rectangle([0, 0, W, 6], fill=Y)
    f = g.A(46); seg = "   ·   ".join(ticker) + "   ·   "
    sw = d.textlength(seg, font=f); x0 = 200 - (t * 150) % sw
    while x0 < W:
        d.text((x0, 54), seg, font=f, fill=INK, anchor="lm"); x0 += sw
    d.rectangle([0, 6, 190, 100], fill=Y)
    if logo is not None:
        lg = logo.resize((84, 84), Image.LANCZOS); lay.alpha_composite(lg, (53, 11))
    else:
        d.text((95, 54), tag, font=g.A(40), fill=BG, anchor="mm")
    return lay


def apply_band(src, dest, ticker, logo_path=None, skip=()):
    """Franja fija de noticiero sobre todo el video. skip: lista de (t0, t1) donde no se muestra (p. ej. el cierre)."""
    logo = Image.open(logo_path).convert("RGBA") if logo_path else None
    p = writer(dest + ".tmp.mp4", crf=18)
    for i, im in enumerate(stream(src)):
        t = i / FPS
        if not any(a <= t < b for a, b in skip):
            a = min(1, t / 0.4); im = im.convert("RGBA"); im.alpha_composite(fade_layer(band_layer(t, ticker, logo), a), (0, BAND_Y)); im = im.convert("RGB")
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); os.replace(dest + ".tmp.mp4", dest)


# ---------------------------------------------------------------- fondos
def fondo_iter(clip, n, color, dark=0.5):
    if clip:
        r = g.lector_fondo(clip, n)
        for _ in range(n):
            raw = r.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                yield Image.fromarray((g.teñir(np.frombuffer(raw, np.uint8).reshape(H, W, 3), color) * dark).astype(np.uint8))
            else:
                yield Image.new("RGB", (W, H), BG)
        r.stdout.close(); r.wait()
    else:
        for _ in range(n):
            yield Image.new("RGB", (W, H), BG)


def _caps(caption, marks, vo):
    return g.trozos(caption, marks, vo) if caption else None


def _cap_at(caps, t, cache):
    cur = caps[0][1]
    for ini, txt in caps:
        if t >= ini:
            cur = txt
    cache.setdefault(cur, g.caption_layer(cur)); return cache[cur]


def _common(im, t, head, caps, cache, start, total):
    im.alpha_composite(head)
    if caps:
        im.alpha_composite(_cap_at(caps, t, cache), (0, 1200))
    progress(im, start, t, total)
    return im


def _text_block(text, font, maxw, fill=INK, align="mm"):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words, lines, cur = text.split(), [], ""
    for w in words:
        tt = (cur + " " + w).strip()
        if d.textlength(tt, font=font) <= maxw:
            cur = tt
        else:
            lines.append(cur); cur = w
    lines.append(cur); return lines


# ---------------------------------------------------------------- plantillas
def render_cifra(dest, dur, valor, texto, color, clip=None, caption="", marks=(), vo=None, tag="", start=0, total=0, sobre=None):
    n = round(dur * FPS); head = marca(tag); caps = _caps(caption, marks, vo or dur); cache = {}
    sub = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(sub); f = g.A(64)
    for i, ln in enumerate(_text_block(texto, f, W - 160)):
        d.text((W / 2, 50 + i * 78), ln, font=f, fill=INK, anchor="mm")
    top = None
    if sobre:
        top = Image.new("RGBA", (W, 90), (0, 0, 0, 0)); dd = ImageDraw.Draw(top); ft = g.A(40); w = dd.textlength(sobre, font=ft) + 40
        dd.rectangle([W / 2 - w / 2, 10, W / 2 + w / 2, 80], fill=Y); dd.text((W / 2, 45), sobre, font=ft, fill=BG, anchor="mm")
    p = writer(dest)
    for fidx, bg in enumerate(fondo_iter(clip, n, color)):
        t = fidx / FPS; im = bg.convert("RGBA")
        if top:
            im.alpha_composite(fade_layer(top, ease(t / 0.3)), (0, 330))
        im.alpha_composite(numero_layer(valor, t - 0.1), (0, 430))
        im.alpha_composite(fade_layer(sub, ease((t - 0.5) / 0.4)), (0, 860 + int((1 - ease((t - 0.5) / 0.4)) * 30)))
        p.stdin.write(_common(im, t, head, caps, cache, start, total).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def render_top(dest, dur, num, titulo, sub, color, clip=None, caption="", marks=(), vo=None, tag="", start=0, total=0):
    """Paso de cuenta regresiva: el número entra desde la izquierda, el título se apila debajo."""
    n = round(dur * FPS); head = marca(tag); caps = _caps(caption, marks, vo or dur); cache = {}
    numl = Image.new("RGBA", (W, 520), (0, 0, 0, 0)); ImageDraw.Draw(numl).text((90, 260), f"#{num}", font=g.A(440), fill=Y, anchor="lm", stroke_width=10, stroke_fill=BG)
    tl = Image.new("RGBA", (W, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(tl); ft = g.A(84)
    lines = _text_block(titulo, ft, W - 160)
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=ft) + 50; d.rectangle([70, 20 + i * 104, 70 + w, 112 + i * 104], fill=BG); d.text((95, 66 + i * 104), ln, font=ft, fill=INK, anchor="lm")
    for j, sl in enumerate(_text_block(sub, g.B(40), W - 180)):
        d.text((80, 40 + len(lines) * 104 + j * 50), sl, font=g.B(40), fill=Y, anchor="lm")
    p = writer(dest)
    for fidx, bg in enumerate(fondo_iter(clip, n, color, 0.55)):
        t = fidx / FPS; im = bg.convert("RGBA"); e = ease(t / 0.35)
        im.alpha_composite(fade_layer(numl, e), (int(-500 * (1 - e)), 330))
        e2 = ease((t - 0.3) / 0.35); im.alpha_composite(fade_layer(tl, e2), (int(300 * (1 - e2)), 850))
        p.stdin.write(_common(im, t, head, caps, cache, start, total).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def render_sabias(dest, dur, dato, color, clip=None, caption="", marks=(), vo=None, tag="", start=0, total=0):
    """Sello amarillo ¿SABÍAS QUE…? que gira al entrar y el dato que se escribe letra por letra."""
    n = round(dur * FPS); head = marca(tag); caps = _caps(caption, marks, vo or dur); cache = {}
    st = Image.new("RGBA", (760, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle([10, 10, 750, 190], 24, fill=Y, outline=BG, width=8); d.text((380, 100), "¿SABÍAS QUE…?", font=g.A(96), fill=BG, anchor="mm")
    ft = g.A(78); lines = _text_block(dato, ft, W - 180); total_chars = sum(len(l) for l in lines)
    p = writer(dest)
    for fidx, bg in enumerate(fondo_iter(clip, n, color, 0.45)):
        t = fidx / FPS; im = bg.convert("RGBA"); e = ease(t / 0.35)
        s2 = st.rotate(-8 + 20 * (1 - e), expand=True, resample=Image.BICUBIC).resize((int(st.width * (0.6 + 0.4 * e) * 1.0), int(st.height * (0.6 + 0.4 * e))))
        im.alpha_composite(fade_layer(s2, e), (int(W / 2 - s2.width / 2), 380))
        shown = int(max(0, t - 0.5) * 38); y = 700; d2 = ImageDraw.Draw(im)
        for ln in lines:
            part = ln[:max(0, shown)]; shown -= len(ln)
            if part:
                d2.text((W / 2, y), part, font=ft, fill=INK, anchor="mm", stroke_width=5, stroke_fill=BG)
            y += 96
        p.stdin.write(_common(im, t, head, caps, cache, start, total).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def _cover(img, w, h, fx=0.5, fy=0.5, z=1.0):
    sc = max(w / img.width, h / img.height) * z; iw, ih = int(img.width * sc), int(img.height * sc)
    big = img.resize((iw, ih), Image.BICUBIC); x = int(min(max(fx * iw - w / 2, 0), iw - w)); y = int(min(max(fy * ih - h / 2, 0), ih - h))
    return big.crop((x, y, x + w, y + h))


def render_split(dest, dur, img_a, img_b, lab_a="ANTES", lab_b="AHORA", titulo="", fa=(0.5, 0.4), fb=(0.5, 0.4), tag="", caption="", marks=(), vo=None, start=0, total=0):
    """Pantalla dividida arriba/abajo con barra amarilla que se abre y etiquetas ANTES / AHORA."""
    n = round(dur * FPS); head = marca(tag); caps = _caps(caption, marks, vo or dur); cache = {}
    A = Image.open(img_a).convert("RGB"); B = Image.open(img_b).convert("RGB"); hh = (H - 300) // 2
    def chip(txt):
        c = Image.new("RGBA", (W, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(c); f = g.A(70); w = d.textlength(txt, font=f) + 50
        d.rectangle([60, 10, 60 + w, 100], fill=Y); d.text((85, 55), txt, font=f, fill=BG, anchor="lm"); return c
    ca, cb = chip(lab_a), chip(lab_b)
    tt_l = None
    if titulo:
        tt_l = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); ImageDraw.Draw(tt_l).text((W / 2, 60), titulo, font=g.A(64), fill=INK, anchor="mm", stroke_width=6, stroke_fill=BG)
    p = writer(dest)
    for fidx in range(n):
        t = fidx / FPS; k = t / dur; im = Image.new("RGBA", (W, H), BG + (255,))
        e = ease(t / 0.45)
        a = ImageOps.grayscale(_cover(A, W, hh, *fa, z=1.0 + 0.06 * k)).convert("RGB")
        b = _cover(B, W, hh, *fb, z=1.0 + 0.06 * k)
        im.paste(a, (int(-W * (1 - e)), 260)); im.paste(b, (int(W * (1 - e)), 260 + hh + 40))
        ImageDraw.Draw(im).rectangle([0, 260 + hh, int(W * e), 260 + hh + 40], fill=Y)
        im.alpha_composite(fade_layer(ca, ease((t - 0.4) / 0.3)), (0, 260 + hh - 130)); im.alpha_composite(fade_layer(cb, ease((t - 0.6) / 0.3)), (0, 260 + hh + 60))
        if tt_l:
            im.alpha_composite(fade_layer(tt_l, ease((t - 0.8) / 0.3)), (0, H - 230))
        p.stdin.write(_common(im, t, head, caps, cache, start, total).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def render_mapa(dest, dur, puntos, titulo="", tag="", caption="", marks=(), vo=None, start=0, total=0, bbox=None):
    """Mapa estilo radar: cuadrícula, puntos que laten y una ruta punteada que viaja de un punto al siguiente.
    puntos: [(nombre, lat, lon), ...]; bbox: (lon_min, lat_min, lon_max, lat_max)."""
    n = round(dur * FPS); head = marca(tag); caps = _caps(caption, marks, vo or dur); cache = {}
    lons = [p[2] for p in puntos]; lats = [p[1] for p in puntos]
    if not bbox:
        pad = max(8, (max(lons) - min(lons)) * 0.25); bbox = (min(lons) - pad, min(lats) - pad, max(lons) + pad, max(lats) + pad)
    x0, y0, x1, y1 = 60, 380, W - 60, 1560
    sc = min((x1 - x0) / (bbox[2] - bbox[0]), (y1 - y0) / (bbox[3] - bbox[1]))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; mlon, mlat = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    proj = lambda lat, lon: (cx + (lon - mlon) * sc, cy - (lat - mlat) * sc)
    base = Image.new("RGBA", (W, H), (8, 16, 30, 255)); d = ImageDraw.Draw(base)
    step = 10
    for lon in range(int(bbox[0] // step * step), int(bbox[2]) + step, step):
        x, _ = proj(0, lon); d.line([x, 300, x, 1640], fill=(30, 60, 90), width=2)
    for lat in range(int(bbox[1] // step * step), int(bbox[3]) + step, step):
        _, y = proj(lat, 0); d.line([0, y, W, y], fill=(30, 60, 90), width=2)
    _, ye = proj(0, 0)
    if 300 < ye < 1640:
        d.line([0, ye, W, ye], fill=(60, 110, 150), width=3); d.text((W - 70, ye - 10), "ECUADOR · LÍNEA 0°", font=g.B(24), fill=(90, 140, 180), anchor="rb")
    pts = [proj(p[1], p[2]) for p in puntos]
    tl = None
    if titulo:
        tl = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); ImageDraw.Draw(tl).text((W / 2, 60), titulo, font=g.A(72), fill=INK, anchor="mm", stroke_width=6, stroke_fill=BG)
    seg_t = max(0.6, (dur - 1.2) / max(1, len(pts) - 1))
    p = writer(dest)
    for fidx in range(n):
        t = fidx / FPS; im = base.copy(); d = ImageDraw.Draw(im)
        for i in range(len(pts) - 1):
            k = max(0, min(1, (t - 0.4 - i * seg_t) / (seg_t * 0.8)))
            if k <= 0:
                continue
            (ax, ay), (bx, by) = pts[i], pts[i + 1]; mx, my = (ax + bx) / 2, min(ay, by) - abs(bx - ax) * 0.35
            path = [((1 - u) ** 2 * ax + 2 * (1 - u) * u * mx + u ** 2 * bx, (1 - u) ** 2 * ay + 2 * (1 - u) * u * my + u ** 2 * by) for u in np.linspace(0, k, 60)]
            for j in range(0, len(path) - 1, 2):
                d.line([path[j], path[j + 1]], fill=Y, width=8)
            hx, hy = path[-1]; d.ellipse([hx - 14, hy - 14, hx + 14, hy + 14], fill=INK)
        for i, ((x, y), (nm, *_)) in enumerate(zip(pts, puntos)):
            appear = 0.2 + i * seg_t
            if t < appear:
                continue
            r = 16 + 10 * (0.5 + 0.5 * math.sin((t - appear) * 5)); ring = 30 + 60 * ((t - appear) % 1.0)
            d.ellipse([x - ring, y - ring, x + ring, y + ring], outline=(246, 201, 14, int(200 * (1 - (t - appear) % 1.0))), width=4)
            d.ellipse([x - r, y - r, x + r, y + r], fill=Y, outline=BG, width=4)
            f = g.A(54); w = d.textlength(nm, font=f) + 30; lx = min(max(x - w / 2, 30), W - 30 - w)
            d.rectangle([lx, y + 40, lx + w, y + 110], fill=BG); d.text((lx + w / 2, y + 75), nm, font=f, fill=INK, anchor="mm")
        if tl:
            im.alpha_composite(fade_layer(tl, ease(t / 0.4)), (0, 300))
        p.stdin.write(_common(im, t, head, caps, cache, start, total).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def render_portada(dest, dur, serie, titulo, estado="PREVIA", color="#1F4FB8", clip=None, tag="", start=0, total=0):
    """Portada de serie: nombre de la serie, chip de estado (PREVIA / RESULTADO) y título; mismo diseño en cada capítulo."""
    n = round(dur * FPS); head = marca(tag); col = g.rgb(color)
    top = Image.new("RGBA", (W, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(top); d.text((W / 2, 80), serie, font=g.A(70), fill=INK, anchor="mm")
    chip = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(chip); f = g.A(130); w = d.textlength(estado, font=f) + 80
    d.rectangle([W / 2 - w / 2, 20, W / 2 + w / 2, 180], fill=col); d.text((W / 2, 100), estado, font=f, fill=INK, anchor="mm")
    tl = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(tl); ft = g.A(96)
    for i, ln in enumerate(_text_block(titulo, ft, W - 140)):
        d.text((W / 2, 60 + i * 116), ln, font=ft, fill=Y, anchor="mm", stroke_width=6, stroke_fill=BG)
    p = writer(dest)
    for fidx, bg in enumerate(fondo_iter(clip, n, col, 0.45)):
        t = fidx / FPS; im = bg.convert("RGBA")
        im.alpha_composite(fade_layer(top, ease(t / 0.3)), (0, 380))
        e = ease((t - 0.2) / 0.35); c2 = chip.resize((int(W * (0.7 + 0.3 * e)), int(200 * (0.7 + 0.3 * e)))); im.alpha_composite(fade_layer(c2, e), (int(W / 2 - c2.width / 2), 560))
        im.alpha_composite(fade_layer(tl, ease((t - 0.45) / 0.35)), (0, 820))
        im.alpha_composite(head); progress(im, start, t, total)
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
