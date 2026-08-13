"""Static Quandora staging bundle-version and reminder instruction contracts."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / "plugins" / "quandora-staging"
EXPECTED_VERSION = "1.42"
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


def test_static_factor_and_strategy_instruction_contracts_are_identical():
    blocks = [_version_block(skill) for skill in SKILLS]
    assert blocks[0] == blocks[1]
    block = blocks[0]
    required = (
        "first entry into any Quandora skill in the current conversation",
        "does not already contain one successful `qd_check_plugin_version` call",
        "call it once before the business entry point",
        "verbatim as `installed_version`",
        "opaque release label",
        "never parse, order, or normalize it",
        "If `update_available=false`, continue silently.",
        "The latest Quandora plugin version is <latest_version>. Please update the plugin.",
        "A Quandora Staging MCP access token is valid for 7 days.",
        "After 7 days, use the prompt below to ask your agent to refresh the connection",
        "it should use automatic refresh first and CLI re-authentication only if required",
        "provide this exact copyable prompt in a fenced `text` block",
        "Refresh the Quandora Staging MCP connection. If automatic refresh fails, re-authenticate it with the CLI.",
        "Then immediately continue the user's original request.",
        "missing, disabled, invisible, or fails",
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


def test_static_skills_state_seven_day_host_managed_oauth_without_stale_ttl_claims():
    for skill in SKILLS:
        text = skill.read_text(encoding="utf-8")
        lowered = text.lower()
        assert "access tokens expire after 7 days" in text
        assert "seven-day lifetime" in text
        assert "one hour" not in lowered
        assert "one-hour" not in lowered
        assert "24 hours" not in lowered
        assert "24-hour" not in lowered
        assert "oauth and all credentials are handled by the host" in lowered
        assert "stored rotating refresh token automatically" in lowered


def test_static_instruction_contract_never_automates_updates_or_asserts_a_grammar():
    for skill in SKILLS:
        text = skill.read_text(encoding="utf-8")
        reminder = _version_block(skill).lower()
        assert "never install, update, uninstall, or reload a plugin" in reminder
        assert "immediately start oauth or reauthorize merely because of the version result" in reminder
        assert "provide a platform-specific command in the version reminder" in reminder
        assert "not permission to run it during the version check" in reminder
        assert "opaque release label" in reminder
        for fixed_grammar in (
            "semantic version",
            "semver",
            "three-component",
            "x.y.z",
            "staging suffix",
        ):
            assert fixed_grammar not in text.lower()
