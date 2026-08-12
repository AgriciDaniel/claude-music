#!/usr/bin/env python3
"""claude-music web dashboard server.

Python-stdlib-only local HTTP server: no pip installs, runs with the system
python3. Serves the single-page dashboard, shells out to music_engine.py (via
uv, inside the ACE-Step venv) for generation, streams NDJSON progress from its
stderr, and maintains per-track metadata sidecars in
<output_dir>/.claude-music/meta/ so ratings and "generate similar" survive the
lossy output filenames.

Security posture: binds 127.0.0.1 only, one generation at a time, all file
serving is restricted to the configured output_dir, subprocesses always use
argument lists (never a shell).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

WEBAPP_DIR = Path(__file__).resolve().parent
SKILL_DIR = WEBAPP_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
CONFIG_PATH = SKILL_DIR / "config.json"

AUDIO_EXTS = {".flac", ".wav", ".mp3", ".opus", ".aac", ".m4a", ".ogg"}
CAPTION_MAX = 512
LYRICS_MAX = 4096
GENERATION_TIMEOUT_SEC = 15 * 60

# Filename scheme produced by music_engine.py rename_outputs():
#   slug_YYYYmmdd-HHMM_NN[_stem][_sSEED].ext  (suffix -2/-3 on collision)
FILENAME_RE = re.compile(
    r"^(?P<slug>.+)_(?P<date>\d{8}-\d{4})_(?P<index>\d{2})"
    r"(?P<stem>(?:_[a-z0-9-]+)*?)(?:_s(?P<seed>\d+))?(?:-\d+)?$"
)


def load_config():
    """Read the skill's config.json. Returns {} when missing/broken."""
    try:
        with CONFIG_PATH.open() as f:
            cfg = json.load(f)
        return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}


def resolve_output_dir(cfg):
    raw = cfg.get("output_dir") or "~/Music/claude-music-output"
    return Path(os.path.expanduser(raw)).resolve()


def is_configured(cfg):
    ace = cfg.get("ace_step_dir", "")
    return bool(ace) and ace != "CHANGE_ME" and Path(os.path.expanduser(ace)).is_dir()


def merge_caption(user_text, tag_lists, limit=CAPTION_MAX):
    """User text + deduped comma-tags from the selected genres, capped."""
    seen = set()
    parts = []
    for chunk in [user_text or ""] + list(tag_lists or []):
        for tag in str(chunk).split(","):
            tag = tag.strip()
            key = tag.lower()
            if tag and key not in seen:
                seen.add(key)
                parts.append(tag)
    return ", ".join(parts)[:limit].rstrip(", ")


UPLOAD_MAX_BYTES = 200 * 1024 * 1024
SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]")

# Loudness targets and codecs per platform, from references/post-processing.md.
OPTIMIZE_TARGETS = {
    "spotify": {"lufs": -14.0, "ext": ".flac",
                "args": ["-ar", "44100", "-sample_fmt", "s16", "-c:a", "flac"]},
    "apple": {"lufs": -16.0, "ext": ".flac",
              "args": ["-ar", "44100", "-sample_fmt", "s16", "-c:a", "flac"]},
    "youtube": {"lufs": -14.0, "ext": ".mp3",
                "args": ["-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000"]},
    "tiktok": {"lufs": -14.0, "ext": ".m4a",
               "args": ["-c:a", "aac", "-b:a", "256k", "-ar", "44100"]},
    "podcast": {"lufs": -16.0, "ext": ".mp3",
                "args": ["-c:a", "libmp3lame", "-b:a", "192k", "-ac", "1"]},
}


def safe_upload_dest(output_dir, raw_name):
    """Sanitized, collision-free destination for an uploaded file, or None.

    Same whitelist as music_export.sh: basename only, [a-zA-Z0-9._-].
    Never returns an existing path (appends -2, -3, ...).
    """
    name = SAFE_NAME_RE.sub("", Path(unquote(str(raw_name))).name)
    stem, ext = os.path.splitext(name)
    stem = stem.strip(".")
    if not stem or ext.lower() not in AUDIO_EXTS:
        return None
    output_dir = Path(output_dir)
    dest = output_dir / f"{stem}{ext.lower()}"
    n = 2
    while dest.exists():
        dest = output_dir / f"{stem}-{n}{ext.lower()}"
        n += 1
    return dest


