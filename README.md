# claude-music

AI music production skill for [Claude Code](https://claude.ai/code), powered by [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5).

Generate full songs, covers, remixes, and more — just by describing what you want.

## Quick Start (5 minutes)

**You only need to run ONE command.** The installer handles everything else.

### Step 1: Download this skill

Open a terminal and paste:

```bash
git clone https://github.com/AgriciDaniel/claude-music.git
cd claude-music
```

### Step 2: Run the installer

```bash
bash install.sh
```

The installer will:
- Check your system (GPU, Python, FFmpeg)
- Install ACE-Step 1.5 if you don't have it (asks first)
- Download the AI models (~5GB, asks first)
- Configure everything automatically
- Link the skill to Claude Code

**That's it.** No config files to edit. No terminal commands to memorize.

### Step 3: Make music

Open Claude Code (CLI, Desktop app, or VS Code) and say:

> "Generate a chill lo-fi beat, 60 seconds"

Or:

> "Make me a pop song about summer with female vocals"

Or use the command directly:

```
/music generate --caption "upbeat pop, female vocal, catchy" --duration 60
```

## What You Can Do

| Say this... | What happens |
|-------------|-------------|
| "Make me a song about..." | Generates a full song with vocals |
| "Create an instrumental jazz piece" | Instrumental generation |
| "Make a rock cover of this song" | Style transfer from reference audio |
| "Fix the chorus, make it more energetic" | Edits just that section |
| "Export for Spotify" | Loudness-optimized, platform-ready file |
| "Surprise me with something random" | Random genre, instant generation |

## Requirements

- **Claude Code** — [Get it here](https://claude.ai/code) (CLI, Desktop, or VS Code extension)
- **NVIDIA GPU** — 4GB+ VRAM minimum, 8GB+ recommended
  - No GPU? It works on CPU too, just much slower
- **Storage** — ~10GB free (for ACE-Step + AI models)

The installer handles everything else (Python, FFmpeg, uv, ACE-Step).

## Features

- **10 Sub-Skills**: generate, cover, repaint, compose, export, analyze, enhance, random, library, lora
- **50+ Languages**: English, Spanish, Chinese, Japanese, Korean, and more
- **Quality Presets**: draft (~15s) to max (~5min) — pick your speed/quality tradeoff
- **Platform Export**: Spotify, YouTube, TikTok, podcast, CD — one command each
- **LoRA Training**: Fine-tune on 3-10 songs for your own custom style
- **30+ Genre Recipes**: Built-in knowledge of optimal settings per genre
- **Safety**: No overwrites, VRAM management, disk space checks

## Quality Presets

| Preset | Speed | Best for |
|--------|-------|----------|
| `--quality draft` | ~15s | Quick ideas, exploring (4 variants) |
| `--quality standard` | ~15s | Default, everyday use (2 variants) |
| `--quality high` | ~25s | Better lyrics/structure |
| `--quality max` | ~3-5min | Highest quality possible |

## Commands Reference

```
/music generate   — Create music from text + lyrics
/music cover      — Remake a song in a different style
/music repaint    — Edit a section of a song
/music compose    — Songwriting help (lyrics, caption, BPM)
/music export     — Export for Spotify/YouTube/TikTok/etc
/music analyze    — Check BPM, key, loudness
/music enhance    — Normalize, denoise, separate stems
/music random     — Random generation (surprise me!)
/music library    — Browse your generated music
/music lora       — Train custom styles
/music setup      — Check if everything works
```

## How It Works

1. You describe what you want (or use `/music generate`)
2. Claude crafts the right caption, lyrics, and parameters
3. ACE-Step 1.5 generates the audio locally on your GPU
4. You listen, iterate, and export

No cloud API. No subscription. Everything runs on your machine.

## GPU Requirements

| Setup | VRAM | Speed |
|-------|------|-------|
| Turbo (default) | ~8GB | ~15 seconds |
| Turbo + Thinking | ~14GB | ~25 seconds |
| XL (best quality) | ~16GB | ~30 seconds |

## Uninstall

```bash
cd claude-music
bash uninstall.sh
```

Removes skill links only. Your generated music and ACE-Step are untouched.

## Architecture

<details>
<summary>Click to expand (for developers)</summary>

```
claude-music/
├── install.sh              # Interactive installer (handles everything)
├── uninstall.sh            # Clean removal
├── skills/
│   ├── claude-music/       # Main orchestrator
│   │   ├── SKILL.md        # Routing, safety, VRAM management
│   │   ├── config.json     # Auto-configured by installer
│   │   ├── scripts/        # 7 executable scripts
│   │   └── references/     # 7 on-demand knowledge docs
│   └── claude-music-*/     # 10 sub-skill directories
```

The skill wraps ACE-Step 1.5's Python API directly — no server needed.
Scripts output JSON for Claude to parse. Symlinks connect the repo to `~/.claude/skills/`.

</details>

## License

MIT

## Credits

- [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5) by ACE Studio / Timedomain + StepFun
- Built for [Claude Code](https://claude.ai/code) by Anthropic
