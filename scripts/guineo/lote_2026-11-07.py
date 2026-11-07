"""Lote del 7 de noviembre de 2026. Crea lotes/actual.json y lotes/GUIONES.md.

Cada escena es una frase del guion. Al grabar, haz una pausa corta entre frases:
el generador usa esas pausas para sincronizar la voz con los graficos.
"""
import json, os

CIERRE = {"tipo": "cierre", "texto": "COMENTA Y SÍGUENOS"}
SIGUE = "Comenta y síguenos en Guineo Deportes."

def t(texto, sobre):
    return {"tipo": "titular", "texto": texto, "sobre": sobre}

def cifra(valor, texto):
    return {"tipo": "cifra", "valor": valor, "texto": texto}

def duo(a, at, b, bt, pie):
    return {"tipo": "duo", "a": a, "a_texto": at, "b": b, "b_texto": bt, "pie": pie}

def partido(e1, c1, e2, c2, hora, pie):
    return {"tipo": "partido", "equipos": [{"nombre": e1, "color": c1}, {"nombre": e2, "color": c2}], "hora": hora, "pie": pie}

def marcador(e1, c1, g1, e2, c2, g2, pie):
    return {"tipo": "marcador", "equipos": [{"nombre": e1, "color": c1, "goles": g1}, {"nombre": e2, "color": c2, "goles": g2}], "pie": pie}

def prota(rol, nombre, dato, color):
    return {"tipo": "protagonista", "rol": rol, "nombre": nombre, "dato": dato, "color": color}

ORE, CUE, EME, LIB, GYE, LEO = "#1E8A4C", "#B3202A", "#0B4EA2", "#C9971A", "#2F7FC1", "#6B7280"
BSC, LDU, MAC, IDV, DEL, UCA = "#B8860B", "#1F2A44", "#2F9BD6", "#1B1B1B", "#0E7C86", "#2B6CB0"
MAN, MUS, TEC, ECU, CRC, BOL, AUC = "#1D5FA8", "#8B1E2D", "#C8102E", "#0B3D91", "#C8102E", "#1E8A4C", "#C9971A"