def ffprobe_info(path):
    """Container/stream info via ffprobe, or None when undecodable."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", str(path)],
            capture_output=True, text=True, timeout=30)
        info = json.loads(out.stdout)
        if not info.get("format") or not float(info["format"].get("duration", 0)):
            return None
        return info
    except Exception:
        return None


def parse_loudnorm_json(text):
    """Extract the loudnorm JSON block that ffmpeg prints on stderr."""
    for m in reversed(list(re.finditer(r"\{[^{}]*\}", text or ""))):
        try:
            obj = json.loads(m.group(0))
        except ValueError:
            continue
        if isinstance(obj, dict) and "input_i" in obj:
            return obj
    return None


def measure_loudness(path):
    """One loudnorm analysis pass. Returns the measured dict or None."""
    try:
        out = subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path),
             "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
             "-f", "null", "-"],
            capture_output=True, text=True, timeout=300)
        return parse_loudnorm_json(out.stderr)
    except Exception:
        return None


LOSSY_CODECS = {"mp3", "aac", "vorbis", "opus", "wmav2"}


def build_audit(probe, loudnorm):
    """Assemble an audit report from ffprobe + loudnorm measurements.

    Pure function: no subprocesses, unit-testable. Streaming targets are
    -14 LUFS / -1 dBTP (references/post-processing.md).
    """
    report = {"measured": {}, "findings": []}
    fmt = (probe or {}).get("format") or {}
    stream = next((s for s in (probe or {}).get("streams", [])
                   if s.get("codec_type") == "audio"), {})
    m = report["measured"]
    if fmt.get("duration"):
        m["duration_sec"] = round(float(fmt["duration"]), 1)
    if fmt.get("bit_rate"):
        m["bitrate_kbps"] = round(int(fmt["bit_rate"]) / 1000)
    m["codec"] = stream.get("codec_name")
    if stream.get("sample_rate"):
        m["sample_rate_hz"] = int(stream["sample_rate"])
    m["channels"] = stream.get("channels")

    def flag(level, text, fix=None):
        report["findings"].append({"level": level, "text": text, "fix": fix})

    if loudnorm:
        try:
            lufs = float(loudnorm["input_i"])
            tp = float(loudnorm["input_tp"])
            lra = float(loudnorm["input_lra"])
        except (KeyError, TypeError, ValueError):
            lufs = tp = lra = None
        if lufs is not None:
            m["loudness_lufs"] = lufs
            m["true_peak_dbtp"] = tp
            m["loudness_range_lu"] = lra
            if lufs < -17:
                flag("warn", f"Quiet for streaming: {lufs:.1f} LUFS vs the "
                     "-14 LUFS target. Platforms will not turn it up.",
                     "Run Optimize to normalize loudness.")
            elif lufs > -11:
                flag("warn", f"Loud: {lufs:.1f} LUFS. Streaming platforms "
                     "will turn it down and it may sound squashed.",
                     "Run Optimize to normalize loudness.")
            else:
                flag("ok", f"Loudness {lufs:.1f} LUFS sits well for "
                     "streaming (-14 LUFS target).")
            if tp is not None and tp > -1.0:
                flag("warn", f"True peak {tp:.2f} dBTP exceeds -1 dBTP: "
                     "clipping risk after lossy encoding.",
                     "Run Optimize; it enforces a -1 dBTP ceiling.")
            if lra is not None and lra < 3:
                flag("info", f"Loudness range {lra:.1f} LU is very narrow; "
                     "the track has little dynamic movement.")
    else:
        flag("info", "Loudness could not be measured.")

    if m.get("channels") == 1:
        flag("info", "Mono audio. Fine for podcasts, unusual for music.")
    if m.get("sample_rate_hz") and m["sample_rate_hz"] < 44100:
        flag("warn", f"Sample rate {m['sample_rate_hz']} Hz is below the "
             "44.1 kHz release standard.")
    if m.get("codec") in LOSSY_CODECS:
        flag("info", f"Lossy source ({m['codec']}). Re-encoding loses a "
             "little more quality each time; keep a lossless master if "
             "you have one.")
    return report


def suggest_fix(error_msg):
    """Map common engine failures to a plain-language suggestion."""
    msg = (error_msg or "").lower()
    if "out of memory" in msg or "cuda oom" in msg:
        return ("The GPU ran out of memory. Close other GPU-heavy apps, "
                "or try draft quality, a shorter duration, or a smaller batch. "
                "The max preset needs the most VRAM.")
    if "uv" in msg and ("not found" in msg or "no such file" in msg):
        return ("The uv package manager is missing. Install it with: "
                "curl -LsSf https://astral.sh/uv/install.sh | sh")
    if "change_me" in msg or "ace-step" in msg and "not" in msg:
        return "ACE-Step is not configured. Run install.sh from the repo."
    if "timed out" in msg:
        return ("Generation took longer than 15 minutes. Try a lower quality "
                "preset or shorter duration; first runs also download models.")
    if "no space left" in msg:
        return "The disk holding the output folder is full."
    return None


def free_vram_mb():
    """Free VRAM in MB via nvidia-smi, or None when unavailable."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5)
        return int(out.stdout.strip().splitlines()[0])
    except Exception:
        return None


