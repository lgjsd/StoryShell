---
name: story-runtime
description: Run one turn of a structured text-adventure from reusable canon plus mutable run state. Use when interpreting player action, speaking as scene characters, narrating consequences, and producing bounded state updates without rewriting canon.
---

# Story Runtime

Run one turn at a time.

Assume the main agent has already resolved which story and which run are active before this skill is used.

## Turn contract
1. Read current state.
2. Read the active scene and relevant character files.
3. Interpret player input.
4. Resolve consequences.
5. Produce:
   - player-facing narration/dialogue
   - a compact state-update summary

## Rules
- Keep engine voice clear.
- Put strong personality into characters, not the engine.
- Never treat a meta state command as roleplay.
- Do not rewrite canon during play.
- Emit bounded state deltas against the active run, not edits to reusable canon.
