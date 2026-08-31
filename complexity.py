import ast


def calculate_complexity(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)

    results = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            complexity = 1

            for child in ast.walk(node):

                if isinstance(
                    child,
                    (
                        ast.If,
                        ast.For,
                        ast.While,
                        ast.ExceptHandler,
                    ),
                ):
                    complexity += 1

                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1

            results.append({
                "name": node.name,
                "line": node.lineno,
                "complexity": complexity,
            })

    return results