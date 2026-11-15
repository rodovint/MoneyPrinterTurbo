"""Pizarra tactica animada para los reels de Guineo Comunicaciones.

Dibuja la mitad de ataque de una cancha (el arco arriba) y anima una jugada
paso a paso. Dos estilos: "pizarra" (tiza sobre pizarra verde) y "pixel"
(recreacion estilo videojuego retro).

Formato del grafico en el lote:
{
  "tipo": "pizarra",                  # o "pixel" (equivale a estilo pixel)
  "estilo": "pizarra" | "pixel",
  "titulo": "ASI FUE EL 1-0",
  "local": {"nombre": "ORENSE", "color": "#1E8A4C"},
  "rival": {"nombre": "EMELEC", "color": "#0B4EA2"},
  "jugadores": [
    {"id": "9", "equipo": "local", "x": 50, "y": 45},
    {"id": "4", "equipo": "rival", "x": 45, "y": 30},
    {"id": "1", "equipo": "rival", "x": 50, "y": 3, "arquero": true}
  ],
  "balon": "7",                       # id del jugador que la tiene, o [x, y]
  "pasos": [
    {"mover": {"9": [60, 25]}, "balon": "9", "flecha": "pase", "texto": "PASE FILTRADO"},
    {"balon": [52, -2], "flecha": "tiro", "gol": true, "texto": "GOLAZO"}
  ]
}
Coordenadas en 0-100: x de izquierda a derecha, y desde la linea de gol (0)
hasta la mitad de la cancha (100). y < 0 es dentro del arco.
flecha: "pase" (linea), "conduccion" (punteada), "tiro" (gruesa) o nada.
"""
import math

from PIL import Image, ImageDraw

import jugadas

LW, LH = 1080, 900
INK, Y, BG = (248, 246, 238), (246, 201, 14), (13, 20, 17)


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _estado(c, t, dur):
    """Posiciones de jugadores y balon en el instante t, mas los trazos ya hechos."""
    pos = {j["id"]: (float(j["x"]), float(j["y"])) for j in c["jugadores"]}
    b0 = c.get("balon")
    ball = pos[b0] if isinstance(b0, str) and b0 in pos else tuple(b0 or (50, 50))
    pasos = c.get("pasos", [])
    ini, hold = 0.6, 1.0
    util = max(dur - ini - hold, 0.5 * max(len(pasos), 1))
    tramo = util / max(len(pasos), 1)
    trazos, texto, gol, mov = [], None, False, []
    for k, p in enumerate(pasos):
        lt = (t - ini - k * tramo) / tramo
        if lt <= 0:
            break
        e = _ease(lt)
        nuevos = {i: tuple(map(float, v)) for i, v in p.get("mover", {}).items()}
        fin_pos = {**pos, **nuevos}
        objetivo = p.get("balon")
        if isinstance(objetivo, str) and objetivo in fin_pos:
            b1 = fin_pos[objetivo]
        elif objetivo is not None:
            b1 = tuple(map(float, objetivo))
        else:
            b1 = ball
        for i, v in nuevos.items():
            a = pos[i]
            cur = (a[0] + (v[0] - a[0]) * e, a[1] + (v[1] - a[1]) * e)
            mov.append((a, cur))
            pos[i] = cur
        nb = (ball[0] + (b1[0] - ball[0]) * e, ball[1] + (b1[1] - ball[1]) * e)
        if p.get("flecha") and b1 != ball:
            trazos.append((p["flecha"], ball, nb, lt >= 1))
        ball = nb
        texto = p.get("texto") or texto
        if lt >= 1 and p.get("gol"):
            gol = True
        if lt < 1:
            break
    return pos, ball, trazos, mov, texto, gol


def _cancha(d, s, x0, y0, x1, y1, linea, grosor):
    w, h = x1 - x0, y1 - y0
    P = lambda x, y: (x0 + x / 100 * w, y0 + y / 100 * h)
    d.rectangle([x0, y0, x1, y1], outline=linea, width=grosor)
    # area grande, chica, punto penal, arco del area
    a0, a1 = P(50 - 29.6, 0), P(50 + 29.6, 31.4)
    d.rectangle([a0[0], a0[1], a1[0], a1[1]], outline=linea, width=grosor)
    c0, c1 = P(50 - 13.5, 0), P(50 + 13.5, 10.5)
    d.rectangle([c0[0], c0[1], c1[0], c1[1]], outline=linea, width=grosor)
    pp = P(50, 21)
    r = 9.15 / 68 * w
    d.arc([pp[0] - r, pp[1] - r, pp[0] + r, pp[1] + r], 37, 143, fill=linea, width=grosor)
    d.ellipse([pp[0] - 3 * s, pp[1] - 3 * s, pp[0] + 3 * s, pp[1] + 3 * s], fill=linea)
    # arco
    g0, g1 = P(50 - 5.4, -4), P(50 + 5.4, 0)
    d.rectangle([g0[0], g0[1], g1[0], g1[1]], outline=linea, width=grosor)
    # medio circulo de la mitad
    mc = P(50, 100)
    d.arc([mc[0] - r, mc[1] - r, mc[0] + r, mc[1] + r], 180, 360, fill=linea, width=grosor)
    return P


