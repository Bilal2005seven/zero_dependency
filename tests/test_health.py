import unittest

from repomind.health import calculate_health_score


class TestHealth(unittest.TestCase):

    def test_perfect_repository(self):
        result = calculate_health_score(
            security_issues=[],
            cycles=[],
            complexity_results=[],
            unused_functions=[]
        )

        self.assertEqual(result["score"], 100)
        self.assertEqual(result["grade"], "EXCELLENT")

    def test_security_penalty(self):
        security_issues = [
            {
                "type": "Dangerous eval()",
                "severity": "HIGH",
                "line": 10
            }
        ]

        result = calculate_health_score(
            security_issues=security_issues,
            cycles=[],
            complexity_results=[],
            unused_functions=[]
        )

        self.assertEqual(result["score"], 85)

    def test_cycle_penalty(self):
        result = calculate_health_score(
            security_issues=[],
            cycles=[["a", "b", "a"]],
            complexity_results=[],
            unused_functions=[]
        )

        self.assertEqual(result["score"], 90)

    def test_score_never_below_zero(self):
        security_issues = [
            {
                "type": "Critical",
                "severity": "HIGH",
                "line": 1
            }
        ] * 20

        result = calculate_health_score(
            security_issues=security_issues,
            cycles=[],
            complexity_results=[],
            unused_functions=[]
        )

        self.assertEqual(result["score"], 0)


if __name__ == "__main__":
    unittest.main()