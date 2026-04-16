# ACE-Step 1.5 + Claude Code Music Skill — Deep Research Brief

> **Instructions for Research Agent**: You are conducting exhaustive research to inform the creation of the best possible Claude Code skill for AI music generation using ACE-Step 1.5. This skill will be called `claude-music`. Search the web, fetch documentation, read GitHub repos, and compile findings into structured, actionable intelligence. NO FLUFF — every sentence must be directly useful for building the skill. Use tables, code blocks, and parameter recipes wherever possible.

---

## WHAT I ALREADY KNOW (DO NOT REPEAT)

I already have full knowledge of:
- ACE-Step 1.5 architecture (LM + DiT + VAE + Qwen3-Embedding)
- All Python API functions (`generate_music`, `understand_music`, `create_sample`, `format_sample`)
- All REST API endpoints (`/release_task`, `/query_result`, `/v1/audio`, `/format_input`, `/create_random_sample`)
- Full `GenerationParams` and `GenerationConfig` parameter lists (50+ params)
- All task types (text2music, cover, repaint, extract, lego, complete)
- GPU tier system, quantization options, CPU offloading
- Basic installation and launch commands
- The Tutorial.md philosophy (human-centered generation, elephant rider metaphor)
- Model variants: 2B (base/sft/turbo), 4B XL (xl-base/xl-sft/xl-turbo), LM (0.6B/1.7B/4B)

**Skip all of the above. Focus ONLY on what's below.**

---

## DOMAIN 1: ACE-Step Prompt Engineering Masterclass

### 1A. Caption/Tag Crafting (CRITICAL)

Research and compile:

1. **Genre-Specific Tag Recipes**: For each of the following genres, find the EXACT tag combinations that produce the best results with ACE-Step 1.5. Search Reddit (r/aimusic, r/ACE_Step), Discord servers, GitHub issues/discussions, blog posts, and community guides:
   - Pop, Rock, Hip-Hop/Rap, Electronic/EDM, Jazz, Classical, Lo-Fi, R&B/Soul, Country, Metal, Ambient, Latin, Afrobeat, K-Pop, Phonk, Trap, Drill, House, Techno, DnB, Reggaeton, Bossa Nova, Blues, Folk, Punk, Synthwave/Retrowave, Cinematic/Epic, Chiptune/8-bit

   Format as a table:
   | Genre | Optimal Tags | BPM Range | Recommended Key | Best Model Variant | Notes |

2. **Vocal Style Tags**: What specific tag phrases control vocal characteristics? Compile a reference of:
   - Male vs female voice control tags
   - Vocal texture tags (breathy, raspy, powerful, falsetto, whisper, growl, operatic)
   - Choir/harmony tags
   - Vocal effects (autotune, reverb, ad-libs)
   - Rap/spoken word vs singing differentiation

3. **Instrument Specification Tags**: What's the full vocabulary of instruments ACE-Step responds to? Which instrument names produce the most distinctive results? Are there multi-instrument combination tags that work well together?

4. **Production/Mixing Tags**: Tags that control production quality, mixing style, lo-fi vs hi-fi, vintage vs modern, compressed vs dynamic, analog vs digital feel.

5. **Mood/Atmosphere Tags**: Comprehensive mood taxonomy that ACE-Step actually responds to (not just generic adjectives). What emotional descriptors produce the most consistent results?

6. **Negative Prompt Patterns**: What `lm_negative_prompt` values effectively suppress unwanted elements? Compile community-tested negative prompts.

7. **Caption Length Sweet Spot**: What's the empirically optimal caption length? Too short = vague, too long = conflicting. Find community consensus.

### 1B. Lyrics Formatting Deep Dive

1. **Structure Tag Effectiveness**: Beyond `[Verse]`, `[Chorus]`, `[Bridge]` — what other structure tags does ACE-Step respond to? Test reports for:
   - `[Intro]`, `[Outro]`, `[Pre-Chorus]`, `[Hook]`, `[Drop]`, `[Breakdown]`, `[Interlude]`, `[Ad-lib]`, `[Instrumental]`, `[Solo]`, `[Rap]`, `[Spoken]`
   - Do nested tags work? (e.g., `[Verse 1]`, `[Chorus x2]`)

