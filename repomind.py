import sys
import argparse
from pathlib import Path

from scanner import scan_repository
from parser import parse_file
from graph import build_dependency_graph, detect_cycles
from complexity import calculate_complexity
from deadcode import find_unused_functions
from security import scan_security
from health import calculate_health_score


def print_header(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


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
        help="Path to the repository"
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
        action = "store_true",
        help="Show health analysis"
    )

    args = cli.parse_args()

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
        all_security_issues.extend(
            analysis["security"]
        )

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
                    f"⚠ {issue['type']} "
                    f"[{issue['severity']}] "
                    f"{issue['file']} "
                    f"(line {issue['line']})"
                )

        else:

            print("✓ No security issues found")

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
                        f"  └──> {dependency}"
                    )

            else:

                print("  └──> None")

        print_header("CIRCULAR DEPENDENCIES")

        if cycles:

            for cycle in cycles:

                print("⚠ CYCLE DETECTED:")

                print(
                    " → ".join(cycle)
                )

        else:

            print(
                "✓ No circular dependencies detected"
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
                    f"  ⚠ {issue['type']} "
                    f"[{issue['severity']}] "
                    f"{issue['file']} "
                    f"(line {issue['line']})"
                )

        else:

            print("  ✓ No issues found")

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
                "✓ No potentially unused "
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
                        f"  └──> {dependency}"
                    )

            else:

                print("  └──> None")

        # --------------------------------------------------
        # CYCLES
        # --------------------------------------------------

        print_header("CIRCULAR DEPENDENCIES")

        if cycles:

            for cycle in cycles:

                print("⚠ CYCLE DETECTED:")

                print(
                    " → ".join(cycle)
                )

        else:

            print(
                "✓ No circular dependencies detected"
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