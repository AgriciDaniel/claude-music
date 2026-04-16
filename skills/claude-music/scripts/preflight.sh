#!/usr/bin/env bash
# Pre-flight safety checks for claude-music operations
# Usage: bash preflight.sh [INPUT] [OUTPUT]
# Output: JSON with pass/fail, errors, warnings
set -euo pipefail

INPUT="${1:-}"
OUTPUT="${2:-}"
ERRORS=()
WARNINGS=()

# Check input file
if [ -n "$INPUT" ] && [ "$INPUT" != "-" ]; then
    if [ ! -f "$INPUT" ]; then
        ERRORS+=("Input file not found: $INPUT")
    else
        EXT="${INPUT##*.}"
        EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')
        case "$EXT_LOWER" in
            mp3|wav|flac|ogg|opus|aac|m4a|wma|aiff|alac) ;;
            mp4|mkv|webm|mov) WARNINGS+=("Input is a video file; audio will be extracted") ;;
            *) WARNINGS+=("Unrecognized audio format: .$EXT_LOWER") ;;
        esac
    fi
fi

# Check output path
if [ -n "$OUTPUT" ]; then
    if [ -n "$INPUT" ] && [ "$INPUT" = "$OUTPUT" ]; then
        ERRORS+=("Output path equals input path: $OUTPUT")
    fi
    if [ -f "$OUTPUT" ]; then
        WARNINGS+=("Output file already exists: $OUTPUT (will not overwrite)")
    fi
    OUTPUT_DIR=$(dirname "$OUTPUT")
    if [ ! -d "$OUTPUT_DIR" ]; then
        if ! mkdir -p "$OUTPUT_DIR" 2>/dev/null; then
            ERRORS+=("Cannot create output directory: $OUTPUT_DIR")
        fi
    fi
    if command -v df &>/dev/null && [ -d "$OUTPUT_DIR" ]; then
        FREE_KB=$(df --output=avail "$OUTPUT_DIR" 2>/dev/null | tail -1 | xargs)
        if [ -n "$FREE_KB" ] && [ "$FREE_KB" -lt 512000 ]; then
            WARNINGS+=("Low disk space: $(( FREE_KB / 1024 ))MB free in $OUTPUT_DIR")
        fi
    fi
fi

# Check ACE-Step
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config.json"
if [ -f "$CONFIG" ] && command -v python3 &>/dev/null; then
    ACE_STEP_DIR=$(python3 -c "import json; print(json.load(open('$CONFIG'))['ace_step_dir'])" 2>/dev/null)
fi
ACE_STEP_DIR="${ACE_STEP_DIR:-}"
if [ ! -d "$ACE_STEP_DIR" ]; then
    ERRORS+=("ACE-Step not found at $ACE_STEP_DIR")
fi

PASS=true
[ ${#ERRORS[@]} -gt 0 ] && PASS=false

ERRORS_JSON="[]"
if [ ${#ERRORS[@]} -gt 0 ]; then
    ERRORS_JSON=$(printf '%s\n' "${ERRORS[@]}" | jq -R . | jq -s .)
fi
WARNINGS_JSON="[]"
if [ ${#WARNINGS[@]} -gt 0 ]; then
    WARNINGS_JSON=$(printf '%s\n' "${WARNINGS[@]}" | jq -R . | jq -s .)
fi

cat <<EOF
{
  "pass": $PASS,
  "errors": $ERRORS_JSON,
  "warnings": $WARNINGS_JSON
}
EOF
