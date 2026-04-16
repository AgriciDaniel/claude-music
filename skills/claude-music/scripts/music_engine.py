#!/usr/bin/env python3
"""ACE-Step Music Engine for claude-music skill.

Subcommands:
  generate    Text-to-music generation
  cover       Style transfer using reference audio
  repaint     Selective section regeneration
  extract     Track separation (base model only)
  lego        Add instrument layer (base model only)
  complete    Audio completion (base model only)

Usage:
  python3 music_engine.py generate --caption "upbeat pop" --duration 60
  python3 music_engine.py cover --src-audio song.mp3 --caption "jazz version"
  python3 music_engine.py repaint --src-audio song.mp3 --start 30 --end 60

All structured output is JSON to stdout. Progress/debug info goes to stderr.
"""

import argparse
import gc
import json
import os
import shutil
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Quality presets
# ---------------------------------------------------------------------------

QUALITY_PRESETS = {
    "draft": {
        "model": "acestep-v15-turbo",
        "lm_model": None,
        "inference_steps": 8,
        "guidance_scale": 0.0,
        "thinking": False,
        "batch_size": 4,
        "shift": 1.0,
    },
    "standard": {
        "model": "acestep-v15-turbo",
        "lm_model": None,
        "inference_steps": 8,
        "guidance_scale": 0.0,
        "thinking": False,
        "batch_size": 2,
        "shift": 1.0,
    },
    "high": {
        "model": "acestep-v15-turbo",
        "lm_model": "acestep-5Hz-lm-1.7B",
        "inference_steps": 8,
        "guidance_scale": 0.0,
        "thinking": True,
        "batch_size": 2,
        "shift": 1.0,
    },
    "max": {
        "model": "acestep-v15-base",
        "lm_model": "acestep-5Hz-lm-1.7B",
        "inference_steps": 65,
        "guidance_scale": 4.0,
        "thinking": True,
        "batch_size": 1,
        "shift": 6.0,
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg):
    """Print to stderr for progress messages (keeps stdout clean for JSON)."""
    print(msg, file=sys.stderr, flush=True)


def get_free_vram_mb():
    """Return free VRAM in MB, or -1 if not available."""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            free, total = torch.cuda.mem_get_info()
            return int(free / (1024 * 1024))
    except Exception:
        pass
    return -1


def output_json(data):
    """Print JSON result to stdout."""
    print(json.dumps(data, indent=2, default=str))


def error_json(msg, suggestion=None):
    """Print error JSON and exit."""
    result = {"success": False, "error": msg}
    if suggestion:
        result["suggestion"] = suggestion
    output_json(result)
    sys.exit(1)


def get_output_path(args, task_type, index=0):
    """Generate an output file path."""
    if args.output and index == 0:
        return args.output

    output_dir = os.path.expanduser(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fmt = args.format if args.format != "wav32" else "wav"

    if index > 0 or not args.output:
        return os.path.join(output_dir, f"{task_type}_{timestamp}_{index + 1:02d}.{fmt}")
    return args.output


def resolve_quality(args):
    """Apply quality preset, then override with explicit args."""
    preset = QUALITY_PRESETS.get(args.quality, QUALITY_PRESETS["standard"])

    if args.model is None:
        args.model = preset["model"]
    if args.lm_model is None and not hasattr(args, "_lm_model_set"):
        args.lm_model = preset["lm_model"]
    if args.inference_steps is None:
        args.inference_steps = preset["inference_steps"]
    if args.guidance_scale is None:
        args.guidance_scale = preset["guidance_scale"]
    if args.batch is None:
        args.batch = preset["batch_size"]
    if args.shift is None:
        args.shift = preset["shift"]
    if not hasattr(args, "thinking") or args.thinking is None:
        args.thinking = preset["thinking"]

    return args


# ---------------------------------------------------------------------------
# ACE-Step initialization
# ---------------------------------------------------------------------------

def initialize_acestep(args):
    """Load ACE-Step models. Returns (handler, llm_handler, status_msg)."""
    project_root = Path(args.ace_step_dir)
    sys.path.insert(0, str(project_root))

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["TORCHAUDIO_USE_BACKEND"] = "ffmpeg"

    from acestep.handler import AceStepHandler
    log(f"Loading DiT model: {args.model}...")

    handler = AceStepHandler()
    t0 = time.time()
    status, success = handler.initialize_service(
        project_root=str(project_root),
        config_path=args.model,
        device="auto",
        use_flash_attention=True,
        offload_to_cpu=True,
        offload_dit_to_cpu=True,
    )

    if not success:
        return None, None, f"DiT init failed: {status}"

    load_time = time.time() - t0
    log(f"DiT ready in {load_time:.1f}s: {status}")

    llm_handler = None
    if args.lm_model and args.thinking:
        log(f"Loading LM: {args.lm_model}...")
        t1 = time.time()
        try:
            from acestep.llm_inference import LLMHandler
            llm_handler = LLMHandler()

            # Try vllm first, fall back to PyTorch native
            backend = "vllm"
            try:
                import vllm  # noqa: F401
            except ImportError:
                backend = "pt"
                log("vllm not available, using PyTorch backend for LM")

            lm_status, lm_success = llm_handler.initialize(
                checkpoint_dir=str(project_root / "checkpoints"),
                lm_model_path=args.lm_model,
                backend=backend,
                device="cuda",
                offload_to_cpu=True,
            )
            if not lm_success:
                log(f"LM init failed: {lm_status}, continuing without thinking mode")
                llm_handler = None
            else:
                log(f"LM ready in {time.time() - t1:.1f}s ({backend} backend)")
        except Exception as e:
            log(f"LM load failed ({e}), continuing without thinking mode")
            llm_handler = None

    return handler, llm_handler, status


# ---------------------------------------------------------------------------
# Subcommand: generate
# ---------------------------------------------------------------------------

def cmd_generate(args):
    """Text-to-music generation."""
    args = resolve_quality(args)

    if not args.caption and not args.lyrics:
        error_json(
            "Must provide --caption and/or --lyrics",
            "Example: music_engine.py generate --caption 'upbeat pop' --lyrics '[Verse] Hello world'"
        )

    # Validate input lengths (ACE-Step limits)
    if args.caption and len(args.caption) > 512:
        log(f"WARNING: Caption truncated from {len(args.caption)} to 512 chars")
        args.caption = args.caption[:512]
    if args.lyrics and len(args.lyrics) > 4096:
        log(f"WARNING: Lyrics truncated from {len(args.lyrics)} to 4096 chars")
        args.lyrics = args.lyrics[:4096]

    handler, llm_handler, status = initialize_acestep(args)
    if handler is None:
        error_json(status)

    from acestep.inference import generate_music, GenerationParams, GenerationConfig

    params = GenerationParams(
        caption=args.caption or "",
        lyrics=args.lyrics or "",
        instrumental=args.instrumental,
        vocal_language=args.language,
        bpm=args.bpm,
        keyscale=args.key or "",
        timesignature=args.time_sig or "",
        duration=args.duration if args.duration and args.duration > 0 else -1.0,
        inference_steps=args.inference_steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
        shift=args.shift,
        task_type="text2music",
        thinking=args.thinking if llm_handler else False,
    )

    config = GenerationConfig(
        batch_size=args.batch,
        use_random_seed=(args.seed < 0),
        audio_format=args.format,
    )

    save_dir = os.path.expanduser(args.output_dir)
    os.makedirs(save_dir, exist_ok=True)

    log(f"Generating {args.batch} variant(s), {args.duration}s, {args.model}...")
    t0 = time.time()
    result = generate_music(
        dit_handler=handler,
        llm_handler=llm_handler,
        params=params,
        config=config,
        save_dir=save_dir,
    )
    gen_time = time.time() - t0

    if not result or not result.success:
        err = result.error if result else "Unknown generation error"
        error_json(err)

    outputs = []
    for i, audio in enumerate(result.audios or []):
        path = None
        for key in ("path", "audio_path", "save_path", "file_path"):
            if key in audio and audio[key]:
                path = audio[key]
                break
        if not path:
            for v in audio.values():
                if isinstance(v, str) and os.path.isfile(v):
                    path = v
                    break

        if path and os.path.isfile(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            seed = audio.get("params", {}).get("seed", -1)
            outputs.append({
                "path": path,
                "seed": seed,
                "duration_sec": args.duration if args.duration and args.duration > 0 else "auto",
                "size_mb": round(size_mb, 2),
                "index": i + 1,
            })

    output_json({
        "success": True,
        "task_type": "text2music",
        "model": args.model,
        "lm_model": args.lm_model if llm_handler else None,
        "quality": args.quality,
        "outputs": outputs,
        "params": {
            "caption": args.caption,
            "lyrics": args.lyrics[:200] + "..." if args.lyrics and len(args.lyrics) > 200 else args.lyrics,
            "bpm": args.bpm,
            "key": args.key,
            "duration": args.duration,
            "instrumental": args.instrumental,
            "language": args.language,
            "inference_steps": args.inference_steps,
            "guidance_scale": args.guidance_scale,
            "shift": args.shift,
            "thinking": args.thinking if llm_handler else False,
        },
        "timing": {
            "generation_sec": round(gen_time, 1),
        },
        "count": len(outputs),
        "playback_hint": f"ffplay -nodisp -autoexit \"{outputs[0]['path']}\"" if outputs else None,
    })


# ---------------------------------------------------------------------------
# Subcommand: cover
# ---------------------------------------------------------------------------

def cmd_cover(args):
    """Style transfer / cover generation from reference audio."""
    args = resolve_quality(args)

    if not args.src_audio:
        error_json("Must provide --src-audio for cover mode")
    if not os.path.isfile(args.src_audio):
        error_json(f"Source audio not found: {args.src_audio}")

    handler, llm_handler, status = initialize_acestep(args)
    if handler is None:
        error_json(status)

    from acestep.inference import generate_music, GenerationParams, GenerationConfig

    params = GenerationParams(
        caption=args.caption or "",
        lyrics=args.lyrics or "",
        instrumental=args.instrumental,
        vocal_language=args.language,
        bpm=args.bpm,
        keyscale=args.key or "",
        timesignature=args.time_sig or "",
        duration=args.duration if args.duration and args.duration > 0 else -1.0,
        inference_steps=args.inference_steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
        shift=args.shift,
        task_type="cover",
        src_audio=args.src_audio,
        cover_noise_strength=args.cover_strength,
        thinking=args.thinking if llm_handler else False,
    )

    config = GenerationConfig(
        batch_size=args.batch,
        use_random_seed=(args.seed < 0),
        audio_format=args.format,
    )

    save_dir = os.path.expanduser(args.output_dir)
    os.makedirs(save_dir, exist_ok=True)

    log(f"Generating cover (strength={args.cover_strength})...")
    t0 = time.time()
    result = generate_music(
        dit_handler=handler,
        llm_handler=llm_handler,
        params=params,
        config=config,
        save_dir=save_dir,
    )
    gen_time = time.time() - t0

    if not result or not result.success:
        error_json(result.error if result else "Cover generation failed")

    outputs = []
    for i, audio in enumerate(result.audios or []):
        path = None
        for key in ("path", "audio_path", "save_path", "file_path"):
            if key in audio and audio[key]:
                path = audio[key]
                break
        if not path:
            for v in audio.values():
                if isinstance(v, str) and os.path.isfile(v):
                    path = v
                    break
        if path and os.path.isfile(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            seed = audio.get("params", {}).get("seed", -1)
            outputs.append({
                "path": path, "seed": seed,
                "size_mb": round(size_mb, 2), "index": i + 1,
            })

    output_json({
        "success": True,
        "task_type": "cover",
        "model": args.model,
        "outputs": outputs,
        "params": {
            "src_audio": args.src_audio,
            "cover_strength": args.cover_strength,
            "caption": args.caption,
        },
        "timing": {"generation_sec": round(gen_time, 1)},
        "count": len(outputs),
        "playback_hint": f"ffplay -nodisp -autoexit \"{outputs[0]['path']}\"" if outputs else None,
    })


# ---------------------------------------------------------------------------
# Subcommand: repaint
# ---------------------------------------------------------------------------

def cmd_repaint(args):
    """Selective section regeneration."""
    args = resolve_quality(args)

    if not args.src_audio:
        error_json("Must provide --src-audio for repaint mode")
    if not os.path.isfile(args.src_audio):
        error_json(f"Source audio not found: {args.src_audio}")

    handler, llm_handler, status = initialize_acestep(args)
    if handler is None:
        error_json(status)

    from acestep.inference import generate_music, GenerationParams, GenerationConfig

    params = GenerationParams(
        caption=args.caption or "",
        lyrics=args.lyrics or "",
        instrumental=args.instrumental,
        vocal_language=args.language,
        bpm=args.bpm,
        keyscale=args.key or "",
        duration=args.duration if args.duration and args.duration > 0 else -1.0,
        inference_steps=args.inference_steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
        shift=args.shift,
        task_type="repaint",
        src_audio=args.src_audio,
        repainting_start=args.start,
        repainting_end=args.end,
        thinking=args.thinking if llm_handler else False,
    )

    config = GenerationConfig(
        batch_size=args.batch,
        use_random_seed=(args.seed < 0),
        audio_format=args.format,
    )

    save_dir = os.path.expanduser(args.output_dir)
    os.makedirs(save_dir, exist_ok=True)

    log(f"Repainting {args.start}s-{args.end}s...")
    t0 = time.time()
    result = generate_music(
        dit_handler=handler,
        llm_handler=llm_handler,
        params=params,
        config=config,
        save_dir=save_dir,
    )
    gen_time = time.time() - t0

    if not result or not result.success:
        error_json(result.error if result else "Repaint failed")

    outputs = []
    for i, audio in enumerate(result.audios or []):
        path = None
        for key in ("path", "audio_path", "save_path", "file_path"):
            if key in audio and audio[key]:
                path = audio[key]
                break
        if not path:
            for v in audio.values():
                if isinstance(v, str) and os.path.isfile(v):
                    path = v
                    break
        if path and os.path.isfile(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            seed = audio.get("params", {}).get("seed", -1)
            outputs.append({
                "path": path, "seed": seed,
                "size_mb": round(size_mb, 2), "index": i + 1,
            })

    output_json({
        "success": True,
        "task_type": "repaint",
        "model": args.model,
        "outputs": outputs,
        "params": {
            "src_audio": args.src_audio,
            "start": args.start, "end": args.end,
            "caption": args.caption,
        },
        "timing": {"generation_sec": round(gen_time, 1)},
        "count": len(outputs),
        "playback_hint": f"ffplay -nodisp -autoexit \"{outputs[0]['path']}\"" if outputs else None,
    })


# ---------------------------------------------------------------------------
# Subcommand: extract
# ---------------------------------------------------------------------------

def cmd_extract(args):
    """Track separation (base model only)."""
    args = resolve_quality(args)
    if "turbo" in (args.model or ""):
        args.model = "acestep-v15-base"
        log("Switched to base model (extract requires base)")

    if not args.src_audio:
        error_json("Must provide --src-audio for extract mode")
    if not os.path.isfile(args.src_audio):
        error_json(f"Source audio not found: {args.src_audio}")

    handler, llm_handler, status = initialize_acestep(args)
    if handler is None:
        error_json(status)

    from acestep.inference import generate_music, GenerationParams, GenerationConfig

    params = GenerationParams(
        caption=args.caption or "",
        task_type="extract",
        src_audio=args.src_audio,
        inference_steps=args.inference_steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
    )

    config = GenerationConfig(
        batch_size=1,
        audio_format=args.format,
    )

    save_dir = os.path.expanduser(args.output_dir)
    os.makedirs(save_dir, exist_ok=True)

    log("Extracting tracks...")
    t0 = time.time()
    result = generate_music(
        dit_handler=handler, llm_handler=None,
        params=params, config=config, save_dir=save_dir,
    )
    gen_time = time.time() - t0

    if not result or not result.success:
        error_json(result.error if result else "Extract failed")

    outputs = []
    for i, audio in enumerate(result.audios or []):
        path = None
        for key in ("path", "audio_path", "save_path", "file_path"):
            if key in audio and audio[key]:
                path = audio[key]
                break
        if path and os.path.isfile(path):
            outputs.append({"path": path, "index": i + 1})

    output_json({
        "success": True, "task_type": "extract",
        "outputs": outputs,
        "timing": {"generation_sec": round(gen_time, 1)},
        "count": len(outputs),
    })


# ---------------------------------------------------------------------------
# Subcommand: lego
# ---------------------------------------------------------------------------

def cmd_lego(args):
    """Multi-track / add layer (base model only)."""
    args = resolve_quality(args)
    if "turbo" in (args.model or ""):
        args.model = "acestep-v15-base"
        log("Switched to base model (lego requires base)")

    if not args.src_audio:
        error_json("Must provide --src-audio for lego mode")
    if not os.path.isfile(args.src_audio):
        error_json(f"Source audio not found: {args.src_audio}")

    handler, llm_handler, status = initialize_acestep(args)
    if handler is None:
        error_json(status)

    from acestep.inference import generate_music, GenerationParams, GenerationConfig

    params = GenerationParams(
        caption=args.caption or "",
        lyrics=args.lyrics or "",
        task_type="lego",
        src_audio=args.src_audio,
        inference_steps=args.inference_steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
    )

    config = GenerationConfig(batch_size=1, audio_format=args.format)

    save_dir = os.path.expanduser(args.output_dir)
    os.makedirs(save_dir, exist_ok=True)

    log("Adding layer...")
    t0 = time.time()
    result = generate_music(
        dit_handler=handler, llm_handler=llm_handler,
        params=params, config=config, save_dir=save_dir,
    )
    gen_time = time.time() - t0

    if not result or not result.success:
        error_json(result.error if result else "Lego failed")

    outputs = []
    for i, audio in enumerate(result.audios or []):
        path = None
        for key in ("path", "audio_path", "save_path", "file_path"):
            if key in audio and audio[key]:
                path = audio[key]
                break
        if path and os.path.isfile(path):
            outputs.append({"path": path, "index": i + 1})

    output_json({
        "success": True, "task_type": "lego",
        "outputs": outputs,
        "timing": {"generation_sec": round(gen_time, 1)},
        "count": len(outputs),
    })


# ---------------------------------------------------------------------------
# Subcommand: complete
# ---------------------------------------------------------------------------

def cmd_complete(args):
    """Audio completion (base model only)."""
    args = resolve_quality(args)
    if "turbo" in (args.model or ""):
        args.model = "acestep-v15-base"
        log("Switched to base model (complete requires base)")

    if not args.src_audio:
        error_json("Must provide --src-audio for complete mode")
    if not os.path.isfile(args.src_audio):
        error_json(f"Source audio not found: {args.src_audio}")

    handler, llm_handler, status = initialize_acestep(args)
    if handler is None:
        error_json(status)

    from acestep.inference import generate_music, GenerationParams, GenerationConfig

    params = GenerationParams(
        caption=args.caption or "",
        lyrics=args.lyrics or "",
        task_type="complete",
        src_audio=args.src_audio,
        duration=args.duration if args.duration and args.duration > 0 else -1.0,
        inference_steps=args.inference_steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
    )

    config = GenerationConfig(batch_size=1, audio_format=args.format)

    save_dir = os.path.expanduser(args.output_dir)
    os.makedirs(save_dir, exist_ok=True)

    log("Completing audio...")
    t0 = time.time()
    result = generate_music(
        dit_handler=handler, llm_handler=llm_handler,
        params=params, config=config, save_dir=save_dir,
    )
    gen_time = time.time() - t0

    if not result or not result.success:
        error_json(result.error if result else "Complete failed")

    outputs = []
    for i, audio in enumerate(result.audios or []):
        path = None
        for key in ("path", "audio_path", "save_path", "file_path"):
            if key in audio and audio[key]:
                path = audio[key]
                break
        if path and os.path.isfile(path):
            outputs.append({"path": path, "index": i + 1})

    output_json({
        "success": True, "task_type": "complete",
        "outputs": outputs,
        "timing": {"generation_sec": round(gen_time, 1)},
        "count": len(outputs),
    })


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="ACE-Step Music Engine for claude-music skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    # Read default from config.json if available
    default_ace_dir = None
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        try:
            import json as _json
            with open(config_path) as _f:
                _cfg = _json.load(_f)
            val = _cfg.get("ace_step_dir", "")
            if val and val != "CHANGE_ME":
                default_ace_dir = val
        except Exception:
            pass

    if not default_ace_dir:
        error_json(
            "ACE-Step path not configured",
            "Edit config.json and set ace_step_dir to your ACE-Step 1.5 installation path"
        )

    parser.add_argument("--ace-step-dir", default=default_ace_dir,
                        help="ACE-Step installation directory")
    parser.add_argument("--model", default=None,
                        help="DiT model variant (acestep-v15-turbo, acestep-v15-base, acestep-v15-xl-turbo, etc.)")
    parser.add_argument("--lm-model", default=None,
                        help="LM model (acestep-5Hz-lm-0.6B, acestep-5Hz-lm-1.7B, acestep-5Hz-lm-4B, or none)")
    parser.add_argument("--quality", default="standard", choices=["draft", "standard", "high", "max"],
                        help="Quality preset (overridable by specific params)")
    parser.add_argument("--format", default="flac", choices=["flac", "wav", "mp3", "wav32", "opus", "aac"],
                        help="Output audio format")
    parser.add_argument("--seed", type=int, default=-1, help="Random seed (-1 for random)")
    parser.add_argument("--batch", type=int, default=None, help="Batch size (number of variants)")
    parser.add_argument("--output", default=None, help="Output file path (for single output)")
    parser.add_argument("--output-dir", default="~/Music/claude-music-output",
                        help="Output directory for generated files")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- generate ---
    p_gen = sub.add_parser("generate", help="Text-to-music generation")
    p_gen.add_argument("--caption", "-c", default="", help="Music description/style tags")
    p_gen.add_argument("--lyrics", "-l", default="", help="Lyrics with structure tags")
    p_gen.add_argument("--instrumental", action="store_true", help="Instrumental only (no vocals)")
    p_gen.add_argument("--language", default="en", help="Vocal language code (en, zh, ja, etc.)")
    p_gen.add_argument("--bpm", type=int, default=None, help="Beats per minute (30-300)")
    p_gen.add_argument("--key", default=None, help="Musical key (e.g., 'C major', 'Am')")
    p_gen.add_argument("--time-sig", default=None, help="Time signature (2, 3, 4, 6)")
    p_gen.add_argument("--duration", type=float, default=60.0, help="Duration in seconds (10-600)")
    p_gen.add_argument("--inference-steps", type=int, default=None, help="Diffusion steps")
    p_gen.add_argument("--guidance-scale", type=float, default=None, help="CFG guidance scale")
    p_gen.add_argument("--shift", type=float, default=None, help="Timestep shift factor")
    p_gen.add_argument("--thinking", action="store_true", default=None, help="Enable LM thinking mode")
    p_gen.add_argument("--no-thinking", dest="thinking", action="store_false", help="Disable LM thinking")
    p_gen.set_defaults(func=cmd_generate)

    # --- cover ---
    p_cov = sub.add_parser("cover", help="Cover/style transfer from reference audio")
    p_cov.add_argument("--src-audio", required=True, help="Source audio file")
    p_cov.add_argument("--caption", "-c", default="", help="New style description")
    p_cov.add_argument("--lyrics", "-l", default="", help="New lyrics (optional)")
    p_cov.add_argument("--cover-strength", type=float, default=0.5,
                        help="Reference fidelity (0.0=reimagine, 1.0=faithful)")
    p_cov.add_argument("--instrumental", action="store_true")
    p_cov.add_argument("--language", default="en")
    p_cov.add_argument("--bpm", type=int, default=None)
    p_cov.add_argument("--key", default=None)
    p_cov.add_argument("--time-sig", default=None)
    p_cov.add_argument("--duration", type=float, default=-1.0)
    p_cov.add_argument("--inference-steps", type=int, default=None)
    p_cov.add_argument("--guidance-scale", type=float, default=None)
    p_cov.add_argument("--shift", type=float, default=None)
    p_cov.add_argument("--thinking", action="store_true", default=None)
    p_cov.add_argument("--no-thinking", dest="thinking", action="store_false")
    p_cov.set_defaults(func=cmd_cover)

    # --- repaint ---
    p_rep = sub.add_parser("repaint", help="Selective section regeneration")
    p_rep.add_argument("--src-audio", required=True, help="Source audio file")
    p_rep.add_argument("--start", type=float, default=0.0, help="Repaint start (seconds)")
    p_rep.add_argument("--end", type=float, default=-1.0, help="Repaint end (seconds, -1=end of file)")
    p_rep.add_argument("--caption", "-c", default="", help="Style description for repainted section")
    p_rep.add_argument("--lyrics", "-l", default="")
    p_rep.add_argument("--instrumental", action="store_true")
    p_rep.add_argument("--language", default="en")
    p_rep.add_argument("--bpm", type=int, default=None)
    p_rep.add_argument("--key", default=None)
    p_rep.add_argument("--duration", type=float, default=-1.0)
    p_rep.add_argument("--inference-steps", type=int, default=None)
    p_rep.add_argument("--guidance-scale", type=float, default=None)
    p_rep.add_argument("--shift", type=float, default=None)
    p_rep.add_argument("--thinking", action="store_true", default=None)
    p_rep.add_argument("--no-thinking", dest="thinking", action="store_false")
    p_rep.set_defaults(func=cmd_repaint)

    # --- extract ---
    p_ext = sub.add_parser("extract", help="Track separation (base model only)")
    p_ext.add_argument("--src-audio", required=True)
    p_ext.add_argument("--caption", "-c", default="")
    p_ext.add_argument("--inference-steps", type=int, default=None)
    p_ext.add_argument("--guidance-scale", type=float, default=None)
    p_ext.add_argument("--shift", type=float, default=None)
    p_ext.add_argument("--thinking", action="store_true", default=None)
    p_ext.add_argument("--no-thinking", dest="thinking", action="store_false")
    # extract doesn't need lyrics/bpm/key/etc, set defaults
    p_ext.set_defaults(func=cmd_extract, lyrics="", instrumental=False, language="en",
                       bpm=None, key=None, time_sig=None, duration=-1.0)

    # --- lego ---
    p_lego = sub.add_parser("lego", help="Add instrument layer (base model only)")
    p_lego.add_argument("--src-audio", required=True)
    p_lego.add_argument("--caption", "-c", default="", help="Description of layer to add")
    p_lego.add_argument("--lyrics", "-l", default="")
    p_lego.add_argument("--inference-steps", type=int, default=None)
    p_lego.add_argument("--guidance-scale", type=float, default=None)
    p_lego.add_argument("--shift", type=float, default=None)
    p_lego.add_argument("--thinking", action="store_true", default=None)
    p_lego.add_argument("--no-thinking", dest="thinking", action="store_false")
    p_lego.set_defaults(func=cmd_lego, instrumental=False, language="en",
                        bpm=None, key=None, time_sig=None, duration=-1.0)

    # --- complete ---
    p_comp = sub.add_parser("complete", help="Audio completion (base model only)")
    p_comp.add_argument("--src-audio", required=True)
    p_comp.add_argument("--caption", "-c", default="")
    p_comp.add_argument("--lyrics", "-l", default="")
    p_comp.add_argument("--duration", type=float, default=-1.0, help="Target total duration")
    p_comp.add_argument("--inference-steps", type=int, default=None)
    p_comp.add_argument("--guidance-scale", type=float, default=None)
    p_comp.add_argument("--shift", type=float, default=None)
    p_comp.add_argument("--thinking", action="store_true", default=None)
    p_comp.add_argument("--no-thinking", dest="thinking", action="store_false")
    p_comp.set_defaults(func=cmd_complete, instrumental=False, language="en",
                        bpm=None, key=None, time_sig=None)

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help(sys.stderr)
        error_json("No command specified", "Use: music_engine.py generate|cover|repaint|extract|lego|complete")

    try:
        args.func(args)
    except KeyboardInterrupt:
        log("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        error_json(f"Unexpected error: {e}", traceback.format_exc()[:500])


if __name__ == "__main__":
    main()
