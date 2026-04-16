# Song Structure Templates

## Standard Pop (3-4 min)
```
[Intro]         8 bars    ~15s at 120 BPM
[Verse 1]       16 bars   ~30s
[Pre-Chorus]    8 bars    ~15s
[Chorus]        16 bars   ~30s
[Verse 2]       16 bars   ~30s
[Pre-Chorus]    8 bars    ~15s
[Chorus]        16 bars   ~30s
[Bridge]        8 bars    ~15s
[Chorus]        16 bars   ~30s
[Outro]         8 bars    ~15s
Total: ~225s (3:45)
```

## Rock (3-5 min)
```
[Intro]         8-16 bars
[Verse 1]       16 bars
[Chorus]        16 bars
[Verse 2]       16 bars
[Chorus]        16 bars
[Guitar Solo]   16-32 bars
[Bridge]        8 bars
[Chorus]        16-32 bars
[Outro]         8-16 bars
```

## Hip-Hop/Rap (3-4 min)
```
[Intro]         4-8 bars
[Verse 1]       16 bars    (16-20 seconds of rap)
[Hook/Chorus]   8 bars
[Verse 2]       16 bars
[Hook/Chorus]   8 bars
[Verse 3]       16 bars    (optional)
[Hook/Chorus]   8 bars
[Outro]         4-8 bars
```

## EDM/Electronic (4-6 min)
```
[Intro]         16-32 bars
[Build]         8-16 bars
[Drop]          16-32 bars
[Breakdown]     16 bars
[Build]         8-16 bars
[Drop]          16-32 bars
[Outro]         16-32 bars
```

## Ballad (3-5 min)
```
[Intro]         8 bars (piano/acoustic)
[Verse 1]       16 bars
[Verse 2]       16 bars
[Chorus]        16 bars
[Verse 3]       16 bars
[Chorus]        16 bars
[Bridge]        8 bars (emotional peak)
[Chorus]        16-32 bars (bigger)
[Outro]         8-16 bars (fade)
```

## Lo-Fi/Ambient (2-5 min)
```
[Intro]         8-16 bars
[Section A]     16-32 bars
[Section B]     16-32 bars
[Section A']    16-32 bars (variation)
[Outro]         8-16 bars
(No traditional verse/chorus — evolving texture)
```

## Short Form (30-60s, TikTok/Reels)
```
[Hook]          4-8 bars   ~8-15s (instantly catchy)
[Verse]         8 bars     ~15s
[Hook]          4-8 bars   ~8-15s (repeat)
Total: ~30-45s
```

## Timing Calculator

**Bars to seconds**: `seconds = (bars × beats_per_bar × 60) / BPM`

| BPM | 8 bars (4/4) | 16 bars | 32 bars |
|-----|-------------|---------|---------|
| 80 | 24s | 48s | 96s |
| 100 | 19s | 38s | 77s |
| 120 | 16s | 32s | 64s |
| 140 | 14s | 27s | 55s |
| 160 | 12s | 24s | 48s |

## Sources

- **Structure tag vocabulary**: ACE-Step Musician's Guide (`<ace_step_dir>/docs/en/ace_step_musicians_guide.md`) — the tags `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Drop]`, `[Build]`, `[Hook]`, `[Guitar Solo]`, `[Piano Interlude]`, `[Fade Out]` are verbatim from its structure-tag section.
- **Section length conventions**: generalized Western popular-music practice (Jason Blume, *Six Steps to Songwriting Success*; Pat Pattison, *Writing Better Lyrics*). These are starting points — ACE-Step respects the tags loosely, not strictly.
- **Timing calculator formula**: standard `seconds = (bars × 4) / (BPM / 60)` for 4/4 time.

**Observed behavior**: ACE-Step's 5Hz LM is more likely to preserve section boundaries when `thinking: true` + lyrics include explicit `[Tag]` markers. Without tags, the model infers structure from caption alone — results are coherent but less predictable.
