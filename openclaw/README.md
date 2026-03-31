# StoryShell OpenClaw stack

This directory is the canonical source of truth for the shipped OpenClaw side of StoryShell.
The live `~/.openclaw/` home is only the materialized runtime copy.

Current scope:
- one chat-facing router profile
- one author worker
- one director worker
- four low-cognition skills
- deterministic repo -> OpenClaw materialization
- explicit main-agent install modes

## Install modes

Use the materialization scripts deliberately:

- `preserve`
  - keep the user's current main/default agent
  - install StoryShell skills into `workspace/skills/`
  - add `story-author` and `story-director`
  - widen the current main agent's `subagents.allowAgents`

- `add`
  - do everything from `preserve`
  - also add a dedicated `story-main` agent
  - do not replace the user's main/default agent

- `replace`
  - replace the current main/default agent config with the StoryShell main-agent preset
  - keep the main/default slot, but point it at a dedicated StoryShell workspace
  - still add `story-author` and `story-director`

The main point: StoryShell should be installable without forcing every user into the same main-agent posture.

## Install vs sync

- `sync_storyshell_stack.py`
  - materializes repo-owned files into one explicit OpenClaw home
  - writes the deterministic config batch payload
  - does **not** apply config unless `--apply-config` is passed

- `install_storyshell_stack.py`
  - uses the same materialization path
  - applies the generated batch payload by default
  - use `--skip-config-apply` when you want install-shaped file materialization without changing config yet

This is one-way materialization from repo to OpenClaw home, not bidirectional synchronization.

## Minimal rehearsal

```bash
cd /home/javier/StoryShell
TMP_OPENCLAW_HOME="$(mktemp -d)"
python3 openclaw/scripts/sync_storyshell_stack.py   --openclaw-home "$TMP_OPENCLAW_HOME"   --main-agent-mode preserve   --json
```

Then inspect:
- `$TMP_OPENCLAW_HOME/workspace/skills/story-routing/`
- `$TMP_OPENCLAW_HOME/workspace/skills/story-authoring/`
- `$TMP_OPENCLAW_HOME/workspace/skills/story-runtime/`
- `$TMP_OPENCLAW_HOME/workspace/skills/story-state/`
- `$TMP_OPENCLAW_HOME/workspace-story-author/`
- `$TMP_OPENCLAW_HOME/workspace-story-director/`
- `$TMP_OPENCLAW_HOME/storyshell-manifest.json`
- `$TMP_OPENCLAW_HOME/tmp/storyshell-agent-config.batch.json`
