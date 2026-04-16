#!/usr/bin/env bash
# Setup and verify ACE-Step installation for claude-music
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config.json"
if [ -f "$CONFIG" ] && command -v python3 &>/dev/null; then
    ACE_STEP_DIR=$(python3 -c "import json; print(json.load(open('$CONFIG'))['ace_step_dir'])" 2>/dev/null)
fi
ACE_STEP_DIR="${ACE_STEP_DIR:-}"
OUTPUT_DIR="$HOME/Music/claude-music-output"

echo "=== claude-music Setup ==="
echo ""

if [ ! -d "$ACE_STEP_DIR" ]; then
    echo "ERROR: ACE-Step 1.5 not found at $ACE_STEP_DIR"
    exit 1
fi
echo "[OK] ACE-Step 1.5 found at $ACE_STEP_DIR"

if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "[OK] uv $(uv --version 2>&1 | head -1)"

command -v ffmpeg &>/dev/null && echo "[OK] ffmpeg found" || echo "WARNING: ffmpeg not found (sudo apt install ffmpeg)"
command -v jq &>/dev/null && echo "[OK] jq found" || echo "WARNING: jq not found (sudo apt install jq)"

if command -v nvidia-smi &>/dev/null; then
    GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1)
    VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
    echo "[OK] GPU: $GPU (${VRAM}MB VRAM)"
else
    echo "WARNING: nvidia-smi not found"
fi

echo ""
echo "Checking model checkpoints..."
MISSING=0
for model in "acestep-v15-turbo" "vae" "Qwen3-Embedding-0.6B"; do
    [ -d "$ACE_STEP_DIR/checkpoints/$model" ] && echo "  [OK] $model" || { echo "  [MISSING] $model"; MISSING=$((MISSING + 1)); }
done
for model in "acestep-5Hz-lm-0.6B" "acestep-5Hz-lm-1.7B" "acestep-v15-base" "acestep-v15-xl-turbo"; do
    [ -d "$ACE_STEP_DIR/checkpoints/$model" ] && echo "  [OK] $model (optional)" || echo "  [--] $model (optional)"
done

[ "$MISSING" -gt 0 ] && echo "" && echo "Missing required checkpoints. Run: cd $ACE_STEP_DIR && uv run acestep-download"

mkdir -p "$OUTPUT_DIR"
echo ""
echo "[OK] Output: $OUTPUT_DIR"
echo ""
echo "=== Setup Complete ==="
