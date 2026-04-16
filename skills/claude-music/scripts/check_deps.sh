#!/usr/bin/env bash
# Check dependencies for claude-music skill
# Output: JSON array of tool statuses
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config.json"
if [ -f "$CONFIG" ] && command -v python3 &>/dev/null; then
    ACE_STEP_DIR=$(python3 -c "import json; print(json.load(open('$CONFIG'))['ace_step_dir'])" 2>/dev/null)
fi
ACE_STEP_DIR="${ACE_STEP_DIR:-}"

check_tool() {
    local name="$1" cmd="$2" install_hint="$3" required="$4"
    # Split cmd into array for safe execution (no eval)
    read -ra CMD_ARGS <<< "$cmd"
    if "${CMD_ARGS[@]}" &>/dev/null; then
        local version
        version=$("${CMD_ARGS[@]}" 2>&1 | head -1 | sed 's/[^0-9.]//g' | head -c 20)
        echo "{\"name\":\"$name\",\"installed\":true,\"version\":\"$version\",\"required\":$required}"
    else
        echo "{\"name\":\"$name\",\"installed\":false,\"install\":\"$install_hint\",\"required\":$required}"
    fi
}

RESULTS=()
RESULTS+=("$(check_tool "uv" "uv --version" "curl -LsSf https://astral.sh/uv/install.sh | sh" true)")
RESULTS+=("$(check_tool "ffmpeg" "ffmpeg -version" "sudo apt install ffmpeg" true)")
RESULTS+=("$(check_tool "ffprobe" "ffprobe -version" "sudo apt install ffmpeg" true)")
RESULTS+=("$(check_tool "jq" "jq --version" "sudo apt install jq" true)")
RESULTS+=("$(check_tool "ffplay" "ffplay -version" "sudo apt install ffmpeg" false)")

if [ -d "$ACE_STEP_DIR" ] && [ -f "$ACE_STEP_DIR/pyproject.toml" ]; then
    RESULTS+=("{\"name\":\"ace-step\",\"installed\":true,\"version\":\"1.5\",\"path\":\"$ACE_STEP_DIR\",\"required\":true}")
else
    RESULTS+=("{\"name\":\"ace-step\",\"installed\":false,\"install\":\"Install ACE-Step 1.5 to $ACE_STEP_DIR\",\"required\":true}")
fi

for model in "acestep-v15-turbo" "vae" "Qwen3-Embedding-0.6B"; do
    if [ -d "$ACE_STEP_DIR/checkpoints/$model" ]; then
        RESULTS+=("{\"name\":\"checkpoint:$model\",\"installed\":true,\"required\":true}")
    else
        RESULTS+=("{\"name\":\"checkpoint:$model\",\"installed\":false,\"install\":\"uv run acestep-download\",\"required\":true}")
    fi
done

for lm in "acestep-5Hz-lm-0.6B" "acestep-5Hz-lm-1.7B"; do
    if [ -d "$ACE_STEP_DIR/checkpoints/$lm" ]; then
        RESULTS+=("{\"name\":\"checkpoint:$lm\",\"installed\":true,\"required\":false}")
    else
        RESULTS+=("{\"name\":\"checkpoint:$lm\",\"installed\":false,\"install\":\"uv run acestep-download\",\"required\":false}")
    fi
done

if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
    RESULTS+=("{\"name\":\"nvidia-gpu\",\"installed\":true,\"version\":\"$GPU_NAME\",\"required\":true}")
else
    RESULTS+=("{\"name\":\"nvidia-gpu\",\"installed\":false,\"install\":\"Install NVIDIA drivers\",\"required\":true}")
fi

mkdir -p "$HOME/Music/claude-music-output" 2>/dev/null
RESULTS+=("{\"name\":\"output-dir\",\"installed\":true,\"path\":\"$HOME/Music/claude-music-output\",\"required\":true}")

echo "["
for i in "${!RESULTS[@]}"; do
    [ "$i" -lt "$(( ${#RESULTS[@]} - 1 ))" ] && echo "  ${RESULTS[$i]}," || echo "  ${RESULTS[$i]}"
done
echo "]"
