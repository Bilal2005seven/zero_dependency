from pathlib import Path


def build_dependency_graph(analyses):
    """
    Build a graph showing which project files depend on which modules.
    """

    module_map = {}

    for analysis in analyses:
        path = Path(analysis["path"])

        module_name = (
            path.with_suffix("")
            .as_posix()
            .replace("/", ".")
        )

        module_map[module_name] = analysis["path"]

    graph = {}

    for analysis in analyses:
        path = analysis["path"]

        module_name = (
            Path(path)
            .with_suffix("")
            .as_posix()
            .replace("/", ".")
        )

        graph[module_name] = []

        for imported_module in analysis["imports"]:
            if imported_module in module_map:
                graph[module_name].append(imported_module)

    return graph


def detect_cycles(graph):
    """
    Detect circular dependencies using DFS.
    """

    NOT_VISITED = 0
    VISITING = 1
    COMPLETED = 2

    state = {
        node: NOT_VISITED
        for node in graph
    }

    cycles = []

    def dfs(node, path):
        state[node] = VISITING
        path.append(node)

        for neighbour in graph[node]:

            if state[neighbour] == NOT_VISITED:
                dfs(neighbour, path)

            elif state[neighbour] == VISITING:

                cycle_start = path.index(neighbour)
                cycle = path[cycle_start:] + [neighbour]

                cycles.append(cycle)

        path.pop()
        state[node] = COMPLETED

    for node in graph:
        if state[node] == NOT_VISITED:
            dfs(node, [])

    return cycles