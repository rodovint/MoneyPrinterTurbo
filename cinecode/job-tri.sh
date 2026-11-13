#!/usr/bin/env bash
# Guineo · Atleti compra el 50% del Atlético FC (2026-11-13): narration Andrea + Luis
set -u
O=cinecode/out-tri; mkdir -p $O
timeout 420 uv run python cinecode/edge_take.py cinecode/takes-atleti.json $O/vo || echo "edge timeout/fail"
ls -R $O | head -30
