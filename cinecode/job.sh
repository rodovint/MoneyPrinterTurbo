#!/usr/bin/env bash
# Job 47 (2026-11-24): clips imagen→video (LTX-Video distilled, Space gratis de HF) de las 8 escenas de Berna
set -u
O=cinecode/out/berna-i2v; mkdir -p $O
pip install -q gradio_client >/dev/null 2>&1
python3 - <<'PY'
import shutil, time, traceback
from gradio_client import Client, handle_file
E = "claymation stop-motion animation, plasticine figures, miniature stadium set, rain falling"
S = {
 "estadio": "the camera slowly glides over a miniature stadium at night in heavy rain, plasticine fans in the stands shift and wave, floodlights flicker",
 "equipos": "two lines of plasticine football players stand in the mud in the rain, they shift their weight, turn their heads, adjust their shirts, rain falling",
 "barrida": "a plasticine player in yellow slides into a tackle against a player in red, mud splashes up in slow motion, the red player falls",
 "pelea": "plasticine football players shove and wrestle in the mud, arms swinging, mud splashing, policemen run in, the referee in black waves his arms",
 "arbitro": "the plasticine referee in black blows his whistle and waves his arms, policemen run toward the brawl behind him, mud splashing",
 "marcador": "rain runs down an old wooden scoreboard, number plates swing slightly in the wind, floodlight glow pulses",
 "vestuario": "a single bare light bulb swings and flickers in a dark plasticine locker room, hanging red shirts sway slightly",
 "final": "the plasticine referee in black walks slowly away across the empty muddy pitch in the rain, floodlights in the background",
}
c = Client("Lightricks/ltx-video-distilled")
for k, p in S.items():
    for intento in range(4):
        try:
            r = c.predict(prompt=E + ": " + p, negative_prompt="blurry, distorted, deformed faces, text, watermark, morphing", input_image_filepath=handle_file(f"lotes/img/berna/{k}.png"),
                          input_video_filepath=None, height_ui=832, width_ui=480, mode="image-to-video", duration_ui=5, ui_frames_to_use=9,
                          seed_ui=42, randomize_seed=False, ui_guidance_scale=1, improve_texture_flag=True, api_name="/image_to_video")
            v = r[0]["video"] if isinstance(r[0], dict) else r[0]
            shutil.copy(v, f"cinecode/out/berna-i2v/{k}.mp4"); print("OK", k); break
        except Exception as e:
            print("ERR", k, intento, str(e)[:300]); time.sleep(60)
PY
