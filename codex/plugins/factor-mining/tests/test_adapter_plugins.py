import json
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[2]


class AdapterPluginTests(unittest.TestCase):
    def _read_json(self, path: Path):
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def _text_files(self):
        ignored_dirs = {".git", "__pycache__"}
        for path in REPO_ROOT.rglob("*"):
            if any(part in ignored_dirs for part in path.parts):
                continue
            if path.is_file():
                try:
                    yield path, path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue

    def test_removed_legacy_open_adapter_references(self):
        banned_terms = ("open" + "code", "Open" + "Code")

        self.assertFalse((REPO_ROOT / banned_terms[0]).exists())
        for path, text in self._text_files():
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                for term in banned_terms:
                    self.assertNotIn(term, text)

    def test_claude_code_plugin_is_self_contained(self):
        plugin_root = REPO_ROOT / "claude-code"
        manifest = self._read_json(plugin_root / ".claude-plugin" / "plugin.json")
        skill = plugin_root / "skills" / "factor-mining" / "SKILL.md"
        scripts = plugin_root / "scripts"

        self.assertEqual(manifest["name"], "factor-mining")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue(skill.exists())
        self.assertTrue((scripts / "factor_api.py").exists())
        self.assertTrue((scripts / "factor_setup.py").exists())
        self.assertTrue((scripts / "factor_upload_backtest.py").exists())
        self.assertTrue((scripts / "factor_mining_agent_lib" / "api.py").exists())
        self.assertNotIn("../codex", skill.read_text(encoding="utf-8"))

    def test_openclaw_plugin_manifest_and_skill_are_present(self):
        plugin_root = REPO_ROOT / "openclaw"
        manifest = self._read_json(plugin_root / "openclaw.plugin.json")
        skill = plugin_root / "skills" / "factor-mining" / "SKILL.md"
        scripts = plugin_root / "scripts"

        self.assertEqual(manifest["name"], "factor-mining")
        self.assertIn("skills", manifest)
        self.assertTrue(skill.exists())
        self.assertIn("name: factor-mining", skill.read_text(encoding="utf-8"))
        self.assertTrue((scripts / "factor_api.py").exists())
        self.assertTrue((scripts / "factor_mining_agent_lib" / "api.py").exists())


if __name__ == "__main__":
    unittest.main()