2. **Lyric Density Rules**: Words-per-second by genre. How many words fit in a 30s, 60s, 120s, 240s track? Find empirical data, not theoretical.

3. **Multilingual Lyrics**: Which languages produce the best vocal quality? Rankings from community testing. Any language mixing patterns that work well?

4. **Lyric Artifacts Prevention**: Community-discovered techniques to prevent:
   - Lyric skipping/dropping
   - Words bleeding into each other
   - Wrong pronunciation
   - Timing misalignment
   - Repetition loops

### 1C. Parameter Recipes (The Gold)

Research specific parameter combinations that the community has found optimal for different scenarios:

1. **"Radio-Ready Pop Song" recipe**: exact params (steps, CFG, guidance_interval, shift, model, thinking, etc.)
2. **"Lo-fi Study Beats" recipe**: params for chill, looping-friendly instrumentals
3. **"Epic Cinematic Score" recipe**: params for orchestral, dramatic compositions
4. **"Clean Rap/Hip-Hop" recipe**: params that produce clear rap vocals with tight beats
5. **"Ambient Soundscape" recipe**: params for long, evolving atmospheric pieces
6. **"High-Energy EDM" recipe**: params for drops, buildups, festival-ready tracks
7. **"Acoustic/Folk" recipe**: params for organic, natural-sounding instruments
8. **"Instrumental Jazz" recipe**: params for improvisational, complex harmony
9. **"Maximum Quality" recipe**: the absolute best quality settings regardless of speed
10. **"Fast Draft" recipe**: fastest generation that still sounds good

For each recipe, provide: `model_variant`, `inference_steps`, `guidance_scale`, `cfg_interval_start/end`, `shift`, `thinking`, `lm_temperature`, `lm_cfg_scale`, `use_adg`, `sampler_mode`, `infer_method`, `duration`, `batch_size`

---

## DOMAIN 2: ACE-Step Community Ecosystem & Integrations

### 2A. Community Projects Worth Knowing

