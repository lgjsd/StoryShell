# StoryShell progress

Last updated: 2026-03-31

## Current checkpoint

StoryShell is no longer just a plan document. The scaffold exists as a real repo-owned OpenClaw stack with the install/materialization seam, single-agent mode split, explicit play-entry/bootstrap contract, helper scripts, and focused tests all present.

The repo is still in scaffold phase, not gameplay phase.

## What is now built

### 1. Repo skeleton exists

The repo now has the intended top-level shape:
- `openclaw/`
- `src/storyshell/`
- `scripts/`
- `tests/`
- `docs/development/`

That means the project has crossed from "idea plus plan" into "inspectable scaffold with executable plumbing".

### 2. Repo-owned OpenClaw assets exist

The canonical OpenClaw-side assets are now present in `openclaw/`:
- one agent workspace template:
  - `story-main`
- one agent config snippet:
  - `openclaw/config/story-main-agent.json5`
- three specialist skills:
  - `story-authoring`
  - `story-runtime`
  - `story-state`

Mode classification and play-entry bootstrap now live in the always-loaded main agent contract instead of a separate routing skill.

The mode split is explicit inside one agent:
- `author` for creating, revising, importing, and repairing canon
- `play` for in-fiction turn resolution after story/run selection
- `state` for explicit save/load/reset/patch/branch style control of mutable run data

### 3. Materialization/install path exists

The repo now has a real one-way repo -> OpenClaw materialization path:
- `openclaw/scripts/sync_storyshell_stack.py`
- `openclaw/scripts/install_storyshell_stack.py`
- `src/storyshell/openclaw_storyshell_stack.py`

Implemented behavior:
- loads the existing OpenClaw agent list
- supports three main-agent modes:
  - `preserve`
  - `add`
  - `replace`
- writes a deterministic config batch payload
- writes a `storyshell-manifest.json`
- materializes the three specialist skills into the main workspace skill tree
- materializes stable wrappers into the main workspace `bin/` directory
- materializes a dedicated `story-main` workspace only when `add` or `replace` needs it

The main design choice here is already in place: install posture is explicit, instead of forcing one global replacement policy on every OpenClaw home.

### 4. Core play-entry protocol is now explicit

The main agent contract now spells out the hot-path bootstrap sequence for play:
- resolve which story is active
- resolve whether to continue, load, branch, restart, or initialize a run
- load only the manifest, active run, and relevant canon
- only then hand off to runtime turn resolution

The package contract is also now explicit:
- reusable canon lives under `stories/<slug>/canon/`
- reset defaults live at `stories/<slug>/state/initial.json`
- mutable run data lives under `stories/<slug>/runs/` and `stories/<slug>/saves/`

### 5. Low-cognition helper surface exists

Two small deterministic helpers now exist:
- `scripts/validate_storyshell_package.py`
- `scripts/storyshell_state_tool.py`

Current helper surface:
- package validation for the minimal game-package shape
- state inspection with `show`
- state reset from an initial JSON file
- shallow JSON patching for run-state edits

This is still deliberately small, but it is real and usable.

### 6. Focused verification exists

There is now a focused stack test file at:
- `tests/test_openclaw_storyshell_stack.py`

It currently checks:
- `preserve` mode keeps the existing main agent unchanged
- `add` mode adds exactly one dedicated `story-main`
- `replace` mode reuses the main slot while pointing it at the StoryShell workspace
- sync/materialization writes the expected manifest, batch payload, skills, and wrappers without creating unused worker workspaces

## Validation performed at this checkpoint

### Unit tests

Ran:

```bash
cd /home/javier/StoryShell
python3 -m unittest tests.test_openclaw_storyshell_stack -v
```

Result: 4 tests passed.

### Temp-home materialization rehearsal

A disposable temp-home sync rehearsal also succeeded with a stubbed `openclaw` CLI config surface.

What that confirmed in practice:
- the sync path can materialize the StoryShell assets into an OpenClaw home
- `preserve` mode leaves the existing main-agent config intact
- the manifest and wrapper scripts are written where expected
- the dedicated `story-main` workspace is no longer created unless a mode needs it

So the scaffold is not only statically present; its installation path has been exercised in a bounded rehearsal.

## What is still not built

This repo is still missing the actual game layer.

Not yet implemented:
- a real story-turn execution engine
- richer package compilation/linting beyond the minimal validator
- route/branch authoring helpers
- a sample playable game package
- save-slot / branching workflow beyond the current small state helper surface
- schema/version migration helpers
- broader end-to-end tests for real play loops

In other words: the shell exists, but the game machinery inside it is still mostly future work.

## Honest status

StoryShell is currently at **scaffold proved, gameplay deferred**.

That is good progress.
It means the boring but necessary installation and mode-separation work is already done early, which should make later story/runtime work less chaotic.

It also means this repo should not yet be described as a finished interactive fiction engine. Right now it is a cleanly-shaped OpenClaw scaffold for one.

## Likely next steps

Reasonable next moves from here:
1. add one tiny canonical sample game package
2. define the exact runtime turn contract between canon, mutable state, and player-facing output
3. sharpen the single-agent operating contract between author/play/state mode boundaries
4. expand tests from install plumbing into one or two full play-loop rehearsals
5. only then widen authoring/runtime capability

## Repo-state note

The repo now has an initial scaffold commit, but it is still very early-stage. The main thing that is solid is the install/materialization seam plus the single-agent mode split, not the gameplay layer.
