# ACE-Step 1.5 + Claude Code Music Skill — Deep Research Report

**Research Date**: April 15, 2026
**Status**: Compiled from official docs, GitHub discussions, community guides, blog posts, and forum posts

---

## Domain 1: ACE-Step Prompt Engineering Masterclass

### Finding 1.1: Caption Crafting Principles

**Source**: Official Tutorial.md, Musician's Guide, community testing (AngeloSpace, ComfyUI discussions)
**Confidence**: High
**Actionable for skill**: Yes

**Key principle**: ACE-Step responds far more to clean, mechanical prompt components than expressive language. Tags behave like control signals. Vague aesthetic phrasing that works in Suno often messes up results in ACE-Step.

**Caption format**: Natural language OR comma-separated tags both work. The model is trained to be compatible with various formats. However, community testing shows **structured comma-separated tags produce more consistent results** than prose descriptions.

**Caption length**: Hard limit of **512 characters**. Sweet spot is **100-300 characters**. Too short = vague, too long = conflicting signals.

**Caption anatomy** (combine multiple dimensions):
1. **Genre** (required): pop, rock, jazz, electronic, folk, hip-hop, lo-fi, synthwave
2. **Instruments** (highly recommended): acoustic guitar, piano, synth pads, 808 drums, strings
3. **Vocal style** (recommended): female vocal, male vocal, breathy, powerful, raspy
4. **Mood/atmosphere** (recommended): melancholic, energetic, intimate, dark
5. **Tempo descriptor** (optional if BPM set): slow tempo, fast tempo, mid-tempo
6. **Era/reference** (optional): "in the style of 80s synthwave", "reminiscent of Bon Iver"
7. **Production style** (optional): lo-fi production, polished studio, raw live recording

**Best vs Worst examples**:
- ❌ "a sad song" → too vague
- ❌ "ambient, metal" → contradictory
- ✅ "melancholic piano ballad with soft female vocals, gentle string accompaniment, slow tempo, intimate and heartbreaking atmosphere"
- ✅ "rock song with crunchy rhythm guitar, punchy snare, and gravelly male vocals"

### Finding 1.2: Genre-Specific Tag Recipes

**Source**: Official paper examples, Ambience AI guide, ComfyUI community, AngeloSpace testing, Purz blog
**Confidence**: Medium-High (compiled from multiple community sources)
**Actionable for skill**: Yes

| Genre | Optimal Tags | BPM Range | Recommended Key | Best Model | Notes |
|-------|-------------|-----------|-----------------|------------|-------|
| Pop | pop, dance pop, synthpop, catchy, upbeat, synth, female/male vocal | 110-130 | C, G, D major | turbo/sft | Most reliable genre |
| Rock | rock, classic rock, hard rock, electric guitar, bass, drums, powerful vocals | 110-140 | E, A, G major/minor | sft | Add "crunchy" for distortion |
| Hip-Hop/Rap | hiphop, rap, trap, boom bap, 808 bass, deep male voice | 80-100 | Various | turbo | Use "b-box" tag for beatboxing |
| Electronic/EDM | electronic, edm, house, techno, trance, synth, pulsing bass | 120-140 | Am, Cm | turbo | Duration 90-120s most stable |
| Jazz | jazz, smooth jazz, saxophone, piano, double bass, brushed drums | 100-140 | F, Bb, Eb | sft/base | Complex harmony works well |
| Classical | classical, orchestral, symphony, strings, brass, woodwinds | 60-120 | C, G, D | base | Use "neoclassical" for modern |
| Lo-Fi | lo-fi, chill, relaxed, vinyl crackle, mellow piano, soft drums | 70-90 | C, F, Am | turbo | Great for instrumentals |
| R&B/Soul | rnb, rhythm and blues, soul, neo soul, groove, smooth vocals | 70-100 | Eb, Ab, Bb | sft | "Late 90s" adds character |
| Country | country, acoustic guitar, banjo, fiddle, twang, storytelling | 100-130 | G, C, D | sft | Add "honky-tonk" for classic |
| Metal | metal, heavy metal, distorted guitars, double bass drumming, aggressive | 140-200 | Dm, Em, Am | base | Use steps:100, cfg:1, dpm_adaptive for best results per community |
| Ambient | ambient, atmospheric, ethereal, pad synths, spacious reverb | 60-90 | Cm, Am | turbo | Good for long durations |
| K-Pop | k-pop, maximalist, trap verse, R&B pre-chorus, explosive chorus | 100-130 | Various | sft | Genre-hop between sections |
| Phonk | phonk, dark, cowbell, distorted 808, memphis rap, aggressive | 130-145 | Fm, Cm | turbo | |
| Trap | trap, 808, hi-hats, dark, heavy bass, atmospheric | 130-170 | Various minor | turbo | |
| House | house, deep house, four-on-the-floor, synth stabs, groovy | 120-130 | Am, Cm | turbo | |
| Techno | techno, industrial, mechanical, driving rhythm, minimal | 125-150 | Am, Dm | turbo | |
| DnB | drum and bass, fast breakbeats, heavy bass, energetic | 170-180 | Various | sft | High BPM works |
| Synthwave | synthwave, retrowave, 80s synth, neon, nostalgic, analog | 100-120 | Am, Fm | sft | Very popular with ACE-Step |
| Cinematic | cinematic orchestral, epic, film score, dramatic, strings, brass | 80-120 | Cm, Dm | base/xl-base | Best with higher steps |
| Bossa Nova | bossa nova, brazilian, gentle guitar, soft percussion, romantic | 120-140 | C, G, F | sft | Nylon guitar tags help |
| Blues | blues, 12-bar blues, slide guitar, soulful, gritty vocals | 80-120 | E, A, G | sft | |
| Folk | folk, acoustic folk, singer-songwriter, fingerpicking, warm | 90-130 | G, C, D, Em | sft | |
| Punk | punk, punk rock, fast, raw, distorted, shouting vocals | 160-200 | E, A, D | sft | |
| UK Garage | UK garage, two-step, shuffling hi-hats, punchy kick, chopped vocals | 130-140 | Various | sft | |
| Neo-Soul | neo-soul, live drums, hip-hop pocket, warm bass, Rhodes piano | 80-100 | Eb, Ab | sft | |
| Chiptune | chiptune, 8-bit, retro game, pixel, square wave | 120-160 | C, Am | turbo | |

