#!/usr/bin/env bash
# Wrapper for ACE-Step music engine
# Usage: bash music_engine.sh <subcommand> [args]
# Handles: path setup, VRAM pre-check, environment variables, uv invocation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/music_engine.py"
CONFIG="$SCRIPT_DIR/../config.json"

# Read ACE-Step path from config.json
if [ -f "$CONFIG" ] && command -v python3 &>/dev/null; then
    ACE_STEP_DIR=$(python3 -c "import json; print(json.load(open('$CONFIG'))['ace_step_dir'])" 2>/dev/null)
fi
ACE_STEP_DIR="${ACE_STEP_DIR:-}"

# Pre-flight: check ACE-Step exists
if [ ! -d "$ACE_STEP_DIR" ]; then
    echo '{"success":false,"error":"ACE-Step not found at '"$ACE_STEP_DIR"'","suggestion":"Install ACE-Step 1.5 or update config.json"}'
    exit 1
fi

# Pre-flight: check uv exists
if ! command -v uv &>/dev/null; then
    echo '{"success":false,"error":"uv not found","suggestion":"Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"}'
    exit 1
fi

# Pre-flight: VRAM check (warn if very low, don't block)
if command -v nvidia-smi &>/dev/null; then
    FREE_VRAM=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
    if [ -n "$FREE_VRAM" ] && [ "$FREE_VRAM" -lt 4000 ]; then
        echo '{"success":false,"error":"Insufficient VRAM: '"$FREE_VRAM"'MB free (minimum 4GB needed)","suggestion":"Close other GPU applications or use --quality draft"}' >&2
    fi
fi

# Set environment variables
export TOKENIZERS_PARALLELISM=false
export TORCHAUDIO_USE_BACKEND=ffmpeg

# Run via uv from ACE-Step directory (ensures correct Python + deps)
cd "$ACE_STEP_DIR"
exec uv run python3 "$SCRIPT" --ace-step-dir "$ACE_STEP_DIR" "$@"
