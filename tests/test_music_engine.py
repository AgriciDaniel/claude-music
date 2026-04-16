"""Contract tests for music_engine.py.

Goals (per Refactor Plan R7):
  (a) Quality presets resolve to expected model/step/batch values.
  (b) JSON output contract is enforced (stdout = one JSON object).
  (c) Cover-mode parameter mapping: src_audio + cover_noise_strength (NOT
      reference_audio / audio_cover_strength — regression guard for the bug
      fixed in Session 1).
  (d) config.json has the CHANGE_ME placeholder or a valid absolute path.

These tests do NOT import torch or acestep — they must be GPU-free and run
in under 1 second so CI stays fast.
"""
from __future__ import annotations

import ast
import io
import json
import subprocess
from contextlib import redirect_stdout

import pytest


# ---------------------------------------------------------------------------
# (a) Quality preset contract
# ---------------------------------------------------------------------------

EXPECTED_PRESETS = {
    "draft":    {"model": "acestep-v15-turbo", "lm_model": None,                    "inference_steps": 8,  "guidance_scale": 0.0, "thinking": False, "batch_size": 4, "shift": 1.0},
    "standard": {"model": "acestep-v15-turbo", "lm_model": None,                    "inference_steps": 8,  "guidance_scale": 0.0, "thinking": False, "batch_size": 2, "shift": 1.0},
    "high":     {"model": "acestep-v15-turbo", "lm_model": "acestep-5Hz-lm-1.7B",  "inference_steps": 8,  "guidance_scale": 0.0, "thinking": True,  "batch_size": 2, "shift": 1.0},
    "max":      {"model": "acestep-v15-base",  "lm_model": "acestep-5Hz-lm-1.7B",  "inference_steps": 65, "guidance_scale": 4.0, "thinking": True,  "batch_size": 1, "shift": 6.0},
}


def test_quality_presets_structure():
    from music_engine import QUALITY_PRESETS

    assert set(QUALITY_PRESETS.keys()) == set(EXPECTED_PRESETS.keys()), (
        f"Preset names changed. Update refactor plan + parameters.md. "
        f"Expected {set(EXPECTED_PRESETS.keys())}, got {set(QUALITY_PRESETS.keys())}"
    )

    for name, expected in EXPECTED_PRESETS.items():
        actual = QUALITY_PRESETS[name]
        for key, value in expected.items():
            assert actual.get(key) == value, (
                f"Preset '{name}' field '{key}': expected {value!r}, got {actual.get(key)!r}"
            )


def test_max_preset_uses_base_model():
    """Guard: 'max' quality must NOT use turbo — base model is required for
    repaint/extract/lego/complete task types."""
    from music_engine import QUALITY_PRESETS

    assert QUALITY_PRESETS["max"]["model"] == "acestep-v15-base"
    assert QUALITY_PRESETS["max"]["inference_steps"] >= 50
    assert QUALITY_PRESETS["max"]["guidance_scale"] >= 1.0


def test_draft_preset_optimized_for_batch():
    """Guard: 'draft' ships batch_size=4 for random/exploration workflows."""
    from music_engine import QUALITY_PRESETS

    assert QUALITY_PRESETS["draft"]["batch_size"] == 4
    assert QUALITY_PRESETS["draft"]["inference_steps"] == 8  # turbo fast path


# ---------------------------------------------------------------------------
# (b) JSON output contract
# ---------------------------------------------------------------------------

def test_output_json_is_valid_stdout():
    """output_json() writes exactly one parseable JSON object to stdout."""
    from music_engine import output_json

    buf = io.StringIO()
    with redirect_stdout(buf):
        output_json({"success": True, "count": 3, "outputs": []})

    payload = buf.getvalue()
    parsed = json.loads(payload)  # will raise if not valid JSON
    assert parsed["success"] is True
    assert parsed["count"] == 3


def test_error_json_exits_nonzero_with_json():
    """error_json() writes JSON error to stdout AND exits with code 1."""
    from music_engine import error_json

    buf = io.StringIO()
    with redirect_stdout(buf):
        with pytest.raises(SystemExit) as exc_info:
            error_json("test error", suggestion="run --help")

    assert exc_info.value.code == 1
    parsed = json.loads(buf.getvalue())
    assert parsed["success"] is False
    assert parsed["error"] == "test error"
    assert parsed["suggestion"] == "run --help"


