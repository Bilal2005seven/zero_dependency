from pathlib import Path


IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
}


def scan_repository(root_path, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = set()

    root = Path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"Repository not found: {root_path}")

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    exclude_dirs = set(exclude_dirs)

    files = []

    for path in root.rglob("*.py"):
        relative_parts = path.relative_to(root).parts

        if any(
            excluded in relative_parts
            for excluded in IGNORED_DIRS | exclude_dirs
        ):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        files.append({
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "lines": len(content.splitlines()),
        })

    return files