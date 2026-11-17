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
    (ultimo tramo a menos de 10 dB del nivel tipico) y nunca deja mas de ~0.095 s por letra."""
    import numpy as np
    import torch
    a = wav.squeeze().cpu().numpy().astype(np.float32)
    v = max(1, int(0.02 * sr))
    rms = np.array([np.sqrt(np.mean(a[i:i + v] ** 2)) + 1e-9 for i in range(0, len(a), v)])
    db = 20 * np.log10(rms)
    voz = np.where(db > np.percentile(db, 90) - 10)[0]
    fin = (voz[-1] + 1) * v if len(voz) else len(a)
    # 17/11: el tope anterior (0.075 s/letra) cortaba frases largas ("la vuelta al mu...").
    fin = min(fin + int(0.15 * sr), int((0.095 * len(texto) + 0.8) * sr), len(a))
    a = a[:fin].copy()
    f = min(len(a), int(0.08 * sr))
    a[-f:] *= np.linspace(1, 0, f)
    # Mui pidio su voz mas fuerte (16/11): nivel parejo a -16 dBFS RMS (Andrea queda mas baja).
    rms_voz = np.sqrt(np.mean(a[a != 0] ** 2)) if np.any(a) else 0
    if rms_voz > 0:
        a = np.clip(a * (0.16 / rms_voz), -0.99, 0.99)
    print(f"cola recortada: {len(wav.squeeze()) / sr:.2f} s -> {len(a) / sr:.2f} s", flush=True)
    return torch.from_numpy(a).unsqueeze(0)


def puntaje(wav, sr, texto):
    """Menor es mejor: duracion fuera de lo normal, picos (gritos/ruidos) y tono que sube al final
    en frases que no son pregunta."""
    import numpy as np
    a = wav.squeeze().cpu().numpy().astype(np.float32)
    dur = len(a) / sr
    esperado = 0.062 * len(texto) + 0.3
    p_dur = abs(dur - esperado) / esperado
    v = int(0.02 * sr)
    rms = np.array([np.sqrt(np.mean(a[i:i + v] ** 2)) for i in range(0, len(a) - v, v)]) + 1e-9
    voz = rms[rms > np.percentile(rms, 30)]
    p_pico = max(0.0, 20 * np.log10(rms.max() / np.median(voz)) - 9) / 3 if len(voz) else 0
    f0 = []
    n = int(0.04 * sr)
    lo, hi = int(sr / 320), int(sr / 70)
    for i in range(0, len(a) - n, n // 2):
        x = a[i:i + n] - a[i:i + n].mean()
        if np.sqrt(np.mean(x ** 2)) < np.median(voz) * 0.5:
            continue
        c = np.correlate(x, x, "full")[n - 1:]
        if c[0] <= 0:
            continue
        j = lo + int(np.argmax(c[lo:hi]))
        if c[j] / c[0] > 0.45:
            f0.append(sr / j)
    p_tono = 0.0
    sube = 1.0
    if len(f0) >= 8:
        sube = float(np.median(f0[-3:]) / np.median(f0))
        if not texto.strip().endswith("?"):
            p_tono = max(0.0, sube - 1.08) * 8
    return p_dur + p_pico + p_tono, f"dur {dur:.2f}/{esperado:.2f} s, pico {p_pico:.2f}, final x{sube:.2f}"


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
    import torch
    for t in pendientes:
        t1 = time.time()
        # Mui (16/11): sin tono arriba al cerrar las afirmaciones y sin ruidos raros.
        # Las exclamaciones se leen como afirmacion; se hacen 3 tomas y queda la mejor.
        habla = t.replace("¡", "").replace("!", ".").replace("..", ".").strip()
        tomas = []
        for k in range(3):
            torch.manual_seed(1000 + k)
            w = recortar_cola(m.generate(habla, language_id="es", audio_prompt_path=REF,
                                         exaggeration=0.4, cfg_weight=0.5, temperature=0.6), m.sr, habla)
            p, info = puntaje(w, m.sr, habla)
            print(f"  toma {k + 1}: {info} -> {p:.2f}", flush=True)
            tomas.append((p, k, w))
        p, k, wav = min(tomas, key=lambda x: x[0])
        dest = ruta(lote, t)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        ta.save(dest, wav, m.sr)
        print(f"ok ({time.time() - t1:.0f} s, toma {k + 1}): {t}", flush=True)

if __name__ == "__main__":
    main(sys.argv[1])
