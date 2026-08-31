import unittest
from pathlib import Path

from repomind.complexity import calculate_complexity


class TestComplexity(unittest.TestCase):

    def setUp(self):
        self.file = Path(__file__).parent / "fixtures" / "complex_test.py"

    def test_complexity_returns_list(self):
        result = calculate_complexity(self.file)

        self.assertIsInstance(result, list)

    def test_simple_function_complexity(self):
        result = calculate_complexity(self.file)

        simple = next(
            function
            for function in result
            if function["name"] == "simple"
        )

        self.assertEqual(simple["complexity"], 1)

    def test_medium_function_complexity(self):
        result = calculate_complexity(self.file)

        medium = next(
            function
            for function in result
            if function["name"] == "medium"
        )

        self.assertEqual(medium["complexity"], 2)


if __name__ == "__main__":
    unittest.main()