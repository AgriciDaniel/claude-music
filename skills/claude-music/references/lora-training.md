# LoRA/LoKr Training Guide for ACE-Step 1.5

## Overview

Train custom LoRA adapters to capture specific vocal styles, genres, instruments, or production aesthetics from a small dataset of 3-10 reference songs.

## Dataset Preparation

### Requirements
- **Minimum songs**: 3 (better: 5-10)
- **Format**: WAV or FLAC preferred (MP3 OK but lossy)
- **Length per song**: 30-300 seconds
- **Quality**: High quality, no noise/clipping
- **Consistency**: All songs should share the target style characteristic

### Dataset Layout
```
~/Music/lora-datasets/my_style/
├── song_01.wav
├── song_02.wav
├── song_03.wav
├── song_04.wav
└── song_05.wav
```

### Tips
- For **voice cloning**: Use 5+ songs from same singer, same genre
- For **genre specialization**: Use 5-10 representative songs
- For **instrument focus**: Solo instrument recordings work best
- For **production style**: Same producer/mixing engineer tracks

## LoRA vs LoKr

| Aspect | LoRA | LoKr |
|--------|------|------|
| Method | Low-Rank Adaptation | Kronecker product decomposition |
| Training time (RTX 5070 Ti) | ~1 hour | ~12 minutes |
| Quality | Higher fidelity to reference | Good, slightly less precise |
| VRAM | ~10GB | ~8GB |
| File size | ~20-50MB | ~10-30MB |
| Best for | Voice cloning, precise style | Quick experiments, genre adaptation |

## Training Commands

### LoRA (Standard)
```bash
cd <ace_step_dir>  # See config.json for your ACE-Step path

uv run python3 -m acestep.training.train_lora \
  --checkpoint-dir ./checkpoints \
  --model-variant turbo \
  --dataset-dir ~/Music/lora-datasets/my_style/ \
  --output-dir ./lora_output/my_style \
  --method lora \
  --rank 16 \
  --learning-rate 1e-4 \
  --steps 1000 \
  --batch-size 1
```

### LoKr (Fast)
```bash
cd <ace_step_dir>  # See config.json for your ACE-Step path

uv run python3 -m acestep.training.train_lora \
  --checkpoint-dir ./checkpoints \
  --model-variant turbo \
  --dataset-dir ~/Music/lora-datasets/my_style/ \
  --output-dir ./lora_output/my_style \
  --method lokr \
  --rank 16 \
  --learning-rate 1e-4 \
  --steps 500 \
  --batch-size 1
```

## Hyperparameter Guide

| Parameter | Default | Range | Notes |
|-----------|---------|-------|-------|
| `rank` (r) | 16 | 4-64 | Higher = more capacity. 16 is safe default |
| `learning-rate` | 1e-4 | 1e-5 to 5e-4 | Lower for voice cloning, higher for genre |
| `steps` | 1000 | 200-5000 | More songs = more steps needed |
| `batch-size` | 1 | 1-4 | Limited by VRAM. 1 is safest |
| `model-variant` | turbo | turbo/sft/base | Train on the model you'll generate with |

## Training Time Estimates

| GPU | LoRA (1000 steps) | LoKr (500 steps) |
|-----|-------------------|-------------------|
| RTX 3060 12GB | ~2 hours | ~25 min |
| RTX 4070 Ti | ~1 hour | ~15 min |
| RTX 5070 Ti 16GB | ~45 min | ~12 min |
| RTX 4090 24GB | ~30 min | ~8 min |

## Evaluation

1. Generate 4-8 test songs with the LoRA active
2. Listen for: style similarity, vocal quality, artifact presence
3. If too weak: increase rank or steps
4. If overfitting (all songs sound identical): reduce steps or add more training data
5. Compare with and without LoRA to confirm it's adding value

## Important Notes

- LoRAs **cannot be stacked** in ACE-Step 1.5 — use one at a time
- Train on the **same model variant** you'll use for generation
- The LoRA output directory must be accessible at generation time
- See official docs: `<ace_step_dir>/docs/en/LoRA_Training_Tutorial.md`
