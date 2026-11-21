"""Versiones del logo SRF a partir del escudo de Mui (21/11)."""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ORIG = sys.argv[1]
FD = "/home/claude/mpt2/scripts/guineo/fonts/"
NEG = lambda n: ImageFont.truetype(FD + "InterDisplay-Black.otf", n)
NEGI = lambda n: ImageFont.truetype(FD + "InterDisplay-BlackItalic.otf", n)
S = 2048  # se dibuja al doble y se reduce (bordes suaves)
C = S // 2
ORO, ORO2, CREMA = (222, 178, 52), (150, 112, 22), (250, 242, 220)
VERDE, VERDE2, SOMBRA = (22, 92, 48), (10, 52, 28), (6, 30, 16)
GUINEO = "/home/claude/mpt2/scripts/guineo/logo-guineo.png"


def balon(r):
    im = Image.open(ORIG).convert("RGB")
    cx, cy, rr = 570, 635, 121
    b = im.crop((cx - rr, cy - rr, cx + rr, cy + rr)).resize((2 * r, 2 * r), Image.LANCZOS)
    m = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse([2, 2, 2 * r - 2, 2 * r - 2], fill=255)
    b.putalpha(m.filter(ImageFilter.GaussianBlur(2)))
    return b


def estrella(d, x, y, r, col):
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.28
        pts.append((x + rad * math.cos(a), y + rad * math.sin(a)))
    d.polygon(pts, fill=col)


def estela(d, bx, by, r):
    """Estela dorada del balón hacia abajo-izquierda, en franjas que se afinan."""
    ang = math.radians(158)  # dirección de la cola
    for k, (off, largo, ancho, col) in enumerate([(-0.55, 2.9, 0.20, ORO), (-0.15, 3.5, 0.26, ORO), (0.3, 3.0, 0.18, CREMA), (0.65, 2.2, 0.12, ORO)]):
        px, py = -math.sin(ang), math.cos(ang)
        x0, y0 = bx + px * off * r, by + py * off * r
        x1, y1 = x0 + math.cos(ang) * largo * r, y0 + math.sin(ang) * largo * r
        w = ancho * r
        d.polygon([(x0 + px * w, y0 + py * w), (x0 - px * w, y0 - py * w), (x1, y1)], fill=col)


def texto_contorno(d, xy, txt, f, fill=CREMA, borde=ORO, gb=14, sombra=True, anchor="mm"):
    x, y = xy
    if sombra:
        d.text((x + 10, y + 14), txt, font=f, fill=SOMBRA, anchor=anchor, stroke_width=gb + 8, stroke_fill=SOMBRA)
    d.text((x, y), txt, font=f, fill=borde, anchor=anchor, stroke_width=gb, stroke_fill=borde)
    d.text((x, y), txt, font=f, fill=fill, anchor=anchor, stroke_width=4, stroke_fill=ORO2)


def texto_arco(lienzo, txt, f, radio, centro_ang, col, abajo=True):
    """Texto curvado sobre el aro (abajo se lee de izquierda a derecha)."""
    d0 = ImageDraw.Draw(lienzo)
    anchos = [d0.textlength(ch, font=f) for ch in txt]
    total = sum(anchos) + 6 * len(txt)
    ang_total = total / radio
    a = centro_ang + ang_total / 2 if abajo else centro_ang - ang_total / 2
    for ch, w in zip(txt, anchos):
        paso = (w + 6) / radio
        am = a - paso / 2 if abajo else a + paso / 2
        x, y = C + radio * math.cos(am), C + radio * math.sin(am)
        t = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((100, 100), ch, font=f, fill=col, anchor="mm")
        rot = -math.degrees(am) + 90 if abajo else -math.degrees(am) - 90
        t = t.rotate(rot, resample=Image.BICUBIC)
        lienzo.alpha_composite(t, (int(x - 100), int(y - 100)))
        a = a - paso if abajo else a + paso


def disco(firma=True):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    R = 960
    d.ellipse([C - R, C - R, C + R, C + R], fill=ORO)
    d.ellipse([C - R + 26, C - R + 26, C + R - 26, C + R - 26], fill=ORO2)
    d.ellipse([C - R + 38, C - R + 38, C + R - 38, C + R - 38], fill=VERDE2)
    # verde con degradado radial
    g = Image.new("L", (S, S), 0)
    gd = ImageDraw.Draw(g)
    for i in range(40):
        rr = (R - 140) * (1 - i / 40)
        gd.ellipse([C - rr, C - rr * 1.0 - 120, C + rr, C + rr - 120], fill=int(255 * i / 40))
    g = g.filter(ImageFilter.GaussianBlur(60))
    verde = Image.new("RGBA", (S, S), VERDE + (255,))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([C - R + 140, C - R + 140, C + R - 140, C + R - 140], fill=255)
    oscuro = Image.new("RGBA", (S, S), VERDE2 + (255,))
    capa = Image.composite(verde, oscuro, g)
    im.paste(capa, (0, 0), m)
    d = ImageDraw.Draw(im)
    rr = R - 140
    d.ellipse([C - rr, C - rr, C + rr, C + rr], outline=ORO, width=12)
    # líneas de cancha tenues
    lin = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(lin).arc([C - 1100, C + 160, C + 1100, C + 900], 200, 340, fill=(60, 140, 80, 255), width=8)
    m2 = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m2).ellipse([C - rr + 8, C - rr + 8, C + rr - 8, C + rr - 8], fill=255)
    im.paste(lin, (0, 0), Image.composite(lin.getchannel("A"), Image.new("L", (S, S), 0), m2))
    if firma:
        texto_arco(im, "POR GUINEO COMUNICACIONES", NEG(62), R - 72, math.pi / 2, CREMA, abajo=True)
        for a in (math.radians(140), math.radians(40)):
            estrella(ImageDraw.Draw(im), C + (R - 72) * math.cos(a), C + (R - 72) * math.sin(a), 22, CREMA)
        texto_arco(im, "★  EST. 2026  ★", NEG(54), R - 72, -math.pi / 2, CREMA, abajo=False)
    return im


