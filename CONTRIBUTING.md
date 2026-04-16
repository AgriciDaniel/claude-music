# Contributing to claude-music

Thanks for wanting to help. This project has a narrow mission — make ACE-Step 1.5 easy to use from Claude Code — so contributions are accepted in these categories:

## Accepted contributions

| Category | Examples |
|---|---|
| **Genre recipes** | A new entry in `skills/claude-music/references/genre-recipes.md` with caption + BPM + key defaults, backed by ≥2 sources. |
| **Parameter presets** | New `QUALITY_PRESETS` entries in `scripts/music_engine.py` (only if they test out better on a specific workload; show your A/B). |
| **Bug fixes** | Fix a broken path, a crash, a JSON-contract violation. Include a test in `tests/` that would fail without the fix. |
| **Platform ports** | Windows (`install.ps1`) and macOS tweaks. Keep them parallel to `install.sh`. |
| **Reference doc corrections** | Anything in `skills/claude-music/references/` that is factually wrong. Cite the source of the correction. |
| **LoRA/training docs** | Practical tips from successful runs. Must include training config that reproduces. |

## Not accepted

- Scope creep (other music-gen models — those get their own skill).
- Mass renames / format-only PRs (noise).
- "AI-flavor" fluff in docs (marketing language, hedges, emojis).
- Anything that requires closed-source services as runtime deps.

## Adding a genre recipe — step by step

1. Pick a genre not already in `references/genre-recipes.md` or that has incomplete tags.
2. Generate **≥4 samples** using your proposed caption at different seeds. Listen. If it doesn't consistently produce recognizable output, the caption needs more work.
3. Fill in the row:
   - Caption tags (3-5, following `references/prompt-guide.md` formula)
   - BPM range + sweet spot
   - Typical keys (major/minor)
   - Model variant (turbo/base)
   - Quality preset (draft/standard/high/max)
4. Add a "Detailed Recipe" block below the table with a tested caption + params.
5. Cite your sources in the file's `## Sources` section (Musician's Guide, research doc, or listener reference tracks).

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

All 13 contract tests must pass. They run in <1 second and do not require a GPU.

## Syntax checks (no GPU needed)

```bash
# Shell
bash -n install.sh uninstall.sh skills/claude-music/scripts/*.sh

# Python
python3 -m py_compile skills/claude-music/scripts/*.py tests/*.py

# JSON
python3 -m json.tool .claude-plugin/plugin.json
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool skills/claude-music/config.json
```

CI runs the same checks plus `ruff check` and shellcheck.

## PR checklist

- [ ] Change is in one of the Accepted categories above.
- [ ] No personal paths leaked in `config.json` (leave as `CHANGE_ME`).
- [ ] No `eval` in new shell code; use array execution (`"${ARR[@]}"`).
- [ ] Tests added if fixing a bug; existing tests still pass.
- [ ] New claims in reference docs are cited under `## Sources`.
- [ ] If changing `GenerationParams` field names, `tests/test_music_engine.py::test_cover_mode_uses_src_audio_not_reference_audio` still passes (or is updated with a source-of-truth pointer).
- [ ] `ruff check skills/ tests/` clean.
- [ ] CI green.

## Security issues

Do not open a public issue. See `SECURITY.md`.

## Licensing

By contributing, you agree your work is licensed under MIT (see `LICENSE`).