def parse_progress_line(line):
    """One stderr line -> event dict or None (model logs are not JSON)."""
    line = line.strip()
    if not line.startswith("{"):
        return None
    try:
        obj = json.loads(line)
    except ValueError:
        return None
    if isinstance(obj, dict) and "event" in obj:
        return obj
    return None


def parse_range_header(value, size):
    """'bytes=a-b' -> (start, end) inclusive, or None when unusable."""
    m = re.match(r"^bytes=(\d*)-(\d*)$", value or "")
    if not m or size <= 0:
        return None
    start_s, end_s = m.groups()
    if start_s == "" and end_s == "":
        return None
    if start_s == "":
        # suffix range: last N bytes
        length = min(int(end_s), size)
        if length == 0:
            return None
        return size - length, size - 1
    start = int(start_s)
    if start >= size:
        return None
    end = min(int(end_s), size - 1) if end_s else size - 1
    if end < start:
        return None
    return start, end


def safe_audio_path(output_dir, raw_name):
    """Resolve a client-supplied file name inside output_dir, or None."""
    name = Path(unquote(raw_name)).name  # strips any directory components
    if not name or name.startswith("."):
        return None
    candidate = (output_dir / name).resolve()
    try:
        candidate.relative_to(output_dir)
    except ValueError:
        return None
    if candidate.suffix.lower() not in AUDIO_EXTS or not candidate.is_file():
        return None
    return candidate


def parse_engine_filename(stem):
    """Recover date/seed from a rename_outputs() stem, for orphan files."""
    m = FILENAME_RE.match(stem)
    if not m:
        return {}
    out = {"slug": m.group("slug")}
    if m.group("seed"):
        out["seed"] = int(m.group("seed"))
    try:
        out["created"] = datetime.strptime(
            m.group("date"), "%Y%m%d-%H%M").isoformat()
    except ValueError:
        pass
    return out


