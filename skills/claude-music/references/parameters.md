# ACE-Step 1.5 Full Parameter Reference

## GenerationParams

### Text Inputs
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `caption` | str | `""` | <512 chars | Music style/genre description |
| `lyrics` | str | `""` | <4096 chars | Song lyrics with structure tags |
| `instrumental` | bool | False | | Force instrumental (no vocals) |

### Music Metadata
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `bpm` | int | None | 30-300 | Tempo. None = auto-detect via LM |
| `keyscale` | str | `""` | e.g. "C major" | Musical key. Empty = auto |
| `timesignature` | str | `""` | 2/3/4/6 | Time signature. Empty = auto |
| `vocal_language` | str | `"unknown"` | ISO 639-1 | Language code. "unknown" = auto |
| `duration` | float | -1.0 | 10-600 sec | Target length. -1 = auto from lyrics |

### Generation Control
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `inference_steps` | int | 8 | 1-200 | Diffusion steps. Turbo: 8, Base: 32-65 |
| `guidance_scale` | float | 7.0 | 0-20 | CFG strength. 0 = off, higher = stricter |
| `seed` | int | -1 | any | Random seed. -1 = random |
| `shift` | float | 1.0 | 0.1-10 | Timestep shift. Higher = different texture |
| `use_adg` | bool | False | | Adaptive Dual Guidance |
| `cfg_interval_start` | float | 0.0 | 0-1 | When guidance starts (ratio) |
| `cfg_interval_end` | float | 1.0 | 0-1 | When guidance ends (ratio) |
| `infer_method` | str | "ode" | ode/sde | Diffusion method |
| `sampler_mode` | str | "euler" | euler/heun | Sampler type |

### Task Type
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `task_type` | str | "text2music" | text2music, cover, repaint, extract, lego, complete |

### Audio-to-Audio (Cover/Repaint)
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reference_audio` | str | None | Reference audio for cover mode |
| `src_audio` | str | None | Source audio for repaint/extract/lego/complete |
| `audio_cover_strength` | float | 1.0 | 0.0 (reimagine) to 1.0 (faithful) |
| `repainting_start` | float | 0.0 | Repaint region start (seconds) |
| `repainting_end` | float | -1.0 | Repaint region end (-1 = end of file) |

### LM (5Hz Language Model) Control
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `thinking` | bool | True | Enable Chain-of-Thought reasoning |
| `lm_temperature` | float | 0.85 | LLM sampling temperature |
| `lm_cfg_scale` | float | 2.0 | LLM CFG strength |
| `lm_top_k` | int | 0 | Top-k sampling (0 = disabled) |
| `lm_top_p` | float | 0.9 | Nucleus sampling |
| `lm_negative_prompt` | str | "NO USER INPUT" | Negative prompt for LM |
| `use_cot_metas` | bool | True | LM generates metadata (BPM, key, etc.) |
| `use_cot_caption` | bool | True | LM rewrites/expands caption |
| `use_cot_language` | bool | True | LM detects vocal language |

### Post-Processing
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_normalization` | bool | True | Loudness normalization |
| `normalization_db` | float | -1.0 | Target peak dB |
| `fade_in_duration` | float | 0.0 | Fade in (seconds) |
| `fade_out_duration` | float | 0.0 | Fade out (seconds) |

## GenerationConfig
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_size` | int | 2 | Number of variants (1-8) |
| `audio_format` | str | "flac" | flac/wav/mp3/wav32/opus/aac |
| `use_random_seed` | bool | True | Random seed per batch item |

## Quality Presets (music_engine.py)

| Preset | model | lm_model | steps | guidance | shift | batch | thinking |
|--------|-------|----------|-------|----------|-------|-------|----------|
| draft | turbo | none | 8 | 0.0 | 1.0 | 4 | false |
| standard | turbo | none | 8 | 0.0 | 1.0 | 2 | false |
| high | turbo | 1.7B | 8 | 0.0 | 1.0 | 2 | true |
| max | base | 1.7B | 65 | 4.0 | 6.0 | 1 | true |

## Model Variants

| Model | Params | Steps | Speed | VRAM | Use |
|-------|--------|-------|-------|------|-----|
| acestep-v15-turbo | 2B | 8 | ~15s | ~8GB | Default, fast |
| acestep-v15-sft | 2B | 32-50 | ~1-2min | ~8GB | Better quality |
| acestep-v15-base | 2B | 50-65 | ~2-3min | ~8GB | Highest 2B quality |
| acestep-v15-xl-turbo | 4B | 8 | ~20s | ~14GB | XL fast |
| acestep-v15-xl-sft | 4B | 32-50 | ~2-3min | ~14GB | XL balanced |
| acestep-v15-xl-base | 4B | 50-65 | ~3-5min | ~14GB | Maximum quality |

## LM Models

| Model | Params | VRAM | Speed | Quality |
|-------|--------|------|-------|---------|
| acestep-5Hz-lm-0.6B | 0.6B | ~3GB | Fast | Basic planning |
| acestep-5Hz-lm-1.7B | 1.7B | ~8GB | Medium | Good metadata + caption |
| acestep-5Hz-lm-4B | 4B | ~12GB | Slow | Best reasoning |
