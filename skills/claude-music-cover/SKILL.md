---
name: claude-music-cover
description: >
  Creates cover versions and style transfers of existing songs using ACE-Step 1.5.
  Takes a reference audio file and generates a new version with different style,
  genre, or vocal characteristics while preserving musical structure.
when_to_use: >
  Use when the user asks to cover, remake, reimagine, style-transfer, or produce
  a different version of an existing audio file.
allowed-tools:
  - Bash
  - Read
---

# claude-music-cover — Cover/Style Transfer

## Worked example (input → command → output)

**User**: "Turn this pop song into a jazz cover" (hands over `~/Music/my_song.flac`)

**Command**:
```bash
bash ~/.claude/skills/claude-music/scripts/music_engine.sh \
  --quality standard \
  cover \
  --src-audio "$HOME/Music/my_song.flac" \
  --caption "smooth jazz, saxophone, piano trio, warm, live recording feel" \
  --cover-strength 0.5
```

**Expected JSON on stdout**:
```json
{
  "success": true,
  "task_type": "cover",
  "model": "acestep-v15-turbo",
  "outputs": [
    {"path": "/home/$USER/Music/claude-music-output/cover_20260416_121040_01.flac",
     "seed": 4921, "size_mb": 2.47, "index": 1},
    {"path": "/home/$USER/Music/claude-music-output/cover_20260416_121040_02.flac",
     "seed": 81244, "size_mb": 2.52, "index": 2}
  ],
  "params": {
    "src_audio": "/home/$USER/Music/my_song.flac",
    "cover_strength": 0.5,
    "caption": "smooth jazz, saxophone, piano trio, warm, live recording feel"
  },
  "timing": {"generation_sec": 29.4},
  "count": 2
}
```

Note: `--cover-strength` maps to ACE-Step's `cover_noise_strength` (0.0 = fully reimagine source, 1.0 = stay close to source). The code passes `src_audio` + `cover_noise_strength` — the older `reference_audio`/`audio_cover_strength` field names are wrong and guarded by a regression test.

## Pre-Flight

1. Verify source audio exists: `bash ~/.claude/skills/claude-music/scripts/preflight.sh "$SRC_AUDIO" "$OUTPUT"`
2. Check GPU: `bash ~/.claude/skills/claude-music/scripts/detect_gpu.sh`

## Usage

```bash
# Jazz cover of a pop song
bash ~/.claude/skills/claude-music/scripts/music_engine.sh cover \
  --src-audio /path/to/original.mp3 \
  --caption "smooth jazz, saxophone, piano trio" \
  --cover-strength 0.5

# Same genre, different mood
bash ~/.claude/skills/claude-music/scripts/music_engine.sh cover \
  --src-audio song.flac \
  --caption "acoustic version, stripped back, intimate" \
  --cover-strength 0.7

# Complete reimagination
bash ~/.claude/skills/claude-music/scripts/music_engine.sh cover \
  --src-audio track.wav \
  --caption "electronic, synthwave, 80s retro" \
  --cover-strength 0.2

# Cover with new lyrics
bash ~/.claude/skills/claude-music/scripts/music_engine.sh cover \
  --src-audio original.mp3 \
  --caption "rock, electric guitar, powerful male vocal" \
  --lyrics "[Verse] New lyrics here..." \
  --cover-strength 0.5
```

## Cover Strength Guide

`--cover-strength` controls `cover_noise_strength` (how much of the source audio's latent is preserved):

| Value | Effect | Use When |
|-------|--------|----------|
| 0.0 | Pure noise — complete reimagination, only caption guides output | Major genre transformation |
| 0.2-0.3 | Loose inspiration — new arrangement, some structural similarity | Different genre/mood |
| 0.4-0.5 | Moderate transfer — recognizable structure, new details | Balanced cover (default) |
| 0.6-0.7 | Faithful adaptation — preserves melody/rhythm, changes timbre | Same genre, different voice |
| 0.8-1.0 | Close to source — minimal changes, mostly regeneration | Voice swap, subtle tweaks |

## Parameters

| Parameter | Flag | Default | Description |
|-----------|------|---------|-------------|
| Source audio | `--src-audio` | required | Path to reference audio file |
| Caption | `--caption` / `-c` | `""` | New style description |
| Lyrics | `--lyrics` / `-l` | `""` | New lyrics (optional) |
| Cover strength | `--cover-strength` | 0.5 | Noise preservation (0.0=pure noise/reimagine, 1.0=closest to source) |
| Quality | `--quality` | standard | draft/standard/high/max |
| Format | `--format` | flac | Output audio format |

## Reference Audio Tips

- **Supported formats**: MP3, WAV, FLAC, OGG, AAC, M4A
- **Optimal length**: Match your target duration (model uses the full reference)
- **Quality matters**: Higher quality reference = better style extraction
- **Loudness**: Normalize reference to ~-14 LUFS for consistency
