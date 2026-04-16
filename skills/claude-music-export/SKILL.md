---
name: claude-music-export
description: >
  Exports music for specific platforms with optimal format, loudness, and metadata.
  Supports Spotify, Apple Music, YouTube, TikTok, podcast, CD, streaming, and archive
  formats. Uses FFmpeg for loudness normalization, format conversion, and metadata tagging.
when_to_use: >
  Use when the user asks to export, convert format, prepare for a specific platform
  (Spotify, YouTube, TikTok, podcast, CD), normalize loudness, or tag audio metadata.
allowed-tools:
  - Bash
  - Read
---

# claude-music-export — Platform Export

## Platform Presets

### Spotify / Apple Music / Streaming
```bash
ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11:print_format=summary \
  -ar 44100 -sample_fmt s16 -c:a flac output_spotify.flac
```

### YouTube
```bash
ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11 \
  -c:a libmp3lame -b:a 320k -ar 48000 output_youtube.mp3
```

### TikTok / Instagram Reels
```bash
ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11 \
  -c:a aac -b:a 256k -ar 44100 output_tiktok.m4a
```

### Podcast
```bash
ffmpeg -i input.flac -af loudnorm=I=-16:TP=-1:LRA=11 \
  -c:a libmp3lame -b:a 192k -ar 44100 -ac 1 output_podcast.mp3
```

### CD Quality
```bash
ffmpeg -i input.flac -ar 44100 -sample_fmt s16 -c:a pcm_s16le output_cd.wav
```

### Archive (Lossless)
```bash
ffmpeg -i input.flac -c:a flac -compression_level 8 output_archive.flac
```

### Web (Small file)
```bash
ffmpeg -i input.flac -c:a libopus -b:a 128k output_web.opus
```

## Loudness Targets

| Platform | LUFS | True Peak | Notes |
|----------|------|-----------|-------|
| Spotify | -14 | -1 dBTP | Auto-normalized on ingest |
| Apple Music | -16 | -1 dBTP | Sound Check normalization |
| YouTube | -14 | -1 dBTP | Loudness normalized |
| TikTok | -14 | -1 dBTP | |
| Podcast | -16 to -18 | -1 dBTP | Mono recommended |
| CD | ~-9 to -12 | 0 dBTP | No normalization standard |

## Metadata Tagging

```bash
ffmpeg -i input.flac \
  -metadata title="Song Title" \
  -metadata artist="Artist Name" \
  -metadata album="Album Name" \
  -metadata date="2026" \
  -metadata genre="Pop" \
  -metadata comment="Generated with ACE-Step 1.5" \
  -c:a copy output_tagged.flac
```

## Batch Export

For exporting to multiple platforms at once, run commands sequentially:
```bash
# Export for all major platforms
for PLATFORM in spotify youtube tiktok podcast; do
  bash ~/.claude/skills/claude-music/scripts/music_export.sh "$PLATFORM" input.flac
done
```
