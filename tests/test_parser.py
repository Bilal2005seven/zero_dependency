import unittest
from pathlib import Path

from parser import parse_file


class TestParser(unittest.TestCase):

    def setUp(self):
        self.file = Path("sample_project/main.py")

    def test_parser_returns_data(self):
        result = parse_file(self.file)

        self.assertIsInstance(result, dict)

    def test_functions_detected(self):
        result = parse_file(self.file)

        self.assertIn("functions", result)
        self.assertIsInstance(result["functions"], list)

    def test_imports_detected(self):
        result = parse_file(self.file)

        self.assertIn("imports", result)
        self.assertIsInstance(result["imports"], list)


if __name__ == "__main__":
    unittest.main()