# Audio Post-Processing Reference

## Platform Loudness Standards

| Platform | Integrated LUFS | True Peak | LRA | Notes |
|----------|----------------|-----------|-----|-------|
| Spotify | -14 LUFS | -1 dBTP | 7-15 LU | Auto-normalized |
| Apple Music | -16 LUFS | -1 dBTP | — | Sound Check |
| YouTube | -14 LUFS | -1 dBTP | — | Auto-normalized |
| TikTok/Reels | -14 LUFS | -1 dBTP | — | |
| Podcast | -16 to -18 LUFS | -1 dBTP | — | Mono recommended |
| CD | ~-9 to -12 RMS | 0 dBTP | — | No standard |
| Radio | -10 to -14 LUFS | -1 dBTP | — | Heavily compressed |

## FFmpeg Loudness Commands

### Measure Loudness
```bash
ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | grep -A20 '"input_'
```

### Two-Pass Normalization (Best Quality)
```bash
# Pass 1: Measure
STATS=$(ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1)

# Extract values (parse JSON output)
# Pass 2: Apply with measured values
ffmpeg -i input.flac -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=<val>:measured_TP=<val>:measured_LRA=<val>:measured_thresh=<val>:offset=<val>:linear=true" -c:a flac output.flac
```

### Single-Pass (Quick)
```bash
ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11 -c:a flac output.flac
```

## Format Conversion

| From → To | Command | Use Case |
|-----------|---------|----------|
| FLAC → MP3 320k | `ffmpeg -i in.flac -c:a libmp3lame -b:a 320k out.mp3` | Distribution |
| FLAC → AAC 256k | `ffmpeg -i in.flac -c:a aac -b:a 256k out.m4a` | Apple/TikTok |
| FLAC → Opus 128k | `ffmpeg -i in.flac -c:a libopus -b:a 128k out.opus` | Web |
| WAV → FLAC | `ffmpeg -i in.wav -c:a flac out.flac` | Lossless compress |
| 48kHz → 44.1kHz | `ffmpeg -i in.flac -ar 44100 out.flac` | CD standard |
| Stereo → Mono | `ffmpeg -i in.flac -ac 1 out.flac` | Podcast |

## Metadata Tagging
```bash
ffmpeg -i input.flac \
  -metadata title="Song Title" \
  -metadata artist="Artist Name" \
  -metadata album="Album Name" \
  -metadata date="2026" \
  -metadata genre="Pop" \
  -metadata comment="Generated with ACE-Step 1.5 via claude-music" \
  -c:a copy output.flac
```

## AI Enhancement Pipeline (Reuses Video Skill)

1. **Stem Separate** (Demucs): `source ~/.video-skill/bin/activate && python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py separate input.flac`
2. **Denoise Vocals** (DeepFilterNet3): `python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py denoise vocals.wav`
3. **Remix**: Combine processed stems back with FFmpeg amerge/amix
4. **Normalize**: Two-pass loudnorm to target platform LUFS
5. **Export**: Convert to target format with metadata

## Scripts used here

- `scripts/music_export.sh` — implements the FFmpeg loudnorm + format conversion commands above. Supports targets: spotify, apple, youtube, tiktok, podcast, cd, radio, mono-podcast.
- `scripts/music_engine.sh extract` — stem separation via ACE-Step's `extract` task_type (alternative to Demucs).

## Sources

- **Platform loudness targets**: Spotify (artists.spotify.com/help/article/loudness-normalization), Apple Sound Check specification, YouTube Loudness Normalization documentation, AES TD1006 broadcast spec for radio.
- **FFmpeg loudnorm filter**: `ffmpeg -h filter=loudnorm` + EBU R128 reference (tech.ebu.ch/docs/r/r128.pdf).
- **AI enhancement path**: cross-skill integration with `~/.claude/skills/claude-video/scripts/audio_enhance.py` (sibling skill); Demucs (github.com/facebookresearch/demucs) for stem separation; DeepFilterNet3 (github.com/Rikorose/DeepFilterNet) for vocal denoising.

**Gap (Theme 6 of research plan)**: LANDR/Ozone-style AI mastering integration pending user access; `references/mastering.md` will ship a ≥4-preset library once Theme 6 completes.
