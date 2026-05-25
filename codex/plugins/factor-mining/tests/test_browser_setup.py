import io
import sys
import unittest
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from factor_mining_agent_lib.browser_setup import collect_agent_key_via_browser


class BrowserSetupTests(unittest.TestCase):
    def test_browser_setup_collects_key_over_loopback_without_logging_secret(self):
        secret = "vt_browser_secret_1234567890abcdef"
        opened_urls = []
        stderr = io.StringIO()

        def submit_key(url):
            opened_urls.append(url)
            request = Request(
                url,
                data=urlencode({"api_key": secret}).encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urlopen(request, timeout=5) as response:
                body = response.read().decode("utf-8")
            self.assertIn("saved", body.lower())

        collected = collect_agent_key_via_browser(stderr=stderr, open_browser=submit_key, timeout=5)

        self.assertEqual(collected, secret)
        self.assertEqual(len(opened_urls), 1)
        self.assertIn("127.0.0.1", opened_urls[0])
        self.assertNotIn(secret, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
