# StoryShell OpenClaw stack

This directory is the canonical source of truth for the shipped OpenClaw side of StoryShell.
The live `~/.openclaw/` home is only the materialized runtime copy.

Current scope:
- one StoryShell main-agent profile
- three internal modes: author, play, and state
- four low-cognition skills
- deterministic repo -> OpenClaw materialization
- explicit main-agent install modes

## Install modes

Use the materialization scripts deliberately:

- `preserve`
  - keep the user's current main/default agent
  - install StoryShell skills into `workspace/skills/`
  - install StoryShell wrappers into `workspace/bin/`
  - do not add any StoryShell worker agents

- `add`
  - keep everything from `preserve`
  - also add exactly one dedicated `story-main` agent
  - do not replace the user's main/default agent

- `replace`
  - replace the current main/default agent config with the StoryShell main-agent preset
  - keep the main/default slot, but point it at a dedicated StoryShell workspace

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

The sync/install scripts expect an **initialized OpenClaw home** plus a working
`openclaw config get agents.list --json` surface. So a blank `mktemp -d` alone is
not enough.

For a bounded rehearsal, use either:
- an already initialized temp/copy OpenClaw home, or
- a stubbed `openclaw` command in tests/CI.

Then inspect:
- `<openclaw-home>/workspace/skills/story-routing/`
- `<openclaw-home>/workspace/skills/story-authoring/`
- `<openclaw-home>/workspace/skills/story-runtime/`
- `<openclaw-home>/workspace/skills/story-state/`
- `<openclaw-home>/workspace/bin/`
- `<openclaw-home>/storyshell-manifest.json`
- `<openclaw-home>/tmp/storyshell-agent-config.batch.json`
