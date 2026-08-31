import ast


def scan_security(file_path):
    """
    Scan a Python file for common security issues.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)

    issues = []

    for node in ast.walk(tree):

        # Dangerous eval()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):

                if node.func.id == "eval":
                    issues.append({
                        "type": "Dangerous eval()",
                        "severity": "HIGH",
                        "line": node.lineno,
                        "message": "eval() can execute arbitrary code.",
                    })

                elif node.func.id == "exec":
                    issues.append({
                        "type": "Dangerous exec()",
                        "severity": "HIGH",
                        "line": node.lineno,
                        "message": "exec() can execute arbitrary code.",
                    })

        # Weak hashing
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):

                if node.func.attr in ("md5", "sha1"):
                    issues.append({
                        "type": "Weak Hash Algorithm",
                        "severity": "MEDIUM",
                        "line": node.lineno,
                        "message": f"Weak hashing algorithm: {node.func.attr}",
                    })

    return issues