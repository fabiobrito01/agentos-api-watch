import unittest
from unittest.mock import patch,MagicMock
from watch import check
class T(unittest.TestCase):
 @patch('urllib.request.urlopen')
 def test_ok(self,m):m.return_value.__enter__.return_value.status=200;self.assertTrue(check('https://example.com')['ok'])
