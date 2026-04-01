from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from storyshell.openclaw_storyshell_stack import (
    STORY_MAIN_AGENT_ID,
    StoryShellError,
    _load_openclaw_config,
    build_storyshell_agent_batch,
    sync_storyshell_stack,
)


class StoryShellStackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.existing_config = {
            "agents": {
                "list": [
                    {
                        "id": "main",
                        "default": True,
                        "workspace": "/tmp/openclaw/workspace",
                        "provider": "openai",
                        "model": "gpt-5.4",
                        "thinkingDefault": "medium",
                    }
                ]
            }
        }
        self.defaults_only_config = {
            "agents": {
                "defaults": {
                    "workspace": "/tmp/openclaw/workspace",
                    "provider": "openai",
                    "model": "gpt-5.4",
                    "thinkingDefault": "medium",
                }
            }
        }

    def _completed_process(
        self,
        *,
        returncode: int,
        args: list[str],
        stdout: str = "",
        stderr: str = "",
    ) -> mock.Mock:
        return mock.Mock(returncode=returncode, args=args, stdout=stdout, stderr=stderr)

    def _merged_agents(self, mode: str) -> list[dict[str, object]]:
        batch = build_storyshell_agent_batch(
            existing_config=self.existing_config,
            openclaw_home="/tmp/openclaw-home",
            main_agent_mode=mode,
        )
        self.assertEqual(batch[0]["path"], "agents.list")
        return batch[0]["value"]

    def test_preserve_mode_keeps_existing_main_only(self) -> None:
        agents = self._merged_agents("preserve")
        ids = [entry["id"] for entry in agents]
        self.assertEqual(ids, ["main"])
        main_entry = next(entry for entry in agents if entry["id"] == "main")
        self.assertEqual(main_entry["workspace"], "/tmp/openclaw/workspace")
        self.assertEqual(main_entry["provider"], "openai")
        self.assertEqual(main_entry["model"], "gpt-5.4")
        self.assertEqual(main_entry["thinkingDefault"], "medium")
        self.assertNotIn("subagents", main_entry)

    def test_add_mode_adds_exactly_one_dedicated_story_main(self) -> None:
        agents = self._merged_agents("add")
        ids = [entry["id"] for entry in agents]
        self.assertIn(STORY_MAIN_AGENT_ID, ids)
        self.assertEqual(ids.count(STORY_MAIN_AGENT_ID), 1)
        story_main = next(entry for entry in agents if entry["id"] == STORY_MAIN_AGENT_ID)
        self.assertFalse(story_main["default"])
        self.assertEqual(story_main["workspace"], "/tmp/openclaw-home/workspace-story-main")
        self.assertNotIn("subagents", story_main)
        self.assertNotIn("model", story_main)
        self.assertNotIn("thinkingDefault", story_main)

    def test_replace_mode_reuses_main_slot(self) -> None:
        agents = self._merged_agents("replace")
        ids = [entry["id"] for entry in agents]
        self.assertIn("main", ids)
        self.assertNotIn(STORY_MAIN_AGENT_ID, ids)
        main_entry = next(entry for entry in agents if entry["id"] == "main")
        self.assertEqual(main_entry["workspace"], "/tmp/openclaw-home/workspace-story-main")
        self.assertNotIn("subagents", main_entry)
        self.assertEqual(main_entry["provider"], "openai")
        self.assertEqual(main_entry["model"], "gpt-5.4")
        self.assertEqual(main_entry["thinkingDefault"], "medium")

    def test_preserve_mode_returns_no_batch_for_defaults_only_config(self) -> None:
        batch = build_storyshell_agent_batch(
            existing_config=self.defaults_only_config,
            openclaw_home="/tmp/openclaw-home",
            main_agent_mode="preserve",
        )
        self.assertEqual(batch, [])

    def test_add_mode_synthesizes_implicit_main_from_defaults_only_config(self) -> None:
        batch = build_storyshell_agent_batch(
            existing_config=self.defaults_only_config,
            openclaw_home="/tmp/openclaw-home",
            main_agent_mode="add",
        )
        self.assertEqual(batch[0]["path"], "agents.list")
        agents = batch[0]["value"]
        ids = [entry["id"] for entry in agents]
        self.assertEqual(ids.count("main"), 1)
        self.assertEqual(ids.count(STORY_MAIN_AGENT_ID), 1)
        main_entry = next(entry for entry in agents if entry["id"] == "main")
        self.assertEqual(main_entry["id"], "main")
        self.assertTrue(main_entry["default"])
        self.assertEqual(main_entry["workspace"], "/tmp/openclaw/workspace")
        self.assertNotIn("provider", main_entry)
        self.assertNotIn("model", main_entry)
        self.assertNotIn("thinkingDefault", main_entry)
        story_main = next(entry for entry in agents if entry["id"] == STORY_MAIN_AGENT_ID)
        self.assertFalse(story_main["default"])
        self.assertNotIn("provider", story_main)
        self.assertNotIn("model", story_main)
        self.assertNotIn("thinkingDefault", story_main)

    def test_replace_mode_does_not_copy_defaults_only_model_settings(self) -> None:
        batch = build_storyshell_agent_batch(
            existing_config=self.defaults_only_config,
            openclaw_home="/tmp/openclaw-home",
            main_agent_mode="replace",
        )
        self.assertEqual(batch[0]["path"], "agents.list")
        agents = batch[0]["value"]
        self.assertEqual([entry["id"] for entry in agents], ["main"])
        main_entry = agents[0]
        self.assertEqual(main_entry["workspace"], "/tmp/openclaw-home/workspace-story-main")
        self.assertTrue(main_entry["default"])
        self.assertNotIn("provider", main_entry)
        self.assertNotIn("model", main_entry)
        self.assertNotIn("thinkingDefault", main_entry)

    @mock.patch("storyshell.openclaw_storyshell_stack.subprocess.run")
    def test_load_openclaw_config_reads_agents_subtree(self, mock_run: mock.Mock) -> None:
        mock_run.return_value = mock.Mock(
            returncode=0,
            stdout=json.dumps(self.defaults_only_config["agents"]),
            stderr="",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "openclaw.json"
            config_path.write_text("{}\n", encoding="utf-8")
            loaded = _load_openclaw_config(config_path, openclaw_command="openclaw")
        self.assertEqual(loaded, self.defaults_only_config)
        self.assertEqual(mock_run.call_args.args[0], ["openclaw", "config", "get", "agents", "--json"])

    @mock.patch("storyshell.openclaw_storyshell_stack._load_openclaw_config")
    def test_sync_materializes_files_without_applying_config(self, mock_load_config: mock.Mock) -> None:
        mock_load_config.return_value = self.existing_config
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / "openclaw.json").write_text("{}\n", encoding="utf-8")
            report = sync_storyshell_stack(openclaw_home=home, dry_run=False, apply_config=False)
            self.assertEqual(report["mainAgentMode"], "preserve")
            self.assertTrue((home / "storyshell-manifest.json").exists())
            self.assertTrue((home / "tmp" / "storyshell-agent-config.batch.json").exists())
            self.assertTrue((home / "workspace" / "skills" / "story-authoring" / "SKILL.md").exists())
            self.assertTrue((home / "workspace" / "skills" / "story-state" / "SKILL.md").exists())
            self.assertTrue((home / "workspace" / "bin" / "storyshell-state").exists())
            self.assertFalse((home / "workspace-story-main").exists())
            batch_payload = json.loads((home / "tmp" / "storyshell-agent-config.batch.json").read_text(encoding="utf-8"))
            self.assertEqual(batch_payload[0]["path"], "agents.list")
            self.assertEqual(batch_payload[0]["value"][0]["workspace"], "/tmp/openclaw/workspace")

    @mock.patch("storyshell.openclaw_storyshell_stack.subprocess.run")
    @mock.patch("storyshell.openclaw_storyshell_stack._load_openclaw_config")
    def test_sync_preserve_defaults_only_skips_config_apply(self, mock_load_config: mock.Mock, mock_run: mock.Mock) -> None:
        mock_load_config.return_value = self.defaults_only_config
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / "openclaw.json").write_text("{}\n", encoding="utf-8")
            report = sync_storyshell_stack(openclaw_home=home, dry_run=False, apply_config=True)
            self.assertFalse(report["configApplied"])
            self.assertTrue((home / "workspace" / "skills" / "story-authoring" / "SKILL.md").exists())
            batch_payload = json.loads((home / "tmp" / "storyshell-agent-config.batch.json").read_text(encoding="utf-8"))
            self.assertEqual(batch_payload, [])
        mock_run.assert_not_called()

    @mock.patch("storyshell.openclaw_storyshell_stack._load_openclaw_config")
    def test_sync_add_mode_materializes_dedicated_story_main_skills(self, mock_load_config: mock.Mock) -> None:
        mock_load_config.return_value = self.existing_config
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / "openclaw.json").write_text("{}\n", encoding="utf-8")
            report = sync_storyshell_stack(
                openclaw_home=home,
                dry_run=False,
                apply_config=False,
                main_agent_mode="add",
            )
            self.assertEqual(report["mainAgentMode"], "add")
            self.assertTrue((home / "workspace" / "skills" / "story-authoring" / "SKILL.md").exists())
            self.assertTrue((home / "workspace-story-main" / "AGENTS.md").exists())
            self.assertTrue((home / "workspace-story-main" / "skills" / "story-authoring" / "SKILL.md").exists())
            self.assertTrue((home / "workspace-story-main" / "skills" / "story-runtime" / "SKILL.md").exists())
            self.assertTrue((home / "workspace-story-main" / "skills" / "story-state" / "SKILL.md").exists())
            self.assertTrue((home / "workspace-story-main" / "bin" / "storyshell-validate").exists())

    @mock.patch("storyshell.openclaw_storyshell_stack._load_openclaw_config")
    def test_sync_replace_mode_materializes_dedicated_story_main_skills(self, mock_load_config: mock.Mock) -> None:
        mock_load_config.return_value = self.existing_config
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / "openclaw.json").write_text("{}\n", encoding="utf-8")
            report = sync_storyshell_stack(
                openclaw_home=home,
                dry_run=False,
                apply_config=False,
                main_agent_mode="replace",
            )
            self.assertEqual(report["mainAgentMode"], "replace")
            self.assertTrue((home / "workspace-story-main" / "AGENTS.md").exists())
            self.assertTrue((home / "workspace-story-main" / "skills" / "story-authoring" / "SKILL.md").exists())
            self.assertTrue((home / "workspace-story-main" / "skills" / "story-runtime" / "SKILL.md").exists())
            self.assertTrue((home / "workspace-story-main" / "skills" / "story-state" / "SKILL.md").exists())
            self.assertTrue((home / "workspace-story-main" / "bin" / "storyshell-state").exists())

    @mock.patch("storyshell.openclaw_storyshell_stack.subprocess.run")
    @mock.patch("storyshell.openclaw_storyshell_stack._load_openclaw_config")
    def test_sync_apply_config_uses_batch_file_when_supported(
        self,
        mock_load_config: mock.Mock,
        mock_run: mock.Mock,
    ) -> None:
        mock_load_config.return_value = self.existing_config
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            config_path = home / "openclaw.json"
            config_path.write_text("{}\n", encoding="utf-8")
            batch_file = home / "tmp" / "storyshell-agent-config.batch.json"
            batch_command = ["openclaw", "config", "set", "--batch-file", str(batch_file)]
            mock_run.return_value = self._completed_process(returncode=0, args=batch_command)
            report = sync_storyshell_stack(openclaw_home=home, dry_run=False, apply_config=True)
        self.assertTrue(report["configApplied"])
        self.assertEqual(report["configApplyMode"], "batch-file")
        self.assertEqual(report["configCommand"], batch_command)
        self.assertEqual(report["configCommands"], [batch_command])
        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_run.call_args.args[0], batch_command)
        self.assertEqual(mock_run.call_args.kwargs["env"]["OPENCLAW_CONFIG_PATH"], str(config_path))

    @mock.patch("storyshell.openclaw_storyshell_stack.subprocess.run")
    @mock.patch("storyshell.openclaw_storyshell_stack._load_openclaw_config")
    def test_sync_apply_config_falls_back_when_batch_file_unsupported(
        self,
        mock_load_config: mock.Mock,
        mock_run: mock.Mock,
    ) -> None:
        mock_load_config.return_value = self.existing_config
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            config_path = home / "openclaw.json"
            config_path.write_text("{}\n", encoding="utf-8")
            batch_file = home / "tmp" / "storyshell-agent-config.batch.json"
            batch_command = ["openclaw", "config", "set", "--batch-file", str(batch_file)]
            fallback_command = ["openclaw", "config", "set", "agents.list"]

            def run_side_effect(command: list[str], **kwargs: object) -> mock.Mock:
                self.assertEqual(kwargs["env"]["OPENCLAW_CONFIG_PATH"], str(config_path))
                if command == batch_command:
                    return self._completed_process(
                        returncode=2,
                        args=command,
                        stderr="error: unknown option '--batch-file'",
                    )
                self.assertEqual(command[:4], fallback_command)
                self.assertEqual(command[-1], "--strict-json")
                json.loads(command[4])
                return self._completed_process(returncode=0, args=command)

            mock_run.side_effect = run_side_effect
            report = sync_storyshell_stack(openclaw_home=home, dry_run=False, apply_config=True)
        self.assertTrue(report["configApplied"])
        self.assertEqual(report["configApplyMode"], "strict-json-fallback")
        self.assertEqual(report["configCommands"][0], batch_command)
        self.assertEqual(report["configCommands"][1][:4], fallback_command)
        self.assertEqual(report["configCommands"][1][-1], "--strict-json")
        self.assertEqual(report["configFallbackReason"], "error: unknown option '--batch-file'")
        self.assertEqual(mock_run.call_count, 2)

    @mock.patch("storyshell.openclaw_storyshell_stack.subprocess.run")
    @mock.patch("storyshell.openclaw_storyshell_stack._load_openclaw_config")
    def test_sync_apply_config_raises_when_fallback_write_fails(
        self,
        mock_load_config: mock.Mock,
        mock_run: mock.Mock,
    ) -> None:
        mock_load_config.return_value = self.existing_config
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / "openclaw.json").write_text("{}\n", encoding="utf-8")
            batch_file = home / "tmp" / "storyshell-agent-config.batch.json"
            batch_command = ["openclaw", "config", "set", "--batch-file", str(batch_file)]

            def run_side_effect(command: list[str], **_: object) -> mock.Mock:
                if command == batch_command:
                    return self._completed_process(
                        returncode=2,
                        args=command,
                        stderr="error: unknown option '--batch-file'",
                    )
                return self._completed_process(
                    returncode=1,
                    args=command,
                    stderr="error: config path rejected",
                )

            mock_run.side_effect = run_side_effect
            with self.assertRaises(StoryShellError) as exc_info:
                sync_storyshell_stack(openclaw_home=home, dry_run=False, apply_config=True)
        self.assertIn("OpenClaw config apply fallback failed", str(exc_info.exception))
        self.assertIn("agents.list", str(exc_info.exception))


if __name__ == "__main__":
    unittest.main()
