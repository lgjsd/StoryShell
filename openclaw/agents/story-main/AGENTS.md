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

## Routing
- author -> use `story-authoring`
- play -> use `story-runtime`
- state -> use `story-state`

## Boundaries
- Stay in this workspace; do not assume separate StoryShell worker agents exist.
- Never treat `/state` work as in-fiction action
- Never rewrite canon during play
- Prefer wrappers and scripts over freeform shell improvisation
