---
name: claude-music-analyze
description: >
  Analyzes audio files for BPM, musical key, loudness (LUFS), duration, format,
  and quality metrics. Uses ffprobe for metadata and FFmpeg for loudness measurement.
when_to_use: >
  Use when the user asks to analyze, inspect, or measure an audio file — BPM,
  key, loudness, LUFS, duration, codec, or general audio info.
allowed-tools:
  - Bash
  - Read
---

# claude-music-analyze — Audio Analysis

## Quick Analysis (ffprobe)

```bash
# Full metadata
ffprobe -v quiet -print_format json -show_format -show_streams input.flac

# Duration only
ffprobe -v quiet -show_entries format=duration -of csv=p=0 input.flac

# Sample rate, channels, codec
ffprobe -v quiet -show_entries stream=sample_rate,channels,codec_name -of csv=p=0 input.flac
```

## Loudness Measurement (LUFS)

```bash
ffmpeg -i input.flac -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | \
  grep -A 20 '"input_'
```

Key fields in output:
- `input_i`: Integrated loudness (LUFS)
- `input_tp`: True peak (dBTP)
- `input_lra`: Loudness range (LU)

## BPM Detection

Using ffmpeg's `ebur128` for rhythm analysis, or for accurate BPM:
```bash
# If librosa is available in ~/.video-skill/ venv:
source ~/.video-skill/bin/activate
python3 -c "
import librosa
y, sr = librosa.load('input.flac', sr=None)
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
print(f'BPM: {tempo[0]:.1f}' if hasattr(tempo, '__len__') else f'BPM: {tempo:.1f}')
"
```

## Key Detection

```bash
source ~/.video-skill/bin/activate
python3 -c "
import librosa
import numpy as np
y, sr = librosa.load('input.flac', sr=None)
chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
key_idx = np.argmax(np.mean(chroma, axis=1))
print(f'Estimated key: {key_names[key_idx]}')
"
```

## Comprehensive Report

Combine all analyses into a single report:
1. Run ffprobe for format/codec/duration
2. Run loudnorm for LUFS measurement
3. Run librosa for BPM + key (if available)
4. Present as structured summary
