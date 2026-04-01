# StoryShell

StoryShell is an early scaffold for building a low-cognition text-adventure stack on top of OpenClaw.

Right now, the project is focused on the boring but important parts:
- repo-owned OpenClaw assets
- deterministic install/materialization into an OpenClaw home
- one StoryShell main-agent profile
- three operating modes: author, play, and state
- small helper scripts for package validation and save-state inspection/reset/patch
- a tiny sample package for alpha smoke testing

This is **not** a finished interactive-fiction engine yet. The goal of the current phase is to make installation, mode boundaries, and state handling explicit before adding richer gameplay/runtime behavior.

## Design stance

- keep the engine calm
- keep the characters vivid
- keep state explicit and reversible
- keep cognitive load low
- prefer small deterministic wrappers over prompt cleverness

## Current status

StoryShell is suitable for **Linux alpha smoke testing**.
It is not yet suitable for claiming polished gameplay, production readiness, or a complete authoring workflow.

## What the installer supports

The OpenClaw installer currently supports three main-agent modes:

- `replace` — default; replace the current main/default agent config with the StoryShell main-agent preset while keeping the main/default slot and the real main workspace at `<openclaw-home>/workspace`
- `preserve` — keep the user's current main agent and install StoryShell skills/wrappers into the main workspace without taking over the main agent contract
- `add` — keep the user's current main agent and also add one dedicated `story-main` agent on `workspace-story-main`

StoryShell's honest primary path right now is one brain on one workspace: `replace` overrides your actual main OpenClaw workspace and main agent.

Warning: `replace` writes StoryShell root contract files into `<openclaw-home>/workspace/` and reuses the real `main` slot. Do not run it against a workspace/brain you are not willing to override. Use a copied or disposable initialized OpenClaw home if you need safety. StoryShell assumes users already manage their own provider/model setup; it does not pin one for them.

## Quick start

Assumptions:
- OpenClaw is already installed
- Node is already installed
- Python 3 is available as `python3`
- you have an already initialized OpenClaw home, ideally a copied/disposable one for override testing

Clone the repo and install StoryShell into an initialized OpenClaw home:

```bash
git clone <repo-url>
cd StoryShell

python3 openclaw/scripts/install_storyshell_stack.py \
  --openclaw-home "$TEST_OPENCLAW_HOME"
```

If you really want the non-default add-on path, pass `--main-agent-mode add`, but that path is currently secondary to the override install and should be treated as deferred/less-proved behavior.

Then validate the sample package:

```bash
python3 scripts/validate_storyshell_package.py examples/alpha-smoke-package --json
```

If the current scaffold is behaving, the validator should resolve the sample story under `stories/lantern-cellar/` and report `valid: true`.

If you want to test against a different OpenClaw home, pass `--openclaw-home`, but it must point to an **already initialized** OpenClaw home with `openclaw.json`; an explicit `agents.list` is fine, and the defaults-only shape with `agents.defaults.workspace` is also fine. A blank temp directory is not enough.

For the fuller smoke-test checklist, see:
- `docs/testing/linux-alpha-smoke.md`

## How to start testing

The current practical way to start is:
1. install StoryShell into your existing initialized OpenClaw home
2. preferably use a copied or disposable initialized OpenClaw home, because the default path overrides the real main workspace
3. verify the installed StoryShell assets exist in `<openclaw-home>/workspace/`
4. validate the included sample package
5. report setup friction, install surprises, and contract mismatches

That is the honest current surface. The repo is proving install shape and package shape first, and the supported posture is a single StoryShell brain running from the actual main workspace.

## Repository layout

- `openclaw/` — canonical OpenClaw-side assets
- `src/storyshell/` — install/materialization helpers
- `scripts/` — deterministic local helper scripts
- `tests/` — focused stack tests
- `docs/development/` — design notes and progress checkpoints
- `examples/alpha-smoke-package/` — sample package for smoke testing

## Verification

Run the focused scaffold tests from the repo root:

```bash
python3 -m unittest tests.test_openclaw_storyshell_stack -v
```

## Docs

- scaffold plan: `docs/development/storyshell-scaffold-plan.md`
- progress checkpoint: `docs/development/agent-progress.md`
- Linux alpha smoke test: `docs/testing/linux-alpha-smoke.md`

## Current limits

- there is no finished story runtime engine yet
- the sample package is only a smoke-test package, not a meaningful game
- the current state helper is still small: show, reset, and shallow patch
- install modes prove posture and materialization, not production readiness
- the default install path is intentionally risky because it overrides the real main workspace
