#!/usr/bin/env bash
# Guineo · La Tri v2 (2026-11-12): second voice (Luis) for the data lines
set -u
O=cinecode/out-tri; mkdir -p $O
timeout 300 uv run python cinecode/edge_take.py cinecode/takes-tri-luis.json $O/vo-luis || echo "edge timeout/fail"
ls -R $O | head -20
