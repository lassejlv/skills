"""Register the restore hook per agent without disturbing other configuration."""

import json
from pathlib import Path
import sys
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import install_hooks  # noqa: E402


class InstallHooksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mentor-mode-install-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_main(self, *args):
        return install_hooks.main(list(args))

    def config(self, agent):
        return self.root / agent / "config.json"

    def test_preview_writes_nothing(self):
        path = self.config("codex")
        self.assertEqual(self.run_main("--agent", "codex", "--config", str(path)), 0)
        self.assertFalse(path.exists())

    def test_apply_preserves_other_settings_and_is_idempotent(self):
        path = self.config("claude")
        path.parent.mkdir()
        other = {"type": "command", "command": "echo other"}
        original = {"model": "x", "hooks": {
            "SessionStart": [{"matcher": "startup", "hooks": [other]}],
            "Stop": [{"hooks": [other]}]}}
        path.write_text(json.dumps(original))
        for _ in range(2):
            self.run_main("--agent", "claude", "--config", str(path), "--apply")
        config = json.loads(path.read_text())
        self.assertEqual(config["model"], "x")
        self.assertEqual(config["hooks"]["Stop"], original["hooks"]["Stop"])
        groups = config["hooks"]["SessionStart"]
        self.assertEqual(groups[0], original["hooks"]["SessionStart"][0])
        self.assertEqual(sum(install_hooks.is_ours(g) for g in groups), 1)
        self.assertEqual(json.loads(path.with_name("config.json.bak").read_text())["model"], "x")
        self.assertTrue(install_hooks.installed("claude", path))

        self.run_main("--agent", "claude", "--config", str(path), "--uninstall", "--apply")
        config = json.loads(path.read_text())
        self.assertEqual(config["hooks"]["SessionStart"], original["hooks"]["SessionStart"])
        self.assertFalse(install_hooks.installed("claude", path))

    def test_agent_dialects(self):
        for agent in ("claude", "codex", "gemini", "cursor"):
            path = self.config(agent)
            self.run_main("--agent", agent, "--config", str(path), "--apply")
            config = json.loads(path.read_text())
            with self.subTest(agent=agent):
                if agent == "cursor":
                    self.assertEqual(config["version"], 1)
                    [group] = config["hooks"]["sessionStart"]
                    self.assertIn("--agent cursor", group["command"])
                    continue
                [group] = config["hooks"]["SessionStart"]
                handler = group["hooks"][0]
                self.assertIn("--agent " + agent, handler["command"])
                if agent == "gemini":
                    self.assertNotIn("matcher", group)
                    self.assertEqual(handler["timeout"], 5000)
                else:
                    self.assertIn("compact", group["matcher"])
                    self.assertEqual(handler["timeout"], 5)

    def test_invalid_config_is_reported_not_overwritten(self):
        path = self.config("codex")
        path.parent.mkdir()
        path.write_text('{"hooks": []}')
        self.assertEqual(self.run_main("--agent", "codex", "--config", str(path), "--apply"), 1)
        self.assertEqual(path.read_text(), '{"hooks": []}')

    def test_paths_with_spaces_are_quoted(self):
        cmd = install_hooks.command("codex", python="/opt/my python/bin/python3")
        self.assertTrue(cmd.startswith('"/opt/my python/bin/python3" '))


if __name__ == "__main__":
    unittest.main()
