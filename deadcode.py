def find_unused_functions(analyses):
    """
    Find functions that are potentially unused.

    Functions used as framework entry points, test methods,
    constructors, or program entry points are ignored.
    """

    defined_functions = []
    called_functions = set()

    # Collect defined functions
    for analysis in analyses:
        for function in analysis["functions"]:
            defined_functions.append({
                "name": function["name"],
                "file": analysis["path"],
                "line": function["line"],
            })

    # Collect function calls
    for analysis in analyses:
        for call in analysis["calls"]:
            called_functions.add(call)

    unused = []

    for function in defined_functions:

        name = function["name"]
        file = function["file"]

        # Ignore Python special methods
        if name.startswith("__") and name.endswith("__"):
            continue

        # Ignore unittest lifecycle methods
        if name.startswith("test_") or name == "setUp":
            continue

        # Ignore likely web/API entry points
        if file.endswith("api.py"):
            continue

        # Ignore main entry point
        if name == "main":
            continue

        # If nobody calls it, flag it
        if name not in called_functions:
            unused.append(function)

    return unused