# claude-music

AI music production skill for Claude Code, powered by ACE-Step 1.5.

## Project Structure

```
claude-music/
├── install.sh              # Interactive installer (handles ACE-Step + models + config)
├── uninstall.sh            # Removes symlinks only
├── skills/
│   ├── claude-music/       # Main orchestrator
│   │   ├── SKILL.md        # Command routing, safety rules, VRAM tiers
│   │   ├── config.json     # ACE-Step path + generation defaults
│   │   ├── scripts/        # 7 executable scripts (bash + python)
│   │   └── references/     # 7 on-demand knowledge docs
│   ├── claude-music-generate/   # text2music
│   ├── claude-music-cover/      # style transfer
│   ├── claude-music-repaint/    # section editing
│   ├── claude-music-compose/    # songwriting guide
│   ├── claude-music-export/     # platform export
│   ├── claude-music-analyze/    # BPM/key/loudness
│   ├── claude-music-enhance/    # post-processing
│   ├── claude-music-random/     # quick random gen
│   ├── claude-music-library/    # output management
│   └── claude-music-lora/       # LoRA training
```

## How It Works

- **Direct Python API** — Scripts import `acestep` directly via `sys.path.insert`, invoked with `uv run` from the ACE-Step directory. No REST API server needed.
- **Symlink installation** — `install.sh` creates symlinks from `~/.claude/skills/claude-music*` to this repo's `skills/` directory. Edit here, changes are live.
- **JSON output** — All scripts output structured JSON to stdout. Progress/debug goes to stderr. Claude parses the JSON for file paths, seeds, and timing.
- **Config-driven** — `config.json` is the single source of truth for the ACE-Step path. All scripts read from it; no hardcoded paths in code.

## Key Files

| File | Purpose |
|------|---------|
| `skills/claude-music/scripts/music_engine.py` | Core engine — all 6 ACE-Step task types via argparse subcommands |
| `skills/claude-music/scripts/music_engine.sh` | Bash wrapper — env setup, VRAM check, `uv run` invocation |
| `skills/claude-music/scripts/music_export.sh` | FFmpeg platform export (Spotify/YouTube/TikTok/podcast/CD) |
| `skills/claude-music/config.json` | ACE-Step path + generation defaults |
| `skills/claude-music/SKILL.md` | Orchestrator — routes `/music X` to sub-skills |

## Development

### Adding a new sub-skill

1. Create `skills/claude-music-<name>/SKILL.md` with proper frontmatter
2. Add routing rule to `skills/claude-music/SKILL.md` (Command Routing section)
3. Add to Quick Reference table in orchestrator
4. Run `bash install.sh` to create symlink

### Adding a new reference doc

1. Create `skills/claude-music/references/<name>.md`
2. Add to Reference Files table in orchestrator SKILL.md

### Modifying the Python engine

- All generation goes through `music_engine.py` — 6 subcommands: generate, cover, repaint, extract, lego, complete
- Quality presets are in `QUALITY_PRESETS` dict at top of file
- ACE-Step params map to `GenerationParams` dataclass — see `references/parameters.md`
- Cover mode uses `src_audio` + `cover_noise_strength` (NOT `reference_audio` + `audio_cover_strength`)

### Testing

```bash
# Syntax check all scripts
bash -n skills/claude-music/scripts/*.sh install.sh uninstall.sh
python3 -c "import ast; ast.parse(open('skills/claude-music/scripts/music_engine.py').read())"

# Check deps
bash skills/claude-music/scripts/check_deps.sh | python3 -m json.tool

# GPU detection
bash skills/claude-music/scripts/detect_gpu.sh | python3 -m json.tool

# Generate test (30s draft)
bash skills/claude-music/scripts/music_engine.sh --quality draft generate \
  --caption "test pop song" --instrumental --duration 30
```

## Security Notes

- No `eval()` in any script — replaced with array execution
- No hardcoded personal paths — everything reads from `config.json`
- `ffmpeg -n` (no-overwrite) on all export commands
- Basename sanitization on user-provided filenames
- Caption capped at 512 chars, lyrics at 4096 chars (ACE-Step limits)
- `.claude/` directory gitignored (user-specific settings)
