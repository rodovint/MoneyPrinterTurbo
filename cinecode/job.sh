#!/usr/bin/env bash
# Job 46 (2026-11-24): prueba de imagen→video gratis con Spaces de Hugging Face (LTX-Video / Wan) para Guineo Animación
set -u
O=cinecode/out/i2v; mkdir -p $O
pip install -q gradio_client >/dev/null 2>&1
python3 - <<'PY'
import shutil, traceback
from gradio_client import Client, handle_file
img = "lotes/img/berna/pelea.png"
prompt = "claymation stop-motion: plasticine football players shove and wrestle in the mud, arms swinging, mud splashing, rain falling, policemen run in, the referee in black waves his arms, handheld camera, stop-motion animation"
for space in ["Lightricks/ltx-video-distilled", "Lightricks/LTX-Video-Playground", "multimodalart/wan2-1-fast", "Wan-AI/Wan2.2-5B"]:
    try:
        c = Client(space)
        print("=== API", space); print(c.view_api(return_format="str", print_info=False)[:3000])
    except Exception as e:
        print("ERR client", space, e); continue
    try:
        if "ltx" in space.lower():
            r = c.predict(prompt=prompt, negative_prompt="blurry, distorted, text, watermark", input_image_filepath=handle_file(img),
                          input_video_filepath=None, height_ui=704, width_ui=416, mode="image-to-video", duration_ui=4, ui_frames_to_use=9,
                          seed_ui=42, randomize_seed=False, ui_guidance_scale=1, improve_texture_flag=True, api_name="/image_to_video")
        else:
            r = c.predict(handle_file(img), prompt, api_name="/generate_video")
        print("RESULT", space, r)
        v = r[0] if isinstance(r, (list, tuple)) else r
        if isinstance(v, dict): v = v.get("video") or v.get("path")
        shutil.copy(v, f"cinecode/out/i2v/{space.split('/')[1]}.mp4"); print("OK", space)
        break
    except Exception as e:
        print("ERR predict", space); traceback.print_exc()
PY
