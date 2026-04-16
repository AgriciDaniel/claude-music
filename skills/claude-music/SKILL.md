---
name: claude-music
description: >
  AI-powered music production suite using ACE-Step 1.5 via direct Python API.
  Song generation, cover/style transfer, section editing (repaint), track extraction,
  multi-track layering (lego), audio completion, songwriting assistance, audio analysis,
  platform export, and LoRA training. Supports 50+ languages, 10-minute compositions,
  48kHz stereo output. GPU-accelerated on RTX 5070 Ti 16GB.
  Use when user says "music", "song", "generate music", "make a song", "create music",
  "cover song", "remix", "repaint", "edit song", "lyrics", "compose", "songwriting",
  "BPM", "audio export", "music analysis", "stem separation", "LoRA training",
  "ACE-Step", or "/music".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# claude-music — AI Music Production for Claude Code

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/music` | Interactive mode — describe what you want |
| `/music generate` | Text/lyrics to full song (text2music) |
| `/music cover` | Style transfer from reference audio |
| `/music repaint` | Edit a specific section of a song |
| `/music extract` | Separate tracks/stems (base model only) |
| `/music lego` | Add instrument layer (base model only) |
| `/music complete` | Continue/extend audio (base model only) |
| `/music compose` | Songwriting: craft caption + lyrics + params |
| `/music analyze` | BPM, key, loudness, duration analysis |
| `/music export` | Platform-optimized export (Spotify, YouTube, etc.) |
| `/music enhance` | Post-processing: normalize, denoise, stem separate |
| `/music random` | Quick random generation with smart defaults |
| `/music library` | Browse and manage generated music |
| `/music lora` | LoRA/LoKr fine-tuning management |
| `/music setup` | Verify installation and dependencies |

## Orchestration Logic

### Command Routing

When the user provides a specific command, load the matching sub-skill:

- `/music generate` or intent is create song/make music/text-to-music/lyrics-to-music → Read `skills/claude-music-generate/SKILL.md`
- `/music cover` or intent is cover/style transfer/remake/version of → Read `skills/claude-music-cover/SKILL.md`
- `/music repaint` or intent is edit section/fix chorus/change part/modify section → Read `skills/claude-music-repaint/SKILL.md`
- `/music compose` or intent is write lyrics/craft caption/plan song/songwriting → Read `skills/claude-music-compose/SKILL.md`
- `/music analyze` or intent is BPM/key detection/loudness/audio info → Read `skills/claude-music-analyze/SKILL.md`
- `/music export` or intent is export for Spotify/YouTube/platform/format conversion → Read `skills/claude-music-export/SKILL.md`
- `/music enhance` or intent is normalize/denoise/stem separate/master → Read `skills/claude-music-enhance/SKILL.md`
- `/music random` or intent is quick generation/surprise me/random song → Read `skills/claude-music-random/SKILL.md`
- `/music library` or intent is list songs/browse output/manage music → Read `skills/claude-music-library/SKILL.md`
- `/music lora` or intent is train/fine-tune/LoRA/custom style → Read `skills/claude-music-lora/SKILL.md`
- `/music setup` → Run `bash ~/.claude/skills/claude-music/scripts/setup.sh`

### Interactive Mode

When user says `/music` without arguments or describes a task in natural language:
1. Run `bash ~/.claude/skills/claude-music/scripts/check_deps.sh` to verify tools
2. Run `bash ~/.claude/skills/claude-music/scripts/detect_gpu.sh` for GPU info
3. Identify intent from the user's description
4. Route to the appropriate sub-skill
5. If ambiguous, ask the user to clarify

### Multi-Step Pipelines

For complex requests spanning multiple sub-skills (e.g., "compose lyrics, generate a song, then export for Spotify"):
1. Compose lyrics/caption with `/music compose`
2. Generate with `/music generate` using composed output
3. Export with `/music export`
4. Clean up temp files

### Generate-Listen-Iterate Loop

After any generation:
1. Present output file paths and metadata (seed, duration, format)
2. Suggest playback: `ffplay -nodisp -autoexit "<path>"`
3. Ask if user wants to:
   - **Re-generate** with different seed (same params)
   - **Refine** params (adjust caption, BPM, quality)
   - **Repaint** a specific section
   - **Cover** to change style while keeping structure
   - **Export** for a platform

## Safety Rules — MANDATORY

1. **Run preflight before writes**: `bash ~/.claude/skills/claude-music/scripts/preflight.sh "$INPUT" "$OUTPUT"`
2. **Never overwrite source files** — all operations produce new files
3. **Check VRAM before GPU operations**: `bash ~/.claude/skills/claude-music/scripts/detect_gpu.sh`
4. **Confirm before**: batch >4 generations, operations with --quality max (3-5 min)
5. **Auto-execute without confirmation**: single generation (draft/standard), analysis, format conversion, setup
6. **Temp files**: `/tmp/claude-music/` with cleanup trap
7. **Output directory**: `~/Music/claude-music-output/` (auto-created)

## ACE-Step Configuration

- **Installation**: Set `ace_step_dir` in `config.json` (default: see config.json)
- **Invocation**: `bash ~/.claude/skills/claude-music/scripts/music_engine.sh <command> [args]`
- **Config**: `~/.claude/skills/claude-music/config.json`
- **Output**: `~/Music/claude-music-output/`

## Quality Presets

| Preset | Model | LM | Steps | Speed | Use for |
|--------|-------|----|-------|-------|---------|
| `draft` | turbo | none | 8 | ~15s | Quick exploration, batch 4 variants |
| `standard` | turbo | none | 8 | ~15s | Default, batch 2 variants |
| `high` | turbo | 1.7B LM | 8 | ~25s | Better lyrics/structure, thinking mode |
| `max` | base | 1.7B LM | 65 | ~3-5min | Highest quality, single output |

## VRAM Management (RTX 5070 Ti — 16GB)

| Configuration | VRAM | Offload | Notes |
|---------------|------|---------|-------|
| Turbo (no LM) | ~8GB | CPU offload | Default, fast generation |
| Turbo + 0.6B LM | ~10GB | CPU + DiT offload | Thinking mode, lightweight |
| Turbo + 1.7B LM | ~14GB | CPU + DiT offload | Full thinking, tight on VRAM |
| XL Turbo | ~14-16GB | Full offload | Maximum quality DiT, no LM room |

**Rule**: Never run two heavy models simultaneously. The music_engine.py handles VRAM automatically.

## Script Invocation

All ACE-Step operations go through the bash wrapper:
```bash
bash ~/.claude/skills/claude-music/scripts/music_engine.sh <subcommand> [args]
```

The wrapper handles: path setup, environment variables, VRAM pre-check, `uv run` invocation.

**Output is always JSON to stdout.** Parse with `jq` for specific fields.

## Reference Files (Load On-Demand)

| Reference | When to load |
|-----------|-------------|
| `references/prompt-guide.md` | When crafting captions or lyrics |
| `references/parameters.md` | When user asks about specific params or tuning |
| `references/genre-recipes.md` | When targeting a specific genre |
| `references/music-theory.md` | When discussing keys, scales, BPM, song structure |
| `references/post-processing.md` | When exporting, mastering, or enhancing |
| `references/song-structures.md` | When planning song layout |
| `references/lora-training.md` | When training custom LoRA models |

## Sub-Skills

| Skill | Type | Description |
|-------|------|-------------|
| `claude-music-generate` | Generation | Core text2music via ACE-Step Python API |
| `claude-music-cover` | Generation | Style transfer from reference audio |
| `claude-music-repaint` | Editing | Selective section regeneration |
| `claude-music-compose` | Reference | Songwriting guide (caption, lyrics, params) |
| `claude-music-analyze` | Analysis | BPM, key, loudness, metadata via ffprobe/librosa |
| `claude-music-export` | Processing | Platform-specific audio export via FFmpeg |
| `claude-music-enhance` | Processing | Loudness normalization, denoise, stems (reuses video skills) |
| `claude-music-random` | Generation | Quick random generation with genre presets |
| `claude-music-library` | Management | Browse/search generated music output |
| `claude-music-lora` | Training | LoRA/LoKr fine-tuning wrapper |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/music_engine.py` | Core ACE-Step Python API wrapper (all 6 task types) |
| `scripts/music_engine.sh` | Bash wrapper (env, VRAM, uv run) |
| `scripts/detect_gpu.sh` | GPU detection + tier recommendation → JSON |
| `scripts/preflight.sh` | Safety checks for audio files → JSON |
| `scripts/check_deps.sh` | Dependency verification → JSON |
| `scripts/setup.sh` | Installation verification |
| `scripts/music_analyze.py` | Audio analysis (BPM, key, loudness) |
| `scripts/music_export.sh` | FFmpeg platform export commands |