### Finding 1.3: Vocal Style Tags

**Source**: Official Tutorial.md, Musician's Guide, community testing
**Confidence**: High
**Actionable for skill**: Yes

**Gender control**:
- `female vocal`, `female vocals`, `female singer`
- `male vocal`, `male vocals`, `male singer`
- `clear male vocalist`, `clear female vocalist`

**Texture/quality tags**:
- `breathy vocals` — soft, intimate
- `raspy vocals` / `gravelly male vocals` — gritty, worn
- `powerful vocals` / `powerful voice` — belting, strong
- `falsetto` — high, ethereal
- `whisper vocals` — intimate, quiet
- `operatic` — classical singing style
- `screaming vocals` — metal/punk
- `soft vocals` — gentle delivery
- `husky voice` — warm, low

**Choir/harmony**:
- `choir`, `vocal harmonies`, `backing vocals`
- Content in parentheses `(ooh, aah)` is processed as background vocals/harmonies

**Vocal effects**:
- `autotune`, `vocoder` — electronic vocal effects
- Effects are **unstable** — sometimes ignored or mispronounced (per Tutorial.md)

**Rap vs singing**:
- `rap`, `rapping`, `spoken word` — distinct from singing
- `b-box, deep male voice, trap, hip-hop, super fast tempo` — for rap/beatbox
- ALL CAPS in lyrics = higher intensity/shouting: `[Chorus] WE ARE THE CHAMPIONS!`

**A cappella**: Use `a cappella` tag; lyrics can use vowel combinations (`aaaaaaaa, eeeeeeeee`)

**Vocal volume**: `multiplier` parameter (default 1.0) — value of `1.15` provides good vocal presence in mix

### Finding 1.4: Instrument Specification Tags

**Source**: Official docs (1000+ instruments supported), community testing
**Confidence**: High
**Actionable for skill**: Yes

**String instruments**: acoustic guitar, electric guitar, bass guitar, nylon guitar, slide guitar, banjo, fiddle, dobro, ukulele, mandolin, harp, erhu, sitar, cello, violin, viola, double bass, strings (generic orchestral)

**Keys**: piano, Rhodes piano, organ, clavinet, harpsichord, accordion, synth pads, synth lead, mellotron

**Wind/Brass**: saxophone, trumpet, trombone, tuba, flute, clarinet, oboe, harmonica, dizi, brass (generic), woodwinds (generic)

**Percussion**: drums, snare, kick drum, hi-hats, cymbal, cowbell, percussion, bongos, congas, tabla, cajon, timpani

**Electronic**: synth, synthesizer, 808, 808 bass, synth bass, synth stabs, vocoder, drum machine, sequencer, arpeggiator

**Chinese folk** (confirmed via LoRA in awesome-ace-step): dizi, erhu, guzheng, pipa

### Finding 1.5: Production/Mixing Tags

**Source**: Community testing, Tutorial.md
**Confidence**: Medium
**Actionable for skill**: Yes

- `lo-fi production`, `vinyl crackle` — degraded/warm
- `polished studio`, `clean production` — professional
- `raw live recording` — unprocessed feel
- `modern production` — contemporary sound
- `vintage`, `retro` — older recording style
- `rich instrumentation` — full arrangement
- `minimal`, `sparse` — stripped back
- `punchy drums`, `tight bass` — mix characteristics

### Finding 1.6: Mood/Atmosphere Tags

**Source**: Multiple community guides
**Confidence**: Medium-High
**Actionable for skill**: Yes

**High-energy**: energetic, upbeat, powerful, intense, aggressive, driving, explosive, anthemic
**Low-energy**: chill, relaxed, laid-back, mellow, calm, peaceful, serene, ambient
**Emotional**: melancholic, emotional, intimate, heartbreaking, nostalgic, bittersweet, wistful
**Dark**: dark, ominous, haunting, eerie, sinister, brooding, mysterious
**Bright**: happy, joyful, uplifting, triumphant, celebratory, hopeful, radiant
**Atmospheric**: atmospheric, ethereal, dreamy, spacious, vast, cinematic, epic

**Rule**: Avoid contradictory moods in the same prompt (e.g., "upbeat, melancholic")

### Finding 1.7: Negative Prompt Patterns

**Source**: Tutorial.md, community testing
**Confidence**: Medium (limited community data on this specific feature)
**Actionable for skill**: Partially

The `lm_negative_prompt` parameter exists but is **less documented** than positive prompts. Community-tested patterns:
- `"noise, distortion, low quality"` — suppress artifacts
- `"vocals"` — when wanting instrumental only (but `[instrumental]` tag is more reliable)
- `"spoken word"` — when wanting singing not talking

### Finding 1.8: Lyrics Formatting

**Source**: Official Tutorial.md, Musician's Guide, Ambience AI guide, ComfyUI docs
**Confidence**: High
**Actionable for skill**: Yes

**Confirmed working structure tags**:
- `[Verse]`, `[Verse 1]`, `[Verse 2]` — numbered verses work
- `[Chorus]`
- `[Bridge]`
- `[Intro]`
- `[Outro]`
- `[Instrumental]` or `[inst]` — purely instrumental section
- `[Pre-Chorus]`

**Partially working / community-reported**:
- `[Hook]` — sometimes works, sometimes treated as chorus
- `[Rap]` — confirmed in paper examples
- `[Drop]`, `[Breakdown]` — less data

