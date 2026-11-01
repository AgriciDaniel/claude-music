---
name: claude-music-enhance
description: >
  Post-processing for generated music. Default path is FFmpeg loudness
  normalization (fast, CPU-only). Escape hatches: AI vocal denoise for
  artifacts, stem separation for surgical edits. Both escape-hatch paths
  reuse tooling from the claude-video skill.
when_to_use: >
  Use when the user says enhance, normalize, denoise, master, polish,
  loudness, EQ, equalize, improve quality, stem separation, split vocals,
  or wants to clean AI artifacts or their own recording.
allowed-tools:
  - Bash
  - Read
---

# claude-music-enhance — Audio Post-Processing

## Default path: loudness normalization (recommended first)

Loudness-normalize to the platform target in one ffmpeg call. This is the
right answer 90% of the time — the generated audio is already clean; it just
needs the level right.

```bash
# Two-pass loudnorm to -14 LUFS (Spotify/YouTube/Apple/TikTok all target this).
bash ~/.claude/skills/claude-music/scripts/music_export.sh spotify input.flac output.flac
```

See `references/post-processing.md` for the full platform × LUFS table and
the measure-then-apply two-pass recipe if you need manual control.

## Recorded / low-quality source (user's own recordings)

The default path assumes clean ACE-Step output. A user recording (voice
memo, phone, rehearsal room) usually needs tone work before loudness.

**1. Check the source first** — sample rate caps the recoverable top end:

```bash
ffprobe -v error -show_entries stream=codec_name,sample_rate,channels,bit_rate -of json input.m4a
```

Below 22 kHz (8/16 kHz phone or memo audio), everything above half the
sample rate was never recorded. EQ cannot restore it — tell the user before
processing so expectations match the result.

**2. EQ + compress, then loudnorm** — never overwrite the source:

```bash
ffmpeg -n -i input.m4a -af "highpass=f=70,\
equalizer=f=250:t=q:w=1:g=-3,equalizer=f=500:t=q:w=1.2:g=-1.5,\
equalizer=f=1800:t=q:w=1:g=1,equalizer=f=3000:t=q:w=0.9:g=1.5,\
acompressor=threshold=-20dB:ratio=2.5:attack=10:release=150,\
aresample=48000" -c:a pcm_s16le eq.wav
```

Then run the two-pass loudnorm from `references/post-processing.md` on `eq.wav`.

| Filter | Fixes | If the user says… |
|---|---|---|
| `highpass` 70 Hz | Rumble, handling noise | "boomy", "thumping" |
| −3 dB @ 250 Hz | Low-mid mud (often the loudest band in rooms) | "muddy", "muffled" |
| +1–1.5 dB @ 1.8–3 kHz | Clarity / presence | "dull", "far away" |

Start gentle: on a band-limited source, big presence boosts (+4 dB) plus
synthetic high-harmonic excitation read as harsh. Users have asked for less.

**3. Lossy output needs −1.5 dBTP, not −1.** AAC/MP3 encoding overshoots
the WAV's true peak by ~0.3 dB; a −1.0 dBTP master measured −0.7 dBTP as
256k AAC. Use `TP=-1.5` when the final file is lossy, and re-measure the
encoded file, not the WAV.

**No ffmpeg?** On Intel Macs with older macOS, `brew install ffmpeg` builds
every dependency from source (an hour or more; the build dies if its
terminal closes). Meanwhile, macOS `afconvert` decodes and encodes
(`afconvert -f WAVE -d LEI16 in.m4a out.wav`,
`afconvert -f m4af -d aac -b 256000 in.wav out.m4a`), but loudness numbers
need ffmpeg's `loudnorm` to be trusted.

## Escape hatch 1 — AI vocal denoise (only if audible artifacts)

Use only when you hear artifacts in vocals (hissing, AI mush, robot tones).
FFmpeg normalization won't help; you need DeepFilterNet3.

```bash
source ~/.video-skill/bin/activate
python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py denoise \
  input.flac --output output_clean.flac
```

Requires `claude-video` skill + DeepFilterNet3 weights. <1 GB VRAM.

## Escape hatch 2 — stem separation (only if you need surgical edits)

Use only when you need to fix vocals/drums/bass/other separately, then remix.
Not needed for normal enhancement.

```bash
source ~/.video-skill/bin/activate
python3 ~/.claude/skills/claude-video/scripts/audio_enhance.py separate \
  input.flac --model htdemucs_ft --output-dir ./stems/
```

Produces `vocals.wav`, `drums.wav`, `bass.wav`, `other.wav`. ~7 GB VRAM.

## Decision tree

```
Is it the user's own recording (not ACE-Step output)?
    → recorded-source path (check source → EQ/compress → loudnorm)

Is the generated audio too quiet or too loud?
    → use the default path (loudnorm)

Do you hear specific vocal artifacts?
    → escape hatch 1 (denoise) THEN default path (loudnorm)

Do you need to fix one stem (e.g., reduce drums, retune vocal) before final mix?
    → escape hatch 2 (separate) → edit stem → remix → default path (loudnorm)
```

## Format conversion

For platform-specific export (codec/bitrate/sample-rate), use
`claude-music-export` — it wraps `music_export.sh` with the right flags per
target (Spotify FLAC, YouTube MP3 320k, TikTok M4A 256k, etc.).

## Scripts used here

- `scripts/music_export.sh` — default loudnorm + format conversion path.
- `~/.claude/skills/claude-video/scripts/audio_enhance.py` — AI denoise and
  stem separation (external skill; must be installed separately).