def _linea_punteada(d, a, b, fill, width, paso):
    L = math.dist(a, b)
    if L < 1:
        return
    n = int(L // paso)
    for i in range(0, n, 2):
        p0 = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
        p1 = (a[0] + (b[0] - a[0]) * min(i + 1, n) / n, a[1] + (b[1] - a[1]) * min(i + 1, n) / n)
        d.line([p0, p1], fill=fill, width=width)


def _punta(d, a, b, fill, tam):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = [b, (b[0] - tam * math.cos(ang - .45), b[1] - tam * math.sin(ang - .45)),
           (b[0] - tam * math.cos(ang + .45), b[1] - tam * math.sin(ang + .45))]
    d.polygon(pts, fill=fill)


def capa(c, t, dur, fuente_titulo, fuente_num, fuente_texto):
    """Devuelve una capa RGBA de 1080x900 con la jugada en el instante t."""
    if c.get("estilo") in jugadas.ESTILOS or c.get("tipo") in jugadas.ESTILOS:
        return jugadas.capa(c, t, dur, fuente_titulo, fuente_num, fuente_texto)
    pixel = c.get("estilo") == "pixel" or c.get("tipo") == "pixel"
    s = 0.2 if pixel else 1.0
    im = Image.new("RGBA", (round(LW * s), round(LH * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if pixel:
        d.fontmode = "1"
    x0, y0, x1, y1 = 70 * s, 110 * s, (LW - 70) * s, (LH - 30) * s
    if pixel:
        franjas = 8
        for i in range(franjas):
            ya, yb = y0 + (y1 - y0) * i / franjas, y0 + (y1 - y0) * (i + 1) / franjas
            d.rectangle([x0, ya, x1, yb], fill=(58, 140, 52, 255) if i % 2 else (70, 160, 60, 255))
        linea, grosor = (240, 240, 230, 255), 1
    else:
        d.rounded_rectangle([x0 - 20, y0 - 20, x1 + 20, y1 + 20], radius=24, fill=(24, 58, 40, 235))
        linea, grosor = (235, 240, 230, 200), 5
    P = _cancha(d, s, x0, y0, x1, y1, linea, grosor)
    pos, ball, trazos, mov, texto, gol = _estado(c, t, dur)
    loc = _rgb(c.get("local", {}).get("color", "#1E8A4C"))
    riv = _rgb(c.get("rival", {}).get("color", "#B3202A"))
    for a, b in mov:
        _linea_punteada(d, P(*a), P(*b), (255, 255, 255, 120), max(1, round(3 * s)), max(2, 14 * s))
    for kind, a, b, hecho in trazos:
        pa, pb = P(*a), P(*b)
        col = (255, 90, 60, 255) if kind == "tiro" else (*Y, 255)
        w = max(1, round((12 if kind == "tiro" else 7) * s))
        if kind == "conduccion":
            _linea_punteada(d, pa, pb, col, w, max(2, 18 * s))
        else:
            d.line([pa, pb], fill=col, width=w)
        if math.dist(pa, pb) > 30 * s:
            _punta(d, pa, pb, col, max(3, 30 * s))
    for j in c["jugadores"]:
        x, y = P(*pos[j["id"]])
        col = loc if j.get("equipo", "local") == "local" else riv
        if j.get("arquero"):
            col = (230, 200, 40) if j.get("equipo") == "local" else (40, 40, 40)
        if pixel:
            x, y = round(x), round(y)
            d.rectangle([x - 1, y - 6, x + 1, y - 4], fill=(205, 150, 110))   # cabeza
            d.rectangle([x - 3, y - 3, x + 3, y + 1], fill=col)               # camiseta
            d.rectangle([x - 2, y + 2, x - 1, y + 4], fill=(30, 30, 30))      # piernas
            d.rectangle([x + 1, y + 2, x + 2, y + 4], fill=(30, 30, 30))
        else:
            r = 30
            d.ellipse([x - r, y - r, x + r, y + r], fill=(*col, 255), outline=INK, width=4)
            d.text((x, y + 1), str(j.get("dorsal", j["id"])), font=fuente_num, fill=INK, anchor="mm",
                   stroke_width=2, stroke_fill=BG)
    bx, by = P(*ball)
    if pixel:
        d.rectangle([round(bx) - 1, round(by) - 1, round(bx) + 1, round(by) + 1], fill=(255, 255, 255), outline=(20, 20, 20))
    else:
        d.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(255, 255, 255, 255), outline=BG, width=4)
    if pixel:
        im = im.resize((LW, LH), Image.NEAREST)
        d = ImageDraw.Draw(im)
    if c.get("titulo"):
        tw = d.textlength(c["titulo"], font=fuente_titulo) + 50
        d.rectangle([(LW - tw) / 2, 22, (LW + tw) / 2, 92], fill=(*Y, 255))
        d.text((LW / 2, 57), c["titulo"], font=fuente_titulo, fill=BG, anchor="mm")
    if texto:
        d.text((LW / 2, LH - 95), texto, font=fuente_texto, fill=INK, anchor="mm", stroke_width=6, stroke_fill=BG)
    if gol:
        d.text((LW / 2, LH * 0.45), "¡GOL!", font=fuente_titulo.font_variant(size=230), fill=Y, anchor="mm",
               stroke_width=10, stroke_fill=BG)
    return im
