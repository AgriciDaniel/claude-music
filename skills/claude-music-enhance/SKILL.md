---
name: claude-music-enhance
description: >
  Post-processing and enhancement for generated music. Loudness normalization,
  AI noise reduction (DeepFilterNet3), stem separation (Demucs), format conversion.
  Reuses audio processing tools from the claude-video skill ecosystem.
  Use when user says "enhance", "normalize", "denoise", "stem separation",
  "separate vocals", "master", or wants to improve audio quality.
allowed-tools:
  - Bash
  - Read
---

# claude-music-enhance — Audio Post-Processing

## Loudness Normalization (FFmpeg — No GPU)

```bash
# Two-pass loudness normalization to -14 LUFS (Spotify standard)
STATS=$(ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1)
# Extract measured values, then apply:
ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11:measured_I=<val>:measured_TP=<val>:measured_LRA=<val>:measured_thresh=<val>:offset=<val> \
  -c:a flac output_normalized.flac
```

## Stem Separation (Demucs — Reuses Video Skill)

Separate a song into vocals, drums, bass, and other:
```bash
source ~/.video-skill/bin/activate
python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py separate \
  input.flac --model htdemucs_ft --output-dir ./stems/
```

**Output**: `vocals.wav`, `drums.wav`, `bass.wav`, `other.wav`
**VRAM**: ~7GB for htdemucs_ft

## AI Noise Reduction (DeepFilterNet3 — Reuses Video Skill)

Clean up AI artifacts in vocals:
```bash
source ~/.video-skill/bin/activate
python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py denoise \
  input.flac --output output_clean.flac
```

**VRAM**: <1GB

## Format Conversion

```bash
# FLAC to MP3 320k
ffmpeg -i input.flac -c:a libmp3lame -b:a 320k output.mp3

# WAV to FLAC (lossless compression)
ffmpeg -i input.wav -c:a flac output.flac

# 48kHz to 44.1kHz (CD standard)
ffmpeg -i input.flac -ar 44100 output_44k.flac

# Stereo to mono
ffmpeg -i input.flac -ac 1 output_mono.flac
```

## Enhancement Pipeline

For best results, process in this order:
1. **Stem separate** (if needed for individual processing)
2. **Denoise** vocals stem
3. **Remix** stems back together
4. **Normalize** loudness to target LUFS
5. **Export** in target format
