import ast


def parse_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)

    functions = []
    classes = []
    imports = []
    calls = []

    for node in ast.walk(tree):

        # Functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name": node.name,
                "line": node.lineno,
            })

        # Classes
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno,
            })

        # import x
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        # from x import y
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

        # function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)

            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "calls": calls,
    }