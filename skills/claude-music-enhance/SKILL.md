---
name: claude-music-enhance
description: >
  Post-processing for generated music. Default path is FFmpeg loudness
  normalization (fast, CPU-only). Escape hatches: AI vocal denoise for
  artifacts, stem separation for surgical edits. Both escape-hatch paths
  reuse tooling from the claude-video skill.
when_to_use: >
  Use when the user says enhance, normalize, denoise, master, polish,
  loudness, stem separation, split vocals, or wants to clean AI artifacts.
allowed-tools:
  - Bash
  - Read
---

# claude-music-enhance — Audio Post-Processing

## Default path: loudness normalization (recommended first)

Loudness-normalize to the platform target in one ffmpeg call. This is the
right answer 90% of the time — the generated audio is already clean; it just
needs the level right.

```bash
# Two-pass loudnorm to -14 LUFS (Spotify/YouTube/Apple/TikTok all target this).
bash ~/.claude/skills/claude-music/scripts/music_export.sh spotify input.flac output.flac
```

See `references/post-processing.md` for the full platform × LUFS table and
the measure-then-apply two-pass recipe if you need manual control.

## Escape hatch 1 — AI vocal denoise (only if audible artifacts)

Use only when you hear artifacts in vocals (hissing, AI mush, robot tones).
FFmpeg normalization won't help; you need DeepFilterNet3.

```bash
source ~/.video-skill/bin/activate
python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py denoise \
  input.flac --output output_clean.flac
```

Requires `claude-video` skill + DeepFilterNet3 weights. <1 GB VRAM.

## Escape hatch 2 — stem separation (only if you need surgical edits)

Use only when you need to fix vocals/drums/bass/other separately, then remix.
Not needed for normal enhancement.

```bash
source ~/.video-skill/bin/activate
python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py separate \
  input.flac --model htdemucs_ft --output-dir ./stems/
```

Produces `vocals.wav`, `drums.wav`, `bass.wav`, `other.wav`. ~7 GB VRAM.

## Decision tree

```
Is the generated audio too quiet or too loud?
    → use the default path (loudnorm)

Do you hear specific vocal artifacts?
    → escape hatch 1 (denoise) THEN default path (loudnorm)

Do you need to fix one stem (e.g., reduce drums, retune vocal) before final mix?
    → escape hatch 2 (separate) → edit stem → remix → default path (loudnorm)
```

## Format conversion

For platform-specific export (codec/bitrate/sample-rate), use
`claude-music-export` — it wraps `music_export.sh` with the right flags per
target (Spotify FLAC, YouTube MP3 320k, TikTok M4A 256k, etc.).

## Scripts used here

- `scripts/music_export.sh` — default loudnorm + format conversion path.
- `~/.claude/skills/claude-video/scripts/audio_enhance.py` — AI denoise and
  stem separation (external skill; must be installed separately).
