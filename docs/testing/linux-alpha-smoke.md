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
- your default `~/.openclaw` is already initialized, or you have an already initialized alternate OpenClaw home

## Recommended install mode

For external testers, use `add`.

Why:
- it keeps the existing OpenClaw main/default agent posture intact
- it adds one dedicated `story-main` agent for StoryShell
- it materializes a dedicated `workspace-story-main/` without taking over the main slot

Avoid `replace` unless you are intentionally testing main-agent replacement behavior.

## 1. Choose an initialized OpenClaw home

The StoryShell installer expects an already initialized OpenClaw home with a working `openclaw config` surface. In the straightforward case, that means your normal default home at `~/.openclaw`.

If you want isolation, use a copy of an existing initialized OpenClaw home and pass that copy with `--openclaw-home`. A blank `mktemp -d` by itself is not enough.

## 2. Install StoryShell

From the repo root, the simplest path is:

```bash
python3 openclaw/scripts/install_storyshell_stack.py \
  --main-agent-mode add
```

That targets the default initialized OpenClaw home at `~/.openclaw`.

If you are deliberately testing against an alternate initialized home, run:

```bash
python3 openclaw/scripts/install_storyshell_stack.py \
  --openclaw-home "$TEST_OPENCLAW_HOME" \
  --main-agent-mode add
```

## 3. Inspect the installed assets

The smoke-test install is healthy if these paths exist under the OpenClaw home you targeted:

- `<openclaw-home>/workspace/skills/story-authoring/SKILL.md`
- `<openclaw-home>/workspace/skills/story-runtime/SKILL.md`
- `<openclaw-home>/workspace/skills/story-state/SKILL.md`
- `<openclaw-home>/workspace/bin/storyshell-validate`
- `<openclaw-home>/workspace-story-main/AGENTS.md`
- `<openclaw-home>/workspace-story-main/skills/story-authoring/SKILL.md`
- `<openclaw-home>/workspace-story-main/skills/story-runtime/SKILL.md`
- `<openclaw-home>/workspace-story-main/skills/story-state/SKILL.md`
- `<openclaw-home>/workspace-story-main/bin/storyshell-manifest`
- `<openclaw-home>/storyshell-manifest.json`
- `<openclaw-home>/tmp/storyshell-agent-config.batch.json`

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
