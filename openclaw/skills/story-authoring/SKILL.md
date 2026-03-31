---
name: story-authoring
description: Create, expand, revise, or repair structured text-adventure game packages. Use when building world files, character files, scene files, route rules, endings, or initial state from user settings or when editing existing game canon.
---

# Story Authoring

Create or revise the smallest correct set of canon files.

## Rules
- Prefer one file per scene and one file per character.
- Keep secrets explicit in canon files instead of burying them in prose.
- Keep runtime state out of canon files.
- Validate the package before finishing.

## Default package shape
- `manifest.json`
- `world.md`
- `characters/`
- `scenes/`
- `state/initial.json`
- `saves/`
