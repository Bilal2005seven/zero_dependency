import unittest

from repomind.graph import build_dependency_graph, detect_cycles


class TestGraph(unittest.TestCase):

    def test_dependency_graph(self):
        analyses = [
            {
                "path": "a.py",
                "imports": ["b"],
            },
            {
                "path": "b.py",
                "imports": [],
            },
        ]

        graph = build_dependency_graph(analyses)

        self.assertIn("a", graph)
        self.assertIn("b", graph)

        self.assertIn("b", graph["a"])

    def test_no_cycle(self):
        analyses = [
            {
                "path": "a.py",
                "imports": ["b"],
            },
            {
                "path": "b.py",
                "imports": [],
            },
        ]

        graph = build_dependency_graph(analyses)

        cycles = detect_cycles(graph)

        self.assertEqual(cycles, [])

    def test_cycle_detection(self):
        analyses = [
            {
                "path": "a.py",
                "imports": ["b"],
            },
            {
                "path": "b.py",
                "imports": ["a"],
            },
        ]

        graph = build_dependency_graph(analyses)

        cycles = detect_cycles(graph)

        self.assertTrue(cycles)


if __name__ == "__main__":
    unittest.main()