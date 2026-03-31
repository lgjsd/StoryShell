# StoryShell scaffold plan

## Goal

Create a small repo-owned OpenClaw stack for text adventure work with explicit mode separation:
- author
- play
- state

The first pass should optimize for low cognition load rather than narrative richness.

## Scaffold scope

### 1. Repo shape
- create `openclaw/`, `src/`, `scripts/`, `tests/`, and `docs/`
- keep the first tree small and inspectable

### 2. OpenClaw assets
- add workspace templates for `story-main`, `story-author`, and `story-director`
- add small skills for routing, authoring, runtime, and state control
- add config snippets for the three agents

### 3. Materialization path
- add repo-owned `sync_storyshell_stack.py` and `install_storyshell_stack.py`
- follow the research-copilot one-way repo -> OpenClaw materialization model
- write a manifest and deterministic config batch payload

### 4. Override policy
- default install mode: `preserve`
- optional modes: `add`, `replace`
- avoid overwriting the user's existing workspace files when replacing the main agent; use a dedicated StoryShell workspace instead

### 5. Low-cognition helper surface
- add one package validator script
- add one state helper script
- materialize tiny wrappers instead of making agents rediscover repo paths

## Deferred for later
- actual story-turn execution engine
- richer game-package compiler/linter
- branching route authoring helpers
- sample playable game package
- migration helpers for versioned package schema