**Multilingual support**: Prefix lines with language code for multi-language songs:
```
[verse]
[zh]wo3zou3guo4shen1ye4de5jie1dao4
[ko]hamkke si-kkeuleo-un sesang-ui sodong-eul pihae
[es]cantar mi anhelo por ti sin ocultar
[fr]que tu sois le vent qui souffle sur ma main
```

**Intensity control**: ALL CAPS = high intensity/shouting. Normal case = normal intensity.

**Background vocals**: Content in parentheses `(like this)` is processed as background vocals or harmonies.

**Lyric density guidelines** (community-derived):
| Genre | Approx Words/Min | Words for 60s | Words for 120s | Words for 240s |
|-------|------------------|---------------|----------------|----------------|
| Pop | 80-100 | 80-100 | 160-200 | 320-400 |
| Rap | 140-200 | 140-200 | 280-400 | 560-800 |
| Ballad | 50-70 | 50-70 | 100-140 | 200-280 |
| Rock | 70-90 | 70-90 | 140-180 | 280-360 |
| Folk | 60-80 | 60-80 | 120-160 | 240-320 |
| Jazz | 40-60 | 40-60 | 80-120 | 160-240 |
| Metal | 80-120 | 80-120 | 160-240 | 320-480 |

**Lyric artifact prevention**:
- Don't overcrowd lyrics — leave breathing room between sections
- Use `[Instrumental]` between lyric sections for solos/breaks
- Keep consistent metaphor/imagery throughout (don't switch from water to fire to flying)
- Shorter durations (90-120s) produce more consistent lyric adherence
- If model skips words, reduce lyric density or use Repaint to fix specific sections

### Finding 1.9: Parameter Recipes

**Source**: Community testing (ComfyUI discussions, AngeloSpace, official Tutorial.md, vi-control.net)
**Confidence**: Medium-High (community-verified but individual results vary)
**Actionable for skill**: Yes

```python
# Recipe 1: "Radio-Ready Pop Song"
# Source: Musician's Guide + community consensus
params = dict(
    caption="pop, catchy, upbeat, synth, female vocal, polished production, modern",
    bpm=120,
    keyscale="C major",
    duration=180,
    model_variant="acestep-v15-sft",  # or xl-sft for higher quality
    inference_steps=8,  # turbo default
    guidance_scale=3.0,  # turbo doesn't use CFG effectively; base uses 5-9
    shift=3.0,
    thinking=True,
    lm_model="acestep-5Hz-lm-1.7B",
    batch_size=4,
)

# Recipe 2: "Lo-fi Study Beats"
params = dict(
    caption="lo-fi, chill, relaxed, vinyl crackle, mellow piano, soft drums, ambient pads",
    lyrics="[instrumental]",
    bpm=80,
    keyscale="F major",
    duration=120,
    model_variant="acestep-v15-turbo",
    inference_steps=8,
    shift=3.0,
    thinking=True,
    batch_size=4,
)

# Recipe 3: "Epic Cinematic Score"
params = dict(
    caption="cinematic orchestral, epic, dramatic, strings, brass, timpani, building tension, film score",
    lyrics="[instrumental]",
    bpm=90,
    keyscale="D minor",
    duration=180,
    model_variant="xl-base",  # XL for highest quality
    inference_steps=65,  # Higher for base model
    guidance_scale=4.0,  # ComfyUI community: 4.0 sweet spot, 6.0+ degrades
    shift=6.0,  # Higher shift = more structured composition per community
    cfg_interval_start=0.0,
    cfg_interval_end=0.95,
    thinking=True,
    batch_size=2,
)

# Recipe 4: "Clean Rap/Hip-Hop"
params = dict(
    caption="hiphop, rap, trap, 808 bass, crisp hi-hats, deep male voice, punchy drums, dark atmosphere",
    bpm=85,
    keyscale="E minor",
    duration=200,
    model_variant="acestep-v15-sft",
    inference_steps=8,
    shift=3.0,
    thinking=True,
    batch_size=4,
)

# Recipe 5: "Ambient Soundscape"
params = dict(
    caption="ambient, atmospheric, ethereal, pad synths, spacious reverb, evolving textures, deep, meditative",
    lyrics="[instrumental]",
    bpm=70,
    keyscale="C minor",
    duration=300,
    model_variant="acestep-v15-turbo",
    inference_steps=8,
    shift=3.0,
    thinking=True,
    batch_size=2,
)

# Recipe 6: "High-Energy EDM"
params = dict(
    caption="electronic, EDM, house, energetic, synth drops, pulsing bass, festival, euphoric, four-on-the-floor",
    bpm=128,
    keyscale="A minor",
    duration=120,
    model_variant="acestep-v15-turbo",
    inference_steps=8,
    shift=3.0,
    thinking=True,
    batch_size=4,
)

# Recipe 7: "Acoustic/Folk"
params = dict(
    caption="folk, acoustic folk, singer-songwriter, fingerpicking guitar, warm, intimate, organic",
    bpm=110,
    keyscale="G major",
    duration=180,
    model_variant="acestep-v15-sft",
    inference_steps=8,
    shift=3.0,
    thinking=True,
    batch_size=4,
)

# Recipe 8: "Instrumental Jazz"
params = dict(
    caption="jazz, smooth jazz, improvisational, saxophone, piano, double bass, brushed drums, late night, sophisticated",
    lyrics="[instrumental]",
    bpm=120,
    keyscale="Bb major",
    duration=180,
    model_variant="acestep-v15-sft",
    inference_steps=8,
    shift=3.0,
    thinking=True,
    batch_size=4,
)

# Recipe 9: "Maximum Quality" (slow but best)
# Source: ComfyUI community testing (6+ hours)
params = dict(
    model_variant="xl-base",
    inference_steps=65,  # Stable maximum
    guidance_scale=4.0,  # Sweet spot; 6.0+ breaks quality
    shift=6.0,  # Helps structured composition
    cfg_interval_start=0.0,
    cfg_interval_end=0.95,
    infer_method="ode",
    sampler_mode="er_sde",  # or "dpm_adaptive" for metal
    thinking=True,
    lm_model="acestep-5Hz-lm-4B",
    multiplier=1.15,  # Vocal volume boost
    batch_size=2,
    duration=120,  # Start short, scale up
)

# Recipe 10: "Fast Draft"
params = dict(
    model_variant="acestep-v15-turbo",
    inference_steps=8,
    shift=3.0,
    thinking=False,  # Skip LM thinking for speed
    batch_size=8,  # Generate many, pick best
    duration=60,  # Short for quick iteration
)

# Alt Recipe for Metal (from vi-control.net community):
params_metal = dict(
    model_variant="base",
    inference_steps=100,
    guidance_scale=1.0,
    sampler="dpm_adaptive",
    scheduler="Beta",
)
```

---

## Domain 2: ACE-Step Community Ecosystem & Integrations

### Finding 2.1: Community Projects Catalog

**Source**: awesome-ace-step GitHub repo
**Confidence**: High
**Actionable for skill**: Yes

**Alternative UIs**:
- **ace-step-ui** (fspecii): Spotify-like dark UI, 936 Suno-style tags with search/select, song parameter history, 4-language UI (EN/ZH/JA/KO), LoRA/LoKR training with GPU memory optimization. Friendly sliders ("Creativity", "Strictly follow lyrics") instead of raw params.
- **ProdIA-MAX**: Windows-focused fork adding multi-provider LLM integration (OpenRouter, Ollama, OpenAI), Audio Codes pipeline (extract reference codes from existing songs and inject during generation), voice recorder with Whisper transcription, visual chord builder.
- **Majik's Music Studio**: Desktop tool (Qt/C++) for editing LoRA training datasets: per-track caption, lyrics, BPM, key, audio preview.

**ComfyUI Integrations**:
- **Core native nodes**: Built into ComfyUI core. AIO and split model workflows.
- **15-node integration**: Generation, cover, repaint, extend, edit, LoRA, HeartMuLa compatible.
- **30+ node custom pack**: Audio KSamplers with shift control, multi-API lyrics gen (Gemini/Groq/OpenAI/Claude), masking & inpainting.

**VST3/AU Plugin**:
- Official VST3 plugin: JUCE 8 + C++17/GGML inference. Runs on CPU, CUDA, Metal, Vulkan. Includes Ableton-inspired web UI and standalone ace-server.
- **acestep.cpp**: Portable C++17/GGML implementation. Text + lyrics in, stereo 48kHz WAV/MP3 out. Built-in HTTP server with Svelte web UI.
- VST3/AU plugin with six open-source music models. Uses lego mode for vocals over existing DAW audio.

**Training Tools**:
- **Side-Step**: CLI-based LoRA/LoKr toolkit with corrected timestep sampling, VRAM optimization, gradient sensitivity analysis. LoKR is reportedly 5x faster than LoRA.
- **acestep-captioner**: 11B music captioning model (Qwen2.5 Omni). 1000+ instruments, timbre, structure analysis. Accuracy surpasses Gemini Pro 2.5.
- **acestep-transcriber**: Qwen2.5 Omni-based music transcription. Structure annotation, lyrics transcription, 50+ languages.

**Cloud Deployments**:
- **acemusic.ai**: Free hosted AI music generator. Plain text → LLM writes lyrics → ACE-Step generates full audio. Any genre, up to 5 min, shareable links, no signup.
- **WaveSpeedAI**: API-based. Tags + optional lyrics → music. Max 240 seconds. Costs < $0.02/minute.

### Finding 2.2: Recent GitHub Activity

**Source**: GitHub repo
**Confidence**: High
**Actionable for skill**: Yes

**Latest release** (April 2, 2026): ACE-Step 1.5 XL (4B DiT) — three variants: xl-base, xl-sft, xl-turbo. Requires ≥12GB VRAM (with offload), ≥20GB recommended.

**Known bugs/limitations**:
- LoRA adapters cannot be loaded on quantized models (PEFT/TorchAO compatibility issue). Must set INT8 Quantization to None before loading adapter.
- Output inconsistency: Highly sensitive to random seeds and input duration ("gacha-style" results).
- Style-specific weaknesses on certain genres.
- Very long generations (>4 min) may have repetition or structure issues.
- Windows: Epoch-boundary worker reinitialization can cause training stalls.

### Finding 2.3: API Details

**Source**: Official docs, GRADIO_GUIDE.md
**Confidence**: High
**Actionable for skill**: Yes

**REST API launch**: `uv run acestep-api` → serves on port 8001.

**Key API endpoints**:
- `/release_task` — submit generation task
- `/query_result` — poll for results
- `/v1/audio` — OpenAI-compatible endpoint
- `/format_input` — use LM to enhance caption/lyrics
- `/create_random_sample` — random example generation

**Extract/Lego tasks**: Available tracks for extraction: vocals, backing_vocals, drums, bass, guitar, keyboard, percussion, strings, synth, fx, brass, woodwinds.

---

## Domain 3: Music Production Workflows

### Finding 3.1: Recommended Workflow

**Source**: Official Musician's Guide (Discussion #235)
**Confidence**: High
**Actionable for skill**: Yes

```
Write description → Generate batch of 4 → Listen to all four
                                              ├── Love it? → Export!
                                              ├── Close but not quite? → Repaint the weak section
                                              └── Not right? → Tweak prompt & retry
```

**Key workflow insights**:
- **Always generate batches** (2-4 minimum, 8 for exploration). Never generate just 1.
- **AutoGen feature**: Prepares next batch while you listen to current one.
- Typical iterations: **3-4 generations** to get one "good" result (community consensus).
- Start with **shorter durations (90-120s)**, then increase once prompts are dialed in.
- Use **fixed seed** when tuning parameters to isolate variable changes.
- 95% of time spent in Generate tab; LoRA Training is secondary; Dataset Explorer for reference.

### Finding 3.2: Cover Mode Best Practices

**Source**: Discussion #209, Musician's Guide
**Confidence**: High
**Actionable for skill**: Yes

**audio_cover_strength** is the critical parameter:
| Strength | Effect | Use Case |
|----------|--------|----------|
| 0.0-0.3 | Ignores original, pure text generation | Complete reimagining |
| 0.3-0.5 | Major style freedom | Dramatic genre changes (country → metal) |
| 0.5-0.7 | Balanced blend | Moderate changes (pop → jazz) |
| 0.7-0.9 | Follows original closely | Subtle changes (rock → indie rock) |
| 0.9-1.0 | Same structure, minimal changes | Voice/timbre tweaks only |

**Parameter interaction**: When lowering `audio_cover_strength` (more style change), raise `guidance_scale` to ensure model follows your target style description.

```python
# Example: Country → Heavy Metal conversion
params = dict(
    task_type="cover",
    src_audio="country_song.mp3",
    caption="heavy metal rock with heavily distorted electric guitars, "
            "aggressive double bass drumming, powerful screaming vocals, "
            "fast tempo, high energy, intense dark atmosphere",
    audio_cover_strength=0.4,
    inference_steps=28,
    guidance_scale=9.0,
    shift=3.0,
    cfg_interval_start=0.0,
    cfg_interval_end=0.95,
    infer_method="ode",
)
```

### Finding 3.3: Repaint Workflow

**Source**: Official docs, Medium blog
**Confidence**: High
**Actionable for skill**: Yes

- Set `repainting_start` and `repainting_end` in seconds to define the section to regenerate.
- Audio before and after the repainted section stays intact.
- ACE-Step is fast enough to repaint 100 times to find the perfect version.
- Use for: fixing bad chorus, changing instruments in a section, fixing lyric timing, adding/removing vocals.
- **Multi-pass refinement**: Generate → Repaint section A → Repaint section B → Cover for final polish. Quality generally holds for several repaint passes.

---

## Domain 4: LoRA Training Deep Dive

### Finding 4.1: Dataset Preparation

**Source**: Official LoRA Training Tutorial, DigitalOcean guide, FM9 guide, DeepWiki
**Confidence**: High
**Actionable for skill**: Yes

**Minimum dataset**:
- **8 songs minimum** (official: "8 songs, 1 hour on 3090")
- **20-50 songs** for robust style generalization (FM9 guide)
- Quality > quantity: clean, consistent dataset yields sharper LoRA

**Audio requirements**:
- Length: 30-120 seconds per file
- Format: WAV or FLAC at 44.1kHz or higher (avoid compressed MP3)
- Normalize loudness to -14 LUFS for consistency
- Single-instrument or clearly mixed
- Represent target style consistently

**Annotation**:
- Captions are critical. Write accurate descriptive captions: genre, instruments, tempo, mood, key
- Auto-labeling via `acestep-5Hz-lm` (0.6B/1.7B/4B) through Gradio UI
- Alternative: Gemini API via `scripts/lora_data_prepare/gemini_caption.py`
- BPM/Key should come from Key-BPM-Finder, not LM (LM hallucinations on these)
- Lyrics: currently need manual addition for best results
- CSV metadata format with BPM, Key columns auto-detected

**File structure**:
```
audio_files/
├── song1.mp3
├── song1.txt     ← Lyrics for song1.mp3
├── song2.wav
└── song2.txt     ← Lyrics for song2.wav
```

### Finding 4.2: LoRA vs LoKr

**Source**: Official docs, Side-Step docs
**Confidence**: High
**Actionable for skill**: Yes

| Aspect | LoRA | LoKr |
|--------|------|------|
| Speed | 1x (baseline) | ~5-10x faster |
| Quality | Baseline | Comparable (improved in recent updates) |
| VRAM | Higher | Lower |
| Community preference | Standard choice | Gaining adoption due to speed |
| Implementation | PEFT library | LyCORIS library |

**LoKR recommendation from official docs**: "What used to take an hour now only takes 5 minutes—over 10 times faster."

### Finding 4.3: Training Hyperparameters

**Source**: FM9 guide, DeepWiki, official configs
**Confidence**: High
**Actionable for skill**: Yes

```yaml
# Recommended LoRA config
lora_rank: 16          # 8-64. Higher = more capacity, more VRAM
lora_alpha: 32         # Typically 2x rank
target_modules: ["q_proj", "v_proj", "k_proj", "out_proj"]
num_epochs: 100        # Adjust based on dataset size
batch_size: 4
learning_rate: 1.0e-4
warmup_steps: 50
save_every: 25         # Checkpoint interval
```

**Turbo timestep schedule** (training uses 8 discrete timesteps):
`[1.0, 0.9545, 0.9, 0.8333, 0.75, 0.6429, 0.5, 0.3]`

**Training time estimates**:
- RTX 3090 (24GB): ~1 hour for 8 songs
- H200: ~2.5 hours for 23 songs
- LoKr: 5-10x faster than above

**Output size**: 10-100MB depending on rank (vs 1.5B+ full model)

**Important**: LoRA adapters **cannot** be loaded on quantized models. Set INT8 Quantization to None before loading.

### Finding 4.4: Custom Trigger Tags

**Source**: DeepWiki, training docs
**Confidence**: High
**Actionable for skill**: Yes

You can train with a `custom_tag` (e.g., "my_style") that serves as a trigger word. During inference, include this tag in your caption to activate the LoRA's style. Use consistently in both training captions and inference prompts.

---

## Domain 5: Audio Post-Processing Pipeline

### Finding 5.1: Loudness Normalization

**Source**: FFmpeg docs, platform standards, community guides
**Confidence**: High
**Actionable for skill**: Yes

**Platform standards**:
| Platform | Target LUFS | True Peak | Command |
|----------|-------------|-----------|---------|
| Spotify | -14 LUFS | -1 dBTP | `ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1:LRA=11 output.wav` |
| Apple Music | -16 LUFS | -1 dBTP | `ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1:LRA=11 output.wav` |
| YouTube | -14 LUFS | -1 dBTP | `ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1:LRA=11 output.wav` |
| TikTok/Reels | -14 LUFS | -1 dBTP | Same as YouTube |
| Podcast | -16 to -18 LUFS | -1 dBTP | `ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1:LRA=11 output.wav` |
| Broadcast (EBU R128) | -23 LUFS | -1 dBTP | `ffmpeg -i input.wav -af loudnorm=I=-23:TP=-1:LRA=7 output.wav` |

**Two-pass normalization** (higher quality):
```bash
# Pass 1: Measure
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -

# Pass 2: Apply (use measured values from pass 1)
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1:LRA=11:measured_I=-24.5:measured_TP=-5.4:measured_LRA=12:measured_thresh=-35.8 output.wav
```

**ffmpeg-normalize** (recommended tool): `pip install ffmpeg-normalize`
```bash
# Spotify preset
ffmpeg-normalize input.wav -o output.wav -t -14 --true-peak -1

# Batch/album normalization (preserves relative loudness)
ffmpeg-normalize *.wav --batch -o normalized/ -t -14
```

### Finding 5.2: Format Conversion

**Source**: Audio engineering standards
**Confidence**: High
**Actionable for skill**: Yes

ACE-Step outputs **48kHz stereo**.

```bash
# 48kHz → 44.1kHz (CD quality) with high-quality SoX resampler
ffmpeg -i input.wav -af aresample=resampler=soxr:out_sample_rate=44100:precision=28 output.wav

# WAV → MP3 320kbps (streaming)
ffmpeg -i input.wav -codec:a libmp3lame -b:a 320k output.mp3

# WAV → FLAC (lossless archival)
ffmpeg -i input.wav -codec:a flac output.flac

# WAV → Opus (web delivery, excellent quality at low bitrate)
ffmpeg -i input.wav -codec:a libopus -b:a 128k output.opus

# WAV → AAC (Apple ecosystem)
ffmpeg -i input.wav -codec:a aac -b:a 256k output.m4a
```

### Finding 5.3: Stem Separation

**Source**: Community workflows
**Confidence**: Medium-High
**Actionable for skill**: Yes

```bash
# Demucs v4 stem separation
pip install demucs
python -m demucs --two-stems=vocals input.wav      # Vocals + accompaniment
python -m demucs input.wav                          # 4 stems: vocals, drums, bass, other
python -m demucs -n htdemucs_ft input.wav           # Fine-tuned model (higher quality)
python -m demucs -n htdemucs_6s input.wav           # 6 stems: vocals, drums, bass, guitar, piano, other
```

**htdemucs_ft** generally recommended as best quality for most use cases.

### Finding 5.4: BPM & Key Detection

**Source**: Audio analysis tools
**Confidence**: High
**Actionable for skill**: Yes

```bash
# BPM detection with aubio
pip install aubio
aubio tempo input.wav

# Key detection with essentia
pip install essentia
# Python:
import essentia.standard as es
loader = es.MonoLoader(filename='input.wav')
audio = loader()
key_extractor = es.KeyExtractor()
key, scale, strength = key_extractor(audio)

# Alternative: librosa
import librosa
y, sr = librosa.load('input.wav')
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
```

### Finding 5.5: Metadata Tagging

**Source**: Audio standards
**Confidence**: High
**Actionable for skill**: Yes

```bash
# ID3v2.4 tagging with ffmpeg
ffmpeg -i input.wav \
  -metadata title="Song Title" \
  -metadata artist="AI Generated" \
  -metadata album="ACE-Step Output" \
  -metadata genre="Pop" \
  -metadata year="2026" \
  -metadata comment="Generated with ACE-Step 1.5" \
  output.mp3

# Or use mutagen (Python)
pip install mutagen
```

---

## Domain 6: Competitive Landscape

### Finding 6.1: ACE-Step vs Competitors

**Source**: Official benchmarks, Efficienist review, vi-control.net, HeartMuLa comparison
**Confidence**: High
**Actionable for skill**: Yes

**SongEval Benchmarks** (ACE-Step 1.5 XL):
- Overall quality: **4.79** (vs Suno v5: 4.72)
- Style alignment: **47.9** (leads all reported models)
- Human eval: ~85 Emotional Expression, ~82 Innovativeness, ~80 Sound Quality, ~78 Musicality

| Feature | ACE-Step 1.5 | Suno v5 | Udio | MiniMax | Skill Can Add |
|---------|-------------|---------|------|---------|---------------|
| Open source | ✅ MIT | ❌ | ❌ | ❌ | N/A |
| Local deployment | ✅ <4GB VRAM | ❌ Cloud only | ❌ Cloud | ❌ Cloud | N/A |
| Max duration | 10 min (600s) | ~4 min | ~4 min | ~3 min | Extend via chaining |
| Batch generation | Up to 8 | 2 | 2 | 1 | Automated batch+rank |
| Cover/style transfer | ✅ | ✅ | ✅ "Remix" | ❌ | Advanced presets |
| Repaint (section edit) | ✅ | Limited | ✅ | ❌ | Guided repaint workflow |
| Stem extraction | ✅ 12 tracks | ❌ | ❌ | ❌ | Post-process with Demucs |
| LoRA training | ✅ 8 songs | ❌ | ❌ | ❌ | Guided training wizard |
| Lego mode | ✅ | ❌ | ❌ | ❌ | N/A |
| Complete mode | ✅ | ❌ | ❌ | ❌ | N/A |
| Languages | 50+ | 20+ | 10+ | 5+ | N/A |
| Speed (A100) | <2s/song | ~30s | ~30s | ~30s | N/A |
| Commercial use | ✅ MIT license | Subscription | Subscription | Subscription | N/A |
| Consistency | Low (gacha) | High | High | Medium | Batch+rank system |
| Audio quality | Between v4.5-v5 | Highest | High | Good | Post-processing |

**Key community sentiment**: ACE-Step's main weakness is consistency ("gacha-style" results). Its main strengths are local deployment, speed, editing capabilities, and LoRA training. The skill can bridge the consistency gap through batch generation + automated quality ranking.

### Finding 6.2: Suno UX Patterns Worth Adopting

**Source**: Community discussion
**Confidence**: Medium
**Actionable for skill**: Yes

- Suno lets you get away with instinct-driven, mood-based phrasing. ACE-Step requires more structured prompting → skill should auto-enhance prompts.
- Suno's main advantage is one-click simplicity. Skill should offer a "simple mode" with smart defaults.
- Users want to iterate quickly: generate → listen → tweak. Skill should minimize friction.

---

## Domain 7: Skill Architecture Patterns

### Finding 7.1: CLI Audio Tools

**Source**: Tool documentation
**Confidence**: High
**Actionable for skill**: Yes

**Essential CLI tools for the skill**:
- `ffmpeg`: Format conversion, loudness normalization, effects, metadata
- `ffprobe`: Audio file analysis (duration, sample rate, channels, bitrate)
- `sox` (SoX): Audio effects, trimming, padding, mixing, silence detection
- `aubio`: Beat tracking, BPM detection, onset detection
- `essentia`: Comprehensive music information retrieval (key, scale, tempo, energy)
- `librosa` (Python): Music analysis, feature extraction

**Audio playback in terminal**:
- `ffplay` (from ffmpeg): `ffplay -nodisp -autoexit output.wav`
- `aplay` (ALSA): `aplay output.wav`
- `paplay` (PulseAudio): `paplay output.wav`

### Finding 7.2: Progress & Polling Pattern

**Source**: API docs
**Confidence**: High
**Actionable for skill**: Yes

ACE-Step generation takes 2-30 seconds depending on config. The API uses async task submission:
1. Submit task via `/release_task` → get task_id
2. Poll `/query_result` with task_id
3. Result includes audio file paths when complete

For the skill: use polling with progress indicator, or synchronous generation via Python API.

---

## Domain 8: Music Theory Reference

### Finding 8.1: Key/Scale Reference

**Source**: Music theory standards
**Confidence**: High
**Actionable for skill**: Yes

| Key | Mood/Feel | Best Genres | Common Progressions |
|-----|-----------|-------------|-------------------|
| C major | Bright, pure, innocent | Pop, classical, folk | I-V-vi-IV (C-G-Am-F) |
| C minor | Dark, dramatic, intense | Classical, cinematic, metal | i-iv-v (Cm-Fm-Gm) |
| D major | Triumphant, joyful | Rock, country, pop | I-IV-V (D-G-A) |
| D minor | Melancholic, serious | Classical, jazz, ambient | i-iv-VII (Dm-Gm-C) |
| E major | Bright, powerful | Rock, pop, country | I-IV-V (E-A-B) |
| E minor | Dark, contemplative | Rock, folk, metal | i-iv-VII (Em-Am-D) |
| F major | Pastoral, warm | Folk, classical, pop | I-IV-V (F-Bb-C) |
| F minor | Dark, passionate | Classical, R&B, jazz | i-iv-v (Fm-Bbm-Cm) |
| G major | Happy, bright, optimistic | Pop, folk, country | I-IV-V (G-C-D) |
| G minor | Dark, restless | Jazz, classical, R&B | i-iv-VII (Gm-Cm-F) |
| A major | Warm, positive | Pop, rock, country | I-IV-V (A-D-E) |
| A minor | Melancholic, versatile | Pop, rock, electronic | i-iv-v (Am-Dm-Em) |
| Bb major | Bold, heroic | Jazz, classical, brass | I-IV-V (Bb-Eb-F) |
| Eb major | Majestic, warm | Jazz, classical, soul | I-vi-IV-V |
| Ab major | Rich, romantic | R&B, jazz, soul | I-vi-ii-V |

**Modes** (ACE-Step supports via keyscale):
| Mode | Character | Example Use |
|------|-----------|-------------|
| Dorian | Jazzy minor, sophisticated | Jazz, funk, lo-fi |
| Mixolydian | Bluesy major, relaxed | Blues, rock, folk |
| Lydian | Dreamy, ethereal | Film scores, ambient |
| Phrygian | Spanish, dark, exotic | Flamenco, metal |

**ACE-Step key stability**: Common keys (C, G, D, Am, Em) are most stable. Rare keys may be ignored or shifted. 4/4 time is most reliable; 3/4, 6/8 usually OK; complex signatures (5/4, 7/8) are experimental.

### Finding 8.2: BPM Reference by Genre

**Source**: Music production standards, confirmed against ACE-Step training data distribution
**Confidence**: High
**Actionable for skill**: Yes

| Genre | BPM Range | Sweet Spot | Time Sig |
|-------|-----------|------------|----------|
| Ambient | 50-90 | 70 | 4/4 |
| Ballad | 60-80 | 70 | 4/4 or 3/4 |
| Blues | 60-120 | 90 | 4/4 |
| Bossa Nova | 100-140 | 120 | 4/4 |
| Cinematic/Epic | 70-130 | 100 | 4/4 |
| Classical | 40-200 | 100 | 4/4 or 3/4 |
| Country | 100-140 | 120 | 4/4 |
| DnB | 160-180 | 174 | 4/4 |
| Drill | 140-150 | 144 | 4/4 |
| EDM/House | 120-130 | 128 | 4/4 |
| Folk | 90-140 | 110 | 4/4 or 3/4 |
| Funk | 100-130 | 110 | 4/4 |
| Hip-Hop | 80-100 | 90 | 4/4 |
| Jazz | 80-180 | 130 | 4/4 or 3/4 |
| K-Pop | 100-140 | 120 | 4/4 |
| Lo-Fi | 60-90 | 80 | 4/4 |
| Metal | 100-200 | 140 | 4/4 |
| Neo-Soul | 75-100 | 85 | 4/4 |
| Phonk | 130-145 | 140 | 4/4 |
| Pop | 100-130 | 120 | 4/4 |
| Punk | 150-200 | 170 | 4/4 |
| R&B | 60-100 | 80 | 4/4 |
| Reggae | 70-90 | 80 | 4/4 |
| Reggaeton | 85-100 | 95 | 4/4 |
| Rock | 100-150 | 120 | 4/4 |
| Synthwave | 80-120 | 105 | 4/4 |
| Techno | 120-150 | 135 | 4/4 |
| Trap | 130-170 | 140 | 4/4 |
| UK Garage | 128-140 | 135 | 4/4 |

**ACE-Step range**: Common (60-180) works well. Extreme values (30 or 280+) have less training data and may be unstable.

### Finding 8.3: Song Structure Templates

**Source**: Music production standards, mapped to ACE-Step tags
**Confidence**: High
**Actionable for skill**: Yes

**Pop (3-4 min, ~120 BPM)**:
```
[Intro]           ~8 bars (16s)
[Verse 1]         ~16 bars (32s)
[Pre-Chorus]      ~8 bars (16s)
[Chorus]          ~16 bars (32s)
[Verse 2]         ~16 bars (32s)
[Pre-Chorus]      ~8 bars (16s)
[Chorus]          ~16 bars (32s)
[Bridge]          ~8 bars (16s)
[Chorus]          ~16 bars (32s)
[Outro]           ~8 bars (16s)
Total: ~240s (4 min)
```

**Rock**:
```
[Intro]           ~4-8 bars
[Verse 1]         ~16 bars
[Chorus]          ~16 bars
[Verse 2]         ~16 bars
[Chorus]          ~16 bars
[Bridge]          ~8 bars
[Chorus]          ~16 bars
```

**Hip-Hop/Rap**:
```
[Verse]           ~16 bars
[Verse]           ~16 bars (continued)
[Chorus]          ~8 bars
[Verse]           ~16 bars
[Bridge]          ~8 bars
[Chorus]          ~8 bars
```

**EDM**:
```
[Intro]           ~16 bars (buildup)
[Verse]           ~16 bars
[Chorus]          ~16 bars
[Verse]           ~16 bars (buildup)
[Bridge]          ~8 bars (breakdown)
[Chorus]          ~16 bars (drop)
```

**Folk**:
```
[Verse]           ~16 bars
[Verse]           ~16 bars
[Chorus]          ~8-16 bars
[Verse]           ~16 bars
[Verse]           ~16 bars
[Chorus]          ~8-16 bars
```

**These match the paper's built-in prompt templates for each genre**.

---

## Appendix A: Quick Reference Card for Skill

### Model Selection Guide

| VRAM | Best Model | Inference Steps | Notes |
|------|-----------|----------------|-------|
| ≤6GB | turbo, 0.6B LM | 8 | No thinking mode, no LM |
| 6-8GB | turbo, 0.6B LM | 8 | Limited LM, pt/mlx backend |
| 8-12GB | turbo or sft, 1.7B LM | 8 | vllm backend ok |
| 12-20GB | XL turbo (with offload+quant) | 8 | XL models accessible |
| 20-24GB | XL sft/base, 4B LM | 8-65 | Full capability |
| 24GB+ | XL base, 4B LM | 65-100 | Maximum quality |

### Caption Template
```
{genre}, {sub-genre}, {instrument1}, {instrument2}, {vocal_style}, {mood}, {atmosphere}, {production_style}, {tempo_descriptor}
```

### Task Type Decision Tree
```
Want new music from text?     → text2music
Want to restyle existing?     → cover (set audio_cover_strength)
Want to fix a section?        → repaint (set start/end times)
Want to isolate a stem?       → extract (specify track name)
Want to add an instrument?    → lego (specify instrument)
Want to extend/complete?      → complete
```

### Critical Settings Summary
- **Turbo models**: inference_steps=8 (fixed, don't change)
- **Base models**: inference_steps=32-100 (higher=better but slower)
- **CFG (guidance_scale)**: Only effective on base model. Sweet spot 4.0. >6.0 degrades quality.
- **Shift**: Affects compositional structure. 3.0 for turbo. 5.0-6.0 for base (community-tested).
- **Thinking mode**: Let LM auto-infer BPM, key, structure. Turn off only if you know exactly what you want.
- **Random seed**: Fix seed when tuning params. Use random for exploring variations.
- **Multiplier**: 1.15 for good vocal presence in mix.

---

## Appendix B: Instruments ACE-Step Recognizes (1000+)

### Confirmed High-Quality Instruments
acoustic guitar, electric guitar, bass guitar, piano, Rhodes piano, organ, synthesizer, synth pads, synth lead, drums, snare, kick drum, hi-hats, cymbals, timpani, saxophone, trumpet, trombone, flute, clarinet, violin, cello, viola, double bass, harp, banjo, fiddle, mandolin, ukulele, harmonica, accordion, 808, drum machine, strings (orchestral), brass (generic), woodwinds (generic), erhu, dizi, guzheng, pipa, tabla, sitar, steel drums, marimba, vibraphone, xylophone, glockenspiel, tubular bells, cowbell, congas, bongos, cajon, djembe, hang drum

### Confirmed Effect/Style Tags
vinyl crackle, tape hiss, chorus effect, reverb, delay, distortion, overdrive, fuzz, wah-wah, tremolo, phaser, flanger, compression

---

*End of research report. All findings indexed for direct encoding into claude-music skill components.*
