"""Backup narration with Piper (offline neural TTS). Usage: piper_take.py <job.json> <outdir> <voice.onnx>"""
import json, os, subprocess, sys, wave
job, out, model = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
for t in json.load(open(job, encoding="utf-8"))["takes"]:
    dest = os.path.join(out, t["id"] + ".wav")
    subprocess.run(["piper", "--model", model, "--output_file", dest, "--length_scale", "0.92"], input=t["text"].encode(), check=False)
    if os.path.exists(dest):
        with wave.open(dest) as w:
            d = w.getnframes() / w.getframerate()
        json.dump([{"w": t["text"], "t": 0.05, "d": round(d - 0.1, 3)}], open(os.path.join(out, t["id"] + ".words.json"), "w"))
        print("piper ok", t["id"], round(d, 2), flush=True)
