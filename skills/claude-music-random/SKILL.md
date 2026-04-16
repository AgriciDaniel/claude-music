---
name: claude-music-random
description: >
  Quick random music generation with smart genre defaults. Picks a random genre,
  crafts an appropriate caption, and generates with draft quality for fast exploration.
when_to_use: >
  Use when user says "random", "surprise me", "quick song", "random music",
  or wants to explore without specific requirements.
model: haiku
allowed-tools:
  - Bash
  - Read
---

# claude-music-random — Quick Random Generation

## Worked example (input → command → output)

**User**: "surprise me"

**Claude picks**: Lo-fi (from the pool below), composes a caption.

**Command**:
```bash
bash ~/.claude/skills/claude-music/scripts/music_engine.sh \
  --quality draft \
  generate \
  --caption "lo-fi hip-hop, chill, atmospheric, vinyl crackle, mellow piano" \
  --instrumental --duration 60
```

**Expected JSON on stdout** (batch=4 from draft preset):
```json
{
  "success": true,
  "task_type": "text2music",
  "model": "acestep-v15-turbo",
  "outputs": [
    {"path": ".../text2music_20260416_121530_01.flac", "seed": 81, "index": 1},
    {"path": ".../text2music_20260416_121530_02.flac", "seed": 84012, "index": 2},
    {"path": ".../text2music_20260416_121530_03.flac", "seed": 44190, "index": 3},
    {"path": ".../text2music_20260416_121530_04.flac", "seed": 2031, "index": 4}
  ],
  "timing": {"generation_sec": 14.8},
  "count": 4
}
```

Then present all four paths and ask which to iterate on.

## Workflow

1. Pick a random genre from the list below
2. Craft a caption using genre-appropriate tags
3. Generate with draft quality (4 variants, ~15s)

## Genre Pool

Pick randomly from: Pop, Rock, Jazz, Lo-fi, Electronic, Hip-hop, R&B, Ambient,
Folk, Synthwave, Bossa Nova, Afrobeat, Funk, Soul, Blues, Country, Reggae,
Classical Piano, Cinematic, Chillwave, House, DnB, Trap, Phonk

## Quick Generate

```bash
# Instrumental random (fastest)
bash ~/.claude/skills/claude-music/scripts/music_engine.sh generate \
  --caption "<genre tags here>" \
  --instrumental --quality draft --duration 60

# With vocals (Claude writes a quick verse + chorus)
bash ~/.claude/skills/claude-music/scripts/music_engine.sh generate \
  --caption "<genre tags>" \
  --lyrics "[Verse] <quick lyrics> [Chorus] <catchy hook>" \
  --quality draft --duration 60
```

## After Generation

Present all 4 variants with paths and suggest: "Want me to refine any of these? I can repaint sections, change the style, or generate more in this direction."
