# Security Policy

## Reporting a vulnerability

**Do not open a public GitHub issue.** Email **agricidaniel@gmail.com** with the subject `claude-music security: <short description>`.

Include:
- Affected version / commit SHA
- Steps to reproduce
- Impact (what an attacker can do)
- Suggested remediation if you have one

Expected response: initial acknowledgement within 7 days. Full triage and patch target: 30 days for anything that leads to code execution, data exfiltration, or privilege escalation on the user's machine.

## Threat model

`claude-music` is a Claude Code skill that invokes a local ACE-Step installation and FFmpeg to produce audio files on the user's machine. It does not start network services, does not call external APIs at runtime, and does not upload generated audio.

The realistic threat surfaces are:

| Surface | Example risk | Mitigation in place |
|---|---|---|
| Shell script injection | User-supplied filename with `$(rm -rf ~)` in it | Basename sanitization `tr -cd 'a-zA-Z0-9._-'` in `music_export.sh`; no `eval` anywhere; array execution in `check_deps.sh`. |
| Arbitrary code execution via config | Malicious `ace_step_dir` in `config.json` pointing at attacker-controlled code | Installer writes the path; user is expected to review `config.json` in their own clone. |
| Caption / lyric injection | Prompt-injection string crafted by attacker to manipulate Claude after generation | Caption capped at 512 chars, lyrics at 4096 chars (ACE-Step limits). These are passed to ACE-Step as raw strings, not to shell. |
| Personal path leak in git history | A user path committed accidentally | `.gitignore` blocks `.claude/settings.json`; `config.json` ships with `CHANGE_ME` placeholder; installer replaces on-disk only. Test `test_config_json_placeholder_or_absolute` guards against committed personal paths. |
| FFmpeg overwrite | Destructive `ffmpeg -y` overwriting user audio | All platform exports use `-n` (no-overwrite) + `check_output()` existence guard. |

## Out of scope

- Vulnerabilities in **ACE-Step** itself — report those to `github.com/ace-step/ACE-Step`.
- Vulnerabilities in **FFmpeg** — report upstream.
- Vulnerabilities in **Claude Code** itself — report to Anthropic.
- Denial-of-service via pathological prompts (ACE-Step may hang on impossible requests; timeouts are the user's responsibility).
- Licensing of the generated audio — consult ACE-Step's license; `claude-music` adds no additional licensing claims.

## Past issues (fixed in Session 1)

Documented in git history for transparency:

- **VULN-001** `eval` in `check_deps.sh` — fixed by replacing with array execution.
- **VULN-002** Personal path leak in `config.json` — fixed with `CHANGE_ME` placeholder + installer-driven replacement.
- **VULN-003** Filename injection in `music_export.sh` — fixed with `tr -cd` sanitization.
- **VULN-004** Unclosed file handle in `music_engine.py` — fixed with `with` statement.
- **VULN-005** `.claude/settings.json` committed — removed and gitignored.
- **VULN-006** `ffmpeg -y` overwrite — replaced with `-n` + existence check.
- **VULN-008** Input length validation missing — added caption/lyrics caps.

Regression guards for all of the above live in `tests/test_music_engine.py`.
