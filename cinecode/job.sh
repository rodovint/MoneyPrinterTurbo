#!/usr/bin/env bash
# Job 21 (2026-11-15): voz es-EC-AndreaNeural para el lote del 15/11 mañana (pedido de Mui, solo por hoy)
set -u
O=cinecode/out; mkdir -p $O
uv run python - <<'PY'
import asyncio, json, subprocess, os, time, edge_tts
d = json.load(open("lotes/borradores/2026-11-15-manana-aprobados.json"))
os.makedirs("/tmp/v", exist_ok=True)
async def tts(t, f):
    await edge_tts.Communicate(t, "es-EC-AndreaNeural", rate="+8%").save(f)
subprocess.check_call(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t","0.7","/tmp/v/sil.wav"])
for r in d:
    n = r["audio"].split("/")[-1]; parts = []
    for k, e in enumerate(r["escenas"]):
        mp3, wav = f"/tmp/v/{n}_{k}.mp3", f"/tmp/v/{n}_{k}.wav"
        for i in range(5):
            try:
                asyncio.run(tts(e["texto"], mp3)); break
            except Exception as ex:
                print("retry", n, k, ex); time.sleep(5 * (i + 1))
        subprocess.check_call(["ffmpeg","-y","-loglevel","error","-i",mp3,"-ar","44100","-ac","1",wav])
        parts += [wav, "/tmp/v/sil.wav"]
    lst = f"/tmp/v/{n}.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts[:-1]))
    subprocess.check_call(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c:a","aac","-b:a","128k",f"cinecode/out/{n}.m4a"])
    print("ok", n)
PY
ls -la $O
