# StoryShell OpenClaw stack

This directory is the canonical source of truth for the shipped OpenClaw side of StoryShell.
The live `~/.openclaw/` home is only the materialized runtime copy.

Current scope:
- one StoryShell main-agent profile
- three internal modes: author, play, and state
- three low-cognition skills
- deterministic repo -> OpenClaw materialization
- explicit main-agent install modes
- always-loaded routing/bootstrap contract in the main agent

## Install modes

Use the materialization scripts deliberately:

- `replace`
  - default and primary path today
  - replace the current main/default agent config with the StoryShell main-agent preset
  - keep the main/default slot and the real main workspace at `workspace/`
  - materialize StoryShell main-agent contract files into `workspace/`
  - materialize StoryShell skills into `workspace/skills/`
  - materialize StoryShell wrappers into `workspace/bin/`
  - preserve the user's existing provider/model selection fields when present
  - risk: this overrides the actual main workspace/brain rather than redirecting to a side workspace

- `preserve`
  - keep the user's current main/default agent
  - install StoryShell skills into `workspace/skills/`
  - install StoryShell wrappers into `workspace/bin/`
  - do not add any StoryShell worker agents
  - do not touch provider/model choices

- `add`
  - secondary path; keep everything from `preserve`
  - also add exactly one dedicated `story-main` agent
  - materialize StoryShell skills, wrappers, and main-agent contract files into `workspace-story-main/`
  - do not replace the user's main/default agent
  - do not pin a provider/model for the added agent

The honest StoryShell contract right now is one brain on one workspace. `replace` is the supported/default behavior, and it is intentionally invasive.

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

The sync/install scripts expect an **initialized OpenClaw home** plus a readable
`agents` config surface. Either of these initialized shapes is enough:
- an explicit `agents.list`
- a defaults-only config with `agents.defaults.workspace`

So a blank `mktemp -d` alone is not enough.

For a bounded rehearsal, use either:
- an already initialized temp/copy OpenClaw home, or
- a stubbed `openclaw` command in tests/CI.

Then inspect:
- `<openclaw-home>/workspace/AGENTS.md` when using `replace`
- `<openclaw-home>/workspace/skills/story-authoring/`
- `<openclaw-home>/workspace/skills/story-runtime/`
- `<openclaw-home>/workspace/skills/story-state/`
- `<openclaw-home>/workspace/bin/`
- `<openclaw-home>/workspace-story-main/skills/` when using `add`
- `<openclaw-home>/workspace-story-main/bin/` when using `add`
- `<openclaw-home>/storyshell-manifest.json`
- `<openclaw-home>/tmp/storyshell-agent-config.batch.json`
