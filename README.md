# StoryShell

StoryShell is a scaffold for a low-cognition OpenClaw text-adventure stack.

Current scope:
- repo-owned OpenClaw assets
- deterministic repo -> OpenClaw materialization
- three-agent split: story-main, story-author, story-director
- four small skills: story-routing, story-authoring, story-runtime, story-state
- basic local helper scripts for package validation and run-state inspection/reset/patch

This repo is intentionally in scaffold phase. It aims to make the install/mode split boring before adding richer game logic.

## Design stance

- keep the engine calm
- keep the characters vivid
- keep state explicit and reversible
- keep cognition load low
- prefer small checklists and wrappers over prompt cleverness

## Install modes

The OpenClaw installer supports three main-agent modes:

- `preserve` — keep the user's current main agent; install StoryShell skills into the main workspace and add the author/director worker agents
- `add` — preserve the user's current main agent and also add a dedicated `story-main` agent
- `replace` — replace the current main/default agent config with the StoryShell main-agent preset while keeping the main agent id/default slot

## Initial repo layout

- `openclaw/` — canonical OpenClaw-side assets
- `src/storyshell/` — install/materialization helpers
- `scripts/` — small deterministic local helpers
- `tests/` — focused stack tests
- `docs/development/` — plan and design notes

## Progress notes

- scaffold plan: `docs/development/storyshell-scaffold-plan.md`
- current progress checkpoint: `docs/development/agent-progress.md`

## Scaffold verification

```bash
cd /home/javier/StoryShell
python3 -m unittest tests.test_openclaw_storyshell_stack -v
```