REELS = [
 dict(titulo="Cuenca vs. Orense (HOY 11:30)", etiqueta="POR NO DESCENDER", color=ORE, aviso="Publicar ANTES de las 11:30 de hoy.", escenas=[
  ("Orense va por otro punto de oro en Cuenca.", t("PUNTO DE ORO EN CUENCA", "ORENSE"), "Estadio Alejandro Serrano Aguilar.jpg"),
  ("Hoy, a las once y media, el cuadro bananero visita a Deportivo Cuenca en el Alejandro Serrano Aguilar.", partido("DEPORTIVO CUENCA", CUE, "ORENSE", ORE, "HOY 11:30", "ESTADIO ALEJANDRO SERRANO AGUILAR"), None),
  ("Cuenca lidera el hexagonal con 44 puntos y Orense es tercero con 39.", duo("44", "DEPORTIVO CUENCA", "39", "ORENSE", "HEXAGONAL POR NO DESCENDER"), None),
  ("Atrás aprieta Técnico Universitario con 37, y los dos últimos bajan a la Serie B.", cifra("37", "TÉCNICO U. · LOS DOS ÚLTIMOS BAJAN A SERIE B"), None),
  ("En su primer duelo del hexagonal empataron cero a cero.", t("0 A 0 EN EL PRIMER DUELO", "EL ANTECEDENTE"), None),
  ("¿Suma Orense en Cuenca?", t("¿SUMA ORENSE EN CUENCA?", "TU OPINIÓN"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="Libertad vs. Emelec (HOY 14:00)", etiqueta="CUADRANGULAR", color=EME, aviso="Publicar antes de las 14:00.", escenas=[
  ("Emelec cierra hoy un año para olvidar.", t("UN AÑO PARA OLVIDAR", "EMELEC"), None),
  ("A las dos de la tarde visita a Libertad en el Reina del Cisne de Loja, sin nada en juego.", partido("LIBERTAD", LIB, "EMELEC", EME, "HOY 14:00", "ESTADIO REINA DEL CISNE, LOJA"), "Estadio Reina del Cisne 02.jpg"),
  ("Libertad ya tiene su cupo a la Sudamericana y Emelec es último del cuadrangular con 42 puntos.", duo("51", "LIBERTAD", "42", "EMELEC", "CUADRANGULAR"), None),
  ("Según la prensa local, en el plantel vencen 15 contratos y se viene una limpieza para 2027.", cifra("15", "CONTRATOS POR VENCER, SEGÚN LA PRENSA"), None),
  ("Además, los jugadores reclaman hasta tres meses de sueldos pendientes.", cifra("3", "MESES DE SUELDOS PENDIENTES, SEGÚN LA PRENSA"), None),
  ("Y el futuro del técnico Ezequiel Medrán todavía no está definido.", prota("TÉCNICO DE EMELEC", "EZEQUIEL MEDRÁN", "FUTURO SIN DEFINIR", EME), None),
  ("Hincha eléctrico, ¿por dónde empieza la reconstrucción?", t("¿POR DÓNDE EMPIEZA LA RECONSTRUCCIÓN?", "HINCHA ELÉCTRICO"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="Leones vs. Guayaquil City (HOY 16:30)", etiqueta="CUADRANGULAR", color=GYE, aviso="Publicar antes de las 16:30.", escenas=[
  ("Guayaquil City se juega hoy la Copa Sudamericana.", t("CITY VA POR LA SUDAMERICANA", "GUAYAQUIL CITY"), None),
  ("A las cuatro y media visita a Leones en el Olímpico de Ibarra.", partido("LEONES", LEO, "GUAYAQUIL CITY", GYE, "HOY 16:30", "ESTADIO OLÍMPICO DE IBARRA"), None),
  ("El segundo lugar del cuadrangular da un cupo, y al City le alcanza con empatar.", t("LE ALCANZA CON EMPATAR", "2.º LUGAR = SUDAMERICANA"), None),
  ("El City tiene 47 puntos y Leones 46.", duo("47", "GUAYAQUIL CITY", "46", "LEONES", "LA PELEA POR EL SEGUNDO LUGAR"), None),
  ("Pero hay una deuda: el City nunca le ha ganado a Leones en Ibarra.", cifra("0", "VICTORIAS DEL CITY EN IBARRA"), None),
  ("¿Rompe la racha el City?", t("¿ROMPE LA RACHA EL CITY?", "TU OPINIÓN"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="Barcelona vs. Liga de Quito (domingo)", etiqueta="HEXAGONAL FINAL", color=BSC, escenas=[
  ("Barcelona y Liga de Quito se ven las caras mañana en el Monumental.", t("BARCELONA VS. LIGA DE QUITO", "ESTADIO MONUMENTAL"), "Estadio BSC.jpg"),
  ("El partido es a las cuatro y media de la tarde, por la sexta fecha del hexagonal final.", partido("BARCELONA", BSC, "LIGA DE QUITO", LDU, "DOM 16:30", "SEXTA FECHA DEL HEXAGONAL FINAL"), None),
  ("Desde 2019 se han visto diez veces en Guayaquil: Liga ganó tres, Barcelona dos y hubo cinco empates.", cifra("10", "PARTIDOS EN GUAYAQUIL DESDE 2019: LIGA 3, BSC 2, EMPATES 5"), None),
  ("Y en el último cruce, en octubre, Liga ganó dos a uno.", marcador("LIGA DE QUITO", LDU, 2, "BARCELONA", BSC, 1, "11 DE OCTUBRE"), None),
  ("Para llenar el estadio, la general norte cuesta seis dólares y la tribuna diez.", duo("$6", "GENERAL NORTE", "$10", "TRIBUNA", "PRECIOS DE LAS ENTRADAS"), None),
  ("Además, mujeres y niños menores de 12 años entran gratis a tribuna si van con alguien que compró su boleto.", cifra("GRATIS", "MUJERES Y NIÑOS MENORES DE 12 EN TRIBUNA, CON ACOMPAÑANTE"), None),
  ("Torero, ¿vas al Monumental?", t("¿VAS AL MONUMENTAL?", "TORERO"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="Trobbiani promete furia", etiqueta="BARCELONA SC", color=BSC, escenas=[
  ("Pablo Trobbiani promete un Barcelona con furia.", prota("TÉCNICO DE BARCELONA", "PABLO TROBBIANI", "PROMETE FURIA", BSC), None),
  ("Tras el tres a cero ante Macará, admitió que les dolió la derrota y que en el segundo tiempo no estuvieron a la altura.", marcador("MACARÁ", MAC, 3, "BARCELONA", BSC, 0, "LA ÚLTIMA DERROTA"), None),
  ("Y lanzó: saldremos el domingo con furia, tragando veneno toda esta semana.", {"tipo": "cita", "texto": "“TRAGANDO VENENO”", "autor": "PABLO TROBBIANI, DT DE BARCELONA"}, None),
  ("Además, dijo que espera que Marcelo Gallardo considere a Jerly Wila y Johan García para la Selección.", t("WILA Y GARCÍA A LA TRI", "EL PEDIDO DE TROBBIANI"), None),
  ("¿Los ves en la Selección?", t("¿LOS VES EN LA TRI?", "TU OPINIÓN"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="Tres equipos por un boleto a la Libertadores", etiqueta="HEXAGONAL FINAL", color=AUC, escenas=[
  ("Tres equipos y un solo boleto a la Libertadores.", t("TRES EQUIPOS, UN BOLETO", "COPA LIBERTADORES 2027"), None),
  ("El tercer lugar del hexagonal final da cupo a la segunda fase previa de la Libertadores 2027.", cifra("3ER", "LUGAR = SEGUNDA FASE PREVIA DE LA LIBERTADORES"), None),
  ("Hoy ese lugar es de Aucas, con 54 puntos.", cifra("54", "PUNTOS DE AUCAS, HOY TERCERO"), None),
  ("Liga de Quito suma 53 y Barcelona 48, a seis del tercer lugar.", duo("53", "LIGA DE QUITO", "48", "BARCELONA", "QUEDAN CINCO FECHAS"), None),
  ("Este domingo, Aucas recibe a Independiente del Valle y Barcelona a Liga.", t("DOMINGO DECISIVO", "AUCAS–IDV · BSC–LIGA"), None),
  ("¿Quién se queda con el boleto?", t("¿QUIÉN SE QUEDA CON EL BOLETO?", "TU OPINIÓN"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="IDV elimina a Delfín de la Copa Ecuador", etiqueta="COPA ECUADOR", color=DEL, escenas=[
  ("Se acabó el sueño copero de Delfín.", t("SE ACABÓ EL SUEÑO COPERO", "DELFÍN"), "Estadio jocay.jpg"),
  ("Independiente del Valle le ganó dos a cero en la vuelta y cerró la semifinal con un global de cinco a cero.", marcador("IND. DEL VALLE", IDV, 2, "DELFÍN", DEL, 0, "GLOBAL 5-0"), None),
  ("Los goles fueron de Djorkaeff Reasco y Junior Sornoza.", t("REASCO Y SORNOZA", "LOS GOLES"), None),
  ("Los rayados jugarán la final en diciembre ante Universidad Católica, en el Alejandro Serrano Aguilar de Cuenca.", partido("IND. DEL VALLE", IDV, "U. CATÓLICA", UCA, "FINAL", "DICIEMBRE · ESTADIO ALEJANDRO SERRANO AGUILAR"), "Estadio Alejandro Serrano Aguilar.jpg"),
  ("Delfín ya piensa en el lunes: visita a Mushuc Runa en la pelea por no descender.", t("AHORA, A SALVARSE", "LUNES ANTE MUSHUC RUNA"), None),
  ("Hincha cetáceo, ¿te dolió la eliminación?", t("¿TE DOLIÓ LA ELIMINACIÓN?", "HINCHA CETÁCEO"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="Manta gana en el descuento", etiqueta="POR NO DESCENDER", color=MAN, escenas=[
  ("Manta se niega a bajar.", t("MANTA SE NIEGA A BAJAR", "POR NO DESCENDER"), "Estadio jocay.jpg"),
  ("El martes le ganó tres a dos a Mushuc Runa en Echaleche, con un penal de Joaquín Vergés en el noveno minuto de descuento.", marcador("MANTA", MAN, 3, "MUSHUC RUNA", MUS, 2, "PENAL DE VERGÉS AL 90+9"), None),
  ("Con ese triunfo llegó a 30 puntos, pero sigue último y a ocho de la salvación.", cifra("8", "PUNTOS DE LA SALVACIÓN"), None),
  ("Quedan cinco fechas y quince puntos en juego.", cifra("15", "PUNTOS EN JUEGO"), None),
  ("El lunes, a las tres y media, visita a Técnico Universitario.", partido("TÉCNICO U.", TEC, "MANTA", MAN, "LUN 15:30", "PRÓXIMO PARTIDO"), None),
  ("¿Se da el milagro en Manta?", t("¿SE DA EL MILAGRO?", "TU OPINIÓN"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="La Tri anuncia su lista el domingo", etiqueta="SELECCIÓN", color=ECU, escenas=[
  ("La Tri ya tiene fecha para su lista.", t("LA TRI DA SU LISTA", "DOMINGO 8 DE NOVIEMBRE"), None),
  ("Marcelo Gallardo anunciará este domingo a los convocados para los amistosos de noviembre.", prota("TÉCNICO DE ECUADOR", "MARCELO GALLARDO", "ANUNCIA LA LISTA", ECU), None),
  ("Ecuador recibe a Costa Rica el viernes 13 en el Atahualpa de Quito.", partido("ECUADOR", ECU, "COSTA RICA", CRC, "VIE 13", "ESTADIO OLÍMPICO ATAHUALPA, QUITO"), None),
  ("Y a Bolivia el martes 17 en el Monumental de Guayaquil.", partido("ECUADOR", ECU, "BOLIVIA", BOL, "MAR 17", "ESTADIO MONUMENTAL, GUAYAQUIL"), "Estadio BSC.jpg"),
  ("¿Qué jugador de la costa merece estar?", t("¿QUIÉN DE LA COSTA MERECE ESTAR?", "TU OPINIÓN"), None),
  (SIGUE, CIERRE, None)]),
 dict(titulo="Lunes del descenso", etiqueta="POR NO DESCENDER", color=TEC, escenas=[
  ("El lunes se mueve la pelea por no descender.", t("LUNES DE DESCENSO", "HEXAGONAL"), None),
  ("A la una de la tarde, Delfín visita a Mushuc Runa.", partido("MUSHUC RUNA", MUS, "DELFÍN", DEL, "LUN 13:00", "HEXAGONAL POR NO DESCENDER"), None),
  ("Mushuc tiene 40 puntos y Delfín 38.", duo("40", "MUSHUC RUNA", "38", "DELFÍN", "LA PELEA POR SALVARSE"), None),
  ("Después, a las tres y media, Técnico Universitario recibe a Manta.", partido("TÉCNICO U.", TEC, "MANTA", MAN, "LUN 15:30", "HEXAGONAL POR NO DESCENDER"), None),
  ("Técnico suma 37 y está en zona de descenso; Manta tiene 30 y es último.", duo("37", "TÉCNICO U.", "30", "MANTA", "LOS DOS ÚLTIMOS BAJAN A SERIE B"), None),
  ("¿Quiénes se salvan?", t("¿QUIÉNES SE SALVAN?", "TU OPINIÓN"), None),
  (SIGUE, CIERRE, None)]),
]

FUENTES = [
 "El Universo, horarios de la sexta jornada: https://www.eluniverso.com/deportes/campeonato-ecuatoriano/liga-pro-2026-calendario-fechas-y-horarios-de-la-sexta-jornada-de-la-fase-final-nota/",
 "El Mercurio, Cuenca–Orense en el Serrano Aguilar: https://elmercurio.com.ec/deportes/2026/11/03/ligapro-partidos-horarios/",
 "El Universo, Orense–Cuenca 0-0 en el hexagonal: https://www.eluniverso.com/deportes/campeonato-ecuatoriano/orense-y-deportivo-cuenca-empatan-sin-goles-en-el-hexagonal-del-descenso-de-la-liga-ecuabet-2026-nota/",
 "El Diario, Libertad–Emelec y contratos: https://www.eldiario.ec/deportes/emelec-ante-libertad-el-partido-del-adios-que-marcara-la-purga-de-cara-a-la-temporada-2027-06112026/",
 "Extra, Emelec: 15 contratos y sueldos: https://www.extra.ec/noticia/deportes/emelec-cuatro-anos-torneos-internacionales-15-contratos-resolver-167223_amp.html",
 "El Universo, Guayaquil City en Ibarra: https://www.eluniverso.com/deportes/campeonato-ecuatoriano/un-triunfo-para-hacer-historia-guayaquil-city-busca-su-primera-victoria-ante-leones-fc-en-ibarra-y-el-cupo-a-la-copa-sudamericana-nota/",
 "El Universo, puntos del cuadrangular: https://www.eluniverso.com/deportes/campeonato-ecuatoriano/libertad-fc-empata-en-su-visita-a-guayaquil-city-y-logra-boleto-para-la-copa-sudamericana-2027-en-la-fecha-5-del-cuadrangular-de-liga-ecuabet-nota/",
 "El Universo, entradas Barcelona–Liga: https://www.eluniverso.com/deportes/campeonato-ecuatoriano/liga-pro-barcelona-sc-anuncia-los-precios-de-las-entradas-para-recibir-a-liga-de-quito-nota/",
 "El Comercio, Liga en Guayaquil desde 2019: https://www.elcomercio.com/deportes/futbol/liga-quito-barcelona-guayaquil-estadio-monumental/",
 "Anecdotarios, último cruce (11 de octubre, 2-1): https://anecdotarios.com/2026/11/06/barcelona-vs-liga-de-quito-previa-horario-y-como-llegan-para-la-fecha-6-del-torneo-ecuatoriano/",
 "El Universo, Trobbiani: https://www.eluniverso.com/deportes/campeonato-ecuatoriano/pablo-trobbiani-promete-furia-de-barcelona-sc-ante-liga-de-quito-vamos-a-salir-a-ganar-nota/",
 "Extra, Trobbiani pide a Wila y García: https://www.extra.ec/noticia/deportes/trobbiani-pide-jugadores-barcelona-tri-calienta-duelo-liga-quito-167119.html",
 "Metro Ecuador, pelea por la Libertadores: https://www.metroecuador.com.ec/deportes/2026/11/05/tres-grandes-y-un-solo-boleto-aucas-liga-y-barcelona-quieren-ir-a-la-libertadores-2027/",
 "Primicias, IDV 2-0 Delfín: https://www.primicias.ec/deportes/futbol/envivo-independiente-valle-delfinsc-semifinal-copa-ecuador-resultado-ver-partido-tv-136449/",
 "El Diario, final en Cuenca: https://www.eldiario.ec/deportes/independiente-del-valle-deja-fuera-a-delfin-y-va-por-el-titulo-de-la-copa-ecuador-05112026/",
 "El Universo, Manta 3-2 Mushuc Runa: https://www.eluniverso.com/deportes/campeonato-ecuatoriano/manta-fc-vence-a-mushuc-runa-en-echaleche-y-suena-con-salvarse-del-descenso-en-la-liga-ecuabet-nota/",
 "Studio Fútbol, penal al 90+9: https://studiofutbol.com.ec/2026/11/03/video-manta-lo-gano-en-la-ultima-vencio-3-2-a-mushuc-runa-con-un-penal-en-el-909/",
 "El Universo, tabla del hexagonal (Delfín 38, Cuenca 44): https://www.eluniverso.com/deportes/campeonato-ecuatoriano/delfin-sc-derrota-al-deportivo-cuenca-y-suena-con-la-salvacion-en-el-hexagonal-por-no-descender-de-liga-ecuabet-nota/",
 "Machala Móvil, Orense 39 y Técnico 37: https://machalamovil.com/orense-rescata-un-empate-ante-tecnico-universitario-y-sigue-fuera-de-la-zona-de-descenso/",
 "Vistazo, lista de la Tri y amistosos: https://www.vistazo.com/deportes/2026-11-06-ecuador-anunciara-lista-convocados-amistosos-internacionales-BD11307699",
]


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    lote, md = [], ["# Guineo Deportes · guiones del 7 de noviembre de 2026", "",
                    "**Cómo grabar:** un audio por reel. Lee las frases en orden y haz una pausa corta (como medio segundo) entre una y otra; así se sincroniza solo.",
                    "**Nombres de archivo:** `01`, `02`... hasta `10` (sirve .m4a, .mp3, .ogg, .opus o .wav).", ""]
    for i, r in enumerate(REELS, 1):
        esc = []
        for texto, graf, foto in r["escenas"]:
            e = {"texto": texto, "grafico": graf}
            if foto:
                e["foto_commons"] = foto
            esc.append(e)
        lote.append({"titulo": r["titulo"], "etiqueta": r["etiqueta"], "color": r["color"], "audio": f"audio/{i:02d}", "escenas": esc})
        md += [f"## {i:02d} · {r['titulo']}"] + ([f"> ⏰ {r['aviso']}"] if r.get("aviso") else []) + [""]
        md += [f"{n}. {texto}" for n, (texto, _, _) in enumerate(r["escenas"], 1)] + [""]
    md += ["## Fuentes", ""] + [f"- {f}" for f in FUENTES] + [""]
    with open(os.path.join(root, "lotes/actual.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(lote, ensure_ascii=False, indent=2) + "\n")
    with open(os.path.join(root, "lotes/GUIONES.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    print(len(lote), "reels")


if __name__ == "__main__":
    main()
