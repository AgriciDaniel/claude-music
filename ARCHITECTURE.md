# Architecture

This document explains the design decisions behind `claude-music`, particularly the ones that diverge from the upstream ACE-Step project's own Claude Code skill (`ACE-Step-1.5/.claude/skills/acestep/`).

## Python API vs REST API

**Decision**: `claude-music` invokes ACE-Step via its Python API using `uv run` and `sys.path.insert`. It does **not** start a REST API server.

**The alternative** (lifted from the ACE-Step team's own skill): their `acestep.sh` is a 44KB bash script that uses `curl` + `jq` against an ACE-Step REST server at `http://127.0.0.1:8001`. Users run `python api.py` (or the provided start script) before the skill can do anything.

**Why we chose Python API**:

1. **No server lifecycle for end users.** A REST server is a long-running process. Someone installing a Claude Code skill expects `/music generate "pop song"` to work, not `/music generate` then "error: server not reachable, run `python api.py` first". The Python-API path has zero servers to manage.

2. **Full `GenerationParams` access.** ACE-Step's REST completion endpoint hides fields like `infer_step`, `shift`, and `infer_method` behind coarse presets. Quality-critical parameters (Theme 2 of the research plan) need direct access. The Python API exposes every field of `GenerationParams`.

3. **One source of truth for errors.** The Python engine writes JSON to stdout and progress to stderr. A REST layer would add a second error surface (HTTP status + transport errors) that Claude has to reason about.

4. **Cost we accept**: 15-30s cold start per `/music` call to import `torch`, `diffusers`, and load the ACE-Step DiT model. This is acceptable because ACE-Step workflows are iteration-heavy — a typical user session is 3-10 generations, each ~30-120s on an RTX 5070 Ti, so cold-start is amortized. A REST server would amortize this further (one cold start per session) but at the cost above.

**When the REST approach would be better**:
- Multi-tenant deployments where many concurrent requests benefit from a warm model.
- CI/benchmark runs where the cold-start cost dominates the workload.
- If the ACE-Step team ships a long-running server binary as part of their package, revisit this decision.

**Flipping the decision**: if future work needs REST (e.g. browser-based dashboards), the `music_engine.py` subcommand handlers can be trivially reused — each is a pure function call on `AceStepHandler.generate_music()`. The refactor is isolated to `music_engine.sh` (replace `uv run` with `curl`) and config (add `api_url`). No sub-skill changes needed.

## Orchestrator + sub-skill layout

**Decision**: `skills/claude-music/` is a single orchestrator. Ten flat sibling sub-skills (`skills/claude-music-generate/`, `-cover/`, etc.) handle specific commands.

**Alternatives considered**:
- **Monolithic** (ACE-Step team's approach): one `SKILL.md` + one `acestep.sh`. Simpler to ship but the SKILL.md has to carry every command, every parameter, every failure mode — at scale it blows past the 500-line soft limit and the 5k-token instruction budget.
- **52-skill fragmentation** (bitwize-music-studio approach): one skill per operation. Marketplace discoverability improves slightly but users face a 52-item skill palette and context-window tax for any multi-step workflow.

**Why the orchestrator + 10 sub-skills sweet spot**:
- Orchestrator SKILL.md is 177 lines (well under 500) and handles routing only.
- Each sub-skill handles one coherent workflow (generate, cover, repaint, etc.) and loads only when that workflow is invoked (progressive disclosure).
- Cross-skill concerns (config resolution, quality presets, GPU detection) live in shared `scripts/` under the orchestrator, not duplicated.

## Symlink-based install

**Decision**: `install.sh` creates symlinks from `~/.claude/skills/claude-music*` to the checked-out repo, rather than copying files.

**Why**:
- Changes to a checked-out skill take effect immediately without reinstall.
- Uninstall is a single `rm` on the symlinks, with the source repo untouched.
- Contributors can `git pull` and have the changes live in Claude Code without a second step.

**Cost**: the repo location is baked into the symlink target; moving the repo requires re-running `install.sh`. Documented in the installer.

## Config-driven paths

**Decision**: a single `config.json` holds `ace_step_dir` (path to the ACE-Step install). Every script reads from it. No hardcoded user-specific paths.

**Why**: security audit VULN-002 found a leaked personal path in the initial version. `CHANGE_ME` placeholder + installer-driven replacement makes the repo shareable without leaking hostnames or usernames.

## JSON-over-stdout contract

**Decision**: every script writes a JSON object to stdout on success; progress and debug go to stderr.

**Why Claude parses this well**: a single `json.loads(stdout)` gets the file path, seed, duration, and metadata — no regex on human-readable output. `stderr` captures the cold-start progress bars without polluting the parseable result.

**Enforced by**: `tests/test_music_engine.py` (R7) will regress any script that violates this contract.
