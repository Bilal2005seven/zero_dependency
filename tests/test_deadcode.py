import unittest

from deadcode import find_unused_functions


class TestDeadCode(unittest.TestCase):

    def test_unused_function_detected(self):
        analyses = [
            {
                "path": "example.py",
                "functions": [
                    {
                        "name": "used_function",
                        "line": 1
                    },
                    {
                        "name": "unused_function",
                        "line": 5
                    }
                ],
                "calls": [
                    "used_function"
                ]
            }
        ]

        result = find_unused_functions(analyses)

        names = [item["name"] for item in result]

        self.assertIn("unused_function", names)

    def test_used_function_not_detected(self):
        analyses = [
            {
                "path": "example.py",
                "functions": [
                    {
                        "name": "used_function",
                        "line": 1
                    }
                ],
                "calls": [
                    "used_function"
                ]
            }
        ]

        result = find_unused_functions(analyses)

        self.assertEqual(result, [])

    def test_special_functions_ignored(self):
        analyses = [
            {
                "path": "example.py",
                "functions": [
                    {
                        "name": "__init__",
                        "line": 1
                    },
                    {
                        "name": "test_something",
                        "line": 5
                    }
                ],
                "calls": []
            }
        ]

        result = find_unused_functions(analyses)

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()