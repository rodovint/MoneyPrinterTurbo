#!/usr/bin/env bash
# Job 26 (2026-11-15): pruebas de pronunciación — clon de Mui con referencias naturales y 2 ajustes, y Andrea a 2 velocidades
set -u
O=cinecode/out; mkdir -p $O
uv venv -q --python 3.11 /tmp/cb && uv pip install -q --python /tmp/cb/bin/python chatterbox-tts "setuptools<81" edge-tts 2>&1 | tail -2
/tmp/cb/bin/python - <<'PY' 2>&1 | grep -v Sampling
import asyncio, subprocess, time, edge_tts, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
O = "cinecode/out"
mui = ["Partidazo hoy en Europa: España recibe a Inglaterra.", "¿Quién gana hoy en Madrid?", "Comenta y síguenos en Guineo Comunicaciones."]
datos = ["Inglaterra, de Thomas Tuchel, suma cuatro triunfos y una sola derrota.", "Es a las tres menos cuarto de la tarde, hora de Ecuador, en el Metropolitano de Madrid."]
async def tts(t, f, r):
    await edge_tts.Communicate(t, "es-EC-AndreaNeural", rate=r).save(f)
for r in ["+0%", "+10%"]:
    for i, t in enumerate(datos):
        asyncio.run(tts(t, f"/tmp/and{i}.mp3", r))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "/tmp/and0.mp3", "-i", "/tmp/and1.mp3", "-filter_complex", "[0][1]concat=n=2:v=0:a=1", f"{O}/andrea_{r.strip('+%')}.wav"])
    print("andrea", r, flush=True)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
ajustes = {"A": dict(exaggeration=0.5, cfg_weight=0.5, temperature=0.8), "B": dict(exaggeration=0.35, cfg_weight=0.3, temperature=0.7)}
for ref in ["dinho", "idv"]:
    for k, aj in ajustes.items():
        partes = []
        for i, t in enumerate(mui):
            wav = m.generate(t, language_id="es", audio_prompt_path=f"cinecode/voz/pruebas/ref-{ref}.wav", **aj)
            f = f"/tmp/{ref}{k}{i}.wav"; ta.save(f, wav, m.sr); partes.append(f)
        lst = "".join(f"[{j}]" for j in range(len(partes)))
        cmd = ["ffmpeg", "-loglevel", "error", "-y"] + sum([["-i", p] for p in partes], []) + ["-filter_complex", f"{lst}concat=n={len(partes)}:v=0:a=1", f"{O}/mui_{ref}_{k}.wav"]
        subprocess.run(cmd)
        print("mui", ref, k, flush=True)
PY
ls -la $O
