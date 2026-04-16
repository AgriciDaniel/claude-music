---
name: claude-music-generate
description: >
  Generate music from text descriptions and lyrics using ACE-Step 1.5 Python API.
  Creates full songs with vocals, instrumentals, or both. Supports 50+ languages,
  10-600 second duration, quality presets (draft/standard/high/max), batch generation.
  Use when user says "generate music", "make a song", "create a track", "text to music",
  or wants to create new music from scratch.
allowed-tools:
  - Bash
  - Read
  - Write
---

# claude-music-generate — Text-to-Music Generation

## Pre-Flight

1. Run `bash ~/.claude/skills/claude-music/scripts/preflight.sh "" "$OUTPUT"` if output specified
2. Run `bash ~/.claude/skills/claude-music/scripts/detect_gpu.sh` to determine quality tier

## Basic Generation

```bash
# Simple instrumental
bash ~/.claude/skills/claude-music/scripts/music_engine.sh generate \
  --caption "upbeat electronic dance music, energetic synths, driving beat" \
  --instrumental --duration 60

# Song with lyrics
bash ~/.claude/skills/claude-music/scripts/music_engine.sh generate \
  --caption "pop ballad, female vocal, piano, emotional" \
  --lyrics "[Verse 1]
Under city lights we found our way
Every word you said still haunts my day
[Chorus]
Hold me close don't let me fall
You're the only one who hears my call" \
  --duration 120 --language en

# High quality with thinking mode
bash ~/.claude/skills/claude-music/scripts/music_engine.sh generate \
  --caption "jazz fusion, saxophone, complex harmony" \
  --quality high --duration 180 --bpm 110 --key "Bb major"

# Quick draft — 4 variants to pick from
bash ~/.claude/skills/claude-music/scripts/music_engine.sh generate \
  --caption "lo-fi hip-hop, chill, atmospheric, vinyl crackle" \
  --quality draft --instrumental --duration 60
```

## Parameters

| Parameter | Flag | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Caption | `--caption` / `-c` | required | <512 chars | Style/genre/instrument description |
| Lyrics | `--lyrics` / `-l` | `""` | <4096 chars | Song lyrics with structure tags |
| Instrumental | `--instrumental` | false | flag | No vocals |
| Language | `--language` | `en` | ISO 639-1 | Vocal language (en, zh, ja, es, fr, etc.) |
| Duration | `--duration` | 60 | 10-600 sec | Target length |
| BPM | `--bpm` | auto | 30-300 | Tempo (auto = model decides) |
| Key | `--key` | auto | e.g. "C major" | Musical key |
| Time Sig | `--time-sig` | auto | 2/3/4/6 | Time signature |
| Quality | `--quality` | standard | draft/standard/high/max | Preset |
| Batch | `--batch` | 2 | 1-8 | Number of variants |
| Format | `--format` | flac | flac/wav/mp3/opus/aac | Output format |
| Seed | `--seed` | -1 | int | Reproducibility (-1 = random) |
| Model | `--model` | auto | turbo/base/sft/xl-* | Override DiT model |

## Quality Presets

- **draft**: turbo, steps=8, no LM, batch=4. Fastest. Use for exploring ideas.
- **standard**: turbo, steps=8, no LM, batch=2. Default. Good balance.
- **high**: turbo + 1.7B LM, thinking=True, batch=2. Better structure/lyrics adherence.
- **max**: base model, steps=65, LM thinking, batch=1. Best quality, ~3-5 min.

## Output

JSON to stdout with paths, seeds, timing:
```json
{
  "success": true,
  "task_type": "text2music",
  "outputs": [{"path": "/home/.../generate_20260416_120000_01.flac", "seed": 42}],
  "playback_hint": "ffplay -nodisp -autoexit \"/path/to/file.flac\""
}
```

## Workflow Tips

1. **Start with draft quality** — generate 4 variants, pick the best direction
2. **Lock the seed** — once you find a good variant, use `--seed <value>` to reproduce it
3. **Iterate on caption** — add/remove descriptors to steer the sound
4. **Use compose first** — for vocal songs, use `/music compose` to craft proper lyrics before generating
5. **Repaint bad sections** — don't regenerate the whole song; use `/music repaint` to fix specific parts

## Caption Crafting Quick Guide

**Formula**: `Genre + mood + instruments + vocal style + production quality`

Good: `"upbeat pop, female vocal, catchy, piano, modern production, 2020s sound"`
Bad: `"a good song"` (too vague)
Bad: `"ambient metal classical hip-hop"` (conflicting genres)

For detailed guidance: load `references/prompt-guide.md`

## Lyrics Quick Guide

- Use structure tags: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Intro]`, `[Outro]`
- Keep lines 4-8 words for best vocal clarity
- ~2-3 words per second (60s song ~ 120-180 words)
- Avoid tongue twisters and complex vocabulary

For detailed guidance: load `references/prompt-guide.md`
