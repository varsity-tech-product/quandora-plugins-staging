import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRATEGY_SKILL = ROOT / "plugins/quandora-staging/skills/strategy-building/SKILL.md"
FACTOR_SKILL = ROOT / "plugins/quandora-staging/skills/factor-mining/SKILL.md"
VERSIONED_MANIFESTS = (
    ROOT / ".claude-plugin/marketplace.json",
    ROOT / ".codebuddy-plugin/marketplace.json",
    ROOT / "kimi.plugin.json",
    ROOT / "plugins/quandora-staging/.claude-plugin/plugin.json",
    ROOT / "plugins/quandora-staging/.codebuddy-plugin/plugin.json",
    ROOT / "plugins/quandora-staging/.codex-plugin/plugin.json",
    ROOT / "plugins/quandora-staging/.cursor-plugin/plugin.json",
)
EXPECTED_VERSION = "1.0.8-staging.36"
KIMI_RUNTIME_SERVER_NAME = "plugin-quandora-staging:quandora-staging"
TOOL_RENAME_MAP = {
    "factor_mining_status": "fm_status",
    "factor_mining_list_public_tasks": "fm_list_tasks",
    "factor_mining_get_plugin_contract": "fm_get_contract",
    "factor_mining_create_task_session": "fm_task_session",
    "factor_mining_create_custom_session": "fm_custom_sess",
    "factor_mining_validate_plugin_source": "fm_validate",
    "factor_mining_request_dedup_context": "fm_dedup_context",
    "factor_mining_upload_backtest_wait": "fm_run_backtest",
    "factor_mining_resume_run": "fm_resume_run",
    "factor_mining_get_backtest_window_cards": "fm_window_cards",
    "factor_mining_create_backtest_png_download_ticket": "fm_png_ticket",
    "factor_mining_create_backtest_raw_artifact_download_ticket": "fm_raw_ticket",
    "factor_mining_get_backtest_png_artifact_chunk": "fm_png_chunk",
    "factor_mining_list_factors": "fm_list_factors",
    "factor_mining_get_factor_history": "fm_get_history",
    "quandora_get_guidance": "qd_get_guidance",
    "strategy_get_contract": "sb_get_contract",
    "strategy_list_eligible_factors": "sb_list_eligible",
    "strategy_get_eligible_factor_detail": "sb_factor_detail",
    "strategy_list_shared_factor_candidates": "sb_shared_list",
    "strategy_add_shared_factor_to_pool": "sb_shared_add",
    "strategy_import_factor": "sb_import_factor",
    "strategy_submit_run": "sb_submit_run",
    "strategy_get_run": "sb_get_run",
    "strategy_resume_run": "sb_resume_run",
    "strategy_get_artifact": "sb_get_artifact",
    "strategy_create_artifact_download_ticket": "sb_file_ticket",
}
FACTOR_SKILL_TOOL_NAMES = {
    "fm_custom_sess",
    "fm_dedup_context",
    "fm_get_contract",
    "fm_get_history",
    "fm_list_factors",
    "fm_list_tasks",
    "fm_png_chunk",
    "fm_png_ticket",
    "fm_raw_ticket",
    "fm_resume_run",
    "fm_run_backtest",
    "fm_status",
    "fm_task_session",
    "fm_validate",
    "fm_window_cards",
    "qd_get_guidance",
    "sb_list_eligible",
}
STRATEGY_SKILL_TOOL_NAMES = {
    "fm_custom_sess",
    "fm_list_factors",
    "fm_resume_run",
    "fm_status",
    "qd_get_guidance",
    "sb_factor_detail",
    "sb_file_ticket",
    "sb_get_artifact",
    "sb_get_contract",
    "sb_get_run",
    "sb_import_factor",
    "sb_list_eligible",
    "sb_resume_run",
    "sb_shared_add",
    "sb_shared_list",
    "sb_submit_run",
}
HOST_MANIFEST_DIGESTS_WITHOUT_VERSION = {
    ".agents/plugins/marketplace.json": "c52ee04d343e0b0b28ea93b9437f8827b7e68237e2a3b625059b2714882a773d",
    ".claude-plugin/marketplace.json": "9d9fef079ab874b48675dd64bb6bb51414f4dc9add630cd8e24a49a47090b6f6",
    ".codebuddy-plugin/marketplace.json": "2e560f71a4c01e9da875e360dd1ef8b47763b0e483e38ac256d1a15e76ed168d",
    ".cursor-plugin/marketplace.json": "2a17699bc34d1897afa6caddf0f3e11177b8822b2581b538a397247b96927567",
    "kimi.plugin.json": "e13fbd9feedd399538b1d4ec1e4fb25dc9ee62cf90565695e5988c74d9f8a1a3",
    "plugins/quandora-staging/.claude-plugin/plugin.json": "16a038cf0b98a8e68f4edb62c2d2d0d82e84e9d1684ab2f4f133a5836f51c0eb",
    "plugins/quandora-staging/.codebuddy-plugin/plugin.json": "99d2e9ffa7eea83ddd5d773e62253461cf6a1585e4233df43acd22b13af0e349",
    "plugins/quandora-staging/.codex-plugin/plugin.json": "3d941f755c66c04cf6ce517f8a31b38b99401c884256d1d68170431f5dbf3b3b",
    "plugins/quandora-staging/.cursor-plugin/plugin.json": "15393ff5220812aa2548638116f24184c4502781ec3c2315b571c92502e2a66a",
    "plugins/quandora-staging/.mcp.json": "3576cf81ba25f7618f4c17932dcf4f864b3b00b14d29889c1c86d6eba4ec6d40",
    "plugins/quandora-staging/mcp.json": "9c8ad1651f18392d43bd6ebe1937b47f02e39afcc9362d651f6056899461a1c0",
}
RECOVERY_ACTIONS = {
    "repair_and_revalidate",
    "create_same_kind_session_after_input_change",
    "retry_same_pending_request",
    "resume_known_run",
    "stop_and_report_trace",
    "repair_then_create_same_kind_session",
}


