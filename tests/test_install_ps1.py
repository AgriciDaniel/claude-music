"""Contract tests for install.ps1 (the Windows installer).

CI runs on Linux, so these are source-level guards rather than executions.
Both cover bugs that made the installer fail on a clean Windows 11 box:

  (a) Encoding: the file contains non-ASCII characters (em dashes). Windows
      PowerShell 5.1 decodes a BOM-less .ps1 as ANSI, which mangles those
      bytes, breaks string parsing, and aborts the script with a cascade of
      "missing terminator" errors. A UTF-8 BOM forces correct decoding.

  (b) PATH refresh: the uv bootstrap installs uv into %USERPROFILE%/.local/bin
      and updates the *persisted* user PATH, but the running process keeps its
      stale copy — so the `Test-Command uv` check on the next line fails and
      the installer exits 1 even though uv installed fine.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_PS1 = REPO_ROOT / "install.ps1"

UTF8_BOM = b"\xef\xbb\xbf"


def test_install_ps1_has_utf8_bom_if_non_ascii():
    """Non-ASCII content in a .ps1 requires a BOM for Windows PowerShell 5.1."""
    raw = INSTALL_PS1.read_bytes()
    body = raw[len(UTF8_BOM):] if raw.startswith(UTF8_BOM) else raw

    try:
        body.decode("ascii")
    except UnicodeDecodeError:
        assert raw.startswith(UTF8_BOM), (
            "install.ps1 contains non-ASCII characters but has no UTF-8 BOM. "
            "Windows PowerShell 5.1 reads BOM-less scripts as ANSI, which "
            "corrupts them and aborts the install with parser errors. Either "
            "save the file as UTF-8 with BOM or keep it pure ASCII."
        )


def test_uv_install_refreshes_path_before_check():
    """uv lands on the persisted PATH, not the current process's copy."""
    lines = INSTALL_PS1.read_text(encoding="utf-8-sig").splitlines()

    install_idx = next(
        (i for i, ln in enumerate(lines) if "astral.sh/uv/install.ps1" in ln),
        None,
    )
    assert install_idx is not None, "uv bootstrap line not found in install.ps1"

    check_idx = next(
        (
            i
            for i, ln in enumerate(lines[install_idx + 1:], start=install_idx + 1)
            if "Test-Command uv" in ln
        ),
        None,
    )
    assert check_idx is not None, "no `Test-Command uv` check after the uv bootstrap"

    between = lines[install_idx + 1:check_idx]
    assert any("$env:Path" in ln for ln in between), (
        "install.ps1 checks for uv immediately after installing it without "
        "refreshing $env:Path. The uv installer updates the persisted user "
        "PATH, but this process still has the old one, so the check fails and "
        "the installer exits 1 on a successful install."
    )


def test_config_json_is_written_without_bom():
    """PS 5.1's `Set-Content -Encoding utf8` emits a BOM that json.load rejects.

    A BOM'd config.json is worse than a missing one: load_config() swallows the
    decode error and silently falls back to built-in defaults, so the
    ace_step_dir the installer just detected is ignored and every generation
    fails with "ACE-Step not found".
    """
    text = INSTALL_PS1.read_text(encoding="utf-8-sig")

    config_writes = [
        ln
        for ln in text.splitlines()
        if "$CONFIG" in ln and ("Set-Content" in ln or "Out-File" in ln)
    ]
    assert not config_writes, (
        "install.ps1 writes config.json with a BOM-emitting cmdlet: "
        f"{config_writes!r}. Use "
        "[System.IO.File]::WriteAllText(..., [System.Text.UTF8Encoding]::new($false)) "
        "instead."
    )
