# ACE-Step Prompt Engineering Guide

## Caption Crafting

### Formula
`Genre + mood + instruments + vocal style + production quality + era reference`

### Dimension Reference

| Dimension | Strong Tags (ACE-Step responds well) |
|-----------|--------------------------------------|
| **Genre** | pop, rock, jazz, electronic, hip-hop, R&B, folk, classical, lo-fi, synthwave, ambient, house, techno, DnB, trap, phonk, bossa nova, afrobeat, country, metal, blues, punk, reggaeton, K-pop, drill |
| **Mood** | melancholic, uplifting, energetic, dreamy, dark, nostalgic, euphoric, intimate, aggressive, peaceful, haunting, triumphant, playful, brooding |
| **Instruments** | acoustic guitar, electric guitar, piano, synth pads, 808 drums, strings, brass, electric bass, saxophone, violin, cello, organ, flute, harp, marimba, tabla, sitar |
| **Vocal** | female vocal, male vocal, breathy, powerful, falsetto, raspy, choir, whispered, operatic, soulful, nasal, deep |
| **Timbre** | warm, bright, crisp, airy, punchy, lush, raw, polished, muddy, sharp, hollow, rich |
| **Production** | lo-fi, high-fidelity, live recording, studio-polished, bedroom pop, overdriven, clean, compressed, spacious, dry, reverb-heavy |
| **Era** | 60s psychedelic, 70s disco, 80s synth-pop, 90s grunge, 2000s pop-punk, 2010s EDM, 2020s hyperpop, vintage soul, retro, modern, futuristic |
| **Rhythm** | slow tempo, mid-tempo, fast-paced, groovy, driving, laid-back, syncopated, straight, swing, shuffle |

### Caption Principles

1. **Specific beats vague**: "sad piano ballad, female breathy vocal, reverb-heavy" > "a sad song"
2. **3-5 descriptors optimal**: Anchors direction without over-constraining
3. **Avoid conflicts**: "ambient metal" or "classical trap" confuse the model
4. **Repetition reinforces**: Mention key elements twice if critical
5. **Don't put BPM/key in caption**: Use `--bpm` and `--key` parameters instead
6. **Less = more creativity**: Fewer descriptors let the model surprise you
7. **Texture words matter**: warm, crisp, airy, punchy directly influence mixing

### Caption Examples

**Good**:
- `"upbeat pop, female vocal, catchy, piano, modern production, 2020s sound"`
- `"dark ambient, deep bass, ethereal pads, haunting atmosphere, reverb-heavy"`
- `"jazz fusion, saxophone, complex harmony, groovy bass, live recording feel"`
- `"lo-fi hip-hop, chill, atmospheric, vinyl crackle, mellow piano, 80 bpm feel"`

**Bad**:
- `"a good song"` (too vague)
- `"ambient metal classical hip-hop"` (conflicting genres)
- `"120 BPM song in C major"` (use params, not caption)

## Lyrics Formatting

### Structure Tags (All Supported)

| Tag | Purpose | Notes |
|-----|---------|-------|
| `[Verse]` / `[Verse 1]` | Narrative progression | Number tags work |
| `[Chorus]` | Emotional climax, hook | Most memorable section |
| `[Pre-Chorus]` | Build energy before chorus | Transitional |
| `[Bridge]` | Contrast with verse/chorus | Usually once |
| `[Intro]` | Opening atmosphere | Often instrumental |
| `[Outro]` | Ending/conclusion | Can be lyrical or fade |
| `[Drop]` | Electronic energy release | EDM genres |
| `[Breakdown]` | Reduced instrumentation | Creates space |
| `[Instrumental]` | No vocals section | Pure music |
| `[Guitar Solo]` | Specific instrument solo | Any instrument works |
| `[Piano Interlude]` | Instrument interlude | Short bridge |
| `[Fade Out]` | Gradual ending | Use at end |
| `[Build]` | Rising energy | Pre-drop |
| `[Hook]` | Catchy repeated phrase | Short, memorable |

### Lyrics Density

| Duration | Words (singing) | Words (rap) | Lines |
|----------|----------------|-------------|-------|
| 30s | 60-90 | 100-150 | 8-12 |
| 60s | 120-180 | 200-300 | 16-24 |
| 120s | 240-360 | 400-600 | 32-48 |
| 180s | 360-540 | 600-900 | 48-72 |
| 240s | 480-720 | 800-1200 | 64-96 |

**Rule of thumb**: ~2-3 words/second for singing, ~4-5 for rap

### Lyrics Best Practices

1. **4-8 words per line** for best vocal clarity
2. **Simple, singable phrasing** — avoid tongue twisters
3. **Match emotion to caption** — melancholic lyrics + upbeat caption = confusion
4. **Chorus should be catchy** — repetition is good in choruses
5. **Line breaks between phrases** — helps timing
6. **Avoid complex vocabulary** — simple words sing better

### Preventing Lyric Artifacts

| Issue | Solution |
|-------|----------|
| Lyric skipping | Reduce total word count; increase `guidance_scale` to 4-7 |
| Words bleeding | Shorter lines (4-6 words); more line breaks |
| Wrong pronunciation | Spell phonetically for non-English; use `--language` correctly |
| Timing misalignment | Match word density to duration; fewer words is safer |
| Repetition loops | Use varied lyrics; avoid identical chorus repetitions > 2x |

## Vocal Control Tags (In Caption)

| Tag | Effect |
|-----|--------|
| `female vocal` | Female singing voice |
| `male vocal` | Male singing voice |
| `breathy vocal` | Airy, intimate vocal texture |
| `powerful vocal` | Strong, belting voice |
| `falsetto` | High register, ethereal |
| `raspy vocal` | Gritty, textured voice |
| `whispered vocal` | Soft, intimate, ASMR-like |
| `choir` | Multi-voice harmony |
| `soulful vocal` | Emotive, R&B-style melisma |
| `operatic vocal` | Classical technique |
| `rap vocal` | Spoken/rhythmic delivery |
| `autotune vocal` | Pitch-corrected, T-Pain style |
