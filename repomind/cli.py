import sys
import argparse
from pathlib import Path

from repomind.scanner import scan_repository
from repomind.parser import parse_file
from repomind.graph import build_dependency_graph, detect_cycles
from repomind.complexity import calculate_complexity
from repomind.deadcode import find_unused_functions
from repomind.security import scan_security
from repomind.health import calculate_health_score
from repomind.html_report import generate_html_report
from repomind import __version__


def print_header(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def _serve_and_open(html_path: Path) -> None:
    """
    Start a localhost HTTP server serving html_path's directory,
    open the dashboard in the default browser, and block until Ctrl+C.
    """
    import http.server
    import socket
    import threading
    import webbrowser

    directory = str(html_path.parent.resolve())
    filename = html_path.name

    # Find a free port by binding to port 0 (OS assigns one)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):  # suppress access log noise
            pass

    httpd = http.server.HTTPServer(("localhost", port), _Handler)
    url = f"http://localhost:{port}/{filename}"

    print(f"\nRepoMind dashboard → {url}")
    print("Press Ctrl+C to stop the server.\n")

    # Open browser slightly after the server is ready
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


def main():

    # ==================================================
    # CLI ARGUMENTS
    # ==================================================

    cli = argparse.ArgumentParser(
        prog="repomind",
        description="Analyze a Python repository"
    )

    cli.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository (default: current directory)"
    )

    cli.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Directory to exclude (can be used multiple times)"
    )

    cli.add_argument(
        "--security",
        action="store_true",
        help="Show security analysis"
    )

    cli.add_argument(
        "--graph",
        action="store_true",
        help="Show dependency graph"
    )

    cli.add_argument(
        "--complexity",
        action="store_true",
        help="Show complexity analysis"
    )

    cli.add_argument(
        "--summary",
        action="store_true",
        help="Show repository health summary"
    )

    cli.add_argument(
        "--health",
        action="store_true",
        help="Show health analysis"
    )

    cli.add_argument(
        "--html",
        nargs="?",
        const=True,          # --html with no filename → open browser mode
        default=None,        # not provided at all
        metavar="OUTPUT",
        help=(
            "Generate an HTML dashboard and open it in the browser. "
            "Optionally supply OUTPUT to write to a specific file "
            "(e.g. --html report.html). Without OUTPUT, a temporary "
            "file is used and a local HTTP server is started."
        )
    )

    cli.add_argument(
        "--version",
        action="version",
        version=f"repomind {__version__}"
    )

    args = cli.parse_args()

    # Use Path(".").resolve() so the CWD at invocation time is used,
    # not the package installation directory.
    root = Path(args.path).resolve()

    # ==================================================
    # VALIDATE PATH
    # ==================================================

    if not root.exists():
        print(f"Error: path does not exist: {root}")
        sys.exit(1)

    if not root.is_dir():
        print(f"Error: path is not a directory: {root}")
        sys.exit(1)

    # ==================================================
    # SCAN REPOSITORY
    # ==================================================

    files = scan_repository(root, args.exclude)

    # ==================================================
    # REPOSITORY BASIC INFO
    # ==================================================

    print("REPO MIND")
    print("=" * 50)

    print(f"Python Files: {len(files)}")

    total_lines = sum(file["lines"] for file in files)
    total_size = sum(file["size"] for file in files)

    print(f"Total LOC:   {total_lines}")
    print(f"Total Size:  {total_size} bytes")

    # ==================================================
    # ANALYZE ALL FILES
    # ==================================================

    all_analysis = []

    for file in files:

        file_path = root / file["path"]

        result = parse_file(file_path)

        complexity = calculate_complexity(file_path)

        security_issues = scan_security(file_path)

        analysis = {
            **file,
            **result,
            "complexity": complexity,
            "security": security_issues,
        }

        all_analysis.append(analysis)

    # ==================================================
    # BUILD GRAPH
    # ==================================================

    dependency_graph = build_dependency_graph(all_analysis)

    cycles = detect_cycles(dependency_graph)

    # ==================================================
    # DEAD CODE
    # ==================================================

    unused_functions = find_unused_functions(all_analysis)

    # ==================================================
    # SECURITY
    # ==================================================

    all_security_issues = []

    for analysis in all_analysis:
        for issue in analysis["security"]:
            all_security_issues.append({**issue, "file": analysis["path"]})

    # ==================================================
    # COMPLEXITY
    # ==================================================

    all_functions = []

    for analysis in all_analysis:

        for function in analysis["complexity"]:

            all_functions.append({
                "file": analysis["path"],
                "name": function["name"],
                "line": function["line"],
                "complexity": function["complexity"],
            })

    # ==================================================
    # HEALTH SCORE
    # ==================================================

    health = calculate_health_score(
        security_issues=all_security_issues,
        cycles=cycles,
        complexity_results=[
            func
            for analysis in all_analysis
            for func in analysis["complexity"]
        ],
        unused_functions=unused_functions
    )

    # ==================================================
    # HTML MODE
    # ==================================================

    if args.html is not None:

        # Determine output path
        if args.html is True:
            # --html with no filename: write next to CWD, open via server
            output_path = Path.cwd() / "repomind_report.html"
            open_server = True
        else:
            # --html report.html: write to explicit file, open via server
            output_path = Path(args.html)
            open_server = True

        report_data = {
            "root": str(root),
            "files": files,
            "total_lines": total_lines,
            "total_size": total_size,
            "all_analysis": all_analysis,
            "dependency_graph": dependency_graph,
            "cycles": cycles,
            "unused_functions": unused_functions,
            "all_security_issues": all_security_issues,
            "all_functions": all_functions,
            "health": health,
        }

        generate_html_report(report_data, output_path)
        print(f"HTML report written to: {output_path.resolve()}")

        if open_server:
            _serve_and_open(output_path)

        return

    # ==================================================
    # DETERMINE MODE
    # ==================================================

    specific_mode = (
        args.security
        or args.graph
        or args.complexity
        or args.summary
        or args.health
    )

    # ==================================================
    # SECURITY MODE
    # ==================================================

    if args.security:

        print_header("SECURITY ANALYSIS")

        if all_security_issues:

            for issue in all_security_issues:

                print(
                    f"[!] {issue['type']} "
                    f"[{issue['severity']}] "
                    f"{issue['file']} "
                    f"(line {issue['line']})"
                )

        else:

            print("[OK] No security issues found")

    # ==================================================
    # GRAPH MODE
    # ==================================================

    elif args.graph:

        print_header("DEPENDENCY GRAPH")

        for module, dependencies in dependency_graph.items():

            print(f"\n{module}")

            if dependencies:

                for dependency in dependencies:

                    print(
                        f"  --> {dependency}"
                    )

            else:

                print("  --> None")

        print_header("CIRCULAR DEPENDENCIES")

        if cycles:

            for cycle in cycles:

                print("[!] CYCLE DETECTED:")

                print(
                    " -> ".join(cycle)
                )

        else:

            print(
                "[OK] No circular dependencies detected"
            )

    # ==================================================
    # COMPLEXITY MODE
    # ==================================================

    elif args.complexity:

        print_header("COMPLEXITY ANALYSIS")

        if all_functions:

            most_complex = max(
                all_functions,
                key=lambda x: x["complexity"]
            )

            print(
                f"\nMost Complex Function: "
                f"{most_complex['name']}"
            )

            print(
                f"File: {most_complex['file']}"
            )

            print(
                f"Line: {most_complex['line']}"
            )

            print(
                f"Complexity: "
                f"{most_complex['complexity']}"
            )

            print("\nAll Functions:")

            for function in all_functions:

                print(
                    f"  {function['name']:20} "
                    f"Complexity: "
                    f"{function['complexity']}"
                )

        else:

            print("No functions found")

    # ==================================================
    # SUMMARY MODE
    # ==================================================

    elif args.summary:

        print_header("REPOSITORY HEALTH")

        print(
            f"Health Score: "
            f"{health['score']} / 100"
        )

        print(
            f"Grade:        "
            f"{health['grade']}"
        )

        print(
            f"\nPython Files: "
            f"{len(files)}"
        )

        print(
            f"Total LOC:    "
            f"{total_lines}"
        )

        print(
            f"Security Issues: "
            f"{len(all_security_issues)}"
        )

        print(
            f"Circular Dependencies: "
            f"{len(cycles)}"
        )

        print(
            f"Unused Functions: "
            f"{len(unused_functions)}"
        )

        if all_functions:

            most_complex = max(
                all_functions,
                key=lambda x: x["complexity"]
            )

            print(
                f"Most Complex: "
                f"{most_complex['name']} "
                f"({most_complex['complexity']})"
            )
        # ==================================================
    # HEALTH MODE
    # ==================================================

    elif args.health:

        print_header("REPOSITORY HEALTH")

        print(
            f"Health Score: "
            f"{health['score']} / 100"
        )

        print(
            f"Grade:        "
            f"{health['grade']}"
        )

        print("\nHealth Details:")

        print(
            f"  Python Files: "
            f"{len(files)}"
        )

        print(
            f"  Total LOC: "
            f"{total_lines}"
        )

        print(
            f"  Security Issues: "
            f"{len(all_security_issues)}"
        )

        print(
            f"  Circular Dependencies: "
            f"{len(cycles)}"
        )

        print(
            f"  Unused Functions: "
            f"{len(unused_functions)}"
        )

        if all_functions:

            most_complex = max(
                all_functions,
                key=lambda x: x["complexity"]
            )

            print(
                f"  Most Complex Function: "
                f"{most_complex['name']}"
            )

            print(
                f"  Complexity: "
                f"{most_complex['complexity']}"
            )

    # ==================================================
    # FULL REPORT
    # ==================================================

    else:

        # --------------------------------------------------
        # CODE ANALYSIS
        # --------------------------------------------------

        print_header("CODE ANALYSIS")

        for analysis in all_analysis:

            print(
                f"\nFILE: "
                f"{analysis['path']}"
            )

            print("-" * 50)

            print("Functions:")

            if analysis["functions"]:

                for function in analysis["functions"]:

                    print(
                        f"  {function['name']} "
                        f"(line {function['line']})"
                    )

            else:

                print("  None")

            print("Classes:")

            if analysis["classes"]:

                for cls in analysis["classes"]:

                    print(
                        f"  {cls['name']} "
                        f"(line {cls['line']})"
                    )

            else:

                print("  None")

            print("Imports:")

            if analysis["imports"]:

                for imp in analysis["imports"]:

                    print(f"  {imp}")

            else:

                print("  None")

            print("Calls:")

            if analysis["calls"]:

                for call in analysis["calls"]:

                    print(f"  {call}")

            else:

                print("  None")

        # --------------------------------------------------
        # COMPLEXITY
        # --------------------------------------------------

        if all_functions:

            most_complex = max(
                all_functions,
                key=lambda x: x["complexity"]
            )

            print_header("COMPLEXITY SUMMARY")

            print(
                f"\nMost Complex Function: "
                f"{most_complex['name']}"
            )

            print(
                f"File: {most_complex['file']}"
            )

            print(
                f"Line: {most_complex['line']}"
            )

            print(
                f"Complexity: "
                f"{most_complex['complexity']}"
            )

        # --------------------------------------------------
        # SECURITY
        # --------------------------------------------------

        print("\nSecurity:")

        if all_security_issues:

            for issue in all_security_issues:

                print(
                    f"  [!] {issue['type']} "
                    f"[{issue['severity']}] "
                    f"{issue['file']} "
                    f"(line {issue['line']})"
                )

        else:

            print("  [OK] No issues found")

        # --------------------------------------------------
        # DEAD CODE
        # --------------------------------------------------

        print_header("POTENTIALLY UNUSED FUNCTIONS")

        if unused_functions:

            for function in unused_functions:

                print(
                    f"{function['name']:20} "
                    f"{function['file']} "
                    f"(line {function['line']})"
                )

        else:

            print(
                "[OK] No potentially unused "
                "functions found"
            )

        # --------------------------------------------------
        # DEPENDENCY GRAPH
        # --------------------------------------------------

        print_header("DEPENDENCY GRAPH")

        for module, dependencies in dependency_graph.items():

            print(f"\n{module}")

            if dependencies:

                for dependency in dependencies:

                    print(
                        f"  --> {dependency}"
                    )

            else:

                print("  --> None")

        # --------------------------------------------------
        # CYCLES
        # --------------------------------------------------

        print_header("CIRCULAR DEPENDENCIES")

        if cycles:

            for cycle in cycles:

                print("[!] CYCLE DETECTED:")

                print(
                    " -> ".join(cycle)
                )

        else:

            print(
                "[OK] No circular dependencies detected"
            )

        # --------------------------------------------------
        # HEALTH
        # --------------------------------------------------

        print_header("REPOSITORY HEALTH")

        print(
            f"Health Score: "
            f"{health['score']} / 100"
        )

        print(
            f"Grade:        "
            f"{health['grade']}"
        )

        # --------------------------------------------------
        # COMPLEXITY DETAILS
        # --------------------------------------------------

        print("\nComplexity:")

        if all_functions:

            for function in all_functions:

                print(
                    f"  {function['name']:20} "
                    f"Complexity: "
                    f"{function['complexity']}"
                )

        else:

            print("  None")


if __name__ == "__main__":
    main()
