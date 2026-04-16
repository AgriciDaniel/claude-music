# claude-music

AI-powered music production skill for [Claude Code](https://claude.ai/code), powered by [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5).

Generate full songs, covers, remixes, and more — directly from your terminal.

## Features

- **Text-to-Music** — Generate songs from captions and lyrics (50+ languages)
- **Cover/Style Transfer** — Transform existing songs into new genres
- **Section Editing (Repaint)** — Fix a chorus, change instruments in a section
- **Track Extraction** — Separate vocals, drums, bass (base model)
- **Multi-Track Layering (Lego)** — Add instrument layers (base model)
- **Audio Completion** — Extend and continue existing audio (base model)
- **Songwriting Assistant** — Caption crafting, lyrics formatting, BPM/key selection
- **Audio Analysis** — BPM detection, key estimation, loudness measurement
- **Platform Export** — Spotify, YouTube, TikTok, podcast, CD-ready formats
- **LoRA Training** — Fine-tune on 3-10 songs for custom styles

## Requirements

- [Claude Code](https://claude.ai/code) (CLI, Desktop, or VS Code extension)
- [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5) installed locally
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- NVIDIA GPU with 4GB+ VRAM (8GB+ recommended, 16GB+ for XL models)
- FFmpeg (for audio export and analysis)

## Installation

```bash
# 1. Clone this repo
git clone https://github.com/AgriciDaniel/claude-music.git
cd claude-music

# 2. Install ACE-Step 1.5 (if not already installed)
git clone https://github.com/ace-step/ACE-Step-1.5.git ~/Desktop/Local-AI-Models/ACE-Step-1.5
cd ~/Desktop/Local-AI-Models/ACE-Step-1.5
uv sync
uv run acestep-download  # Download model checkpoints

# 3. Install the Claude Code skill
cd /path/to/claude-music
bash install.sh

# 4. Verify installation
bash ~/.claude/skills/claude-music/scripts/setup.sh
```

## Configuration

Edit `skills/claude-music/config.json` to set your ACE-Step path:

```json
{
  "ace_step_dir": "/path/to/your/ACE-Step-1.5",
  "output_dir": "~/Music/claude-music-output"
}
```

## Usage

In Claude Code, use `/music` or natural language:

```
/music generate --caption "upbeat pop, female vocal" --duration 60
/music cover --src-audio song.mp3 --caption "jazz version"
/music repaint --src-audio song.mp3 --start 30 --end 60
/music compose    # Songwriting assistance
/music analyze    # BPM, key, loudness
/music export     # Platform-optimized export
/music random     # Quick random generation
```

## Quality Presets

| Preset | Speed | Use for |
|--------|-------|---------|
| `--quality draft` | ~15s | Quick exploration (4 variants) |
| `--quality standard` | ~15s | Default (2 variants) |
| `--quality high` | ~25s | Better lyrics/structure (LM thinking) |
| `--quality max` | ~3-5min | Highest quality (base model, 65 steps) |

## Architecture

```
claude-music/
├── install.sh                         # Symlinks skills to ~/.claude/skills/
├── uninstall.sh                       # Removes symlinks
├── skills/
│   ├── claude-music/                  # Main orchestrator
│   │   ├── SKILL.md                   # Routing, safety rules, VRAM management
│   │   ├── config.json                # ACE-Step paths + defaults
│   │   ├── scripts/
│   │   │   ├── music_engine.py        # Core Python engine (6 task types)
│   │   │   ├── music_engine.sh        # Bash wrapper (env + uv run)
│   │   │   ├── music_export.sh        # Platform FFmpeg exports
│   │   │   ├── detect_gpu.sh          # GPU detection -> JSON
│   │   │   ├── preflight.sh           # Safety checks -> JSON
│   │   │   ├── check_deps.sh          # Dependency verification -> JSON
│   │   │   └── setup.sh               # Installation verification
│   │   └── references/                # 7 on-demand knowledge docs
│   ├── claude-music-generate/         # Text-to-music sub-skill
│   ├── claude-music-cover/            # Cover/style transfer sub-skill
│   ├── claude-music-repaint/          # Section editing sub-skill
│   ├── claude-music-compose/          # Songwriting assistant
│   ├── claude-music-export/           # Platform export sub-skill
│   ├── claude-music-analyze/          # Audio analysis sub-skill
│   ├── claude-music-enhance/          # Post-processing sub-skill
│   ├── claude-music-random/           # Quick random generation
│   ├── claude-music-library/          # Output management
│   └── claude-music-lora/             # LoRA training sub-skill
```

## How It Works

The skill wraps ACE-Step 1.5's Python API directly — no server required. Each command:

1. Loads the DiT model (turbo: ~15s cold start, base: ~20s)
2. Optionally loads the 5Hz LM for thinking mode
3. Generates audio via the diffusion pipeline
4. Outputs JSON with file paths, seeds, and timing
5. Files saved to `~/Music/claude-music-output/`

## GPU Requirements

| Configuration | VRAM | Notes |
|---------------|------|-------|
| Turbo (default) | ~8GB | Fast, good quality |
| Turbo + 1.7B LM | ~14GB | Better lyrics adherence |
| XL Turbo | ~14-16GB | Maximum quality DiT |

## Uninstall

```bash
bash uninstall.sh
```

This removes symlinks only. Your repo, generated music, and ACE-Step installation are untouched.

## License

MIT

## Credits

- [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5) by ACE Studio / Timedomain + StepFun
- Built for [Claude Code](https://claude.ai/code) by Anthropic
