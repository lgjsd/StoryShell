---
name: story-authoring
description: Create, expand, revise, repair, or import structured text-adventure story packages. Use when building or editing reusable canon such as world files, character files, scene files, rules, endings, imports, or default initial state.
---

# Story Authoring

Create or revise the smallest correct set of reusable canon files.

## Rules
- Prefer one file per scene and one file per character.
- Keep secrets explicit in canon files instead of burying them in prose.
- Keep runtime state out of canon files.
- Keep reusable canon separate from mutable runs and saves.
- Validate the package before finishing.

## Default package shape
- `stories/<slug>/manifest.json`
- `stories/<slug>/canon/world.md`
- `stories/<slug>/canon/characters/`
- `stories/<slug>/canon/scenes/`
- `stories/<slug>/canon/rules/` when needed
- `stories/<slug>/state/initial.json`
- `stories/<slug>/runs/`
- `stories/<slug>/saves/`

## Boundary
- Edit canon plus default initial-state content.
- Do not patch active run files during ordinary authoring work.
