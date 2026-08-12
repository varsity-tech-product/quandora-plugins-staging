"""Quandora staging bundle-version and reminder-skill contracts."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / "plugins" / "quandora-staging"
EXPECTED_VERSION = "1.0.8-staging.42"
SKILLS = (
    PLUGIN / "skills" / "factor-mining" / "SKILL.md",
    PLUGIN / "skills" / "strategy-building" / "SKILL.md",
)
VERSION_FILES = (
    PLUGIN / ".codex-plugin" / "plugin.json",
    PLUGIN / ".claude-plugin" / "plugin.json",
    PLUGIN / ".codebuddy-plugin" / "plugin.json",
    PLUGIN / ".cursor-plugin" / "plugin.json",
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / ".codebuddy-plugin" / "marketplace.json",
    ROOT / ".cursor-plugin" / "marketplace.json",
    ROOT / ".agents" / "plugins" / "marketplace.json",
    ROOT / "kimi.plugin.json",
)


def _declared_versions(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "version":
                yield item
            yield from _declared_versions(item)
    elif isinstance(value, list):
        for item in value:
            yield from _declared_versions(item)


def _version_block(skill: Path) -> str:
    text = skill.read_text(encoding="utf-8")
    return text.split("## Plugin Version Reminder\n", 1)[1].split(
        "<!-- end-plugin-version-reminder -->", 1
    )[0]


def test_all_existing_manifests_marketplaces_and_skills_share_one_version():
    assert all(path.is_file() for path in VERSION_FILES)
    versions = [
        version
        for path in VERSION_FILES
        for version in _declared_versions(json.loads(path.read_text(encoding="utf-8")))
    ]
    assert len(versions) == 9
    assert set(versions) == {EXPECTED_VERSION}
    for skill in SKILLS:
        match = re.search(r"^Bundled plugin version: (\S+)$", skill.read_text(), re.MULTILINE)
        assert match is not None
        assert match.group(1) == EXPECTED_VERSION


def test_factor_and_strategy_share_the_exact_conversation_level_check_contract():
    blocks = [_version_block(skill) for skill in SKILLS]
    assert blocks[0] == blocks[1]
    block = blocks[0]
    required = (
        "first entry into any Quandora skill in the current conversation",
        "does not already contain one successful `qd_check_plugin_version` call",
        "call it once before the business entry point",
        "verbatim as `installed_version`",
        "If `update_available=false`, continue silently.",
        "The latest Quandora plugin version is <latest_version>. Please update the plugin.",
        "Then continue the user's original request.",
        "missing, invisible, or fails",
        "do not retry the check",
        "without a version message",
        "does not call it or remind again",
        "optional for connection readiness",
        "absence alone never triggers connection recovery",
        "not a business action",
        "then call `fm_status`",
        "one business call `sb_list_eligible`",
        "then call `sb_get_contract`",
    )
    for phrase in required:
        assert phrase in block
    for platform_or_command in (
        "codex mcp",
        "/mcp",
        "claude",
        "kimi",
        "cursor",
        "codebuddy",
        "http://",
        "https://",
    ):
        assert platform_or_command not in block.lower()


def test_skills_state_24_hour_host_managed_oauth_without_one_hour_claims():
    for skill in SKILLS:
        text = skill.read_text(encoding="utf-8")
        lowered = text.lower()
        assert "access tokens expire after 24 hours" in text
        assert "24-hour lifetime" in text
        assert "one hour" not in lowered
        assert "one-hour" not in lowered
        assert "oauth and all credentials are handled by the host" in lowered
        assert "stored rotating refresh token automatically" in lowered
