#!/usr/bin/env python3
"""rank.py — stub for Theme 3 of the research plan (batch + rank pipeline).

Contract (see references/ranking-method.md for the full method):

    rank.py --input-dir <dir-of-flacs> --caption <original-prompt> [--lyrics <text>]

Emits a JSON report to stdout listing, for each input audio:
    - CLAP caption-cosine score (from the LAION CLAP model)
    - DNSMOS score (speech/music quality; informational)
    - SongEval dimension scores (musicality/coherence/production)
    - LLM-judge score (Claude or Opus on the caption + audio summary)

The weighted composite is defined in `references/ranking-method.md` §Scoring.

This file is a STUB in Session 2. Session 3 installs librosa / laion-clap /
SongEval (research plan gap G12) and fills in the scoring functions. Until
then, the stub emits a deterministic placeholder JSON so downstream tooling
can be developed against the real output shape.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCHEMA_VERSION = "0.1.0-stub"


def _stub_score(audio_path: Path, caption: str) -> dict:
    """Placeholder score until Session 3 ships the real pipeline."""
    return {
        "path": str(audio_path),
        "size_bytes": audio_path.stat().st_size if audio_path.exists() else 0,
        "scores": {
            "clap_cosine": None,       # will be set in Session 3 (needs laion-clap)
            "dnsmos_overall": None,    # will be set in Session 3 (needs DNSMOS weights)
            "songeval": {              # will be set in Session 3 (needs SongEval)
                "musicality": None,
                "coherence": None,
                "production": None,
            },
            "llm_judge": None,         # will be set in Session 3 (needs Claude API wiring)
            "composite": None,         # weighted sum — spec in ranking-method.md
        },
        "status": "stub",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-rank ACE-Step audio outputs against their caption/lyrics."
    )
    parser.add_argument("--input-dir", required=True,
                        help="Directory containing one or more .flac/.wav/.mp3 files to rank.")
    parser.add_argument("--caption", required=True,
                        help="The original caption used for generation (for CLAP cosine + LLM judge).")
    parser.add_argument("--lyrics", default="",
                        help="Optional: original lyrics for lyric-coherence scoring.")
    parser.add_argument("--output", default=None,
                        help="Optional JSON output file. Defaults to stdout.")
    args = parser.parse_args()

    in_dir = Path(os.path.expanduser(args.input_dir))
    if not in_dir.is_dir():
        print(json.dumps({
            "success": False,
            "error": f"Input directory not found: {in_dir}",
        }), flush=True)
        return 1

    audio_exts = {".flac", ".wav", ".mp3", ".ogg", ".opus", ".m4a"}
    audios = sorted(p for p in in_dir.iterdir() if p.suffix.lower() in audio_exts)

    if not audios:
        print(json.dumps({
            "success": False,
            "error": f"No audio files found in {in_dir}",
            "supported_extensions": sorted(audio_exts),
        }), flush=True)
        return 1

    items = [_stub_score(p, args.caption) for p in audios]
    # Rank by composite when it exists; until then preserve filesystem order.
    items.sort(key=lambda x: (x["scores"]["composite"] is None, x["scores"]["composite"]),
               reverse=False)

    report = {
        "success": True,
        "schema_version": SCHEMA_VERSION,
        "caption": args.caption,
        "lyrics_provided": bool(args.lyrics),
        "input_dir": str(in_dir),
        "n_items": len(items),
        "items": items,
        "note": (
            "This is a stub. Run Session 3 of the research plan to install "
            "librosa + laion-clap + SongEval and enable real scoring."
        ),
    }

    payload = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(payload)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(payload, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
