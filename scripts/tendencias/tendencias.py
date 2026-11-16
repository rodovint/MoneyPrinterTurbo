"""Tendencias Guineo Comunicaciones (Google Trends con trendspyg).

Modos:
  rss      -> lista de tendencias de EC, US, ES, AR y MX (rápido, sin navegador).
  explore  -> rss + curva de 7 días, provincias y búsquedas en alza en Ecuador
              para 3-4 temas deportivos (o los que se pasen separados por coma).

Guarda en lotes/tendencias/auto/ (rss-ultimo.json, explore-ultimo.json y copias
con fecha). Borra copias con más de 3 días.
"""
import datetime as dt
import json
import os
import re
import sys
import time
from zoneinfo import ZoneInfo

import trendspyg as tg

TZ = ZoneInfo("America/Guayaquil")
GEOS = ["EC", "US", "ES", "AR", "MX"]
OUT = "lotes/tendencias/auto"
DEPORTE = re.compile(
    r"\b(vs\.?|v\.|fútbol|futbol|liga|ligapro|gol|goles|selecci[oó]n|copa|partido|mundial|"
    r"eliminatorias|nations|champions|libertadores|sudamericana|premier|laliga|serie a|"
    r"bundesliga|ufc|nba|nfl|mlb|f1|f[oó]rmula|tenis|atp|wta|boxeo|pelea|barcelona sc|emelec|"
    r"liga de quito|independiente del valle|orense|real madrid|messi|cristiano|ronaldo|"
    r"marat[oó]n|ol[ií]mpic\w*|jugador|t[eé]cnico|fichaje|estadio|resultado|en vivo|alineaci\w*|"
    r"football|soccer|match|game|cup|league)\b",
    re.I,
)


def ahora():
    return dt.datetime.now(TZ)


def guardar(nombre, datos):
    os.makedirs(OUT, exist_ok=True)
    sello = ahora().strftime("%Y-%m-%d-%H%M")
    for ruta in (f"{OUT}/{nombre}-ultimo.json", f"{OUT}/{nombre}-{sello}.json"):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
    print("guardado", nombre, sello)


def podar(dias=3):
    limite = (ahora() - dt.timedelta(days=dias)).strftime("%Y-%m-%d")
    for f in os.listdir(OUT):
        m = re.search(r"(\d{4}-\d{2}-\d{2})-\d{4}\.json$", f)
        if m and m.group(1) < limite:
            os.remove(os.path.join(OUT, f))


def es_deporte(t):
    texto = t["keyword"] + " " + " ".join(n.get("headline", "") for n in t.get("news", []))
    return bool(DEPORTE.search(texto))


def modo_rss():
    datos = {"fecha": ahora().isoformat(timespec="minutes"), "fuente": "Google Trends RSS (trendspyg)", "paises": {}}
    for geo in GEOS:
        try:
            env = tg.download_google_trends_rss(geo=geo, normalize=True, include_images=False, max_articles_per_trend=2)
            datos["paises"][geo] = [
                {
                    "tema": t["keyword"],
                    "volumen": t["volume_text"],
                    "volumen_min": t["volume_min"],
                    "desde": t["started_at"],
                    "deporte_probable": es_deporte(t),
                    "titulares": [f'{n.get("headline", "")} ({n.get("source", "")})' for n in t.get("news", [])],
                }
                for t in env["trends"]
            ]
        except Exception as e:  # una fuente caída no frena las demás
            datos["paises"][geo] = {"error": f"{type(e).__name__}: {e}"[:300]}
        time.sleep(2)
    guardar("rss", datos)
    return datos


def impulso(serie):
    """Promedio de las últimas 24 h vs las 24 h anteriores (serie horaria de 7 días)."""
    vals = [p["value"] for p in serie if not p.get("is_partial")]
    if len(vals) < 48:
        return None, None
    ult, ant = sum(vals[-24:]) / 24, sum(vals[-48:-24]) / 24
    if ant == 0:
        return None, "explosiva" if ult > 0 else "sin datos"
    pct = round((ult - ant) / ant * 100)
    estado = "explosiva" if pct >= 100 else "en crecimiento" if pct >= 20 else "estable" if pct > -20 else "en declive"
    return pct, estado


def modo_explore(temas):
    rss = modo_rss()
    if not temas:
        ec = rss["paises"].get("EC")
        ec = ec if isinstance(ec, list) else []
        temas = [t["tema"] for t in sorted(ec, key=lambda t: -t["volumen_min"]) if t["deporte_probable"]][:4]
    datos = {"fecha": ahora().isoformat(timespec="minutes"), "geo": "EC", "periodo": "últimos 7 días (por hora)", "temas": []}
    for i, tema in enumerate(temas):
        if i:
            time.sleep(25)  # Google bloquea si se piden muchas seguidas
        try:
            env = tg.download_google_trends_explore(
                tema, geo="EC", timeframe="now 7-d", engine="auto",
                include_related=True, include_geo=True, max_retries=3, retry_wait=10,
            )
            serie = env.get("interest_over_time", [])
            pct, estado = impulso(serie)
            pico = max(serie, key=lambda p: p["value"]) if serie else None
            regiones = sorted(env.get("interest_by_region", []), key=lambda r: -r["value"])
            datos["temas"].append({
                "tema": tema,
                "impulso_24h_pct": pct,
                "estado": estado,
                "pico": pico,
                "ultimo_valor": serie[-1]["value"] if serie else None,
                "provincias_top": [f'{r["geo_name"]} {r["value"]}' for r in regiones[:8]],
                "el_oro": next((r["value"] for r in regiones if "Oro" in r["geo_name"]), None),
                "busquedas_en_alza": [f'{q["query"]} ({q["formatted_value"]})' for q in env.get("related_queries", {}).get("rising", [])[:8]],
                "serie": [[p["date"][5:13], p["value"]] for p in serie[-48:]],
            })
        except tg.RateLimitError as e:
            datos["temas"].append({"tema": tema, "error": f"RateLimitError: {e}"[:300]})
            break  # parar: insistir alarga el bloqueo
        except Exception as e:
            datos["temas"].append({"tema": tema, "error": f"{type(e).__name__}: {e}"[:300]})
    guardar("explore", datos)


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "rss"
    temas = [t.strip() for t in (sys.argv[2] if len(sys.argv) > 2 else "").split(",") if t.strip()]
    modo_explore(temas) if modo == "explore" else modo_rss()
    podar()
