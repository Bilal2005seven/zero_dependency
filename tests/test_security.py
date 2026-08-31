import unittest
from pathlib import Path

from repomind.security import scan_security


class TestSecurity(unittest.TestCase):

    def setUp(self):
        self.file = Path(__file__).parent / "fixtures" / "security_test.py"

    def test_detects_eval(self):
        issues = scan_security(self.file)

        types = [issue["type"] for issue in issues]

        self.assertIn("Dangerous eval()", types)

    def test_detects_exec(self):
        issues = scan_security(self.file)

        types = [issue["type"] for issue in issues]

        self.assertIn("Dangerous exec()", types)

    def test_detects_weak_hash(self):
        issues = scan_security(self.file)

        types = [issue["type"] for issue in issues]

        self.assertIn("Weak Hash Algorithm", types)


if __name__ == "__main__":
    unittest.main()