import json
import sys
import unittest
from urllib import request
from urllib.error import HTTPError


PLUGIN_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
TESTS_ROOT = PLUGIN_ROOT / "tests"
sys.path.insert(0, str(TESTS_ROOT))

from acceptance.mock_backend import start_mock_backend
from acceptance.run_mock_acceptance import run_failed_job_scenario, run_success_scenario


class MockAcceptanceTests(unittest.TestCase):
    def test_mock_backend_rejects_protected_endpoint_without_agent_key(self):
        with start_mock_backend() as backend:
            req = request.Request(f"{backend.base_url}/tasks", method="GET")

            with self.assertRaises(HTTPError) as raised:
                request.urlopen(req, timeout=5)

        self.assertEqual(raised.exception.code, 401)

    def test_success_scenario_runs_full_helper_flow(self):
        result = run_success_scenario()

        self.assertEqual(result.setup["agent_status"]["key_purpose"], "external_agent")
        self.assertEqual(result.session["session_id"], "session_mock_1")
        self.assertEqual(result.metadata["factor_name"], "Mock Liquidity Stress")
        self.assertTrue(result.upload_summary["ok"])
        self.assertEqual(result.upload_summary["status"], "succeeded")
        self.assertEqual(result.upload_summary["artifact"]["status"], "available")
        self.assertEqual(result.artifact["factor_name"], "Mock Liquidity Stress")

    def test_failed_job_scenario_returns_terminal_failure_summary(self):
        result = run_failed_job_scenario()

        self.assertFalse(result.upload_summary["ok"])
        self.assertEqual(result.upload_summary["status"], "failed")
        self.assertEqual(result.upload_summary["terminal_status"], "failed")
        self.assertEqual(result.upload_summary["failures"][0]["job_id"], "job_mock_1")

    def test_acceptance_results_are_json_serializable(self):
        result = run_success_scenario()

        json.dumps(result.to_dict(), sort_keys=True)


if __name__ == "__main__":
    unittest.main()
