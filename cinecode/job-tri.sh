#!/usr/bin/env bash
# Guineo · Kitu Díaz a un gol de la historia (2026-11-12): narration Andrea + Luis
set -u
O=cinecode/out-tri; mkdir -p $O
timeout 420 uv run python cinecode/edge_take.py cinecode/takes-kitu.json $O/vo || echo "edge timeout/fail"
ls -R $O | head -30
