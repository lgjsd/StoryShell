#!/usr/bin/env python3
"""Validate the minimal StoryShell package layout under stories/<slug>/."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_PATHS = [
    ("manifest.json", "file"),
    ("canon/world.md", "file"),
    ("canon/characters", "dir"),
    ("canon/scenes", "dir"),
    ("state/initial.json", "file"),
    ("runs", "dir"),
    ("saves", "dir"),
]


def _list_story_slugs(stories_root: Path) -> list[str]:
    if not stories_root.exists() or not stories_root.is_dir():
        return []
    return sorted(path.name for path in stories_root.iterdir() if path.is_dir())


def _resolve_story_root(package_root: Path, story_slug: str | None) -> tuple[str | None, Path | None, str | None]:
    stories_root = package_root / "stories"
    if story_slug:
        return story_slug, stories_root / story_slug, None

    slugs = _list_story_slugs(stories_root)
    if not slugs:
        return None, None, f"{stories_root} does not contain any story directories."
    if len(slugs) > 1:
        return None, None, f"{stories_root} contains multiple stories; pass --story <slug>."
    slug = slugs[0]
    return slug, stories_root / slug, None


def validate_package(package_root: Path, *, story_slug: str | None = None) -> dict[str, object]:
    resolved_root = package_root.expanduser().resolve()
    slug, story_root, selection_error = _resolve_story_root(resolved_root, story_slug)
    if selection_error is not None or story_root is None or slug is None:
        return {
            "packageRoot": str(resolved_root),
            "storyRoot": None,
            "storySlug": slug,
            "present": [],
            "missing": ["stories/<slug>/"],
            "valid": False,
            "error": selection_error,
        }

    missing: list[str] = []
    present: list[str] = []
    for relative, expected_kind in REQUIRED_PATHS:
        path = story_root / relative
        canonical_relative = f"stories/{slug}/{relative}"
        if expected_kind == "dir":
            exists = path.is_dir()
        else:
            exists = path.is_file()
        if exists:
            present.append(canonical_relative)
        else:
            missing.append(canonical_relative)
    return {
        "packageRoot": str(resolved_root),
        "storyRoot": str(story_root),
        "storySlug": slug,
        "present": present,
        "missing": missing,
        "valid": not missing,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a minimal StoryShell package under stories/<slug>/.")
    parser.add_argument("package_root", help="Path to the package root that contains stories/<slug>/.")
    parser.add_argument("--story", help="Explicit story slug when the package root contains multiple stories.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    report = validate_package(Path(args.package_root), story_slug=args.story)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        status = "valid" if report["valid"] else "invalid"
        print(f"package root: {report['packageRoot']}")
        if report["storyRoot"]:
            print(f"story root: {report['storyRoot']}")
        print(f"status: {status}")
        if report.get("error"):
            print(f"error: {report['error']}")
        if report["missing"]:
            print("missing:")
            for item in report["missing"]:
                print(f"- {item}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
