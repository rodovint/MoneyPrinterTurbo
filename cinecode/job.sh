#!/usr/bin/env bash
# Job 49 (2026-11-25): Rattín — profundidad (2.5D) de las 8 ilustraciones + 4 clips imagen→video (LTX, token HF de Mui)
set -u
mkdir -p cinecode/out/rattin-depth cinecode/out/rattin-i2v
pip install -q torch --index-url https://download.pytorch.org/whl/cpu >/dev/null 2>&1
pip install -q transformers pillow gradio_client >/dev/null 2>&1
python3 - <<'PY'
import glob, os
from PIL import Image
from transformers import pipeline
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
for f in sorted(glob.glob("lotes/img/rattin/*.png")):
    im = Image.open(f).convert("RGB")
    pipe(im)["depth"].resize(im.size).save("cinecode/out/rattin-depth/" + os.path.basename(f)); print("depth ok", f)
PY
python3 - <<'PY'
import os, shutil, time
from gradio_client import Client, handle_file
E = "claymation stop-motion animation, plasticine figures, miniature 1966 stadium set, sunny afternoon"
S = {
 "alfombra": "the tall plasticine captain sitting on the red carpet stubbornly crosses his arms tighter and turns his head away, the two policemen lean toward him angrily waving their hands",
 "discusion": "the plasticine referee in black and the tall captain argue face to face, both waving their hands wildly, players around shift and react",
 "expulsion": "the plasticine referee in black points firmly to the side again and again, the tall captain opens his arms in protest and shakes his head, players watch",
 "policias": "two plasticine policemen walk forward escorting the tall captain by the arms, he walks slowly with his chin up, the crowd behind moves",
}
tok = os.environ.get("HF_TOKEN") or None
print("token HF:", "sí" if tok else "NO")
try: c = Client("Lightricks/ltx-video-distilled", hf_token=tok)
except TypeError: c = Client("Lightricks/ltx-video-distilled", token=tok)
for k, p in S.items():
    for intento in range(4):
        try:
            r = c.predict(prompt=E + ": " + p, negative_prompt="blurry, distorted, deformed faces, extra limbs, text, watermark, morphing, rain", input_image_filepath=handle_file(f"lotes/img/rattin/{k}.png"),
                          input_video_filepath=None, height_ui=832, width_ui=480, mode="image-to-video", duration_ui=5, ui_frames_to_use=9,
                          seed_ui=42, randomize_seed=False, ui_guidance_scale=1, improve_texture_flag=True, api_name="/image_to_video")
            v = r[0]["video"] if isinstance(r[0], dict) else r[0]
            shutil.copy(v, f"cinecode/out/rattin-i2v/{k}.mp4"); print("OK", k); break
        except Exception as e:
            print("ERR", k, intento, str(e)[:300]); time.sleep(60)
PY
