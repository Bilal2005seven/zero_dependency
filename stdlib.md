<div align="center">

# RepoMind — Standard Library Usage

**A complete reference of Python standard library modules used by RepoMind**

[![PyPI version](https://img.shields.io/pypi/v/repomind)](https://pypi.org/project/repomind/)
[![Python](https://img.shields.io/pypi/pyversions/repomind)](https://pypi.org/project/repomind/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

RepoMind is a **zero-dependency** tool — it relies exclusively on the Python standard library. This document lists every stdlib module used, which source file imports it, and what role it plays.

---

## Module Overview

| Module | Used In | Purpose |
|---|---|---|
| `ast` | `parser.py`, `complexity.py`, `security.py` | Parse Python source into an Abstract Syntax Tree |
| `pathlib` | `scanner.py`, `graph.py`, `html_report.py`, `cli.py` | Object-oriented filesystem path handling |
| `sys` | `cli.py` | Access CLI arguments and exit codes |
| `argparse` | `cli.py` | Parse command-line arguments and flags |
| `html` | `html_report.py` | Escape user-controlled strings for safe HTML output |
| `json` | `html_report.py` | Serialize dependency graph data for D3.js |
| `http.server` | `cli.py` (lazy) | Serve the HTML dashboard over localhost |
| `socket` | `cli.py` (lazy) | Find a free port by binding to port `0` |
| `threading` | `cli.py` (lazy) | Run the HTTP server on a background thread |
| `webbrowser` | `cli.py` (lazy) | Open the dashboard URL in the default browser |

---

## Per-Module Details

### `ast`

> **Imported in:** `parser.py`, `complexity.py`, `security.py`

The `ast` module compiles Python source code into an Abstract Syntax Tree and provides a visitor pattern to walk the tree nodes.

- **`parser.py`** — walks the AST to extract function definitions, class definitions, import statements, and function call sites.
- **`complexity.py`** — counts branching nodes (`If`, `For`, `While`, `Try`, `ExceptHandler`, `With`, `Assert`, `BoolOp`) to compute cyclomatic complexity per function.
- **`security.py`** — detects dangerous call patterns (`eval`, `exec`, `pickle.loads`) and weak hash algorithms (`md5`, `sha1`) by inspecting `Call` nodes.

---

### `pathlib`

> **Imported in:** `scanner.py`, `graph.py`, `html_report.py`, `cli.py`

`pathlib.Path` provides a cross-platform, object-oriented API for filesystem paths.

- **`scanner.py`** — uses `Path.rglob("*.py")` to recursively discover all Python files and filters out excluded directories.
- **`graph.py`** — resolves relative import paths to absolute module names for the dependency graph.
- **`html_report.py`** — resolves the output file path and writes the generated HTML to disk.
- **`cli.py`** — resolves the target project path supplied by the user and the HTML output path.

---

### `sys`

> **Imported in:** `cli.py`

- Calls `sys.exit(0)` after printing version information so the process terminates cleanly.

---

### `argparse`

> **Imported in:** `cli.py`

Provides the full CLI interface for RepoMind.

- Defines positional argument `path` (default: current directory).
- Defines flags: `--security`, `--graph`, `--complexity`, `--health`, `--summary`, `--html`, `--exclude`, `--version`.
- Automatically generates `--help` output.

---

### `html`

> **Imported in:** `html_report.py`

- `html.escape()` is called on every user-supplied string (function names, file paths, security messages) before embedding them in the HTML template, preventing XSS-style injection in the dashboard.

---

### `json`

> **Imported in:** `html_report.py`

- `json.dumps()` serialises the dependency graph (nodes and edges) into a JSON string that is embedded directly in the HTML file and consumed by the D3.js force-directed graph.

---

### `http.server` *(lazy import)*

> **Imported in:** `cli.py` — inside `_serve_and_open()`, only when `--html` is used

- `http.server.HTTPServer` runs a local web server.
- `http.server.SimpleHTTPRequestHandler` is subclassed to serve files from the report's directory and to suppress access-log noise.

---

### `socket` *(lazy import)*

> **Imported in:** `cli.py` — inside `_serve_and_open()`, only when `--html` is used

- Opens a temporary `SOCK_STREAM` socket, binds it to `("localhost", 0)`, and reads back the port number the OS assigned. This guarantees a free port without any hard-coded defaults or collision risks.

---

### `threading` *(lazy import)*

> **Imported in:** `cli.py` — inside `_serve_and_open()`, only when `--html` is used

- Starts the HTTP server on a daemon `Thread` so the main thread stays free to open the browser and wait for `Ctrl+C` without blocking.

---

### `webbrowser` *(lazy import)*

> **Imported in:** `cli.py` — inside `_serve_and_open()`, only when `--html` is used

- `webbrowser.open(url)` launches the dashboard URL in the user's default browser automatically after the server is ready.

---

## Lazy Imports

Four modules — `http.server`, `socket`, `threading`, and `webbrowser` — are imported **lazily** (inside the `_serve_and_open()` function body) rather than at the top of the module. This means:

- They incur zero import overhead when running any mode other than `--html`.
- The CLI starts faster for the common case (terminal analysis).

---

## Requirements

- Python 3.9 or higher
- Zero runtime dependencies (standard library only)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
