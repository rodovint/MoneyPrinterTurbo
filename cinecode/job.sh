#!/usr/bin/env bash
# Job 23 (2026-11-15): buscar música coral épica CC y sonidos (hinchada, whoosh) para el generador de reels
set -u
O=cinecode/out; mkdir -p $O; cd $O
T=../../cinecode/tools/asset_search.py
for q in "epic choir" "epic cinematic choir orchestral" "epic heroic orchestral"; do
  python3 $T search --q "$q" --type music --licence cc0,pd,cc-by --out "m-${q// /_}" 2>&1 | tail -25
done
for q in "stadium crowd cheer" "football crowd goal" "whoosh"; do
  python3 $T search --q "$q" --type sound --licence cc0,pd,cc-by --out "s-${q// /_}" 2>&1 | tail -15
done
