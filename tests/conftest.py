"""Shared pytest fixtures for claude-music tests.

These tests are designed to run WITHOUT a GPU or ACE-Step install — they cover
the CLI contract, preset resolution, config handling, and regression guards on
parameter mapping. Integration tests that exercise real generation are
out-of-scope for CI and live in `tests/integration/` (not yet created).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "skills" / "claude-music" / "scripts"
CONFIG_PATH = REPO_ROOT / "skills" / "claude-music" / "config.json"
CONFIG_EXAMPLE_PATH = REPO_ROOT / "skills" / "claude-music" / "config.example.json"


@pytest.fixture(scope="session")
def scripts_dir() -> Path:
    return SCRIPTS_DIR


@pytest.fixture(scope="session")
def config_json() -> dict:
    """Parsed config: the per-machine config.json when present (dev machines),
    else the tracked config.example.json (CI, fresh clones)."""
    path = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_EXAMPLE_PATH
    with path.open() as f:
        return json.load(f)


@pytest.fixture(scope="session")
def engine_source() -> str:
    """Raw source of music_engine.py — for AST / textual regression guards."""
    return (SCRIPTS_DIR / "music_engine.py").read_text()


@pytest.fixture(scope="session")
def engine_module(_scripts_importable):
    """Imported music_engine module — for parser/preset resolution tests.

    Importing is GPU-free: acestep is only imported inside initialize_acestep().
    """
    import music_engine
    return music_engine


@pytest.fixture(scope="session", autouse=True)
def _scripts_importable():
    """Make music_engine.py importable for direct function tests."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    yield
