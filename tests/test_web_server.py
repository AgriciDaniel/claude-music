"""GPU-free tests for the web dashboard server (skills/claude-music/webapp).

Same conventions as test_music_engine.py: pure-function unit tests, tmp_path
filesystem tests, textual security guards, plus one live loopback smoke test.
No GPU, no ACE-Step, no generation subprocess.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WEBAPP_DIR = REPO_ROOT / "skills" / "claude-music" / "webapp"


@pytest.fixture(scope="session")
def server_module():
    spec = importlib.util.spec_from_file_location(
        "cm_web_server", WEBAPP_DIR / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def server_source() -> str:
    return (WEBAPP_DIR / "server.py").read_text()


# ---------------------------------------------------------------------------
# (a) Caption merging
# ---------------------------------------------------------------------------

def test_merge_caption_dedups_tags(server_module):
    out = server_module.merge_caption(
        "dreamy track", ["lo-fi hip-hop, chill", "ambient, chill"])
    assert out.lower().count("chill") == 1
    assert out.startswith("dreamy track")


def test_merge_caption_caps_length(server_module):
    out = server_module.merge_caption("x" * 600, ["tag"])
    assert len(out) <= 512


def test_merge_caption_empty_inputs(server_module):
    assert server_module.merge_caption("", []) == ""


# ---------------------------------------------------------------------------
# (b) Metadata sidecar store
# ---------------------------------------------------------------------------

def test_meta_store_roundtrip_and_rating(server_module, tmp_path):
    store = server_module.MetaStore(tmp_path)
    (tmp_path / "song_20260812-1200_01_s42.flac").write_bytes(b"x")
    store.write({"id": "song_20260812-1200_01_s42",
                 "file": "song_20260812-1200_01_s42.flac",
                 "caption": "jazz piano", "rating": None,
                 "created": "2026-08-12T12:00:00"})
    lib = store.library()
    assert len(lib) == 1 and lib[0]["caption"] == "jazz piano"
    store.rate("song_20260812-1200_01_s42", 5)
    assert store.read("song_20260812-1200_01_s42")["rating"] == 5


def test_meta_store_lists_orphans_and_drops_deleted(server_module, tmp_path):
    store = server_module.MetaStore(tmp_path)
    (tmp_path / "beat_20260812-1300_01_s99.flac").write_bytes(b"x")
    store.write({"id": "ghost", "file": "ghost.flac", "caption": "gone",
                 "created": "2026-08-12T09:00:00"})
    lib = store.library()
    ids = {e["id"] for e in lib}
    assert "beat_20260812-1300_01_s99" in ids  # orphan audio surfaced
    assert "ghost" not in ids                  # sidecar without audio dropped
    orphan = next(e for e in lib if e["id"] == "beat_20260812-1300_01_s99")
    assert orphan["seed"] == 99 and orphan["orphan"] is True


def test_meta_store_rejects_traversal_ids(server_module, tmp_path):
    store = server_module.MetaStore(tmp_path)
    assert store._path("../../evil") == store.meta_dir / "evil.json"
    assert store._path(".hidden") is None


# ---------------------------------------------------------------------------
# (c) Audio path sanitization
# ---------------------------------------------------------------------------

def test_safe_audio_path_blocks_traversal(server_module, tmp_path):
    (tmp_path / "ok.flac").write_bytes(b"x")
    f = server_module.safe_audio_path
    assert f(tmp_path, "ok.flac") == (tmp_path / "ok.flac").resolve()
    assert f(tmp_path, "../etc/passwd") is None
    assert f(tmp_path, "..%2F..%2Fetc%2Fpasswd") is None
    assert f(tmp_path, "/etc/passwd") is None
    assert f(tmp_path, ".hidden.flac") is None
    assert f(tmp_path, "missing.flac") is None
    assert f(tmp_path, "notes.txt") is None


# ---------------------------------------------------------------------------
# (d) Range header parsing
# ---------------------------------------------------------------------------

def test_parse_range_header(server_module):
    f = server_module.parse_range_header
    assert f("bytes=0-", 1000) == (0, 999)
    assert f("bytes=100-199", 1000) == (100, 199)
    assert f("bytes=-200", 1000) == (800, 999)
    assert f("bytes=900-2000", 1000) == (900, 999)
    assert f("bytes=1000-", 1000) is None
    assert f("bytes=5-2", 1000) is None
    assert f("garbage", 1000) is None
    assert f(None, 1000) is None
    assert f("bytes=0-", 0) is None


# ---------------------------------------------------------------------------
# (e) Engine filename parsing (orphan recovery)
# ---------------------------------------------------------------------------

def test_parse_engine_filename(server_module):
    f = server_module.parse_engine_filename
    info = f("lo-fi-afro-latin_20260812-1548_01_s3128607774")
    assert info["seed"] == 3128607774
    assert info["created"].startswith("2026-08-12T15:48")
    assert f("some-random-download")== {}
    stem = f("mix_20260812-1548_02_vocals_s7")
    assert stem["seed"] == 7


# ---------------------------------------------------------------------------
# (f) NDJSON progress parsing
# ---------------------------------------------------------------------------

def test_parse_progress_line(server_module):
    f = server_module.parse_progress_line
    assert f('{"event": "progress", "pct": 0.4}')["pct"] == 0.4
    assert f('{"event": "stage", "stage": "generating"}')["stage"] == "generating"
    assert f("Loading DiT model: turbo...") is None
    assert f('{"no_event": 1}') is None
    assert f("{broken json") is None
    assert f("") is None


# ---------------------------------------------------------------------------
# (g) Request validation
# ---------------------------------------------------------------------------

def test_validate_generate_request(server_module):
    v = server_module.validate_generate_request
    req, err = v({"caption": "jazz piano", "duration": 60, "bpm": 90,
                  "seed": 42, "key": "A minor", "quality": "draft",
                  "genres": ["Jazz"], "instrumental": True})
    assert err is None
    assert req["bpm"] == 90 and req["seed"] == 42 and req["instrumental"]

    assert v({})[1] is not None                                # no caption
    assert v({"caption": "x" * 513})[1] is not None            # too long
    assert v({"caption": "x", "duration": 5})[1] is not None   # too short
    assert v({"caption": "x", "bpm": 999})[1] is not None      # bpm range
    assert v({"caption": "x", "seed": "abc"})[1] is not None   # bad seed
    assert v({"caption": "x", "quality": "ultra"})[1] is not None
    assert v({"caption": "x", "key": "H sharp; rm -rf"})[1] is not None
    assert v("not a dict")[1] is not None


def test_validate_sanitizes_similar_to(server_module):
    v = server_module.validate_generate_request
    req, err = v({"caption": "x", "similar_to": "../../etc/passwd"})
    assert err is None and req["similar_to"] == "passwd"


# ---------------------------------------------------------------------------
# (h) Security guards (textual, same style as test_no_eval_in_scripts)
# ---------------------------------------------------------------------------

def test_server_has_no_eval_or_shell_true(server_source):
    assert "eval(" not in server_source
    assert "shell=True" not in server_source


def test_server_binds_loopback_only(server_source):
    assert '"127.0.0.1"' in server_source
    assert '"0.0.0.0"' not in server_source


def test_engine_has_progress_flag(engine_module):
    parser = engine_module.build_parser()
    args = parser.parse_args(["--progress", "generate", "-c", "x"])
    assert args.progress is True
    import argparse as _ap
    assert engine_module.make_progress(_ap.Namespace(progress=False)) is None


# ---------------------------------------------------------------------------
# (i) Live loopback smoke test (no GPU, no subprocess)
# ---------------------------------------------------------------------------

def test_live_server_smoke(server_module, tmp_path, monkeypatch):
    handler = server_module.Handler
    monkeypatch.setattr(server_module, "load_config",
                        lambda: {"output_dir": str(tmp_path)})
    handler.runner = server_module.JobRunner(server_module.load_config)
    handler.meta_store = server_module.MetaStore(tmp_path)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        def get(path):
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}{path}", timeout=5) as r:
                return r.status, r.read()

        status, body = get("/api/status")
        assert status == 200
        data = json.loads(body)
        assert data["configured"] is False and data["busy"] is False

        status, body = get("/api/library")
        assert status == 200 and json.loads(body)["tracks"] == []

        status, body = get("/api/genres")
        assert status == 200 and len(json.loads(body)["genres"]) >= 20

        status, body = get("/")
        assert status == 200 and b"Claude Music" in body

        # Unconfigured generate is refused with 503.
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/generate",
            data=json.dumps({"caption": "test"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(req, timeout=5)
        assert exc.value.code == 503
    finally:
        httpd.shutdown()
        httpd.server_close()
