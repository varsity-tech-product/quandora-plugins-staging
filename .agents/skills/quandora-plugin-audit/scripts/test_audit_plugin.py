#!/usr/bin/env python3
"""Unit tests for the deterministic Quandora plugin auditor."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from audit_plugin import _frontmatter, audit_repository


class AuditPluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.plugin = self.repo / "plugins" / "quandora-staging"
        (self.plugin / ".codex-plugin").mkdir(parents=True)
        (self.plugin / ".codex-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
        skill = self.plugin / "skills" / "sample-skill"
        (skill / "agents").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            "description: Audits a sample package. Use when a reviewer requests a package audit.\n"
            "---\n\n"
            "# Sample Skill\n\n"
            "## Tools\n\n"
            "Use `get_sample` for a bounded read.\n",
            encoding="utf-8",
        )
        (skill / "agents" / "openai.yaml").write_text(
            'interface:\n  default_prompt: "Use $sample-skill to audit this package."\n',
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_clean_minimal_plugin_passes(self) -> None:
        findings = audit_repository(
            self.repo,
            self.plugin,
            mode="full",
            public_tools={"get_sample"},
        )
        self.assertEqual(findings, [])

    def test_auditor_skill_metadata_and_resources_are_discoverable(self) -> None:
        skill_root = Path(__file__).resolve().parents[1]
        skill_file = skill_root / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        metadata, findings = _frontmatter(Path("SKILL.md"), text)

        self.assertEqual(findings, [])
        self.assertEqual(metadata["name"], "quandora-plugin-audit")
        self.assertIn("Use for plugin release reviews", metadata["description"])
        for reference in (skill_root / "references").glob("*.md"):
            self.assertIn(f"references/{reference.name}", text)
        self.assertIn("scripts/audit_plugin.py", text)
        self.assertIn("scripts/test_audit_plugin.py", text)

    def test_product_history_language_and_extra_entry_are_blocking(self) -> None:
        readme = self.plugin / "README.md"
        readme.write_text("# Plugin\n\nRelease Order\n\nPlugin 1.4 增加功能。\n", encoding="utf-8")
        (self.plugin / "scripts").mkdir()
        (self.plugin / "scripts" / "helper.sh").write_text("#!/bin/sh\n", encoding="utf-8")

        findings = audit_repository(self.repo, self.plugin, mode="full")
        rules = {item.rule_id for item in findings if item.severity == "error"}

        self.assertTrue({"QD-PACKAGE-001", "QD-PRODUCT-001", "QD-PRODUCT-002"} <= rules)

    def test_changed_mode_does_not_block_on_unchanged_legacy_prose(self) -> None:
        readme = self.plugin / "README.md"
        readme.write_text("Plugin 1.4 legacy note\n", encoding="utf-8")
        skill_path = "plugins/quandora-staging/skills/sample-skill/SKILL.md"

        findings = audit_repository(
            self.repo,
            self.plugin,
            mode="changed",
            changed_paths={skill_path},
            public_tools={"get_sample"},
        )

        self.assertFalse(any(item.path == "plugins/quandora-staging/README.md" for item in findings))

    def test_unknown_tool_is_rejected_against_supplied_contract(self) -> None:
        findings = audit_repository(
            self.repo,
            self.plugin,
            mode="full",
            public_tools={"list_sample"},
        )

        self.assertTrue(
            any(item.rule_id == "QD-CONTRACT-001" and item.severity == "error" for item in findings)
        )


if __name__ == "__main__":
    unittest.main()
