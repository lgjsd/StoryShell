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
                    }
                ]
            }
        }

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

    def test_replace_mode_reuses_main_slot(self) -> None:
        agents = self._merged_agents("replace")
        ids = [entry["id"] for entry in agents]
        self.assertIn("main", ids)
        self.assertNotIn(STORY_MAIN_AGENT_ID, ids)
        main_entry = next(entry for entry in agents if entry["id"] == "main")
        self.assertEqual(main_entry["workspace"], "/tmp/openclaw-home/workspace-story-main")
        self.assertNotIn("subagents", main_entry)

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


if __name__ == "__main__":
    unittest.main()
