---
name: claude-music-compose
description: >
  Songwriting guide for ACE-Step music generation. Helps craft captions (style descriptions),
  lyrics with structure tags, and choose optimal BPM/key/duration/time signature.
when_to_use: >
  Use when user says "compose", "write lyrics", "songwriting", "plan a song",
  "caption help", or needs guidance before generating music.
model: opus
context: fork
agent: music-composer
allowed-tools:
  - Read
---

# claude-music-compose — Songwriting Assistant

This is a READ-ONLY reference skill. Claude uses this knowledge to help craft optimal inputs for `/music generate`.

## Execution

This sub-skill runs in a forked context (`context: fork`) and delegates the actual composition planning to the **music-composer** agent (`skills/claude-music/agents/music-composer.md`). The agent returns structured JSON ready to hand to `music_engine.sh generate`.

The reference material below is what the agent reads when it plans. It is also what you read when the user wants to learn the conventions rather than auto-compose.

## Output Format

After composing, produce these for the generate command:
1. **Caption** (`-c`): Style/genre/instruments/emotion (max 512 chars)
2. **Lyrics** (`-l`): Structured lyrics with tags (max 4096 chars)
3. **Parameters**: `--duration`, `--bpm`, `--key`, `--time-sig`, `--language`

## Caption Crafting

**Formula**: `Genre + mood + instruments + vocal style + production quality`

### Dimensions

| Dimension | Examples |
|-----------|----------|
| Genre | pop, rock, jazz, electronic, hip-hop, R&B, folk, classical, lo-fi, synthwave |
| Mood | melancholic, uplifting, energetic, dreamy, dark, nostalgic, euphoric, intimate |
| Instruments | acoustic guitar, piano, synth pads, 808 drums, strings, brass, electric bass |
| Timbre | warm, bright, crisp, airy, punchy, lush, raw, polished |
| Era | 80s synth-pop, 90s grunge, 2010s EDM, vintage soul, modern trap |
| Production | lo-fi, high-fidelity, live recording, studio-polished, bedroom pop |
| Vocals | female vocal, male vocal, breathy, powerful, falsetto, raspy, choir |
| Rhythm | slow tempo, mid-tempo, fast-paced, groovy, driving, laid-back |

### Principles

1. **Specific beats vague** — "sad piano ballad, female breathy vocal" > "a sad song"
2. **Combine 3-5 dimensions** — anchors the direction precisely
3. **Don't put BPM/key in caption** — use dedicated parameters instead
4. **Avoid conflicting genres** — "ambient metal" confuses the model
5. **Repetition reinforces** — repeat elements you want emphasized
6. **Less detail = more creativity** — let the model surprise you

## Lyrics Structure

### Tags

| Tag | Purpose |
|-----|---------|
| `[Verse]` / `[Verse 1]` | Narrative sections |
| `[Chorus]` | Emotional climax, hook |
| `[Pre-Chorus]` | Build energy before chorus |
| `[Bridge]` | Transition or elevation |
| `[Intro]` | Opening atmosphere |
| `[Outro]` | Ending/conclusion |
| `[Drop]` | Electronic energy release |
| `[Breakdown]` | Reduced instrumentation |
| `[Instrumental]` | No vocals section |
| `[Guitar Solo]` | Specific instrument solo |
| `[Fade Out]` | Fade ending |

### Density Rules

- **~2-3 words per second** of audio
- 30s track: 60-90 words
- 60s track: 120-180 words
- 120s track: 240-360 words
- Keep lines 4-8 words for vocal clarity
- Simple, singable phrasing works best

### Tips

- Match lyrics emotion to caption mood
- Avoid tongue twisters and complex vocabulary
- Use line breaks between phrases
- Chorus should be the most memorable/catchy section
- Bridge should contrast with verse/chorus

## Parameter Selection

### BPM by Genre

| Genre | BPM Range | Sweet Spot |
|-------|-----------|------------|
| Ballad | 60-80 | 70 |
| Lo-fi | 70-90 | 80 |
| R&B | 80-100 | 90 |
| Pop | 100-130 | 120 |
| Rock | 110-140 | 125 |
| House | 120-130 | 125 |
| Hip-hop | 80-115 | 95 |
| EDM | 128-150 | 140 |
| DnB | 160-180 | 174 |
| Trap | 130-170 | 140 |

### Duration Guide

| Song Type | Duration | Notes |
|-----------|----------|-------|
| Jingle/Short | 15-30s | TikTok, ad music |
| Standard | 60-120s | Most songs |
| Full song | 180-300s | Complete arrangement |
| Extended | 300-600s | Ambient, DJ sets |

For detailed reference: load `references/prompt-guide.md` and `references/music-theory.md`
