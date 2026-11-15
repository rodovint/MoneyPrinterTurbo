"""Genera con Chatterbox Multilingual (MIT, CPU) la voz clonada de Mui para las escenas con "voz": "mui".

Uso: python voz_clon.py lotes/actual.json
Deja cada frase en lotes/audio/clon/<clave>.wav (la clave sale del texto y de la referencia),
asi que una frase ya generada no se vuelve a generar. generar.py las lee de ahi.
Referencia: scripts/guineo/voz/mui-ref.wav (unos 10-15 s de Mui, limpia y sin pausas largas).
"""
import hashlib, json, os, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, "voz", "mui-ref.wav")


def clave(texto, ref=REF):
    h = hashlib.sha1()
    h.update(texto.strip().encode("utf-8"))
    h.update(open(ref, "rb").read() if os.path.exists(ref) else b"")
    return h.hexdigest()[:16]


def ruta(lote, texto):
    return os.path.join(os.path.dirname(os.path.abspath(lote)), "audio", "clon", clave(texto) + ".wav")


def main(lote):
    reels = json.load(open(lote, encoding="utf-8"))
    pendientes = []
    for r in reels:
        for e in r["escenas"]:
            if str(e.get("voz", "")).lower() == "mui":
                t = e.get("dicho", e["texto"])
                if not os.path.exists(ruta(lote, t)):
                    pendientes.append(t)
    pendientes = list(dict.fromkeys(pendientes))
    print(f"Frases con voz de Mui por generar: {len(pendientes)}", flush=True)
    if not pendientes:
        return
    import torchaudio as ta
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    t0 = time.time()
    m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    print(f"Modelo cargado en {time.time() - t0:.0f} s", flush=True)
    for t in pendientes:
        t1 = time.time()
        wav = m.generate(t, language_id="es", audio_prompt_path=REF, exaggeration=0.55, cfg_weight=0.5, temperature=0.7)
        dest = ruta(lote, t)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        ta.save(dest, wav, m.sr)
        print(f"ok ({time.time() - t1:.0f} s): {t}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
