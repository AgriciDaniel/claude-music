---
name: claude-music-web
description: >
  Starts the local claude-music web dashboard: a minimalist browser app for
  generating songs with style buttons, live progress, a waveform player, a
  rated library, downloads, and one-click similar generations. Runs entirely
  on 127.0.0.1 with no cloud calls.
when_to_use: >
  Use when the user asks for the music dashboard, web UI, browser app, or a
  visual way to generate and browse songs.
allowed-tools:
  - Bash
  - Read
---

# claude-music-web: Browser Dashboard

## Start

```bash
bash ~/.claude/skills/claude-music/scripts/music_web.sh
```

The launcher starts a stdlib-only Python server bound to `127.0.0.1` (default
port 8765, auto-increments if taken), prints the URL, and opens the browser.
Report the URL to the user and mention Ctrl-C stops it.

Custom port:

```bash
bash ~/.claude/skills/claude-music/scripts/music_web.sh 9000
```

## What the dashboard does

- One generate box: prompt text plus multi-select genre pills (from
  `references/genre-recipes.md`) and presets.
- Live progress percentage while the engine runs (`--progress` NDJSON events).
- Player with waveform bars animating to the audio.
- Library backed by the configured `output_dir`, with 1-5 star ratings stored
  in `<output_dir>/.claude-music/meta/` sidecars.
- Download, open the output folder, and generate a similar track (same
  prompt/settings, fresh seed).
- Drag and drop your own audio file onto the page to add it to the library,
  then: Audit (ffprobe + loudnorm report with fix suggestions), Optimize
  (two-pass loudness normalization for Spotify/Apple/YouTube/TikTok/podcast),
  or Similar (cover-mode generation from the audio with a Loose/Balanced/
  Faithful strength choice).
- The player waveform is the real silhouette of the track; click it to seek,
  and the played portion fills in brand orange.

## Notes

- Only one generation runs at a time (VRAM); concurrent requests get 409.
- If config.json still has `CHANGE_ME`, the page shows setup instructions;
  run `install.sh` first.
- The server never binds non-loopback addresses; do not expose it manually.
