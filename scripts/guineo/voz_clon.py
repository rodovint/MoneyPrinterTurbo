"""Genera con Chatterbox Multilingual (MIT, CPU) la voz clonada de Mui para las escenas con "voz": "mui".

Uso: python voz_clon.py lotes/actual.json
Deja cada frase en lotes/audio/clon/<clave>.wav (la clave sale del texto y de la referencia),
asi que una frase ya generada no se vuelve a generar. generar.py las lee de ahi.
Referencia: scripts/guineo/voz/mui-ref.wav (13 s del audio de Ronaldinho con pausas naturales; elegida por Mui el 15/11).
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


def recortar_cola(wav, sr, texto):
    """Quita el "eeehh" que Chatterbox a veces agrega al final: corta donde termina la voz
    (ultimo tramo a menos de 10 dB del nivel tipico) y nunca deja mas de ~0.075 s por letra."""
    import numpy as np
    import torch
    a = wav.squeeze().cpu().numpy().astype(np.float32)
    v = max(1, int(0.02 * sr))
    rms = np.array([np.sqrt(np.mean(a[i:i + v] ** 2)) + 1e-9 for i in range(0, len(a), v)])
    db = 20 * np.log10(rms)
    voz = np.where(db > np.percentile(db, 90) - 10)[0]
    fin = (voz[-1] + 1) * v if len(voz) else len(a)
    fin = min(fin + int(0.12 * sr), int((0.075 * len(texto) + 0.5) * sr), len(a))
    a = a[:fin].copy()
    f = min(len(a), int(0.08 * sr))
    a[-f:] *= np.linspace(1, 0, f)
    print(f"cola recortada: {len(wav.squeeze()) / sr:.2f} s -> {len(a) / sr:.2f} s", flush=True)
    return torch.from_numpy(a).unsqueeze(0)


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
        wav = recortar_cola(m.generate(t, language_id="es", audio_prompt_path=REF, exaggeration=0.5, cfg_weight=0.5, temperature=0.8), m.sr, t)
        dest = ruta(lote, t)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        ta.save(dest, wav, m.sr)
        print(f"ok ({time.time() - t1:.0f} s): {t}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
