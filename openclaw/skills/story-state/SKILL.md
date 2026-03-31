---
name: story-state
description: Inspect and control mutable text-adventure run state using stable wrappers. Use when the user asks to show current state, save or load a checkpoint, branch a run, restart from initial state, patch flags or relationships, or delete mutable run data.
---

# Story State

Treat state as a first-class reversible object.

## Rules
- Prefer wrappers and patch files over manual prose edits.
- Keep reset and delete distinct.
- Use deterministic state helpers when available.
- If an operation is destructive and the user's intent is unclear, ask once before proceeding.
- Operate on mutable files under `stories/<slug>/runs/` and `stories/<slug>/saves/`, not reusable canon under `stories/<slug>/canon/`.
- Treat `stories/<slug>/state/initial.json` as the reset source, not as the live run file.

## Story split
- Reusable: `stories/<slug>/manifest.json`, `stories/<slug>/canon/`, `stories/<slug>/state/initial.json`
- Mutable: `stories/<slug>/runs/`, `stories/<slug>/saves/`

Use this skill for the mutable side only.

## Current helper surface
- `storyshell-state show <state-file>`
- `storyshell-state reset <state-file> <initial-file>`
- `storyshell-state patch <state-file> <patch-file>`
