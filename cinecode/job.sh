#!/usr/bin/env bash
# Job 6: descargar los 3 dibujos exportados de Canva (estilo 1) y recortarlos a 1080x1920.
set -u
mkdir -p cinecode/out/dibujos
curl -sSL -o cinecode/out/dibujos/p1.png 'https://export-download.canva.com/eTcn4/DAHaeceTcn4/-1/0/0001-1929188228996673706.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQYCGKMUH4R7NKVBA%2F20261109%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261109T044307Z&X-Amz-Expires=81182&X-Amz-Signature=33b3be39356ba6f1aa6afdb212aaf362ee24a12c03e230e24fc9d67ebcf2d82e&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner&response-expires=Tue%2C%2010%20Nov%202026%2003%3A16%3A09%20GMT'
curl -sSL -o cinecode/out/dibujos/p2.png 'https://export-download.canva.com/eTcn4/DAHaeceTcn4/-1/0/0002-1929188228996673706.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQYCGKMUH4R7NKVBA%2F20261110%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261110T013905Z&X-Amz-Expires=6037&X-Amz-Signature=d6ff2ab9c86a151c07809ca52e50d8af5cf9c2ebb0a1f28620d7c9294d588a58&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner&response-expires=Tue%2C%2010%20Nov%202026%2003%3A19%3A42%20GMT'
curl -sSL -o cinecode/out/dibujos/p3.png 'https://export-download.canva.com/eTcn4/DAHaeceTcn4/-1/0/0003-1929188228996673706.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQYCGKMUH4R7NKVBA%2F20261109%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20261109T092002Z&X-Amz-Expires=63668&X-Amz-Signature=34503c61b65e21d2ec08b7cfcf5c3f212f2de5d54abcfabffe73398b53f19ae2&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner&response-expires=Tue%2C%2010%20Nov%202026%2003%3A01%3A10%20GMT'
uv run python - <<'PY'
from PIL import Image
for i, n in enumerate(["entrada", "reloj", "gol"], 1):
    p = f"cinecode/out/dibujos/p{i}.png"
    im = Image.open(p).convert("RGB"); w, h = im.size; print(p, im.size)
    cw = round(h * 9 / 16); x0 = (w - cw) // 2
    im.crop((x0, 0, x0 + cw, h)).resize((1080, 1920), Image.LANCZOS).save(f"cinecode/out/dibujos/{n}.png")
PY
rm -f cinecode/out/dibujos/p?.png
ls -la cinecode/out/dibujos
