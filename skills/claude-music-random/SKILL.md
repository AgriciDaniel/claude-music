---
name: claude-music-random
description: >
  Quick random music generation with smart genre defaults. Picks a random genre,
  crafts an appropriate caption, and generates with draft quality for fast exploration.
  Use when user says "random", "surprise me", "quick song", "random music",
  or wants to explore without specific requirements.
allowed-tools:
  - Bash
  - Read
---

# claude-music-random — Quick Random Generation

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