def _tool_tokens(text: str) -> set[str]:
    return set(re.findall(r"(?<![a-z0-9_])(?:fm|sb|qd)_[a-z0-9_]+", text))


def _without_version(value):
    if isinstance(value, dict):
        return {
            key: _without_version(item)
            for key, item in value.items()
            if key != "version"
        }
    if isinstance(value, list):
        return [_without_version(item) for item in value]
    return value


def _manifest_digest_without_version(path: Path) -> str:
    rendered = json.dumps(
        _without_version(json.loads(path.read_text())),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(rendered).hexdigest()


class ReliabilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.strategy = STRATEGY_SKILL.read_text()
        cls.factor = FACTOR_SKILL.read_text()
        cls.strategy_flat = " ".join(cls.strategy.split())
        cls.factor_flat = " ".join(cls.factor.split())

    def test_tool_name_cutover_is_exact_closed_and_kimi_safe(self) -> None:
        new_names = tuple(TOOL_RENAME_MAP.values())
        self.assertEqual(len(TOOL_RENAME_MAP), 27)
        self.assertEqual(len(new_names), len(set(new_names)))
        self.assertTrue(all(re.fullmatch(r"[a-z][a-z0-9_]*", name) for name in new_names))
        self.assertTrue(all(name.startswith(("fm_", "sb_", "qd_")) for name in new_names))
        self.assertLessEqual(max(map(len, new_names)), 16)
        self.assertEqual(_tool_tokens(self.factor), FACTOR_SKILL_TOOL_NAMES)
        self.assertEqual(_tool_tokens(self.strategy), STRATEGY_SKILL_TOOL_NAMES)
        for old_name in TOOL_RENAME_MAP:
            self.assertNotRegex(
                self.factor,
                rf"(?<![A-Za-z0-9_]){re.escape(old_name)}(?![A-Za-z0-9_])",
            )
            self.assertNotRegex(
                self.strategy,
                rf"(?<![A-Za-z0-9_]){re.escape(old_name)}(?![A-Za-z0-9_])",
            )

        sanitized_server = re.sub(r"[^A-Za-z0-9_]", "_", KIMI_RUNTIME_SERVER_NAME)
        qualified = [f"mcp__{sanitized_server}__{name}" for name in new_names]
        self.assertEqual(len(qualified), len(set(qualified)))
        self.assertLessEqual(max(map(len, qualified)), 63)
        self.assertTrue(all(len(name) <= 64 for name in qualified))

    def test_host_manifests_preserve_connection_and_oauth_identity(self) -> None:
        actual = {
            relative: _manifest_digest_without_version(ROOT / relative)
            for relative in HOST_MANIFEST_DIGESTS_WITHOUT_VERSION
        }
        self.assertEqual(actual, HOST_MANIFEST_DIGESTS_WITHOUT_VERSION)
        launchers = (
            (ROOT / "install-openclaw.sh").read_text()
            + (ROOT / "plugins/quandora-staging/scripts/claude-mcp-login-macos.sh").read_text()
            + (ROOT / "plugins/quandora-staging/scripts/claude-mcp-login-windows.ps1").read_text()
        )
        self.assertIn("quandora-staging", launchers)
        self.assertIn("https://mcp-staging.varsity.lol/quant", launchers)
        self.assertIn("plugin:quandora-staging:quandora-staging", launchers)

    def test_release_notes_require_plugin_update_and_fresh_session_only(self) -> None:
        release_notes = (ROOT / "plugins/quandora-staging/README.md").read_text()
        required = (
            "Update the staging plugin",
            "Close the old chat/session",
            "Start a new chat/session so the host performs a fresh `tools/list`",
            "No credential paste, connection recreation, or OAuth re-login is expected",
        )
        for phrase in required:
            self.assertIn(phrase, release_notes)

    def test_strategy_default_is_one_ten_row_page_and_never_auto_pages(self) -> None:
        required = (
            "make exactly one call with `page_size: 10`",
            "display only that returned page",
            "Do not auto-page",
            "Only when `next_page_token` is non-empty",
            "more results can be requested",
            "Honor an explicit valid `page_size` from 1 through 100",
        )
        for phrase in required:
            self.assertIn(phrase, self.strategy_flat)
        bare_section = self.strategy[
            self.strategy.index('Bare “列出可用因子”') :
            self.strategy.index("### 1. Prepare a Valid Submission")
        ]
        bare_flat = " ".join(bare_section.split()).lower()
        self.assertIn("calls only `sb_list_eligible`", bare_flat)
        self.assertIn("do not ask a clarification question", bare_flat)
        self.assertIn("do not call `sb_get_contract`", bare_flat)
        self.assertIn("do not call `fm_status`", bare_flat)
        self.assertIn("do not call `fm_list_factors`", bare_flat)
        self.assertIn("do not make a second list call", bare_flat)

    def test_strategy_default_table_uses_exact_cs_sharpe_only(self) -> None:
        manual = self.strategy[
            self.strategy.index("#### Manual Selection") :
            self.strategy.index("#### Shared Selection")
        ]
        manual_flat = " ".join(manual.split())
        self.assertIn(
            "with only factor id, name, authoritative FM Task category, rating/grade "
            "status, and exact `cs_sharpe` labeled CS Sharpe when available",
            manual_flat,
        )
        self.assertIn(
            "Do not include Median Sharpe, cross-sectional/time-series capability flags, "
            "or eligibility status in the default table",
            manual_flat,
        )
        self.assertIn("never substitute `median_sharpe`", manual_flat)

    def test_factor_skill_covers_every_closed_recovery_action(self) -> None:
        mentioned = {
            action for action in RECOVERY_ACTIONS if f"`{action}`" in self.factor
        }
        self.assertEqual(mentioned, RECOVERY_ACTIONS)
        required = (
            "at most one bounded replay",
            "exact same pending handle",
            "unchanged validated source",
            "never create a session or alter the request",
            "Normal `running` with `next_action=resume` resumes only",
            "`invalid_backend_response` is not retried identically",
            "`retryable` describes service availability",
            "`recovery_action` controls mutation behavior",
        )
        for phrase in required:
            self.assertIn(phrase.lower(), self.factor_flat.lower())

    def test_public_custom_decision_and_shared_tail_remain_ordered(self) -> None:
        public = self.factor.index("- For a public task:")
        custom = self.factor.index("- For a custom idea:")
        shared = self.factor.index(
            "After either branch returns its scoped contract, continue through the single shared"
        )
        writing = self.factor.index("Before drafting, form a concise research thesis.")
        self.assertLess(public, custom)
        self.assertLess(custom, shared)
        self.assertLess(shared, writing)

    def test_strategy_artifact_registry_remains_exactly_twenty_one_names(self) -> None:
        table = self.strategy[
            self.strategy.index("| Artifact name |") :
            self.strategy.index("When `archiveStatus == completed`")
        ]
        artifact_rows = re.findall(r"^\| `([^`]+)` \|", table, flags=re.MULTILINE)
        self.assertEqual(len(artifact_rows), 21)
        self.assertNotIn("six_charts_data.json", artifact_rows)

    def test_all_versioned_manifests_use_fresh_staging_version(self) -> None:
        discovered = {
            path
            for path in ROOT.rglob("*.json")
            if re.search(r"1\.0\.8-staging\.\d+", path.read_text())
        }
        self.assertEqual(discovered, set(VERSIONED_MANIFESTS))
        seen = 0
        for path in VERSIONED_MANIFESTS:
            payload = json.loads(path.read_text())
            rendered = json.dumps(payload)
            versions = re.findall(r"1\.0\.8-staging\.\d+", rendered)
            self.assertTrue(versions, path)
            self.assertEqual(set(versions), {EXPECTED_VERSION}, path)
            seen += len(versions)
        self.assertEqual(seen, 9)


if __name__ == "__main__":
    unittest.main()
