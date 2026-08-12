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
                       TORCHAUDIO_USE_BACKEND="ffmpeg")
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
                entry = {
                    "id": p.stem,
                    "file": p.name,
                    "created": datetime.now().isoformat(timespec="seconds"),
                    "task": "generate",
                    "caption": request["caption"],
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
    caption = str(body.get("caption") or "").strip()
    if not caption:
        return None, "caption is required"
    if len(caption) > CAPTION_MAX:
        return None, f"caption exceeds {CAPTION_MAX} characters"
    req = {"caption": caption}
    lyrics = body.get("lyrics")
    if lyrics:
        lyrics = str(lyrics)
        if len(lyrics) > LYRICS_MAX:
            return None, f"lyrics exceed {LYRICS_MAX} characters"
        req["lyrics"] = lyrics
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
