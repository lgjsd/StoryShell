# Linux Alpha Smoke Test

StoryShell is currently an OpenClaw scaffold, not a finished interactive-fiction engine.
This smoke test is only meant to prove:

- the repo-owned StoryShell assets install into a disposable OpenClaw home
- the dedicated StoryShell workspace is materialized correctly in `add` mode
- the sample package matches the current StoryShell package shape

## Assumptions

- Linux machine
- Node already installed
- OpenClaw already installed
- Python 3 available as `python3`
- you will use a disposable OpenClaw home, not `~/.openclaw`

## Recommended install mode

For external testers, use `add`.

Why:
- it keeps the existing OpenClaw main/default agent posture intact
- it adds one dedicated `story-main` agent for StoryShell
- it materializes a dedicated `workspace-story-main/` without taking over the main slot

Avoid `replace` unless you are intentionally testing main-agent replacement behavior.

## 1. Prepare a disposable OpenClaw home

The StoryShell installer expects an already initialized OpenClaw home with a working `openclaw config` surface.

Use any throwaway OpenClaw home you already initialized for testing, for example:

```bash
TEST_OPENCLAW_HOME="$(mktemp -d)"
# Populate this directory with an initialized OpenClaw home before continuing.
```

If your only initialized home is your personal one, make a copy outside `~/.openclaw` first and point StoryShell at the copy.

## 2. Install StoryShell into the disposable home

From the repo root:

```bash
python3 openclaw/scripts/install_storyshell_stack.py \
  --openclaw-home "$TEST_OPENCLAW_HOME" \
  --main-agent-mode add
```

This writes the StoryShell assets into the disposable home and applies the generated OpenClaw config batch there.

## 3. Inspect the installed assets

The smoke-test install is healthy if these paths exist:

- `$TEST_OPENCLAW_HOME/workspace/skills/story-authoring/SKILL.md`
- `$TEST_OPENCLAW_HOME/workspace/skills/story-runtime/SKILL.md`
- `$TEST_OPENCLAW_HOME/workspace/skills/story-state/SKILL.md`
- `$TEST_OPENCLAW_HOME/workspace/bin/storyshell-validate`
- `$TEST_OPENCLAW_HOME/workspace-story-main/AGENTS.md`
- `$TEST_OPENCLAW_HOME/workspace-story-main/skills/story-authoring/SKILL.md`
- `$TEST_OPENCLAW_HOME/workspace-story-main/skills/story-runtime/SKILL.md`
- `$TEST_OPENCLAW_HOME/workspace-story-main/skills/story-state/SKILL.md`
- `$TEST_OPENCLAW_HOME/workspace-story-main/bin/storyshell-manifest`
- `$TEST_OPENCLAW_HOME/storyshell-manifest.json`
- `$TEST_OPENCLAW_HOME/tmp/storyshell-agent-config.batch.json`

## 4. Validate the sample package

The repo-owned smoke-test package lives at:

- `examples/alpha-smoke-package/`

Run:

```bash
python3 scripts/validate_storyshell_package.py examples/alpha-smoke-package --json
```

The validator should resolve the single sample story under `stories/lantern-cellar/` and report `valid: true`.

## Current limits

- There is no finished story runtime engine yet.
- The sample package is only a package-shape probe, not a meaningful game.
- The state helper is still small: show, reset, and shallow patch.
- `preserve`, `add`, and `replace` only cover install posture and workspace materialization; they do not make StoryShell production-ready.
- Expect rough edges around real play loops, save workflows, and authoring ergonomics.
