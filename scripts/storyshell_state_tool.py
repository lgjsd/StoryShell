#!/usr/bin/env python3
"""Small deterministic helper for StoryShell run-state inspection and editing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any


class StateToolError(RuntimeError):
    pass


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateToolError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StateToolError(f"invalid json at {path}: {exc}") from exc


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _shallow_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _shallow_merge(dict(merged[key]), value)
        else:
            merged[key] = value
    return merged


def cmd_show(state_file: Path) -> int:
    payload = _load_json(state_file)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_reset(state_file: Path, initial_file: Path) -> int:
    payload = _load_json(initial_file)
    _write_json(state_file, payload)
    print(json.dumps({"status": "reset", "stateFile": str(state_file), "source": str(initial_file)}, indent=2, sort_keys=True))
    return 0


def cmd_patch(state_file: Path, patch_file: Path) -> int:
    state_payload = _load_json(state_file)
    patch_payload = _load_json(patch_file)
    if not isinstance(state_payload, dict) or not isinstance(patch_payload, dict):
        raise StateToolError("state and patch payloads must both be JSON objects.")
    merged = _shallow_merge(state_payload, patch_payload)
    _write_json(state_file, merged)
    print(json.dumps({"status": "patched", "stateFile": str(state_file), "patchFile": str(patch_file)}, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect and modify StoryShell run-state JSON files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("show", help="Print one state file.")
    show_parser.add_argument("state_file")

    reset_parser = subparsers.add_parser("reset", help="Replace one state file from the initial state.")
    reset_parser.add_argument("state_file")
    reset_parser.add_argument("initial_file")

    patch_parser = subparsers.add_parser("patch", help="Shallow-merge a JSON patch into one state file.")
    patch_parser.add_argument("state_file")
    patch_parser.add_argument("patch_file")

    args = parser.parse_args(argv)
    try:
        if args.command == "show":
            return cmd_show(Path(args.state_file).expanduser().resolve())
        if args.command == "reset":
            return cmd_reset(
                Path(args.state_file).expanduser().resolve(),
                Path(args.initial_file).expanduser().resolve(),
            )
        if args.command == "patch":
            return cmd_patch(
                Path(args.state_file).expanduser().resolve(),
                Path(args.patch_file).expanduser().resolve(),
            )
    except StateToolError as exc:
        print(json.dumps({"status": "failed", "message": str(exc)}, indent=2, sort_keys=True))
        return 1
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
