"""Estilos nuevos para recrear jugadas en los reels de Guineo Comunicaciones.

Se usan desde pizarra.capa() cuando el grafico trae "estilo": "retro" o "tv"
(o "tipo": "retro" / "tv"). Mismo formato de jugada que la pizarra clasica:
jugadores (con "nombre" opcional para la etiqueta), balon y pasos.

- "retro": videojuego de 16 bits. Cancha en perspectiva de transmision, tribuna
  animada detras del arco, jugadores con sprite (pelo, piel, camiseta con sombra,
  piernas que corren), balon que se eleva en los tiros, marcador tipo consola y
  ¡GOL! pixelado con confeti. Pixeles finos (escala 1/2), sin el look de bloques.
- "tv": grafico tactico de transmision moderna. Cancha en perspectiva, lineas con
  brillo, fichas con anillo de color y etiqueta con nombre, pases en curva que se
  dibujan solos, estela del balon y pulso sobre el protagonista.

Campos extra opcionales del grafico:
  "marcador": {"local": "RAV", "rival": "FOR", "antes": [0, 0], "despues": [1, 0], "minuto": "35'"}
  jugador: "nombre": "DONATI", "destacado": true
  paso: "curva": 0.25 (curvatura del pase, + hacia arriba de la pantalla)
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LW, LH = 1080, 900
INK, Y, BG = (248, 246, 238), (246, 201, 14), (13, 20, 17)


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _mezcla(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- perspectiva
def _homografia(src, dst):
    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    h = np.linalg.solve(np.array(A, float), np.array(b, float))
    return np.append(h, 1).reshape(3, 3)


def _alcance(c):
    """Hasta que profundidad de la cancha llega la jugada (la camara se acerca a la accion)."""
    ys = [float(j["y"]) for j in c["jugadores"]]
    for p in c.get("pasos", []):
        ys += [float(v[1]) for v in p.get("mover", {}).values()]
        if isinstance(p.get("balon"), list):
            ys.append(float(p["balon"][1]))
    return max(42.0, min(100.0, max(ys) + 14))


def _proyector(s, arriba=190, abajo=890, ancho_arriba=600, ancho_abajo=1240, fondo=100.0):
    """(x, y) de cancha 0-100 -> pixel de la capa (escala s). El arco queda arriba, lejos.
    'fondo' es la profundidad (y) que cae en el borde de abajo: menos = camara mas cerca."""
    cx = LW / 2
    dst = [(cx - ancho_arriba / 2, arriba), (cx + ancho_arriba / 2, arriba),
           (cx + ancho_abajo / 2, abajo), (cx - ancho_abajo / 2, abajo)]
    Hm = _homografia([(0, 0), (100, 0), (100, fondo), (0, fondo)], dst)

    def P(x, y):
        v = Hm @ np.array([x, y, 1.0])
        return (v[0] / v[2] * s, v[1] / v[2] * s)

    def escala(x, y):  # pixeles de pantalla por unidad de cancha en x
        a, b = P(x - 1, y), P(x + 1, y)
        return math.dist(a, b) / 2 / s

    return P, escala


def _poligono_cancha(d, P, pts, **kw):
    d.polygon([P(*p) for p in pts], **kw)


def _lineas_cancha(d, P, fill, width, pasos=24):
    def seg(a, b):
        d.line([P(*a), P(*b)], fill=fill, width=width)

    def caja(x0, y0, x1, y1):
        seg((x0, y0), (x1, y0)); seg((x1, y0), (x1, y1)); seg((x1, y1), (x0, y1)); seg((x0, y1), (x0, y0))

    caja(0, 0, 100, 100)
    caja(50 - 29.6, 0, 50 + 29.6, 31.4)
    caja(50 - 13.5, 0, 50 + 13.5, 10.5)
    r = 9.15 / 68 * 100
    # arco del area (solo la parte fuera del area grande)
    arc = [(50 + r * math.cos(a), 21 + r * 68 / 52.5 * math.sin(a)) for a in np.linspace(0.65, math.pi - 0.65, pasos)]
    arc = [p for p in arc if p[1] >= 31.4]
    if len(arc) > 1:
        d.line([P(*p) for p in arc], fill=fill, width=width)
    # medio circulo de la mitad
    mc = [(50 + r * math.cos(a), 100 - r * 68 / 52.5 * math.sin(a)) for a in np.linspace(0, math.pi, pasos)]
    d.line([P(*p) for p in mc], fill=fill, width=width)
    return r


# ---------------------------------------------------------------- estado de la jugada
def _estado(c, t, dur):
    """Igual que la pizarra clasica, mas el progreso del paso actual y la curva."""
    pos = {j["id"]: (float(j["x"]), float(j["y"])) for j in c["jugadores"]}
    b0 = c.get("balon")
    ball = pos[b0] if isinstance(b0, str) and b0 in pos else tuple(b0 or (50, 50))
    pasos = c.get("pasos", [])
    ini, hold = 0.5, 1.3
    util = max(dur - ini - hold, 0.6 * max(len(pasos), 1))
    tramo = util / max(len(pasos), 1)
    trazos, texto, gol, corriendo, alto = [], None, None, set(), 0.0
    portador = b0 if isinstance(b0, str) else None
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
            pos[i] = (a[0] + (v[0] - a[0]) * e, a[1] + (v[1] - a[1]) * e)
            if lt < 1:
                corriendo.add(i)
        curva = float(p.get("curva", 0.18 if p.get("flecha") == "pase" else 0.0))
        nb = _bezier(ball, b1, curva, e)
        if p.get("flecha") and b1 != ball:
            trazos.append({"tipo": p["flecha"], "a": ball, "b": b1, "curva": curva, "e": e, "hecho": lt >= 1})
        if p.get("flecha") == "tiro" and lt < 1:
            alto = 4 * e * (1 - e)
        if lt < 1 and objetivo is None and nuevos and portador in nuevos:
            nb = pos[portador]
        ball = nb
        if isinstance(objetivo, str):
            portador = objetivo
        elif objetivo is not None:
            portador = None
        texto = p.get("texto") or texto
        if lt >= 1 and p.get("gol"):
            gol = t - (ini + (k + 1) * tramo)
        if lt < 1:
            break
    return pos, ball, trazos, texto, gol, corriendo, alto


def _bezier(a, b, curva, e):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    cx, cy = mx - dy * curva, my + dx * curva
    u = 1 - e
    return (u * u * a[0] + 2 * u * e * cx + e * e * b[0], u * u * a[1] + 2 * u * e * cy + e * e * b[1])


def _ruta(tr, n=28):
    return [_bezier(tr["a"], tr["b"], tr["curva"], tr["e"] * i / n) for i in range(n + 1)]


# ---------------------------------------------------------------- estilo RETRO (16 bits)
SPRITE = [  # 12 x 18, se le agrega contorno automatico
    "....hhhh....",
    "...hhhhhh...",
    "...hsssss...",
    "...sssss....",
    "....sss.....",
    "..cccccccc..",
    ".scccccccCs.",
    ".sccccccCCs.",
    ".scccccCCCs.",
    "..ccccCCCC..",
    "..wwwwwwww..",
    "..wwwwwwww..",
    "..ss....ss..",
    "..ss....ss..",
    "..kk....kk..",
    "..kk....kk..",
    ".kkk...kkk..",
]
PIERNAS_A = ["..ss.....ss.", "..ss.....ss.", ".kk......kk.", ".kk.......kk", "kkk.......kk"]
PIERNAS_B = ["....ss.ss...", "....ss.ss...", "....kk.kk...", "....kk.kk...", "...kkk.kkk.."]


def _sprite(col, cuadro, arquero=False):
    filas = SPRITE[:12] + (SPRITE[12:] if cuadro == 0 else (PIERNAS_A if cuadro == 1 else PIERNAS_B))
    camiseta = col
    sombra = tuple(max(0, int(v * 0.62)) for v in camiseta)
    short = (245, 245, 245) if sum(camiseta) < 330 else (35, 35, 45)
    pal = {"h": (40, 26, 18), "s": (214, 160, 118), "c": camiseta, "C": sombra, "w": short, "k": (25, 25, 30)}
    if arquero:
        pal["c"], pal["C"] = (60, 200, 90), (30, 130, 55)
    h, w = len(filas), len(filas[0])
    im = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    px = im.load()
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch in pal:
                px[x + 1, y + 1] = (*pal[ch], 255)
    a = np.array(im)
    lleno = a[..., 3] > 0
    borde = np.zeros_like(lleno)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        borde |= np.roll(np.roll(lleno, dy, 0), dx, 1)
    borde &= ~lleno
    a[borde] = (12, 14, 20, 255)
    return Image.fromarray(a)


def _texto_pixel(texto, fuente, color, borde=(12, 14, 20)):
    """Texto sin suavizado (pixel), con borde de 1 px."""
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t_, r, b = tmp.textbbox((0, 0), texto, font=fuente)
    im = Image.new("RGBA", (r - l + 4, b - t_ + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        d.text((2 - l + dx, 2 - t_ + dy), texto, font=fuente, fill=(*borde, 255))
    d.text((2 - l, 2 - t_), texto, font=fuente, fill=(*color, 255))
    return im


def _retro(c, t, dur, fuente_titulo, fuente_num, fuente_texto):
    s = 0.5
    w, h = round(LW * s), round(LH * s)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    P, esc = _proyector(s, arriba=200, abajo=900, ancho_arriba=760, ancho_abajo=1500, fondo=_alcance(c))
    loc = _rgb(c.get("local", {}).get("color", "#1E8A4C"))
    riv = _rgb(c.get("rival", {}).get("color", "#B3202A"))

    # tribuna detras del arco, con hinchas que se mueven
    ty0, ty1 = round(120 * s), round(P(0, -7)[1])
    d.rectangle([0, ty0, w, ty1], fill=(28, 30, 44, 255))
    rnd = random.Random(int(t * 7))
    base = random.Random(7)
    for yy in range(ty0 + 2, ty1 - 3, 4):
        for xx in range(1, w, 3):
            colr = base.choice([loc, loc, Y, (230, 230, 230), (60, 60, 80)])
            salto = 1 if rnd.random() < 0.18 else 0
            d.rectangle([xx, yy - salto, xx + 1, yy + 1 - salto], fill=(*colr, 255))
    d.rectangle([0, ty1 - 3, w, ty1], fill=(*Y, 255))  # valla publicitaria lisa

    # cesped a franjas, en perspectiva, con un margen fuera de la cancha
    d.rectangle([0, ty1, w, h], fill=(56, 138, 50, 255))
    franjas = 14
    for i in range(franjas):
        y_a, y_b = -9 + i * (115 / franjas), -9 + (i + 1) * (115 / franjas)
        colr = (62, 150, 56) if i % 2 else (74, 166, 64)
        _poligono_cancha(d, P, [(-60, y_a), (160, y_a), (160, y_b), (-60, y_b)], fill=(*colr, 255))
    _lineas_cancha(d, P, (240, 244, 236, 255), 1)

    # arco con red
    gl, gr = P(50 - 5.4, 0), P(50 + 5.4, 0)
    alto_arco = round((gr[0] - gl[0]) * 0.36)
    fondo = round(alto_arco * 0.45)
    for xx in range(round(gl[0]), round(gr[0]) + 1, 2):
        d.line([(xx, gl[1] - alto_arco - fondo * 0.2), (xx, gl[1] - fondo * 0.1)], fill=(220, 225, 230, 140))
    for yy in range(round(gl[1] - alto_arco), round(gl[1]), 2):
        d.line([(gl[0], yy), (gr[0], yy)], fill=(220, 225, 230, 110))
    for x_ in (gl[0], gr[0]):
        d.rectangle([round(x_) - 1, round(gl[1] - alto_arco), round(x_), round(gl[1])], fill=(250, 250, 250, 255))
    d.rectangle([round(gl[0]) - 1, round(gl[1] - alto_arco) - 1, round(gr[0]), round(gl[1] - alto_arco)], fill=(250, 250, 250, 255))

    pos, ball, trazos, texto, gol, corriendo, alto = _estado(c, t, dur)

    # trazos: puntitos de color (pase amarillo, tiro rojo)
    for tr in trazos:
        col = (255, 80, 60) if tr["tipo"] == "tiro" else Y
        pts = _ruta(tr, 40)
        for i, p in enumerate(pts[:-1]):
            if i % 2 == 0:
                x_, y_ = P(*p)
                d.rectangle([round(x_), round(y_), round(x_) + 1, round(y_) + 1], fill=(*col, 255))

    # jugadores ordenados por profundidad (los lejanos primero)
    cuadro = int(t * 9) % 2 + 1
    orden = sorted(c["jugadores"], key=lambda j: pos[j["id"]][1])
    for j in orden:
        x, y = P(*pos[j["id"]])
        col = loc if j.get("equipo", "local") == "local" else riv
        sp = _sprite(col, cuadro if j["id"] in corriendo else 0, j.get("arquero"))
        d.ellipse([round(x) - 6, round(y) - 2, round(x) + 6, round(y) + 2], fill=(20, 60, 20, 150))
        im.alpha_composite(sp, (round(x - sp.width / 2), round(y - sp.height + 1)))
        if j.get("nombre"):
            tag = _texto_pixel(j["nombre"], fuente_num.font_variant(size=14), INK)
            caja = Image.new("RGBA", (tag.width + 6, tag.height + 2), (*BG, 210))
            caja.alpha_composite(tag, (3, 1))
            if j.get("destacado"):
                ImageDraw.Draw(caja).rectangle([0, 0, caja.width - 1, caja.height - 1], outline=(*Y, 255))
            im.alpha_composite(caja, (round(x - caja.width / 2), round(y - sp.height - caja.height - 2)))
        if j.get("destacado") and int(t * 4) % 2 == 0:
            d.polygon([(x - 3, y - sp.height - 1 - (16 if j.get("nombre") else 0)),
                       (x + 3, y - sp.height - 1 - (16 if j.get("nombre") else 0)),
                       (x, y - sp.height + 3 - (16 if j.get("nombre") else 0))], fill=(*Y, 255))

    # balon con sombra y altura en los tiros
    bx, by = P(*ball)
    lift = alto * 34
    d.ellipse([round(bx) - 3, round(by) - 1, round(bx) + 3, round(by) + 1], fill=(15, 50, 15, 170))
    by -= lift + 3
    d.ellipse([round(bx) - 3, round(by) - 3, round(bx) + 3, round(by) + 3], fill=(250, 250, 250, 255), outline=(15, 15, 20, 255))
    d.point([(round(bx) - 1, round(by) - 1), (round(bx) + 1, round(by) + 1)], fill=(15, 15, 20, 255))

    # marcador tipo consola
    m = c.get("marcador")
    if m:
        gl_l, gl_r = (m.get("despues") if gol is not None else m.get("antes", [0, 0])) or [0, 0]
        f = fuente_num.font_variant(size=17)
        partes = [(m.get("local", "LOC"), INK), (f" {gl_l}-{gl_r} ", Y), (m.get("rival", "RIV"), INK)]
        if m.get("minuto"):
            partes.append(("  " + m["minuto"], (150, 230, 160)))
        x_ = 10
        piezas = [_texto_pixel(tx, f, colr) for tx, colr in partes]
        ancho = sum(p.width for p in piezas) + 12
        d.rectangle([6, 64, 6 + ancho, 64 + piezas[0].height + 6], fill=(*BG, 230), outline=(*Y, 255))
        for p in piezas:
            im.alpha_composite(p, (x_ + 2, 67))
            x_ += p.width

    # ¡GOL! pixelado con confeti
    if gol is not None:
        k = min(1.0, gol / 0.25)
        rnd2 = random.Random(3)
        for i in range(70):
            x0 = rnd2.uniform(0, w)
            vy = rnd2.uniform(30, 80)
            yy = (rnd2.uniform(-h, 0) + gol * vy * 2.2) % h
            colr = rnd2.choice([Y, loc, (255, 255, 255), (255, 90, 60)])
            d.rectangle([round(x0), round(yy), round(x0) + 1, round(yy) + 2], fill=(*colr, 255))
        colr = Y if int(gol * 10) % 2 == 0 else (255, 255, 255)
        g = _texto_pixel("¡GOL!", fuente_titulo.font_variant(size=round(92 + 30 * (1 - k))), colr)
        brinco = abs(math.sin(gol * 7)) * 6 * max(0, 1 - gol / 1.2)
        im.alpha_composite(g, (round(w / 2 - g.width / 2), round(h * 0.60 - g.height / 2 - brinco)))

    im = im.resize((LW, LH), Image.NEAREST)
    # lineas de barrido (CRT) muy suaves
    a = np.array(im)
    a[1::3, :, :3] = (a[1::3, :, :3] * 0.86).astype(np.uint8)
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    _titulo_y_texto(d, c, texto, fuente_titulo, fuente_texto)
    return im


# ---------------------------------------------------------------- estilo TV (transmision)
def _tv(c, t, dur, fuente_titulo, fuente_num, fuente_texto):
    im = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P, esc = _proyector(1.0, arriba=190, abajo=900, ancho_arriba=700, ancho_abajo=1500, fondo=_alcance(c))
    loc = _rgb(c.get("local", {}).get("color", "#1E8A4C"))
    riv = _rgb(c.get("rival", {}).get("color", "#B3202A"))

    # cesped oscuro con franjas y degradado hacia el fondo
    franjas = 12
    for i in range(franjas):
        y_a, y_b = -8 + i * (115 / franjas), -8 + (i + 1) * (115 / franjas)
        base = (22, 70, 42) if i % 2 else (26, 80, 48)
        osc = 0.55 + 0.45 * (i / franjas)
        colr = tuple(int(v * osc) for v in base)
        _poligono_cancha(d, P, [(-60, y_a), (160, y_a), (160, y_b), (-60, y_b)], fill=(*colr, 240))
    # desvanecer los bordes de la cancha
    alfa = Image.new("L", (LW, LH), 0)
    ImageDraw.Draw(alfa).rounded_rectangle([40, 150, LW - 40, LH + 60], radius=60, fill=255)
    alfa = alfa.filter(ImageFilter.GaussianBlur(40))
    im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel("A")), np.array(alfa))))

    # lineas con brillo
    lin = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    _lineas_cancha(ImageDraw.Draw(lin), P, (230, 255, 240, 255), 3)
    gl, gr = P(50 - 5.4, 0), P(50 + 5.4, 0)
    alto_arco = (gr[0] - gl[0]) * 0.34
    ImageDraw.Draw(lin).line([gl, (gl[0], gl[1] - alto_arco), (gr[0], gr[1] - alto_arco), gr], fill=(255, 255, 255, 255), width=4)
    im.alpha_composite(_brillo(lin, 6, 1.4))

    pos, ball, trazos, texto, gol, corriendo, alto = _estado(c, t, dur)

    # pases y tiros: lineas en curva que se dibujan, con brillo y punta
    tl = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tl)
    for tr in trazos:
        col = (255, 76, 60) if tr["tipo"] == "tiro" else Y
        pts = [P(*p) for p in _ruta(tr, 40)]
        if tr["tipo"] == "tiro":  # el tiro sube un poco en pantalla
            pts = [(x, y - 4 * (i / 40) * (1 - i / 40) * 45 * tr["e"]) for i, (x, y) in enumerate(pts)]
        alfa_t = 170 if tr["hecho"] else 255
        if tr["tipo"] == "conduccion":
            for i in range(0, len(pts) - 1, 2):
                dt.line([pts[i], pts[i + 1]], fill=(*col, alfa_t), width=7)
        else:
            dt.line(pts, fill=(*col, alfa_t), width=9 if tr["tipo"] == "tiro" else 7, joint="curve")
        if len(pts) > 3 and math.dist(pts[-4], pts[-1]) > 4:
            _punta(dt, pts[-4], pts[-1], (*col, 255), 30)
    im.alpha_composite(_brillo(tl, 8, 1.6))

    # fichas de jugadores (por profundidad)
    orden = sorted(c["jugadores"], key=lambda j: pos[j["id"]][1])
    for j in orden:
        x, y = P(*pos[j["id"]])
        e = esc(*pos[j["id"]])
        col = loc if j.get("equipo", "local") == "local" else riv
        if j.get("arquero"):
            col = (40, 190, 90)
        rx, ry = 2.3 * e, 0.9 * e
        if j.get("destacado"):
            for k in range(2):
                f = (t * 0.9 + k * 0.5) % 1
                a = int(200 * (1 - f))
                d.ellipse([x - rx * (1 + 1.6 * f), y - ry * (1 + 1.6 * f), x + rx * (1 + 1.6 * f), y + ry * (1 + 1.6 * f)],
                          outline=(*Y, a), width=4)
        d.ellipse([x - rx * 1.25, y - ry * 1.25, x + rx * 1.25, y + ry * 1.25], fill=(0, 0, 0, 90))
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(*col, 110), outline=(*_mezcla(col, (255, 255, 255), 0.35), 255), width=4)
        # ficha de pie: disco con borde blanco
        r = 1.35 * e
        cy = y - r * 1.15
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=(*col, 255), outline=INK, width=3)
        dor = str(j.get("dorsal", j["id"]))
        if dor:
            d.text((x, cy + 1), dor, font=fuente_num.font_variant(size=max(16, int(r * 1.05))), fill=INK, anchor="mm",
                   stroke_width=2, stroke_fill=BG)
        if j.get("nombre"):
            f = fuente_num.font_variant(size=26)
            tw = d.textlength(j["nombre"], font=f) + 26
            yy = cy - r - 40
            d.rounded_rectangle([x - tw / 2, yy, x + tw / 2, yy + 34], radius=17,
                                fill=(*(Y if j.get("destacado") else BG), 235))
            d.text((x, yy + 17), j["nombre"], font=f, fill=BG if j.get("destacado") else INK, anchor="mm")

    # balon con estela y brillo
    bx, by = P(*ball)
    by -= alto * 45
    est = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    de = ImageDraw.Draw(est)
    if trazos and not trazos[-1]["hecho"]:
        ruta = [P(*p) for p in _ruta(trazos[-1], 40)][-9:]
        for i, (x_, y_) in enumerate(ruta):
            r_ = 3 + i * 1.2
            de.ellipse([x_ - r_, y_ - r_ - alto * 45 * (i / 9), x_ + r_, y_ + r_ - alto * 45 * (i / 9)],
                       fill=(255, 255, 255, 25 + i * 18))
    de.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(255, 255, 255, 255))
    im.alpha_composite(_brillo(est, 7, 1.3))
    d.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(255, 255, 255, 255), outline=BG, width=3)

    m = c.get("marcador")
    if m:
        gl_l, gl_r = (m.get("despues") if gol is not None else m.get("antes", [0, 0])) or [0, 0]
        f = fuente_num.font_variant(size=34)
        txt = f"{m.get('local', 'LOC')}  {gl_l} - {gl_r}  {m.get('rival', 'RIV')}"
        tw = d.textlength(txt, font=f) + 40
        d.rounded_rectangle([24, 112, 24 + tw, 166], radius=10, fill=(*BG, 225))
        d.text((44, 139), txt, font=f, fill=INK, anchor="lm")
        if m.get("minuto"):
            f2 = fuente_num.font_variant(size=30)
            mw = d.textlength(m["minuto"], font=f2) + 26
            d.rounded_rectangle([24 + tw + 8, 112, 24 + tw + 8 + mw, 166], radius=10, fill=(*Y, 240))
            d.text((24 + tw + 8 + mw / 2, 139), m["minuto"], font=f2, fill=BG, anchor="mm")

    if gol is not None:
        k = _ease(gol / 0.35)
        destello = Image.new("RGBA", (LW, LH), (*Y, int(110 * max(0, 1 - gol / 0.4))))
        im.alpha_composite(destello)
        f = fuente_titulo.font_variant(size=int(150 + 80 * k))
        d.text((LW / 2, LH * 0.6), "¡GOL!", font=f, fill=Y, anchor="mm", stroke_width=10, stroke_fill=BG)
    _titulo_y_texto(d, c, texto, fuente_titulo, fuente_texto)
    return im


def _brillo(capa, radio, fuerza):
    """Capa + su version desenfocada (glow)."""
    blur = capa.filter(ImageFilter.GaussianBlur(radio))
    a = np.array(blur).astype(np.float32)
    a[..., 3] = np.clip(a[..., 3] * fuerza, 0, 255)
    out = Image.fromarray(a.astype(np.uint8))
    out.alpha_composite(capa)
    return out


def _punta(d, a, b, fill, tam):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = [b, (b[0] - tam * math.cos(ang - .45), b[1] - tam * math.sin(ang - .45)),
           (b[0] - tam * math.cos(ang + .45), b[1] - tam * math.sin(ang + .45))]
    d.polygon(pts, fill=fill)


def _titulo_y_texto(d, c, texto, fuente_titulo, fuente_texto):
    if c.get("titulo"):
        tw = d.textlength(c["titulo"], font=fuente_titulo) + 50
        d.rectangle([(LW - tw) / 2, 22, (LW + tw) / 2, 92], fill=(*Y, 255))
        d.text((LW / 2, 57), c["titulo"], font=fuente_titulo, fill=BG, anchor="mm")
    if texto:
        tw = d.textlength(texto, font=fuente_texto) + 60
        d.rounded_rectangle([(LW - tw) / 2, LH - 140, (LW + tw) / 2, LH - 52], radius=16, fill=(*BG, 215))
        d.text((LW / 2, LH - 96), texto, font=fuente_texto, fill=INK, anchor="mm")


ESTILOS = {"retro": _retro, "tv": _tv}


def capa(c, t, dur, fuente_titulo, fuente_num, fuente_texto):
    estilo = c.get("estilo") if c.get("estilo") in ESTILOS else c.get("tipo")
    return ESTILOS[estilo](c, t, dur, fuente_titulo, fuente_num, fuente_texto)
