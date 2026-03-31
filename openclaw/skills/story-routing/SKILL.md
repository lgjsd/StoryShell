---
name: story-routing
description: Route text-adventure requests into exactly one mode: author, play, or state. Use when a chat-facing agent must distinguish game creation/editing, in-fiction play, and meta state control such as save, load, rewind, branch, reset, or delete.
---

# Story Routing

Classify the request into exactly one mode.

## Mode rules
- `author` -> create, edit, repair, or expand the game package
- `play` -> in-fiction action, scene progression, character dialogue, or playthrough narration
- `state` -> inspect, save, load, rewind, branch, patch, reset, or delete run state

## Boundary rules
- If the request contains both fiction and meta control, prefer `state` unless the user is clearly acting inside the story.
- If the mode is unclear, ask one short clarifying question.
- Do not solve authoring or state work inside play mode.
