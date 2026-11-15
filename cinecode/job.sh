#!/usr/bin/env bash
# Job 25b (2026-11-15): prueba de voz clonada de Mui con Chatterbox Multilingual (MIT) en CPU
set -u
O=cinecode/out; mkdir -p $O
ffmpeg -loglevel error -y -i cinecode/voz/jordy.m4a -t 15 -ac 1 -ar 24000 -af "highpass=f=80,afftdn=nf=-25" /tmp/ref.wav
cp /tmp/ref.wav $O/ref.wav
uv venv -q --python 3.11 /tmp/cb && uv pip install -q --python /tmp/cb/bin/python chatterbox-tts "setuptools<81" 2>&1 | tail -3
/tmp/cb/bin/python -c "import perth; print('perth', perth.PerthImplicitWatermarker)"
uv pip list --python /tmp/cb/bin/python 2>/dev/null | grep -iE "chatterbox|torch " 
/tmp/cb/bin/python - <<'PY'
import time, torch, torchaudio as ta
t0=time.time()
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
print("carga", round(time.time()-t0,1), "s", flush=True)
frases = ["Emelec no gana un título nacional desde 2017.",
          "Hincha eléctrico, ¿sociedad anónima sí o no? Comenta y síguenos en Guineo Comunicaciones."]
for i, f in enumerate(frases):
    t1=time.time()
    wav = m.generate(f, language_id="es", audio_prompt_path="/tmp/ref.wav", exaggeration=0.5, cfg_weight=0.5)
    ta.save(f"cinecode/out/clon_{i}.wav", wav, m.sr)
    print("frase", i, round(time.time()-t1,1), "s para", round(wav.shape[-1]/m.sr,1), "s de audio", flush=True)
PY
ls -la $O
