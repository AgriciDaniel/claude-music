---
name: claude-music-repaint
description: >
  Edit specific sections of a song using ACE-Step 1.5 repaint mode. Fix a bad chorus,
  change instruments in a section, add/remove vocals, or regenerate any time range
  while keeping the rest intact.
  Use when user says "repaint", "edit section", "fix chorus", "change the bridge",
  "regenerate part", or wants to modify a specific time range of a song.
allowed-tools:
  - Bash
  - Read
---

# claude-music-repaint — Section Editing

## Pre-Flight

1. Verify source: `bash ~/.claude/skills/claude-music/scripts/preflight.sh "$SRC_AUDIO" "$OUTPUT"`
2. Identify the section to edit (start/end in seconds)

## Usage

```bash
# Fix a weak chorus (30s-60s)
bash ~/.claude/skills/claude-music/scripts/music_engine.sh repaint \
  --src-audio song.flac \
  --start 30 --end 60 \
  --caption "powerful chorus, big drums, layered vocals"

# Make the intro more atmospheric (0s-15s)
bash ~/.claude/skills/claude-music/scripts/music_engine.sh repaint \
  --src-audio song.flac \
  --start 0 --end 15 \
  --caption "ambient intro, reverb, ethereal pads"

# Change instruments in a bridge (90s-120s)
bash ~/.claude/skills/claude-music/scripts/music_engine.sh repaint \
  --src-audio song.flac \
  --start 90 --end 120 \
  --caption "stripped back bridge, acoustic guitar only, intimate"

# Regenerate the ending (last 30 seconds)
bash ~/.claude/skills/claude-music/scripts/music_engine.sh repaint \
  --src-audio song.flac \
  --start 150 --end -1 \
  --caption "fade out ending, gentle resolution"
```

## Parameters

| Parameter | Flag | Default | Description |
|-----------|------|---------|-------------|
| Source audio | `--src-audio` | required | Song to edit |
| Start | `--start` | 0.0 | Repaint start (seconds) |
| End | `--end` | -1.0 | Repaint end (-1 = end of file) |
| Caption | `--caption` | `""` | Description for the repainted section |
| Lyrics | `--lyrics` | `""` | New lyrics for the section |
| Quality | `--quality` | standard | draft/standard/high/max |

## Section Identification

To find the right timestamps:
1. Play the song: `ffplay -nodisp -autoexit song.flac`
2. Use analysis: `bash ~/.claude/skills/claude-music/scripts/music_engine.sh` (note the timestamps)
3. Common sections at typical BPM (120):
   - Intro: 0-15s
   - Verse 1: 15-45s
   - Chorus 1: 45-75s
   - Verse 2: 75-105s
   - Chorus 2: 105-135s
   - Bridge: 135-155s
   - Final chorus: 155-185s
   - Outro: 185-210s

## Multi-Pass Refinement

Iteratively improve a song:
1. Generate initial version with `/music generate`
2. Listen, identify weak sections
3. Repaint section A → listen → approve or re-repaint
4. Repaint section B → listen → approve
5. Optionally `/music cover` for final polish (low strength ~0.8)

**Tip**: Each repaint produces a complete new file. Keep the previous version in case the repaint is worse.