def completo():
    im = disco()
    d = ImageDraw.Draw(im)
    bx, by, br = C + 120, C + 400, 250
    estela(d, bx, by, br)
    for x, y, r in [(C - 420, C + 250, 46), (C - 280, C + 160, 30), (C - 120, C + 640, 34), (C + 470, C + 230, 26)]:
        estrella(d, x, y, r, CREMA)
    texto_contorno(d, (C, C - 520), "SÚPER", NEGI(250), gb=14)
    texto_contorno(d, (C, C - 250), "RESUMEN", NEGI(330), gb=16)
    texto_contorno(d, (C, C + 30), "FUTBOLERO", NEGI(270), fill=ORO, borde=CREMA, gb=14)
    b = balon(br)
    sh = Image.new("RGBA", b.size, (0, 0, 0, 0))
    sh.putalpha(b.getchannel("A").point(lambda v: v * 0.6))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (bx - br + 16, by - br + 24))
    im.alpha_composite(b, (bx - br, by - br))
    return im.resize((1024, 1024), Image.LANCZOS)


def avatar():
    """Para foto de perfil y esquina del video: SRF grande + balón."""
    im = disco(firma=False)
    d = ImageDraw.Draw(im)
    bx, by, br = C + 330, C + 380, 260
    estela(d, bx, by, br)
    estrella(d, C - 430, C + 470, 56, CREMA)
    texto_contorno(d, (C - 30, C - 110), "SRF", NEGI(720), gb=24)
    b = balon(br)
    im.alpha_composite(b, (bx - br, by - br))
    return im.resize((1024, 1024), Image.LANCZOS)


def marca_agua():
    """Monocromo blanco para poner encima del video."""
    a = avatar()
    alfa = a.getchannel("A")
    gris = a.convert("L").filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v > 150 else 0)
    blanco = Image.new("RGBA", a.size, (255, 255, 255, 0))
    blanco.putalpha(Image.composite(gris, Image.new("L", a.size, 0), alfa).point(lambda v: int(v * 0.85)))
    aro = Image.new("L", a.size, 0)
    ImageDraw.Draw(aro).ellipse([20, 20, 1004, 1004], outline=210, width=14)
    blanco.putalpha(Image.composite(Image.new("L", a.size, 255), blanco.getchannel("A"), aro).point(lambda v: min(v, 220)))
    return blanco


if __name__ == "__main__":
    completo().save("srf-logo.png")
    avatar().save("srf-avatar.png")
    marca_agua().save("srf-marca-agua.png")
    # hoja de comparación
    o = Image.open(ORIG).convert("RGBA").resize((512, 512))
    hoja = Image.new("RGB", (2140, 760), (14, 14, 16))
    d = ImageDraw.Draw(hoja)
    f = ImageFont.truetype(FD + "InterDisplay-Black.otf", 30)
    for i, (n, img) in enumerate([("Original", o), ("Mejorado", Image.open("srf-logo.png").resize((512, 512))),
                                   ("Avatar / esquina", Image.open("srf-avatar.png").resize((512, 512))),
                                   ("Marca de agua", Image.open("srf-marca-agua.png").resize((512, 512)))]):
        x = 20 + i * 530
        if i == 3:
            fondo = Image.open(ORIG).convert("RGB").resize((512, 512)).filter(ImageFilter.GaussianBlur(20))
            hoja.paste(Image.eval(fondo, lambda v: v // 3), (x, 60))
        hoja.paste(img, (x, 60), img)
        d.text((x + 256, 30), n, font=f, fill=(240, 240, 240), anchor="mm")
        # a tamaño de foto de perfil (98 px, recorte circular)
        ch = img.convert("RGBA").resize((98, 98), Image.LANCZOS)
        m = Image.new("L", (98, 98), 0)
        ImageDraw.Draw(m).ellipse([0, 0, 97, 97], fill=255)
        hoja.paste(ch, (x + 207, 600), m)
        d.text((x + 256, 720), "así se ve en 98 px", font=ImageFont.truetype(FD + "InterDisplay-Black.otf", 20), fill=(150, 150, 150), anchor="mm")
    hoja.save("comparacion.jpg", quality=90)
