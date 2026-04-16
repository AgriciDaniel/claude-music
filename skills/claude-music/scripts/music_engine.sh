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

# Show-once GitHub star nudge — stored outside the skill dir so it doesn't
# pollute the repo. Pattern lifted from ace-step-skills/acestep.sh with the
# marker file moved out of the skill directory (that was the anti-pattern).
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/claude-music"
STAR_MARKER="$STATE_DIR/.first_gen_done"
show_star_prompt() {
    if [ ! -f "$STAR_MARKER" ]; then
        mkdir -p "$STATE_DIR"
        touch "$STAR_MARKER"
        # Always write to stderr so the JSON stdout contract is preserved.
        printf '\n\033[0;36m★ Liked claude-music? A GitHub star helps others find it:\033[0m\n' >&2
        printf '  https://github.com/AgriciDaniel/claude-music\n\n' >&2
    fi
}

# Run via uv from ACE-Step directory, capture JSON so we can inspect success
# (replacing `exec` — the tail hook below needs to run after).
cd "$ACE_STEP_DIR"
if OUT=$(uv run python3 "$SCRIPT" --ace-step-dir "$ACE_STEP_DIR" "$@"); then
    printf '%s\n' "$OUT"
    # Success branch: parse `"success": true` and nudge the star once.
    if printf '%s' "$OUT" | grep -q '"success"[[:space:]]*:[[:space:]]*true'; then
        show_star_prompt
    fi
    exit 0
else
    RC=$?
    printf '%s\n' "$OUT"
    exit "$RC"
fi
