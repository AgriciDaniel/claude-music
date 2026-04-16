---
name: claude-music-lora
description: >
  LoRA and LoKr fine-tuning for ACE-Step 1.5. Trains custom styles from 3-10 songs,
  manages trained adapters, and applies them during generation. Uses ACE-Step's
  built-in training pipeline.
when_to_use: >
  Use when the user asks to train a LoRA, fine-tune, clone a voice, make a custom
  style, or use LoKr for personalized music models.
allowed-tools:
  - Bash
  - Read
  - Write
---

# claude-music-lora — LoRA Fine-Tuning

## Overview

Train custom LoRA adapters to capture specific vocal styles, genres, instrument sounds, or production aesthetics. Requires 3-10 songs as training data.

## Dataset Preparation

1. Collect 3-10 songs in the target style (WAV/FLAC preferred, MP3 OK)
2. Place in a directory: `~/Music/lora-datasets/<style_name>/`
3. Songs should be 30-300 seconds each
4. Consistent style/genre across the dataset
5. High audio quality (no noise, no clipping)

## Training

```bash
cd "$(python3 -c "import json; print(json.load(open('$HOME/.claude/skills/claude-music/config.json'))['ace_step_dir'])")"

# LoRA training (standard, ~1 hour on RTX 5070 Ti)
uv run python3 -m acestep.training.train_lora \
  --checkpoint-dir ./checkpoints \
  --model-variant turbo \
  --dataset-dir ~/Music/lora-datasets/my_style/ \
  --output-dir ./lora_output/my_style \
  --rank 16 \
  --learning-rate 1e-4 \
  --steps 1000

# LoKr training (5x faster, ~12 min)
uv run python3 -m acestep.training.train_lora \
  --checkpoint-dir ./checkpoints \
  --model-variant turbo \
  --dataset-dir ~/Music/lora-datasets/my_style/ \
  --output-dir ./lora_output/my_style \
  --method lokr \
  --rank 16 \
  --learning-rate 1e-4 \
  --steps 500
```

## LoRA vs LoKr

| Aspect | LoRA | LoKr |
|--------|------|------|
| Training time | ~1 hour | ~12 min |
| Quality | Higher fidelity | Good, slightly less detailed |
| VRAM | ~10GB | ~8GB |
| Use case | Voice cloning, precise style | Genre adaptation, quick experiments |

## Hyperparameters

| Parameter | Default | Range | Notes |
|-----------|---------|-------|-------|
| Rank (r) | 16 | 4-64 | Higher = more capacity, more VRAM |
| Learning rate | 1e-4 | 1e-5 to 5e-4 | Lower for voice cloning |
| Steps | 1000 | 200-5000 | More data = more steps needed |
| Batch size | 1 | 1-4 | Limited by VRAM |

## Using Trained LoRA

After training, the LoRA is available in ACE-Step's generation pipeline. Refer to ACE-Step documentation at:
`<ace_step_dir>/docs/en/LoRA_Training_Tutorial.md` (see config.json for path)

For detailed reference: load `references/lora-training.md`
