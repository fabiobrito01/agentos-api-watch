import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from watch import check, main


class WatchTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_ok(self, mocked_open):
        mocked_open.return_value.__enter__.return_value.status = 200
        result = check("https://example.com")
        self.assertTrue(result["ok"])
        self.assertEqual(result["attempts"], 1)

    @patch("urllib.request.urlopen")
    def test_expected_status(self, mocked_open):
        mocked_open.return_value.__enter__.return_value.status = 404
        self.assertTrue(check("https://example.com", expected=[404])["ok"])

    @patch("urllib.request.urlopen")
    def test_headers_and_slow_threshold(self, mocked_open):
        mocked_open.return_value.__enter__.return_value.status = 200
        with patch("watch.time.perf_counter", side_effect=[0, 0.01]):
            result = check("https://example.com", headers={"Authorization": "Bearer demo"}, fail_slow_ms=0)
        request = mocked_open.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer demo")
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "slow")

    @patch("watch.check")
    def test_parallel_cli_keeps_input_order(self, mocked_check):
        mocked_check.side_effect = lambda url, *_args: {"url": url, "ok": True, "status": 200, "ms": 1, "attempts": 1}
        self.assertEqual(main(["https://a.test", "https://b.test", "--workers", "2"]), 0)
        self.assertEqual([call.args[0] for call in mocked_check.call_args_list], ["https://a.test", "https://b.test"])

    @patch("urllib.request.urlopen", side_effect=OSError("offline"))
    def test_retries_and_output(self, _mocked_open):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            code = main(["https://example.com", "--retries", "2", "--output", str(output)])
            self.assertEqual(code, 1)
            self.assertIn('"attempts": 3', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
