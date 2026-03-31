---
name: story-state
description: Inspect and control mutable text-adventure run state using stable wrappers. Use when the user asks to show current state, save or load a checkpoint, rewind a run, branch a run, edit flags or relationships, reset a playthrough, or delete a run entirely.
---

# Story State

Treat state as a first-class reversible object.

## Rules
- Prefer wrappers and patch files over manual prose edits.
- Keep reset and delete distinct.
- Use deterministic state helpers when available.
- If an operation is destructive and the user's intent is unclear, ask once before proceeding.

## Current helper surface
- `storyshell-state show <state-file>`
- `storyshell-state reset <state-file> <initial-file>`
- `storyshell-state patch <state-file> <patch-file>`
