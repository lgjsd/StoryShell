# StoryShell scaffold plan

## Goal

Create a small repo-owned OpenClaw stack for text adventure work with explicit mode separation:
- author
- play
- state

The first pass should optimize for low cognition load rather than narrative richness, with one StoryShell agent switching between those three modes.
Mode classification plus play-entry bootstrap should live in the always-loaded main-agent contract, not in a separate routing skill.

## Scaffold scope

### 1. Repo shape
- create `openclaw/`, `src/`, `scripts/`, `tests/`, and `docs/`
- keep the first tree small and inspectable

### 2. OpenClaw assets
- add one workspace template for `story-main`
- keep the routing/bootstrap contract in `AGENTS.md`
- add small skills for authoring, runtime, and state control
- add one config snippet for the StoryShell main agent

### 3. Materialization path
- add repo-owned `sync_storyshell_stack.py` and `install_storyshell_stack.py`
- follow the research-copilot one-way repo -> OpenClaw materialization model
- write a manifest and deterministic config batch payload

### 4. Override policy
- default install mode: `preserve`
- optional modes: `add`, `replace`
- `preserve` should install StoryShell skills/wrappers into the user's main workspace without adding worker agents
- avoid overwriting the user's existing workspace files when replacing the main agent; use a dedicated StoryShell workspace instead

### 5. Story package shape
- each story lives under `stories/<slug>/`
- reusable canon lives under `canon/`
- default reset source lives at `state/initial.json`
- disposable runtime state lives under `runs/` and `saves/`

### 6. Low-cognition helper surface
- add one package validator script
- add one state helper script
- materialize tiny wrappers instead of making agents rediscover repo paths

## Deferred for later
- actual story-turn execution engine
- richer game-package compiler/linter
- branching route authoring helpers
- sample playable game package
- migration helpers for versioned package schema