def test_help_subcommand_is_available():
    """Sanity: --help must return nonzero? No — argparse returns 0 on --help."""
    import sys as _sys
    from pathlib import Path as _Path

    engine = _Path(__file__).resolve().parents[1] / "skills" / "claude-music" / "scripts" / "music_engine.py"
    result = subprocess.run(
        [_sys.executable, str(engine), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"--help failed: {result.stderr}"
    assert "generate" in result.stdout
    assert "cover" in result.stdout
    assert "repaint" in result.stdout


# ---------------------------------------------------------------------------
# (c) Cover-mode parameter mapping — REGRESSION GUARD
# ---------------------------------------------------------------------------

def test_cover_mode_uses_src_audio_not_reference_audio(engine_source):
    """The ACE-Step API field is `src_audio` for cover mode, NOT
    `reference_audio`. The latter was a bug fixed in Session 1 —
    regression guard per Refactor Plan R7."""
    # AST walk: find cmd_cover function and look at its GenerationParams(...) call
    tree = ast.parse(engine_source)
    cover_fn = next(
        (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "cmd_cover"),
        None,
    )
    assert cover_fn is not None, "cmd_cover function not found in music_engine.py"

    gen_params_calls = [
        n for n in ast.walk(cover_fn)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "GenerationParams"
    ]
    assert gen_params_calls, "cmd_cover does not call GenerationParams(...)"

    kwargs = {kw.arg for kw in gen_params_calls[0].keywords if kw.arg}

    assert "src_audio" in kwargs, (
        "Cover mode must pass src_audio — this is the real ACE-Step API field. "
        "If you see this failing, someone reintroduced the Session-1 bug."
    )
    assert "cover_noise_strength" in kwargs, (
        "Cover mode must pass cover_noise_strength — this is the real "
        "ACE-Step API field. Not audio_cover_strength."
    )
    assert "reference_audio" not in kwargs, (
        "Cover mode must NOT pass reference_audio — that field name was "
        "wrong and was removed in Session 1. This is a regression."
    )
    assert "audio_cover_strength" not in kwargs, (
        "Cover mode must NOT pass audio_cover_strength — that field name "
        "was wrong. Use cover_noise_strength instead."
    )


def test_cover_task_type_string(engine_source):
    """Cover mode must set task_type='cover'."""
    tree = ast.parse(engine_source)
    cover_fn = next(
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "cmd_cover"
    )
    gen_params = next(
        n for n in ast.walk(cover_fn)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "GenerationParams"
    )
    task_type_kw = next((kw for kw in gen_params.keywords if kw.arg == "task_type"), None)
    assert task_type_kw is not None
    assert isinstance(task_type_kw.value, ast.Constant)
    assert task_type_kw.value.value == "cover"


# ---------------------------------------------------------------------------
# (d) config.json path resolution
# ---------------------------------------------------------------------------

def test_config_json_has_ace_step_dir_key(config_json):
    assert "ace_step_dir" in config_json
    assert "checkpoint_dir" in config_json
    assert "output_dir" in config_json
    assert "defaults" in config_json


def test_config_json_placeholder_or_absolute(config_json):
    """ace_step_dir must be either CHANGE_ME (pre-install) or a concrete path.
    Anything else suggests an accidentally-committed user path (VULN-002
    regression guard)."""
    ace_dir = config_json["ace_step_dir"]
    assert ace_dir == "CHANGE_ME" or ace_dir.startswith("/") or ace_dir.startswith("~"), (
        f"ace_step_dir should be 'CHANGE_ME' pre-install or an absolute path, "
        f"got: {ace_dir!r}. If a user's personal path leaked, run the installer "
        f"or reset to 'CHANGE_ME' before committing."
    )


def test_config_defaults_shape(config_json):
    """Guard: config defaults declare the keys music_engine.py expects."""
    defaults = config_json["defaults"]
    required = {"model", "quality", "format", "batch_size", "thinking", "language"}
    assert required.issubset(set(defaults.keys())), (
        f"config.defaults is missing keys: {required - set(defaults.keys())}"
    )


# ---------------------------------------------------------------------------
# (e) Security regression guards (from Session 1 audit)
# ---------------------------------------------------------------------------

def test_no_eval_in_scripts():
    """VULN-001 regression: eval() must not appear in any shell script."""
    from pathlib import Path as _P
    scripts = (_P(__file__).resolve().parents[1]
               / "skills" / "claude-music" / "scripts")
    for sh in scripts.glob("*.sh"):
        content = sh.read_text()
        # eval with a following space = the dangerous form; allow `evaluate`
        assert " eval " not in content and not content.startswith("eval "), (
            f"{sh.name} uses eval — replace with array execution "
            f"(VULN-001 regression)."
        )


def test_export_uses_no_overwrite():
    """VULN-006 regression: ffmpeg must use -n (no-overwrite), not -y."""
    from pathlib import Path as _P
    export_sh = (_P(__file__).resolve().parents[1]
                 / "skills" / "claude-music" / "scripts" / "music_export.sh")
    content = export_sh.read_text()
    # Every ffmpeg invocation in export must use -n, not -y
    # (allow mentions in comments)
    lines = [ln for ln in content.splitlines()
             if "ffmpeg " in ln and not ln.strip().startswith("#")]
    for ln in lines:
        assert " -y " not in ln, f"ffmpeg -y (overwrite) in export: {ln.strip()}"