Search the `awesome-ace-step` GitHub repo (https://github.com/ace-step/awesome-ace-step) and compile:

1. **ace-step-ui**: What additional features does it add over the default Gradio UI? Specifically: AI Chat Assistant capabilities, chord progression editor, voice recorder integration. How could these inform our skill's design?

2. **ComfyUI Integration**: How do the ComfyUI nodes work? What workflow patterns do they enable that the CLI/API don't? Any novel node chains worth replicating?

3. **VST3/AU Plugin (C++ GGML)**: Architecture details. Can we interact with it programmatically? Does it expose any APIs?

4. **acestep-captioner**: How does the data annotation tool work? 1000+ instrument recognition — could we use this for music analysis features?

5. **Side-Step (LoRA/LoKr toolkit)**: What does it add over the built-in LoRA training? Any simplified workflows?

6. **Cloud deployments**: WaveSpeedAI, Clore.ai, Runware — how do their APIs differ? Are they OpenAI-compatible? Costs?

7. **Majik's Music Studio**: What audio workstation features does it integrate (stem separation, MIDI extraction, mixing)?

### 2B. Recent GitHub Activity (Last 60 Days)

Search the ACE-Step-1.5 GitHub repo for:
1. **Open issues tagged "bug"**: Any known bugs we should work around in our skill?
2. **Recent PRs**: Any upcoming features or breaking changes?
3. **Discussions**: What are users most frequently asking for? What pain points do they report?
4. **Releases/tags**: Any version beyond what's currently installed?

### 2C. API Ecosystem

1. **OpenRouter Integration**: How does the OpenRouter-compatible API work? Can we use it for chat-style music generation?
2. **Are there any community-built Python wrappers** or SDK libraries that simplify ACE-Step API usage?
3. **Webhook/callback support**: Can the API notify when generation is complete instead of polling?

---

## DOMAIN 3: Music Production Workflows with ACE-Step

### 3A. Professional Workflow Patterns

Research how musicians, producers, and content creators are ACTUALLY using ACE-Step in their workflows:

1. **Song Development Pipeline**: What's the typical workflow from idea → finished song?
   - How many iterations do people typically need?
   - What's the typical batch size per iteration?
   - When do they switch from text2music → cover → repaint?

2. **Integration with DAWs**: How are people getting ACE-Step output into:
   - Ableton Live, FL Studio, Logic Pro, Reaper, DaVinci Resolve Fairlight
   - What format/quality settings do they use?
   - Any BPM sync issues?

3. **Post-Processing Chains**: After ACE-Step generates audio, what do people commonly do?
   - Stem separation (Demucs) → individual track processing
   - Mastering chains (EQ, compression, limiting, stereo widening)
   - Vocal isolation → re-recording with human vocals
   - Using generated instrumentals as backing tracks

4. **Content Creator Workflows**:
   - YouTube BGM generation
   - Podcast intro/outro music
   - TikTok/Reels soundtracks
   - Game soundtrack generation
   - Ad/commercial jingles

### 3B. Cover Mode Workflows

1. **Style Transfer Best Practices**: What `audio_cover_strength` values work best for:
   - Subtle style changes (same genre, different vibe)
   - Major genre changes (rock → jazz)
   - Voice-only changes (keep instrumental, change vocal style)

2. **Reference Audio Preparation**: How should reference audio be prepared?
   - Optimal length, format, loudness level
   - Does quality of reference affect output quality?

### 3C. Repaint/Edit Workflows

1. **Selective Editing Patterns**: How are people using repaint mode effectively?
   - Fixing a bad chorus while keeping the rest
   - Changing instruments in a specific section
   - Adding/removing vocals from a section
   - What `repainting_start`/`repainting_end` granularity works?

2. **Multi-Pass Refinement**: Patterns for iteratively improving a song:
   - Generate → Repaint section A → Repaint section B → Cover for final polish
   - How many repaint passes before quality degrades?

---

## DOMAIN 4: LoRA Training Deep Dive

### 4A. Training Best Practices

Research ACE-Step LoRA training from the official tutorial AND community experience:

1. **Dataset Preparation**:
   - Minimum number of songs needed (community consensus)
   - Optimal song length for training data
   - Audio format/quality requirements
   - Annotation requirements (do you need captions for training data?)
   - What diversity in training data produces best results?

2. **LoRA vs LoKr**:
   - When to use each? Speed vs quality tradeoffs
   - LoKr is 5x faster — but is the quality comparable?
   - Community preference and reasoning

3. **Training Hyperparameters**:
   - Optimal rank (r) values for different use cases
   - Learning rate sweet spots
   - Training duration (steps/epochs)
   - Batch size recommendations
   - GPU memory requirements for training

4. **Use Cases**:
   - Voice cloning (capture a specific singer's style)
   - Genre specialization (make the model excel at one genre)
   - Instrument focus (e.g., train on solo piano pieces)
   - Production style (capture a specific producer's sound)

5. **LoRA Stacking/Mixing**: Can multiple LoRAs be combined? If so, how? Any community success stories?

### 4B. Training Infrastructure

1. **Training time estimates** by GPU tier (RTX 3060 → RTX 4090 → A100)
2. **Dataset tools**: What tools do people use to prepare training datasets?
3. **Evaluation methods**: How do you know if your LoRA is good?

---

## DOMAIN 5: Audio Post-Processing Pipeline

### 5A. Mastering Chain for AI-Generated Music

Research the optimal post-processing pipeline for ACE-Step output:

1. **Loudness Normalization Standards**:
   - Spotify: -14 LUFS, -1 dBTP
   - Apple Music: -16 LUFS, -1 dBTP
   - YouTube: -14 LUFS
   - TikTok/Reels: -14 LUFS
   - Podcast: -16 to -18 LUFS
   - What FFmpeg commands achieve these?

2. **AI Audio Enhancement Pipeline** (for improving ACE-Step output):
   - Demucs stem separation → process stems individually → remix
   - DeepFilterNet3 for vocal cleaning
   - AudioSR for upsampling (if applicable to music)
   - EQ curves that compensate for common ACE-Step artifacts
   - De-essing for harsh sibilants in AI vocals

3. **Format Conversion Best Practices**:
   - ACE-Step outputs 48kHz — when/how to convert to 44.1kHz?
   - Optimal MP3 bitrate for different platforms
   - FLAC vs WAV for archival
   - Opus for web delivery

### 5B. Stem Separation for AI Music

1. **Demucs v4 on ACE-Step output**: How well does stem separation work on AI-generated music vs human recordings?
2. **Use cases**: Isolating vocals for remixing, extracting drums for BPM analysis, getting bass line for transcription
3. **Which Demucs model** works best with ACE-Step output? (htdemucs, htdemucs_ft, htdemucs_6s?)

### 5C. Metadata & Tagging

1. **Music metadata standards**: ID3v2.4 tags, what fields should be auto-populated?
2. **Album art generation**: Can we integrate with image generation for cover art?
3. **BPM detection**: After generation, how to verify actual BPM matches requested BPM?
4. **Key detection**: Tools for verifying the musical key of generated output

---

## DOMAIN 6: Competitive Landscape (What We Can Learn)

### 6A. Suno v4.5/v5 (April 2026)

1. **What UX patterns make Suno successful?** (not the model, the interface/workflow)
2. **Suno's prompt format**: How do Suno users write prompts? Are there transferable patterns?
3. **Suno's song structure controls**: How does it handle verse/chorus/bridge differently?
4. **What Suno users complain about** that ACE-Step solves (or could solve)

### 6B. Udio

1. **Udio's editing capabilities**: How does their "remix" feature compare to ACE-Step's repaint/cover?
2. **Udio's audio quality**: In what specific areas does Udio excel that ACE-Step doesn't?

### 6C. Other Competitors

1. **MiniMax Music**: Any unique features worth learning from?
2. **Mureka**: What's their approach to lyrics-to-music?
3. **Stable Audio (Stability AI)**: Current state, any advantages?
4. **Google MusicFX / MusicLM**: Latest capabilities?

### 6D. Feature Gap Analysis

Compile a table:
| Feature | ACE-Step 1.5 | Suno v5 | Udio | MiniMax | Our Skill Can Add |
Show where our skill can bridge gaps through clever orchestration, post-processing, or complementary tools.

---

## DOMAIN 7: Claude Code Skill Architecture Patterns

### 7A. Agent Skills Standard

1. **Search for the "Agent Skills" open standard** documentation. What's the latest spec?
2. **How do the best Claude Code skills handle local AI model integration?** Find examples beyond the user's own skills.
3. **Plugin vs Skill**: When should this be a plugin (with hooks, agents, MCP) vs a standalone skill? What's the tradeoff?

### 7B. Music-Specific UX Patterns

1. **What would a CLI-first music creation experience look like?** Research terminal-based music tools:
   - SoX (Sound eXchange) — CLI patterns for audio
   - FFmpeg audio filters — which are useful for music?
   - `aubio` — CLI beat/pitch detection
   - `essentia` — music information retrieval CLI
   - `librosa` — Python music analysis

2. **Interactive Generation Patterns**:
   - How should the skill handle the "generate → listen → refine" loop?
   - Should it auto-play generated audio? (What terminal audio players work on Linux?)
   - How to present multiple batch results for user selection?

3. **Progress Feedback**:
   - ACE-Step generation takes 2-30 seconds depending on config
   - How should the skill show progress? (polling the API, progress bars, etc.)

### 7C. MCP Server Considerations

1. **Should ACE-Step be wrapped as an MCP server?** Pros/cons for music generation as MCP
2. **Existing music-related MCP servers**: Are there any? What can we learn?

---

## DOMAIN 8: Music Theory Reference for AI Generation

### 8A. Key/Scale Reference

Compile a practical reference table for the skill:
| Key | Mood/Feel | Best Genres | Common Chord Progressions |
Cover all 12 major and 12 minor keys, plus modes (Dorian, Mixolydian, etc.) that ACE-Step supports.

### 8B. BPM Reference by Genre

| Genre | Typical BPM Range | Sweet Spot BPM | Time Signature |
Cover 30+ genres with empirical BPM ranges.

### 8C. Song Structure Templates

Compile standard song structures by genre:
- Pop: Intro (8 bars) → Verse (16) → Pre-Chorus (8) → Chorus (16) → Verse 2 → Chorus → Bridge (8) → Final Chorus → Outro
- Include timing estimates in seconds at various BPMs
- How these map to ACE-Step's structure tags

### 8D. Lyric Density by Genre

| Genre | Words/Minute | Words for 30s | Words for 60s | Words for 120s | Words for 240s |
Based on real music analysis, not theory.

---

## OUTPUT FORMAT REQUIREMENTS

Structure your research output as follows:

```
## Domain N: [Title]
### Finding [N.X]: [Specific Topic]
**Source**: [URL or "Community consensus from Reddit/Discord"]
**Confidence**: [High/Medium/Low]
**Actionable for skill**: [Yes/No/Partially]

[Content in tables, code blocks, or bullet lists — NO prose paragraphs unless explaining nuance]
```

For parameter recipes, use this format:
```python
# Recipe: [Name]
# Source: [where you found this]
# Quality: [community rating if available]
params = GenerationParams(
    caption="[exact tag string]",
    lyrics="[structure template]",
    bpm=120,
    keyscale="C major",
    duration=60,
    inference_steps=8,
    guidance_scale=7.0,
    # ... all relevant params
)
config = GenerationConfig(
    batch_size=2,
    audio_format="flac",
)
```

**CRITICAL**: Prioritize information that is:
1. **Empirically tested** (community-verified, not theoretical)
2. **Specific to ACE-Step 1.5** (not generic music AI advice)
3. **Actionable** (can be directly encoded into a skill's reference docs or scripts)
4. **Current** (2026 data preferred, nothing older than 2025 unless foundational)

---

## KEY SEARCH QUERIES TO RUN

Use these specific searches to find the best information:

### Reddit & Forums
- `site:reddit.com "ace-step" prompt tips`
- `site:reddit.com "ace-step 1.5" best settings`
- `site:reddit.com "ace-step" vs suno`
- `site:reddit.com "ace-step" lora training`
- `site:reddit.com "ace-step" workflow`
- `r/aimusic ace-step`
- `r/StableDiffusion ace-step` (crossover community)

### GitHub
- `github.com/ace-step/ACE-Step-1.5 discussions`
- `github.com/ace-step/awesome-ace-step`
- `ace-step comfyui workflow`
- `ace-step lora training dataset`

### Technical Blogs & Guides
- `"ace-step 1.5" tutorial prompt engineering`
- `"ace-step" best practices music generation 2026`
- `"ace-step" parameter tuning guide`
- `ace-step cover repaint workflow guide`
- `ace-step vs suno v5 comparison 2026`

### Documentation
- Fetch: https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md
- Fetch: https://github.com/ace-step/awesome-ace-step/blob/main/README.md
- Fetch: https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/LoRA_Training_Tutorial.md
- Fetch: https://github.com/ace-step/ACE-Step-1.5/discussions (browse top discussions)
- Fetch: https://ace-step.github.io/ace-step-v1.5.github.io/ (official v1.5 page)

### YouTube (for workflow patterns)
- `ace-step 1.5 tutorial workflow`
- `ace-step music production`
- `ace-step lora training guide`

---

## FINAL NOTE

This research will directly inform the creation of a Claude Code skill with:
- **12+ sub-skills** (generate, cover, repaint, extract, lego, complete, analyze, lora, export, library, compose, enhance)
- **Reference knowledge base** (genre recipes, parameter presets, music theory, prompt templates)
- **Scripts** (API client, dependency checker, audio post-processing, metadata tagging)
- **Safety rules** (VRAM management, disk space checks, batch confirmation)

Every piece of information you find should be evaluated through the lens: "Can this be encoded into a reusable skill component?"

GO DEEP. Be thorough. This is MAX EFFORT research.
