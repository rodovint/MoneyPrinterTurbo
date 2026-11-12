#!/usr/bin/env python3
"""
buscar_clips.py — busca y descarga clips específicos por escena para MoneyPrinterTurbo.

Uso:
  python buscar_clips.py escenas.json                 # cualquier licencia (revisar antes de publicar)
  python buscar_clips.py escenas.json --solo-cc       # solo videos Creative Commons (más seguro para monetizar)
  python buscar_clips.py escenas.json --candidatos 15 --salida clips

Requiere: yt-dlp y ffmpeg instalados (pip install -U yt-dlp).
Salida:  carpeta con escena_01.mp4, escena_02.mp4... + creditos.txt para la descripción.
Luego, en MoneyPrinterTurbo: Fuente de video = "Local" y sube los clips en orden.
"""
import argparse, json, subprocess, sys, shutil
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def buscar(query, n, solo_cc, min_seg):
    q = f"{query}, creativecommons" if solo_cc else query
    r = run(["yt-dlp", "--flat-playlist", "-j", f"ytsearch{n}:{q}"])
    if r.returncode != 0 or not r.stdout.strip():
        print("   busqueda fallo:", r.stderr.strip()[-300:])
    ids = [json.loads(l)["id"] for l in r.stdout.splitlines() if l.strip()]
    for vid in ids:
        info = run(["yt-dlp", "-j", "--skip-download", f"https://www.youtube.com/watch?v={vid}"])
        if info.returncode != 0:
            print("   info fallo:", vid, info.stderr.strip()[-300:])
            continue
        d = json.loads(info.stdout)
        dur = d.get("duration") or 0
        lic = d.get("license") or ""
        if dur < min_seg or dur > 3 * 3600:
            continue
        if solo_cc and "creative commons" not in lic.lower():
            print("   no CC:", vid, lic or "estandar")
            continue
        return d
    return None

def bajar_tramo(d, inicio, seg, tmp):
    url = d["webpage_url"]
    out = tmp / f"{d['id']}.%(ext)s"
    r = run(["yt-dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
             "--download-sections", f"*{inicio}-{inicio + seg}", "--force-keyframes-at-cuts",
             "-o", str(out), url])
    archivos = list(tmp.glob(f"{d['id']}.*"))
    return archivos[0] if r.returncode == 0 and archivos else None

def normalizar(src, dst, vertical):
    w, h = (1080, 1920) if vertical else (1920, 1080)
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,setsar=1"
    run(["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-an", "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(dst)])
    return dst.exists()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escenas")
    ap.add_argument("--salida", default="clips")
    ap.add_argument("--solo-cc", action="store_true")
    ap.add_argument("--candidatos", type=int, default=10)
    ap.add_argument("--posicion", type=float, default=0.25,
                    help="desde qué parte del video cortar (0.25 = al 25%%, salta intros)")
    a = ap.parse_args()

    for prog in ("yt-dlp", "ffmpeg"):
        if not shutil.which(prog):
            sys.exit(f"Falta {prog}. Instálalo y vuelve a correr.")

    cfg = json.loads(Path(a.escenas).read_text(encoding="utf-8"))
    vertical = cfg.get("formato", "vertical") == "vertical"
    salida = Path(a.salida); salida.mkdir(exist_ok=True)
    tmp = salida / "_tmp"; tmp.mkdir(exist_ok=True)
    creditos, faltan = [], []

    for e in cfg["escenas"]:
        n, seg = e["id"], e.get("segundos", 6)
        dst = salida / f"escena_{n:02d}.mp4"
        if dst.exists():
            print(f"[{n}] ya existe, salto"); continue
        hecho = False
        for q in e["busquedas"]:
            print(f"[{n}] buscando: {q}")
            d = buscar(q, a.candidatos, a.solo_cc, seg + 10)
            if not d:
                continue
            inicio = max(3, int((d["duration"] - seg) * a.posicion))
            src = bajar_tramo(d, inicio, seg, tmp)
            if src and normalizar(src, dst, vertical):
                creditos.append(f"Escena {n}: \"{d.get('title')}\" — {d.get('uploader')} — "
                                f"{d['webpage_url']} — licencia: {d.get('license') or 'estándar de YouTube'}")
                print(f"[{n}] OK -> {dst.name} ({d.get('title')})")
                hecho = True; break
        if not hecho:
            faltan.append(n); print(f"[{n}] sin clip; prueba otra búsqueda o usa material de Pexels")

    shutil.rmtree(tmp, ignore_errors=True)
    (salida / "creditos.txt").write_text("\n".join(creditos), encoding="utf-8")
    print(f"\nListo: {len(cfg['escenas']) - len(faltan)} clips en {salida}/. Créditos en creditos.txt")
    if faltan:
        print("Escenas sin clip:", faltan)

if __name__ == "__main__":
    main()
