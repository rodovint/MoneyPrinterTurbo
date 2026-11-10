"""Render Edge TTS takes (the MoneyPrinter free voice) with word timings.
Usage: edge_take.py <job.json> <outdir>
job: {"takes": [{"id": "...", "voice": "es-EC-LuisNeural", "rate": "+12%", "text": "..."}]}"""
import asyncio, json, os, sys, time
import edge_tts

async def one(t, out):
    com = edge_tts.Communicate(t["text"], t["voice"], rate=t.get("rate", "+0%"), pitch=t.get("pitch", "+0Hz"), boundary="WordBoundary")
    words = []
    with open(os.path.join(out, t["id"] + ".mp3"), "wb") as fh:
        async for ch in com.stream():
            if ch["type"] == "audio":
                fh.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    json.dump(words, open(os.path.join(out, t["id"] + ".words.json"), "w"), ensure_ascii=False)

def main():
    job = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for t in job.get("takes", []):
        for i in range(4):
            try:
                asyncio.run(one(t, out)); print("ok", t["id"]); break
            except Exception as e:
                print("retry", t["id"], type(e).__name__, e); time.sleep(5 * (i + 1))

if __name__ == "__main__":
    main()
