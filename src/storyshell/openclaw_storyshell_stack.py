"""Repo-owned OpenClaw StoryShell stack helpers."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from typing import Any, Mapping


STORY_MAIN_AGENT_ID = "story-main"
STORYSHELL_MANIFEST_VERSION = "storyshell_bootstrap_v0"
OPENCLAW_HOME_PLACEHOLDER = "__OPENCLAW_HOME__"
VALID_MAIN_AGENT_MODES = {"preserve", "add", "replace"}

REPO_ROOT = Path(__file__).resolve().parents[2]
OPENCLAW_ASSETS_ROOT = REPO_ROOT / "openclaw"
OPENCLAW_CONFIG_DIR = OPENCLAW_ASSETS_ROOT / "config"
OPENCLAW_AGENTS_DIR = OPENCLAW_ASSETS_ROOT / "agents"
OPENCLAW_SKILLS_DIR = OPENCLAW_ASSETS_ROOT / "skills"
SCRIPT_ROOT = REPO_ROOT / "scripts"

SKILL_SOURCES = {
    "story-authoring": OPENCLAW_SKILLS_DIR / "story-authoring",
    "story-runtime": OPENCLAW_SKILLS_DIR / "story-runtime",
    "story-state": OPENCLAW_SKILLS_DIR / "story-state",
}
WORKSPACE_TEMPLATES = {
    STORY_MAIN_AGENT_ID: OPENCLAW_AGENTS_DIR / "story-main",
}
AGENT_SNIPPET_PATHS = {
    STORY_MAIN_AGENT_ID: OPENCLAW_CONFIG_DIR / "story-main-agent.json5",
}
PACKAGE_VALIDATOR_SCRIPT = SCRIPT_ROOT / "validate_storyshell_package.py"
STATE_TOOL_SCRIPT = SCRIPT_ROOT / "storyshell_state_tool.py"


class StoryShellError(RuntimeError):
    """Raised when StoryShell stack validation or materialization fails."""


def current_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_mapping(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise StoryShellError(f"{path} must be an object.")
    return dict(value)


def _require_string(value: Any, *, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StoryShellError(f"{path} must be a non-empty string.")
    return value.strip()


def _deep_replace_placeholder(value: Any, *, openclaw_home: Path) -> Any:
    if isinstance(value, str):
        return value.replace(OPENCLAW_HOME_PLACEHOLDER, str(openclaw_home))
    if isinstance(value, list):
        return [_deep_replace_placeholder(item, openclaw_home=openclaw_home) for item in value]
    if isinstance(value, Mapping):
        return {key: _deep_replace_placeholder(item, openclaw_home=openclaw_home) for key, item in value.items()}
    return value


def load_agent_snippet(agent_id: str, *, openclaw_home: str | Path) -> dict[str, Any]:
    path = AGENT_SNIPPET_PATHS.get(agent_id)
    if path is None:
        raise StoryShellError(f"Unknown StoryShell agent id: {agent_id}")
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, Mapping):
        raise StoryShellError(f"{path.name} must contain one object.")
    return _deep_replace_placeholder(parsed, openclaw_home=Path(openclaw_home).expanduser().resolve())


def _copy_owned_directory(source_dir: Path, target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)


def _copy_workspace_template(source_root: Path, target_root: Path) -> list[str]:
    copied_files: list[str] = []
    for source_path in sorted(source_root.rglob("*")):
        if source_path.is_dir():
            continue
        relative_path = source_path.relative_to(source_root)
        target_path = target_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        copied_files.append(str(target_path))
    return copied_files


def _write_materialized_file(target_path: Path, *, content: str, executable: bool = False) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8")
    if executable:
        target_path.chmod(0o755)
    return str(target_path)


def _render_wrapper_script(*, body_lines: list[str]) -> str:
    return "\n".join(["#!/usr/bin/env bash", "set -euo pipefail", *body_lines, ""])


def _build_openclaw_config_env(*, config_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["OPENCLAW_CONFIG_PATH"] = str(config_path)
    return env


def _load_openclaw_config(config_path: Path, *, openclaw_command: str) -> dict[str, Any]:
    if not config_path.exists():
        raise StoryShellError(
            f"OpenClaw config not found at {config_path}. Run OpenClaw onboarding before installing StoryShell."
        )
    completed = subprocess.run(
        [openclaw_command, "config", "get", "agents.list", "--json"],
        capture_output=True,
        text=True,
        check=False,
        env=_build_openclaw_config_env(config_path=config_path),
    )
    if completed.returncode != 0:
        raise StoryShellError(
            "OpenClaw config read failed for "
            f"{config_path} with exit code {completed.returncode}: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    try:
        agents_list = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise StoryShellError(f"OpenClaw config read returned invalid JSON for {config_path}: {exc}") from exc
    return {"agents": {"list": agents_list}}


def _find_main_agent_index(agents_list: list[dict[str, Any]]) -> int:
    for index, entry in enumerate(agents_list):
        if entry.get("id") == "main":
            return index
    for index, entry in enumerate(agents_list):
        if entry.get("default") is True:
            return index
    raise StoryShellError("OpenClaw config does not define a main/default agent.")


def _upsert_agent(agent_list: list[dict[str, Any]], agent: dict[str, Any]) -> None:
    for index, entry in enumerate(agent_list):
        if entry.get("id") == agent.get("id"):
            agent_list[index] = dict(agent)
            return
    agent_list.append(dict(agent))


def build_storyshell_agent_batch(
    *,
    existing_config: Mapping[str, Any],
    openclaw_home: str | Path,
    main_agent_mode: str = "preserve",
    story_main_id: str = STORY_MAIN_AGENT_ID,
) -> list[dict[str, Any]]:
    if main_agent_mode not in VALID_MAIN_AGENT_MODES:
        raise StoryShellError(
            f"mainAgentMode must be one of {sorted(VALID_MAIN_AGENT_MODES)}, got {main_agent_mode!r}."
        )

    config = _require_mapping(existing_config, path="openclawConfig")
    agents = _require_mapping(config.get("agents"), path="openclawConfig.agents")
    existing_list_raw = agents.get("list")
    if not isinstance(existing_list_raw, list) or not existing_list_raw:
        raise StoryShellError("openclawConfig.agents.list must be a non-empty array.")

    merged_agents = [_require_mapping(entry, path=f"openclawConfig.agents.list[{index}]") for index, entry in enumerate(existing_list_raw)]
    main_index = _find_main_agent_index(merged_agents)
    main_entry = dict(merged_agents[main_index])
    main_id = _require_string(main_entry.get("id") or "main", path="openclawConfig.mainAgent.id")

    if main_agent_mode == "preserve":
        merged_agents[main_index] = main_entry
    elif main_agent_mode == "add":
        story_main = load_agent_snippet(STORY_MAIN_AGENT_ID, openclaw_home=openclaw_home)
        story_main["id"] = story_main_id
        story_main["default"] = False
        _upsert_agent(merged_agents, story_main)
    elif main_agent_mode == "replace":
        replacement = load_agent_snippet(STORY_MAIN_AGENT_ID, openclaw_home=openclaw_home)
        replacement["id"] = main_id
        if "default" in main_entry:
            replacement["default"] = main_entry["default"]
        merged_agents[main_index] = replacement

    return [{"path": "agents.list", "value": merged_agents}]


def build_storyshell_manifest(
    *,
    openclaw_home: Path,
    batch_file: Path,
    main_agent_mode: str,
    story_main_id: str,
    wrapper_commands: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    return {
        "manifestVersion": STORYSHELL_MANIFEST_VERSION,
        "materializedAt": current_timestamp(),
        "paths": {
            "openclawHome": str(openclaw_home),
            "repoRoot": str(REPO_ROOT),
            "pythonInterpreter": str(Path(sys.executable).resolve()),
            "openclawConfig": str(openclaw_home / "openclaw.json"),
            "configBatchFile": str(batch_file),
            "packageValidatorScript": str(PACKAGE_VALIDATOR_SCRIPT),
            "stateToolScript": str(STATE_TOOL_SCRIPT),
        },
        "defaults": {
            "mainAgentMode": main_agent_mode,
            "storyMainId": story_main_id,
        },
        "wrapperCommands": {key: dict(value) for key, value in wrapper_commands.items()},
    }


def _build_wrapper_scripts(*, python_interpreter: Path, manifest_path: Path) -> dict[str, str]:
    python_path = str(python_interpreter)
    return {
        "storyshell-python": _render_wrapper_script(body_lines=[f"exec {shlex.quote(python_path)} \"$@\""]),
        "storyshell-validate": _render_wrapper_script(
            body_lines=[f"exec {shlex.join([python_path, str(PACKAGE_VALIDATOR_SCRIPT)])} \"$@\""]
        ),
        "storyshell-state": _render_wrapper_script(
            body_lines=[f"exec {shlex.join([python_path, str(STATE_TOOL_SCRIPT)])} \"$@\""]
        ),
        "storyshell-manifest": _render_wrapper_script(
            body_lines=[f"exec cat {shlex.quote(str(manifest_path))}"]
        ),
    }


def _materialize_wrapper_group(wrapper_dir: Path, wrapper_scripts: Mapping[str, str]) -> dict[str, str]:
    written: dict[str, str] = {}
    for wrapper_name, content in wrapper_scripts.items():
        written[wrapper_name] = _write_materialized_file(wrapper_dir / wrapper_name, content=content, executable=True)
    return written


def _uses_dedicated_story_main_workspace(main_agent_mode: str) -> bool:
    return main_agent_mode in {"add", "replace"}


def _build_skill_targets(*, openclaw_home: Path, use_dedicated_story_main: bool) -> dict[str, dict[str, Path]]:
    targets = {
        "main": {name: openclaw_home / "workspace" / "skills" / name for name in SKILL_SOURCES},
    }
    if use_dedicated_story_main:
        targets[STORY_MAIN_AGENT_ID] = {
            name: openclaw_home / "workspace-story-main" / "skills" / name for name in SKILL_SOURCES
        }
    return targets


def sync_storyshell_stack(
    *,
    openclaw_home: str | Path = "~/.openclaw",
    batch_file: str | Path | None = None,
    apply_config: bool = False,
    openclaw_command: str = "openclaw",
    dry_run: bool = False,
    main_agent_mode: str = "preserve",
    story_main_id: str = STORY_MAIN_AGENT_ID,
) -> dict[str, Any]:
    resolved_home = Path(openclaw_home).expanduser().resolve()
    config_path = resolved_home / "openclaw.json"
    existing_config = _load_openclaw_config(config_path, openclaw_command=openclaw_command)
    batch_operations = build_storyshell_agent_batch(
        existing_config=existing_config,
        openclaw_home=resolved_home,
        main_agent_mode=main_agent_mode,
        story_main_id=story_main_id,
    )
    resolved_batch_file = (
        Path(batch_file).expanduser().resolve()
        if batch_file is not None
        else resolved_home / "tmp" / "storyshell-agent-config.batch.json"
    )
    manifest_path = resolved_home / "storyshell-manifest.json"
    use_dedicated_story_main = _uses_dedicated_story_main_workspace(main_agent_mode)

    workspace_targets = {
        "main": resolved_home / "workspace" / "bin",
    }
    if use_dedicated_story_main:
        workspace_targets[STORY_MAIN_AGENT_ID] = resolved_home / "workspace-story-main" / "bin"
    wrapper_commands = {
        key: {name: str(path / name) for name in _build_wrapper_scripts(python_interpreter=Path(sys.executable).resolve(), manifest_path=manifest_path)}
        for key, path in workspace_targets.items()
    }
    workspace_targets_report = {}
    if use_dedicated_story_main:
        workspace_targets_report[STORY_MAIN_AGENT_ID] = str(resolved_home / "workspace-story-main")
    skill_targets = _build_skill_targets(openclaw_home=resolved_home, use_dedicated_story_main=use_dedicated_story_main)
    skill_targets_report = {
        workspace_id: {name: str(path) for name, path in workspace_skill_targets.items()}
        for workspace_id, workspace_skill_targets in skill_targets.items()
    }

    report: dict[str, Any] = {
        "openclawHome": str(resolved_home),
        "configPath": str(config_path),
        "batchFile": str(resolved_batch_file),
        "manifestFile": str(manifest_path),
        "mainAgentMode": main_agent_mode,
        "storyMainId": story_main_id,
        "batchOperations": batch_operations,
        "ownedTargets": {
            "skills": skill_targets_report,
            "workspaces": workspace_targets_report,
            "manifest": str(manifest_path),
            "wrappers": wrapper_commands,
        },
        "configApplied": False,
        "dryRun": dry_run,
    }

    if dry_run:
        return report

    workspace_roots = {}
    if use_dedicated_story_main:
        workspace_roots[STORY_MAIN_AGENT_ID] = resolved_home / "workspace-story-main"

    copied_skills: dict[str, dict[str, str]] = {}
    copied_workspaces: dict[str, list[str]] = {}
    written_wrappers: dict[str, dict[str, str]] = {}

    for workspace_skill_targets in skill_targets.values():
        for target_path in workspace_skill_targets.values():
            target_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_batch_file.parent.mkdir(parents=True, exist_ok=True)

    for workspace_id, workspace_skill_targets in skill_targets.items():
        copied_skills[workspace_id] = {}
        for skill_name, source_dir in SKILL_SOURCES.items():
            target_path = workspace_skill_targets[skill_name]
            _copy_owned_directory(source_dir, target_path)
            copied_skills[workspace_id][skill_name] = str(target_path)

    for agent_id, workspace_root in workspace_roots.items():
        copied_workspaces[agent_id] = _copy_workspace_template(WORKSPACE_TEMPLATES[agent_id], workspace_root)

    wrapper_payload = _build_wrapper_scripts(
        python_interpreter=Path(sys.executable).resolve(),
        manifest_path=manifest_path,
    )
    for key, wrapper_dir in workspace_targets.items():
        written_wrappers[key] = _materialize_wrapper_group(wrapper_dir, wrapper_payload)

    manifest_payload = build_storyshell_manifest(
        openclaw_home=resolved_home,
        batch_file=resolved_batch_file,
        main_agent_mode=main_agent_mode,
        story_main_id=story_main_id,
        wrapper_commands=wrapper_commands,
    )

    resolved_batch_file.write_text(json.dumps(batch_operations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report["copiedSkills"] = copied_skills
    report["copiedWorkspaceFiles"] = copied_workspaces
    report["writtenWrappers"] = written_wrappers

    if apply_config:
        completed = subprocess.run(
            [openclaw_command, "config", "set", "--batch-file", str(resolved_batch_file)],
            capture_output=True,
            text=True,
            check=False,
            env=_build_openclaw_config_env(config_path=config_path),
        )
        report["configCommand"] = completed.args
        report["configStdout"] = completed.stdout
        report["configStderr"] = completed.stderr
        if completed.returncode != 0:
            raise StoryShellError(
                f"OpenClaw config apply failed with exit code {completed.returncode}: {completed.stderr.strip() or completed.stdout.strip()}"
            )
        report["configApplied"] = True

    return report


def _build_parser(*, install_mode: bool) -> argparse.ArgumentParser:
    description = (
        "Install the repo-owned StoryShell OpenClaw stack."
        if install_mode
        else "Sync the repo-owned StoryShell OpenClaw stack into an OpenClaw home."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--openclaw-home", default="~/.openclaw", help="OpenClaw home directory to materialize into.")
    parser.add_argument("--batch-file", help="Optional explicit path for the generated openclaw config batch payload.")
    parser.add_argument("--openclaw-command", default="openclaw", help="OpenClaw CLI command to use when applying config.")
    parser.add_argument("--dry-run", action="store_true", help="Plan file/config changes without copying files or applying config.")
    parser.add_argument(
        "--main-agent-mode",
        default="preserve",
        choices=sorted(VALID_MAIN_AGENT_MODES),
        help="How to handle the user's main/default agent.",
    )
    parser.add_argument(
        "--story-main-id",
        default=STORY_MAIN_AGENT_ID,
        help="Agent id to use when --main-agent-mode add creates a dedicated StoryShell main agent.",
    )
    if install_mode:
        parser.add_argument("--skip-config-apply", action="store_true", help="Materialize files and batch payload but do not call openclaw config set.")
    else:
        parser.add_argument("--apply-config", action="store_true", help="Also call openclaw config set with the generated batch payload.")
    parser.add_argument("--json", action="store_true", help="Emit the sync/install report as JSON.")
    return parser


def _run_cli(argv: list[str] | None, *, install_mode: bool) -> int:
    parser = _build_parser(install_mode=install_mode)
    args = parser.parse_args(argv)
    apply_config = (not args.skip_config_apply) if install_mode else bool(args.apply_config)
    try:
        report = sync_storyshell_stack(
            openclaw_home=args.openclaw_home,
            batch_file=args.batch_file,
            apply_config=apply_config,
            openclaw_command=args.openclaw_command,
            dry_run=bool(args.dry_run),
            main_agent_mode=args.main_agent_mode,
            story_main_id=args.story_main_id,
        )
    except StoryShellError as exc:
        if args.json:
            print(json.dumps({"status": "failed", "message": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"error: {exc}")
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"openclaw home: {report['openclawHome']}")
        print(f"batch file: {report['batchFile']}")
        print(f"main-agent mode: {report['mainAgentMode']}")
        if args.dry_run:
            print("mode: dry-run")
        elif report["configApplied"]:
            print("config: applied")
        else:
            print("config: batch written only")
    return 0


def sync_storyshell_stack_main(argv: list[str] | None = None) -> int:
    return _run_cli(argv, install_mode=False)


def install_storyshell_stack_main(argv: list[str] | None = None) -> int:
    return _run_cli(argv, install_mode=True)
