import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRATEGY_SKILL = ROOT / "plugins/quandora-staging/skills/strategy-building/SKILL.md"
FACTOR_SKILL = ROOT / "plugins/quandora-staging/skills/factor-mining/SKILL.md"
VERSIONED_MANIFESTS = (
    ROOT / ".claude-plugin/marketplace.json",
    ROOT / "kimi.plugin.json",
    ROOT / "plugins/quandora-staging/.claude-plugin/plugin.json",
    ROOT / "plugins/quandora-staging/.codex-plugin/plugin.json",
    ROOT / "plugins/quandora-staging/.cursor-plugin/plugin.json",
)
EXPECTED_VERSION = "1.0.8-staging.33"
RECOVERY_ACTIONS = {
    "repair_and_revalidate",
    "create_same_kind_session_after_input_change",
    "retry_same_pending_request",
    "resume_known_run",
    "stop_and_report_trace",
    "repair_then_create_same_kind_session",
}


class ReliabilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.strategy = STRATEGY_SKILL.read_text()
        cls.factor = FACTOR_SKILL.read_text()
        cls.strategy_flat = " ".join(cls.strategy.split())
        cls.factor_flat = " ".join(cls.factor.split())

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
        self.assertIn("calls only `strategy_list_eligible_factors`", bare_flat)
        self.assertIn("do not ask a clarification question", bare_flat)
        self.assertIn("do not call `strategy_get_contract`", bare_flat)
        self.assertIn("do not call `factor_mining_status`", bare_flat)
        self.assertIn("do not call `factor_mining_list_factors`", bare_flat)
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
        seen = 0
        for path in VERSIONED_MANIFESTS:
            payload = json.loads(path.read_text())
            rendered = json.dumps(payload)
            versions = re.findall(r"1\.0\.8-staging\.\d+", rendered)
            self.assertTrue(versions, path)
            self.assertEqual(set(versions), {EXPECTED_VERSION}, path)
            seen += len(versions)
        self.assertEqual(seen, 6)


if __name__ == "__main__":
    unittest.main()
