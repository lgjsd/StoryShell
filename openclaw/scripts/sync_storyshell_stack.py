#!/usr/bin/env python3
"""Sync the repo-owned StoryShell OpenClaw stack into an OpenClaw home."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from storyshell.openclaw_storyshell_stack import sync_storyshell_stack_main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(sync_storyshell_stack_main())