class MetaStore:
    """Sidecar JSON store in <output_dir>/.claude-music/meta/."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.meta_dir = self.output_dir / ".claude-music" / "meta"
        self._lock = threading.Lock()

    def _path(self, track_id):
        safe = Path(track_id).name
        if not safe or safe.startswith("."):
            return None
        return self.meta_dir / f"{safe}.json"

    def write(self, entry):
        path = self._path(entry["id"])
        if path is None:
            return
        with self._lock:
            self.meta_dir.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".json.tmp")
            with tmp.open("w") as f:
                json.dump(entry, f, indent=2)
                f.write("\n")
            os.replace(tmp, path)

    def read(self, track_id):
        path = self._path(track_id)
        if path is None or not path.is_file():
            return None
        try:
            with path.open() as f:
                return json.load(f)
        except Exception:
            return None

    def rate(self, track_id, rating):
        with self._lock:
            entry = self.read(track_id)
            if entry is None:
                return None
            entry["rating"] = rating
        self.write(entry)
        return entry

    def library(self):
        """Sidecar entries merged with orphan audio files, newest first."""
        entries = {}
        if self.meta_dir.is_dir():
            for p in self.meta_dir.glob("*.json"):
                try:
                    with p.open() as f:
                        e = json.load(f)
                except Exception:
                    continue
                if isinstance(e, dict) and e.get("id"):
                    entries[e["id"]] = e
        if self.output_dir.is_dir():
            for p in self.output_dir.iterdir():
                if not p.is_file() or p.suffix.lower() not in AUDIO_EXTS:
                    continue
                if p.stem in entries:
                    entries[p.stem].setdefault("file", p.name)
                    continue
                info = parse_engine_filename(p.stem)
                entries[p.stem] = {
                    "id": p.stem,
                    "file": p.name,
                    "caption": None,
                    "rating": None,
                    "orphan": True,
                    "created": info.get("created")
                    or datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                    **({"seed": info["seed"]} if "seed" in info else {}),
                }
        # Drop sidecars whose audio file was deleted by the user.
        result = [e for e in entries.values()
                  if (self.output_dir / e.get("file", "")).is_file()]
        result.sort(key=lambda e: e.get("created") or "", reverse=True)
        return result


class JobRunner:
    """Runs at most one music_engine.py generation subprocess at a time."""

    def __init__(self, cfg_loader):
        self.load_cfg = cfg_loader
        self.lock = threading.Lock()
        self._state_lock = threading.Lock()
        self.state = {"status": "idle", "pct": None, "stage": None,
                      "started_at": None, "result": None, "error": None,
                      "suggestion": None, "request": None}
        self.last_generation_sec = 30.0

    def snapshot(self):
        with self._state_lock:
            snap = dict(self.state)
        if snap["status"] == "generating" and snap["pct"] is None:
            # Time-based fallback when no pct events arrive, capped at 95%.
            elapsed = time.time() - (snap["started_at"] or time.time())
            snap["pct"] = min(0.95, elapsed / max(self.last_generation_sec, 1.0))
            snap["estimated"] = True
        return snap

    def _set(self, **kw):
        with self._state_lock:
            self.state.update(kw)

    def start(self, request, meta_store):
        """Begin generation. Returns error string, or None on accept."""
        cfg = self.load_cfg()
        if not is_configured(cfg):
            return "not_configured"
        if not self.lock.acquire(blocking=False):
            return "busy"
        self._set(status="loading", pct=None, stage="loading_model",
                  started_at=time.time(), result=None, error=None,
                  suggestion=None, request=request)
        threading.Thread(target=self._run, args=(request, cfg, meta_store),
                         daemon=True).start()
        return None

    def _build_cmd(self, request, cfg):
        defaults = cfg.get("defaults") or {}
        quality = request.get("quality") or defaults.get("quality") or "standard"
        fmt = defaults.get("format") or "flac"
        out_dir = str(resolve_output_dir(cfg))
        engine = str(SCRIPTS_DIR / "music_engine.py")
        cmd = ["uv", "run", "python3", engine,
               "--ace-step-dir", os.path.expanduser(cfg["ace_step_dir"]),
               "--progress",
               "--quality", quality,
               "--format", fmt,
               "--naming", "descriptive",
               "--output-dir", out_dir]
        if request.get("seed") is not None:
            cmd += ["--seed", str(int(request["seed"]))]
        if request.get("task") == "cover":
            # Covers default to one variant: kinder to VRAM, and variant
            # exploration matters less when following a source.
            cmd += ["--batch", str(int(request.get("batch") or 1))]
            cmd += ["cover", "--src-audio", request["src_path"],
                    "--cover-strength", str(request.get("cover_strength", 0.5))]
            if request.get("caption"):
                cmd += ["--caption", request["caption"]]
            if request.get("duration"):
                cmd += ["--duration", str(float(request["duration"]))]
        else:
            cmd += ["generate", "--caption", request["caption"],
                    "--duration", str(float(request.get("duration") or 60))]
        if request.get("lyrics"):
            cmd += ["--lyrics", request["lyrics"]]
        if request.get("instrumental"):
            cmd += ["--instrumental"]
        if request.get("bpm"):
            cmd += ["--bpm", str(int(request["bpm"]))]
        if request.get("key"):
            cmd += ["--key", str(request["key"])]
        return cmd, quality, out_dir

    def _run(self, request, cfg, meta_store):
        try:
            cmd, quality, out_dir = self._build_cmd(request, cfg)
            env = dict(os.environ,
                       TOKENIZERS_PARALLELISM="false",
                       TORCHAUDIO_USE_BACKEND="ffmpeg",
                       PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
            proc = subprocess.Popen(
                cmd, cwd=os.path.expanduser(cfg["ace_step_dir"]),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=env)

            def read_stderr():
                for line in proc.stderr:
                    ev = parse_progress_line(line)
                    if not ev:
                        continue
                    if ev["event"] == "stage":
                        stage = ev.get("stage")
                        self._set(stage=stage,
                                  status="generating" if stage == "generating"
                                  else "loading")
                    elif ev["event"] == "progress":
                        if ev.get("pct") is not None:
                            self._set(status="generating", pct=ev["pct"],
                                      stage=ev.get("stage") or None)

            t_err = threading.Thread(target=read_stderr, daemon=True)
            t_err.start()
            try:
                stdout, _ = proc.communicate(timeout=GENERATION_TIMEOUT_SEC)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                self._set(status="error", error="Generation timed out",
                          suggestion=suggest_fix("timed out"))
                return
            t_err.join(timeout=5)

            try:
                result = json.loads(stdout)
            except ValueError:
                tail = (stdout or "").strip()[-300:]
                err = f"Engine produced no JSON (exit {proc.returncode}): {tail}"
                self._set(status="error", error=err,
                          suggestion=suggest_fix(err))
                return
            if not result.get("success"):
                err = result.get("error") or "Generation failed"
                self._set(status="error", error=err,
                          suggestion=result.get("suggestion") or suggest_fix(err))
                return

            gen_sec = (result.get("timing") or {}).get("generation_sec")
            if gen_sec:
                self.last_generation_sec = float(gen_sec)
            for out in result.get("outputs") or []:
                p = Path(out.get("path", ""))
                if not p.name:
                    continue
                result_caption = (result.get("params") or {}).get("caption")
                entry = {
                    "id": p.stem,
                    "file": p.name,
                    "created": datetime.now().isoformat(timespec="seconds"),
                    "task": request.get("task") or "generate",
                    "caption": request["caption"] or result_caption or None,
                    "lyrics": request.get("lyrics"),
                    "instrumental": bool(request.get("instrumental")),
                    "bpm": request.get("bpm"),
                    "key": request.get("key"),
                    "duration": request.get("duration"),
                    "quality": quality,
                    "seed": out.get("seed"),
                    "genres": request.get("genres") or [],
                    "generation_sec": gen_sec,
                    "rating": None,
                }
                if request.get("similar_to"):
                    entry["similar_to"] = request["similar_to"]
                if request.get("task") == "cover":
                    entry["cover_strength"] = request.get("cover_strength")
                    entry["cover_of"] = request.get("src_file")
                meta_store.write(entry)
            self._set(status="done", pct=1.0, result=result)
        except Exception as e:
            self._set(status="error", error=str(e),
                      suggestion=suggest_fix(str(e)))
        finally:
            self.lock.release()


def validate_generate_request(body):
    """Returns (request, None) or (None, error string)."""
    if not isinstance(body, dict):
        return None, "Body must be a JSON object"
    task = body.get("task") or "generate"
    if task not in ("generate", "cover"):
        return None, "task must be generate or cover"
    caption = str(body.get("caption") or "").strip()
    if not caption and task == "generate":
        return None, "caption is required"
    if len(caption) > CAPTION_MAX:
        return None, f"caption exceeds {CAPTION_MAX} characters"
    req = {"caption": caption, "task": task}
    if task == "cover":
        src = Path(str(body.get("src_file") or "")).name
        if not src:
            return None, "src_file is required for cover"
        req["src_file"] = src
        strength = body.get("cover_strength", 0.5)
        try:
            strength = float(strength)
        except (TypeError, ValueError):
            return None, "cover_strength must be a number"
        if not 0.0 <= strength <= 1.0:
            return None, "cover_strength must be between 0.0 and 1.0"
        req["cover_strength"] = strength
    lyrics = body.get("lyrics")
    if lyrics:
        lyrics = str(lyrics)
        if len(lyrics) > LYRICS_MAX:
            return None, f"lyrics exceed {LYRICS_MAX} characters"
        req["lyrics"] = lyrics
    if task == "cover" and not body.get("duration"):
        pass  # cover defaults to the source length (engine duration -1)
    else:
        try:
            duration = float(body.get("duration") or 60)
        except (TypeError, ValueError):
            return None, "duration must be a number"
        if not 10 <= duration <= 600:
            return None, "duration must be between 10 and 600 seconds"
        req["duration"] = duration
    bpm = body.get("bpm")
    if bpm is not None and bpm != "":
        try:
            bpm = int(bpm)
        except (TypeError, ValueError):
            return None, "bpm must be an integer"
        if not 30 <= bpm <= 300:
            return None, "bpm must be between 30 and 300"
        req["bpm"] = bpm
    seed = body.get("seed")
    if seed is not None and seed != "":
        try:
            req["seed"] = int(seed)
        except (TypeError, ValueError):
            return None, "seed must be an integer"
    key = body.get("key")
    if key:
        key = str(key)[:20]
        if not re.match(r"^[A-Ga-g][#b]? ?(major|minor|maj|min|m)?$", key):
            return None, "key looks invalid (expected e.g. 'A minor')"
        req["key"] = key
    quality = body.get("quality")
    if quality:
        if quality not in ("draft", "standard", "high", "max"):
            return None, "quality must be draft, standard, high or max"
        req["quality"] = quality
    req["instrumental"] = bool(body.get("instrumental"))
    genres = body.get("genres")
    if isinstance(genres, list):
        req["genres"] = [str(g)[:40] for g in genres[:12]]
    similar_to = body.get("similar_to")
    if similar_to:
        req["similar_to"] = Path(str(similar_to)).name
    return req, None


class Handler(BaseHTTPRequestHandler):
    server_version = "claude-music-web/0.3"
    # Set by serve():
    runner: JobRunner = None
    meta_store: MetaStore = None

    def log_message(self, fmt, *args):  # quiet default access log
        pass

    # -- helpers ---------------------------------------------------------
    def _json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _file(self, path, content_type):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None
        if length <= 0 or length > 1_000_000:
            return None
        try:
            return json.loads(self.rfile.read(length))
        except Exception:
            return None

    def _output_dir(self):
        return resolve_output_dir(load_config())

    # -- GET -------------------------------------------------------------
    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path in ("/", "/index.html"):
                self._file(WEBAPP_DIR / "index.html", "text/html; charset=utf-8")
            elif path == "/api/status":
                cfg = load_config()
                snap = self.runner.snapshot()
                self._json({
                    "configured": is_configured(cfg),
                    "busy": snap["status"] in ("loading", "generating"),
                    "output_dir": str(resolve_output_dir(cfg)),
                    "free_vram_mb": free_vram_mb(),
                })
            elif path == "/api/genres":
                self._file(WEBAPP_DIR / "genres.json", "application/json")
            elif path == "/api/progress":
                self._json(self.runner.snapshot())
            elif path == "/api/library":
                self._json({"tracks": self.meta_store.library()})
            elif path.startswith("/api/audio/"):
                self._serve_audio(path[len("/api/audio/"):])
            else:
                self._json({"error": "not found"}, 404)
        except BrokenPipeError:
            pass
        except Exception as e:
            try:
                self._json({"error": str(e)}, 500)
            except Exception:
                pass

    def _serve_audio(self, raw_name):
        path = safe_audio_path(self._output_dir(), raw_name)
        if path is None:
            self._json({"error": "not found"}, 404)
            return
        size = path.stat().st_size
        ctype = {
            ".flac": "audio/flac", ".wav": "audio/wav", ".mp3": "audio/mpeg",
            ".opus": "audio/ogg", ".aac": "audio/aac", ".m4a": "audio/mp4",
            ".ogg": "audio/ogg",
        }.get(path.suffix.lower(), "application/octet-stream")
        rng = parse_range_header(self.headers.get("Range"), size)
        with path.open("rb") as f:
            if rng is None:
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                start, remaining = 0, size
            else:
                start, end = rng
                remaining = end - start + 1
                self.send_response(206)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(remaining))
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
            f.seek(start)
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except BrokenPipeError:
                    return
                remaining -= len(chunk)

    # -- upload / analyze / optimize --------------------------------------
    def _handle_upload(self):
        from urllib.parse import parse_qs
        query = parse_qs(urlparse(self.path).query)
        raw_name = (query.get("name") or [""])[0]
        out_dir = self._output_dir()
        dest = safe_upload_dest(out_dir, raw_name)
        if dest is None:
            exts = ", ".join(sorted(AUDIO_EXTS))
            self._json({"error": f"Unsupported file. Use one of: {exts}"}, 400)
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            self._json({"error": "Empty upload"}, 400)
            return
        if length > UPLOAD_MAX_BYTES:
            self._json({"error": "File exceeds the 200 MB upload limit"}, 413)
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        remaining = length
        try:
            with dest.open("wb") as f:
                while remaining > 0:
                    chunk = self.rfile.read(min(65536, remaining))
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)
        except Exception as e:
            dest.unlink(missing_ok=True)
            self._json({"error": f"Upload failed: {e}"}, 500)
            return
        if remaining > 0:
            dest.unlink(missing_ok=True)
            self._json({"error": "Upload was cut short, try again"}, 400)
            return
        probe = ffprobe_info(dest)
        if probe is None:
            dest.unlink(missing_ok=True)
            self._json({"error": "That file does not decode as audio"}, 400)
            return
        entry = {
            "id": dest.stem,
            "file": dest.name,
            "created": datetime.now().isoformat(timespec="seconds"),
            "source": "upload",
            "caption": None,
            "duration": round(float(probe["format"]["duration"]), 1),
            "rating": None,
        }
        self.meta_store.write(entry)
        self._json({"ok": True, "track": entry})

    def _track_and_path(self, body):
        """Resolve {file} from a POST body to (entry_or_None, path_or_None)."""
        raw = (body or {}).get("file") or ""
        path = safe_audio_path(self._output_dir(), raw)
        if path is None:
            return None, None
        return self.meta_store.read(path.stem), path

    def _handle_analyze(self):
        body = self._read_body() or {}
        entry, path = self._track_and_path(body)
        if path is None:
            self._json({"error": "track not found"}, 404)
            return
        if entry and entry.get("audit") and not body.get("refresh"):
            self._json({"ok": True, "audit": entry["audit"], "cached": True})
            return
        probe = ffprobe_info(path)
        if probe is None:
            self._json({"error": "ffprobe could not read this file"}, 500)
            return
        audit = build_audit(probe, measure_loudness(path))
        entry = entry or {"id": path.stem, "file": path.name, "caption": None,
                          "rating": None, "orphan": True,
                          "created": datetime.now().isoformat(timespec="seconds")}
        entry["audit"] = audit
        self.meta_store.write(entry)
        self._json({"ok": True, "audit": audit})

    def _handle_optimize(self):
        body = self._read_body() or {}
        entry, path = self._track_and_path(body)
        if path is None:
            self._json({"error": "track not found"}, 404)
            return
        target = body.get("target") or "spotify"
        spec = OPTIMIZE_TARGETS.get(target)
        if spec is None:
            self._json({"error": f"target must be one of: "
                        f"{', '.join(sorted(OPTIMIZE_TARGETS))}"}, 400)
            return
        measured = measure_loudness(path)
        if measured is None:
            self._json({"error": "Loudness measurement failed "
                        "(is ffmpeg installed?)"}, 500)
            return
        dest = safe_upload_dest(self._output_dir(),
                                f"{path.stem}_{target}{spec['ext']}")
        loudnorm = (
            f"loudnorm=I={spec['lufs']}:TP=-1:LRA=11:"
            f"measured_I={measured['input_i']}:"
            f"measured_TP={measured['input_tp']}:"
            f"measured_LRA={measured['input_lra']}:"
            f"measured_thresh={measured['input_thresh']}:"
            f"offset={measured.get('target_offset', 0)}:linear=true")
        try:
            run = subprocess.run(
                ["ffmpeg", "-hide_banner", "-nostdin", "-n", "-i", str(path),
                 "-af", loudnorm] + spec["args"] + [str(dest)],
                capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            self._json({"error": "Optimization timed out"}, 500)
            return
        if run.returncode != 0 or not dest.is_file():
            tail = (run.stderr or "").strip()[-200:]
            self._json({"error": f"ffmpeg failed: {tail}"}, 500)
            return
        new_entry = {
            "id": dest.stem,
            "file": dest.name,
            "created": datetime.now().isoformat(timespec="seconds"),
            "source": "optimized",
            "optimized_from": path.stem,
            "target": target,
            "caption": (entry or {}).get("caption"),
            "rating": None,
        }
        self.meta_store.write(new_entry)
        self._json({"ok": True, "track": new_entry})

    # -- POST ------------------------------------------------------------
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/generate":
                body = self._read_body()
                req, err = validate_generate_request(body)
                if err:
                    self._json({"error": err}, 400)
                    return
                if req.get("task") == "cover":
                    src = safe_audio_path(self._output_dir(), req["src_file"])
                    if src is None:
                        self._json({"error": "source track not found"}, 404)
                        return
                    req["src_path"] = str(src)
                start_err = self.runner.start(req, self.meta_store)
                if start_err == "busy":
                    self._json({"error": "A generation is already running"}, 409)
                elif start_err == "not_configured":
                    self._json({"error": "ACE-Step not configured. Run install.sh first."}, 503)
                else:
                    self._json({"started": True}, 202)
            elif path == "/api/rate":
                body = self._read_body() or {}
                track_id = str(body.get("id") or "")
                rating = body.get("rating")
                if rating not in (1, 2, 3, 4, 5):
                    self._json({"error": "rating must be 1-5"}, 400)
                    return
                entry = self.meta_store.rate(track_id, rating)
                if entry is None:
                    # Orphan track: create a minimal sidecar so the rating sticks.
                    path_audio = safe_audio_path(
                        self._output_dir(), body.get("file") or f"{track_id}.flac")
                    if path_audio is None:
                        self._json({"error": "unknown track"}, 404)
                        return
                    info = parse_engine_filename(path_audio.stem)
                    entry = {"id": path_audio.stem, "file": path_audio.name,
                             "caption": None, "rating": rating, "orphan": True,
                             "created": info.get("created")
                             or datetime.now().isoformat(timespec="seconds")}
                    self.meta_store.write(entry)
                self._json({"ok": True, "track": entry})
            elif path == "/api/upload":
                self._handle_upload()
            elif path == "/api/analyze":
                self._handle_analyze()
            elif path == "/api/optimize":
                self._handle_optimize()
            elif path == "/api/open-folder":
                folder = str(self._output_dir())
                opener = {"linux": "xdg-open", "darwin": "open",
                          "win32": "explorer"}.get(sys.platform, "xdg-open")
                subprocess.Popen([opener, folder],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                self._json({"ok": True, "folder": folder})
            else:
                self._json({"error": "not found"}, 404)
        except BrokenPipeError:
            pass
        except Exception as e:
            try:
                self._json({"error": str(e)}, 500)
            except Exception:
                pass


def serve(port=8765, max_port=8775):
    cfg = load_config()
    out_dir = resolve_output_dir(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    Handler.runner = JobRunner(load_config)
    Handler.meta_store = MetaStore(out_dir)
    last_err = None
    for p in range(port, max_port + 1):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", p), Handler)
            break
        except OSError as e:
            last_err = e
    else:
        print(f"ERROR: no free port in {port}-{max_port}: {last_err}",
              file=sys.stderr)
        sys.exit(1)
    print(f"claude-music web: http://127.0.0.1:{httpd.server_address[1]}",
          flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="claude-music web dashboard")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    serve(port=args.port, max_port=args.port + 10)
