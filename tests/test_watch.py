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

    @patch("urllib.request.urlopen", side_effect=OSError("offline"))
    def test_retries_and_output(self, _mocked_open):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            code = main(["https://example.com", "--retries", "2", "--output", str(output)])
            self.assertEqual(code, 1)
            self.assertIn('"attempts": 3', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
