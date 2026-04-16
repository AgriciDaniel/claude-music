#!/usr/bin/env bash
# Platform-optimized audio export for claude-music
# Usage: bash music_export.sh <platform> <input> [output]
# Platforms: spotify, apple, youtube, tiktok, podcast, cd, archive, web
set -euo pipefail

PLATFORM="${1:-}"
INPUT="${2:-}"
OUTPUT="${3:-}"

if [ -z "$PLATFORM" ] || [ -z "$INPUT" ]; then
    echo '{"success":false,"error":"Usage: music_export.sh <platform> <input> [output]"}'
    exit 1
fi

if [ ! -f "$INPUT" ]; then
    echo '{"success":false,"error":"Input file not found: '"$INPUT"'"}'
    exit 1
fi

BASENAME=$(basename "$INPUT" | sed 's/\.[^.]*$//' | tr -cd 'a-zA-Z0-9._-')
DIR=$(dirname "$INPUT")

# Safety: don't overwrite existing files
check_output() {
    if [ -f "$1" ]; then
        echo '{"success":false,"error":"Output already exists: '"$1"'","suggestion":"Delete it first or specify a different --output path"}'
        exit 1
    fi
}

case "$PLATFORM" in
    spotify|apple|streaming)
        OUT="${OUTPUT:-${DIR}/${BASENAME}_spotify.flac}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 -sample_fmt s16 -c:a flac "$OUT" 2>/dev/null
        ;;
    youtube)
        OUT="${OUTPUT:-${DIR}/${BASENAME}_youtube.mp3}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a libmp3lame -b:a 320k -ar 48000 "$OUT" 2>/dev/null
        ;;
    tiktok|reels|instagram)
        OUT="${OUTPUT:-${DIR}/${BASENAME}_tiktok.m4a}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a aac -b:a 256k -ar 44100 "$OUT" 2>/dev/null
        ;;
    podcast)
        OUT="${OUTPUT:-${DIR}/${BASENAME}_podcast.mp3}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -af "loudnorm=I=-16:TP=-1:LRA=11" -c:a libmp3lame -b:a 192k -ar 44100 -ac 1 "$OUT" 2>/dev/null
        ;;
    cd)
        OUT="${OUTPUT:-${DIR}/${BASENAME}_cd.wav}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -ar 44100 -sample_fmt s16 -c:a pcm_s16le "$OUT" 2>/dev/null
        ;;
    archive)
        OUT="${OUTPUT:-${DIR}/${BASENAME}_archive.flac}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -c:a flac -compression_level 8 "$OUT" 2>/dev/null
        ;;
    web)
        OUT="${OUTPUT:-${DIR}/${BASENAME}_web.opus}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -c:a libopus -b:a 128k "$OUT" 2>/dev/null
        ;;
    mp3)
        OUT="${OUTPUT:-${DIR}/${BASENAME}.mp3}"
        check_output "$OUT"
        ffmpeg -n -i "$INPUT" -c:a libmp3lame -b:a 320k "$OUT" 2>/dev/null
        ;;
    *)
        echo '{"success":false,"error":"Unknown platform: '"$PLATFORM"'. Use: spotify, youtube, tiktok, podcast, cd, archive, web, mp3"}'
        exit 1
        ;;
esac

if [ -f "$OUT" ]; then
    SIZE=$(stat --format=%s "$OUT" 2>/dev/null || stat -f%z "$OUT" 2>/dev/null)
    SIZE_MB=$(echo "scale=2; $SIZE / 1048576" | bc 2>/dev/null || echo "unknown")
    echo "{\"success\":true,\"platform\":\"$PLATFORM\",\"output\":\"$OUT\",\"size_mb\":$SIZE_MB}"
else
    echo '{"success":false,"error":"Export failed — output not created"}'
    exit 1
fi
