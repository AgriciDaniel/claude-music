# ACE-Step 1.5 Full Parameter Reference

## Contents
- [GenerationParams](#generationparams) — Text Inputs, Music Metadata, Generation Control, Task Type, Audio-to-Audio, LM Control, Post-Processing
- [GenerationConfig](#generationconfig) — batch size, format, seed behavior
- [Quality Presets](#quality-presets-music_enginepy) — draft / standard / high / max
- [Model Variants](#model-variants) — 2B turbo/sft/base + 4B XL equivalents
- [LM Models](#lm-models) — 0.6B / 1.7B / 4B trade-offs
- [Sources](#sources)

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

### Audio-to-Audio (Cover/Repaint/Extract/Lego/Complete)
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `src_audio` | str | None | Source audio path — used by ALL audio-to-audio modes (cover, repaint, extract, lego, complete) |
| `cover_noise_strength` | float | 0.5 | Cover mode: noise to apply to source. 0.0 = faithful to source, 1.0 = fully reimagined. Used by `cover` task_type only. |
| `repainting_start` | float | 0.0 | Repaint region start (seconds) |
| `repainting_end` | float | -1.0 | Repaint region end (-1 = end of file) |

**Cover-mode note**: the ACE-Step demo `examples/generate_saxobeat_cover_spanish.py` uses `src_audio=SOURCE_AUDIO` and `cover_noise_strength=0.5`. Earlier versions of this doc and of `music_engine.py` used `reference_audio` and `audio_cover_strength` — those names are stale/deprecated. Tests in `tests/test_music_engine.py` guard against regression.

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

## Scripts used here

- `scripts/music_engine.py` — the Python engine that consumes every field in
  this reference. `QUALITY_PRESETS` dict (top of file) implements the preset
  table above. Subcommands `generate`, `cover`, `repaint`, `extract`, `lego`,
  `complete` each build a `GenerationParams` with the fields relevant to that
  task type.
- `scripts/music_engine.sh` — bash wrapper that resolves `config.json`,
  checks VRAM, then invokes `uv run python3 music_engine.py` from the
  ACE-Step directory.
- `scripts/rank.py` *(stub)* — will batch-rank outputs against caption; see
  `references/ranking-method.md`.

## Sources

Parameter values and defaults are grounded in:
- **Primary**: ACE-Step 1.5 source `acestep/schema.py` (`GenerationParams`, `GenerationConfig` dataclasses) — the authoritative type definitions.
- **Primary**: Musician's Guide (`<ace_step_dir>/docs/en/ace_step_musicians_guide.md`) — default values and semantic ranges.
- **Primary**: Tutorial (`<ace_step_dir>/docs/en/Tutorial.md`) — inference-step and guidance-scale guidance per model variant.
- **Cover-mode mapping**: `<ace_step_dir>/examples/generate_saxobeat_cover_spanish.py` — verified field names `src_audio` + `cover_noise_strength`.
- **Quality presets** (`draft`/`standard`/`high`/`max`): designed in this skill — see `scripts/music_engine.py:QUALITY_PRESETS`. Values chosen from Tutorial.md §Turbo vs Base.
- **Model VRAM estimates**: cross-referenced `<ace_step_dir>/README.md` hardware table + local measurement on RTX 5070 Ti 16GB (research report: `research/drafts/ace-step-research-report-2026-04-15.md` §Domain 5).

**Known gaps (to be filled in Theme 2 of research plan)**: the `shift`, `infer_method`, `sampler_mode`, and `use_adg` optimal settings per genre are currently defaults; Theme 2 will A/B-test and replace with preset-table-backed values.
