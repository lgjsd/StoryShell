#!/usr/bin/env python3
"""Validate a minimal StoryShell game package layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REQUIRED_PATHS = [
    "manifest.json",
    "world.md",
    "characters",
    "scenes",
    "state/initial.json",
    "saves",
]


def validate_package(game_root: Path) -> dict[str, object]:
    missing: list[str] = []
    present: list[str] = []
    for relative in REQUIRED_PATHS:
        path = game_root / relative
        if path.exists():
            present.append(relative)
        else:
            missing.append(relative)
    return {
        "gameRoot": str(game_root),
        "present": present,
        "missing": missing,
        "valid": not missing,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a minimal StoryShell game package.")
    parser.add_argument("game_root", help="Path to the game package root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    report = validate_package(Path(args.game_root).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        status = "valid" if report["valid"] else "invalid"
        print(f"game root: {report['gameRoot']}")
        print(f"status: {status}")
        if report["missing"]:
            print("missing:")
            for item in report["missing"]:
                print(f"- {item}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
