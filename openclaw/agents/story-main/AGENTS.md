# AGENTS.md

## Startup
1. Read SOUL.md
2. Read TOOLS.md
3. Read USER.md
4. Read MEMORY.md if present

## Core rule
Operate as one StoryShell brain.

Classify every request into exactly one mode:
- author
- play
- state

If ambiguous, ask one short clarifying question.

## Mode boundaries
- `author` -> create, revise, repair, import, or reorganize reusable story canon
- `play` -> run in-fiction turns against one selected story and one selected mutable run
- `state` -> inspect, save, load, branch, patch, reset, or delete mutable run state

If a request mixes fiction with save/load/reset/branch control, prefer `state` unless the user is clearly acting inside the story.

## Play-entry protocol
Before normal turn resolution in `play` mode:

1. Resolve the story.
   - If the user named a story, use it.
   - If exactly one story exists, use it.
   - If multiple stories exist and none is active, ask which story to play.
2. Resolve the run.
   - If the user explicitly asked to continue, load, restart, branch, or use a named save, obey that intent.
   - Otherwise prefer the current/most recent run when that choice is unambiguous.
   - If there is no run yet, initialize a new run from `stories/<slug>/state/initial.json`.
3. Load minimally.
   - Read only the manifest, current run state, active scene, and relevant canon.
   - Do not dump the entire story package into context unless needed.
4. Only after story + run are resolved, use `story-runtime` for the actual turn.

## Story package contract
Treat each story as one directory under `stories/<slug>/` with a strict reusable vs mutable split.

Reusable canon:
- `stories/<slug>/manifest.json`
- `stories/<slug>/canon/world.md`
- `stories/<slug>/canon/characters/`
- `stories/<slug>/canon/scenes/`
- `stories/<slug>/canon/rules/` when needed
- `stories/<slug>/state/initial.json`

Mutable / disposable runtime data:
- `stories/<slug>/runs/`
- `stories/<slug>/saves/`

Play mutates runs and saves, not canon.
Authoring edits canon and initial-state defaults, not active runs.

## Boundaries
- Stay in this workspace; do not assume separate StoryShell worker agents exist.
- Use `story-authoring` for author mode, `story-runtime` for resolved play turns, and `story-state` for mutable-state operations.
- Never treat `/state` work as in-fiction action.
- Never rewrite canon during play.
- Never treat `stories/<slug>/state/initial.json` as the live run file.
- Prefer wrappers and scripts over freeform shell improvisation.
