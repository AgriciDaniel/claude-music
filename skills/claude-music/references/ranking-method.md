# Audio Ranking Method (Theme 3)

## Contents
- [Purpose](#purpose)
- [Pipeline](#pipeline)
- [Scoring](#scoring)
- [Validation](#validation)
- [Installation (Session 3)](#installation-session-3)
- [Sources](#sources)

## Purpose

Rank a batch of ACE-Step-generated audio files against the original caption so that "generate N variants and pick the best" is automatic. This unlocks:

- Theme 2 parameter sweeps (need a signal to optimize for).
- `/music random` batch-4 → auto-pick-top-1 UX.
- Benchmarking claude-music against Suno/Udio (Theme 8).

The ranker must be **GPU-free** enough to run alongside ACE-Step generation (or on CPU after), and **correlated with human judgment** — the research plan's success bar is Spearman ρ ≥ 0.6 against hand-ranked samples.

## Pipeline

```
┌─────────────────────┐
│ ACE-Step generation │   (batch of N flacs, same caption)
│  → N audio files    │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ rank.py             │
│ --input-dir DIR     │
│ --caption TEXT      │
│ --lyrics TEXT       │
└──────────┬──────────┘
           │
           v    for each audio file:
┌─────────────────────────────────────────────┐
│ 1. CLAP caption-cosine          (0.0–1.0)   │
│ 2. DNSMOS overall               (1–5)       │
│ 3. SongEval {musicality,        (1–5 each)  │
│              coherence,                     │
│              production}                    │
│ 4. LLM-judge  (Claude on        (1–5)       │
│    caption + PANN audio tags +              │
│    lyrics transcript)                       │
└──────────┬──────────────────────────────────┘
           │
           v
┌─────────────────────┐
│ Composite score     │  weighted per §Scoring
│ Sort ascending →    │
│ pick top-K          │
└─────────────────────┘
```

## Scoring

The composite score is a weighted linear combination — weights TBD in Session 3 via correlation study on hand-ranked samples. Starting weights (to tune):

| Signal | Weight | Rationale |
|---|---|---|
| CLAP caption-cosine | 0.35 | Does the audio match what was asked for? Most direct prompt-fidelity metric. |
| SongEval musicality | 0.20 | Is it musical (coherent melody/rhythm)? |
| SongEval coherence | 0.15 | Does it hang together structurally? |
| DNSMOS overall | 0.15 | Technical audio quality (rules out clipping/artifacts). |
| LLM-judge | 0.15 | Semantic grounding — catches artifacts the acoustic metrics miss. |

All signals normalized to [0, 1] before weighting. Composite is in [0, 1] where higher = better.

## Validation

Success bar from research plan line 117:

> ρ ≥ 0.6 on a held-out 20-item set — OR — a documented 3-metric weighted scheme with reported ρ.

Validation protocol (Session 3):

1. Generate 40 samples across 4 prompts (10 per prompt).
2. Hand-rank each prompt's 10 samples blind (1-5 integer scale), average across 2 listens.
3. Run `rank.py` on same 40 samples.
4. Compute Spearman ρ per prompt, average.
5. Iterate weights if ρ < 0.6.
6. Hold out 20 more samples; confirm ρ holds.

If ρ < 0.6 with all 5 signals, drop to 3-metric weighted scheme (CLAP + SongEval-musicality + LLM-judge) and report the ρ achieved. Do NOT ship a ranker that correlates with noise.

## Installation (Session 3)

Deferred to Session 3 (gap G12):

```bash
# CLAP (LAION)
uv pip install laion-clap soundfile

# SongEval (ASLP lab toolkit)
git clone https://github.com/ASLP-lab/SongEval research/scratch/SongEval
cd research/scratch/SongEval && uv pip install -e .

# DNSMOS
# Model weights downloaded on first use by the toolkit — follow repo README

# Verify
python3 -c "import laion_clap; print(laion_clap.__version__)"
```

## Sources

- **Research plan** §Theme 3 (lines 99-117) — defines the pipeline, validation bar, and deliverable shape.
- **CLAP**: LAION-CLAP (github.com/LAION-AI/CLAP), HTSAT-fused checkpoint — caption/audio joint embedding model.
- **SongEval**: Wang et al., "SongEval: A Dataset and Benchmark for Song Evaluation" (github.com/ASLP-lab/SongEval). Multi-dimensional song quality scoring.
- **DNSMOS**: Reddy et al., "DNSMOS: A Non-Intrusive Perceptual Objective Speech Quality Metric" (Microsoft Research; adapts to music with known caveats).
- **LLM-judge methodology**: CLaMP2 paper and the practice established in G-Eval (Liu et al. 2023) for reference-free LLM scoring.

**Known gaps / risks**:
- DNSMOS was trained on speech, not music — use as a technical-quality floor, not a musical-quality signal.
- SongEval dimensions require model weights (~500MB) downloaded at setup.
- LLM-judge cost: each item consumes ~2000 tokens. Budget in Theme 2/3 sessions.
