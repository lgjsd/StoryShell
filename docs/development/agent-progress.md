# StoryShell progress

Last updated: 2026-03-31

## Current checkpoint

StoryShell is no longer just a plan document. The scaffold exists as a real repo-owned OpenClaw stack with the install/materialization seam, agent split, skill set, helper scripts, and focused tests all present.

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
- three agent workspace templates:
  - `story-main`
  - `story-author`
  - `story-director`
- three agent config snippets:
  - `openclaw/config/story-main-agent.json5`
  - `openclaw/config/story-author-agent.json5`
  - `openclaw/config/story-director-agent.json5`
- four small skills:
  - `story-routing`
  - `story-authoring`
  - `story-runtime`
  - `story-state`

The role split is now explicit:
- `story-main` is the chat-facing router/orchestrator
- `story-author` is the writer/editor worker
- `story-director` is the lighter read/exec worker for scene/runtime guidance

### 3. Materialization/install path exists

The repo now has a real one-way repo -> OpenClaw materialization path:
- `openclaw/scripts/sync_storyshell_stack.py`
- `openclaw/scripts/install_storyshell_stack.py`
- `src/storyshell/openclaw_storyshell_stack.py`

Implemented behavior:
- loads the existing OpenClaw agent list
- merges in StoryShell workers
- supports three main-agent modes:
  - `preserve`
  - `add`
  - `replace`
- writes a deterministic config batch payload
- writes a `storyshell-manifest.json`
- materializes the four skills into the main workspace skill tree
- materializes dedicated StoryShell workspaces for `story-main`, `story-author`, and `story-director`
- materializes stable wrappers into each workspace `bin/` directory

The main design choice here is already in place: install posture is explicit, instead of forcing one global replacement policy on every OpenClaw home.

### 4. Low-cognition helper surface exists

Two small deterministic helpers now exist:
- `scripts/validate_storyshell_package.py`
- `scripts/storyshell_state_tool.py`

Current helper surface:
- package validation for the minimal game-package shape
- state inspection with `show`
- state reset from an initial JSON file
- shallow JSON patching for run-state edits

This is still deliberately small, but it is real and usable.

### 5. Focused verification exists

There is now a focused stack test file at:
- `tests/test_openclaw_storyshell_stack.py`

It currently checks:
- `preserve` mode keeps the existing main agent and widens `allowAgents`
- `add` mode adds a dedicated `story-main`
- `replace` mode reuses the main slot while pointing it at the StoryShell workspace
- sync/materialization writes the expected manifest, batch payload, skills, workspaces, and wrappers

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
- `preserve` mode produces the expected merged agent batch
- the manifest and wrapper scripts are written where expected
- the dedicated author/director/main workspaces are copied correctly

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
3. decide whether `story-director` remains a light orchestration worker or becomes a stronger runtime/referee agent
4. expand tests from install plumbing into one or two full play-loop rehearsals
5. only then widen authoring/runtime capability

## Repo-state note

At this checkpoint the repo contents exist locally, but there is not yet a committed history in Git. So the progress is real, but still pre-first-commit.
