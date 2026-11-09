"""Download football background clips (Pixabay, filtered by tags) and licensed Commons photos
with the Guineo generator's own functions. Usage: fetch_bg.py <outdir>"""
import importlib.util, json, os, shutil, sys
spec = importlib.util.spec_from_file_location("g", "scripts/guineo/generar.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
out = sys.argv[1]
os.makedirs(out + "/clips", exist_ok=True); os.makedirs(out + "/fotos", exist_ok=True)
clips = g.fondos(os.environ.get("PIXABAY_API_KEY", "").strip(), out + "/clips", cuantos=10)
fotos = {}
for t in ["Estadio Alberto J. Armando field view.jpg", "20170807 La Bombonera - Estadio Alberto Jacinto Armando.jpg",
          "La Bombonera - 2013 (12118717106).jpg", "La Bombonera football stadium.jpg"]:
    ruta, cred = g.foto_commons(t, out + "/fotos")
    if ruta:
        fotos[os.path.basename(ruta)] = {"titulo": t, "credito": cred}
json.dump({"clips": [os.path.basename(c) for c in clips], "fotos": fotos}, open(out + "/bg.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(fotos, ensure_ascii=False))
