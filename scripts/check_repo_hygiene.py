"""Check tracked repository contents and active documentation integrity.

This script intentionally uses only the Python standard library so it can run
in a clean checkout before project dependencies are installed.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ALLOWED_ROOT_FILES = {
    ".dockerignore",
    ".env.example",
    ".gitattributes",
    ".gitignore",
    ".nvmrc",
    ".python-version",
    "AGENTS.md",
    "CHANGELOG.md",
    "Dockerfile",
    "Makefile",
    "README.md",
    "docker-compose.yml",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
    "start_dev.bat",
    "start_dev.ps1",
    "uv.lock",
}

ALLOWED_TOP_LEVEL_DIRS = {
    ".github",
    ".governance",
    "backend",
    "core",
    "data",
    "docs",
    "eval",
    "frontend",
    "kiosk",
    "models",
    "scripts",
    "server",
    "src",
    "submission",
    "tests",
}

FORBIDDEN_PREFIXES = (
    ".local/",
    ".venv/",
    "venv/",
    "env/",
    "node_modules/",
    "frontend/node_modules/",
    "frontend/dist/",
    "data/uploads/",
    "data/sessions/",
    "submission/raw/",
    "submission/work/",
)

FORBIDDEN_SUFFIXES = (
    ".db",
    ".sqlite",
    ".sqlite3",
    ".pem",
    ".key",
    ".log",
    ".bak",
    ".tmp",
    ".temp",
    ".orig",
    ".rej",
)

MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def check_required_files(files: set[str], errors: list[str]) -> None:
    required = {
        "AGENTS.md",
        "README.md",
        ".dockerignore",
        ".github/CODEOWNERS",
        ".github/pull_request_template.md",
        "docs/FEATURES.md",
        "docs/tasks/active/README.md",
        "docs/decisions/README.md",
    }
    for path in sorted(required - files):
        errors.append(f"required repository file is missing: {path}")


def check_root_layout(files: list[str], errors: list[str]) -> None:
    for path in files:
        if "/" in path:
            continue
        if path not in ALLOWED_ROOT_FILES:
            errors.append(f"unexpected root-level file: {path}")

    for path in files:
        top_level = path.split("/", 1)[0]
        if "/" in path and top_level not in ALLOWED_TOP_LEVEL_DIRS:
            errors.append(f"unexpected top-level directory: {top_level}/")


def check_forbidden_tracked_paths(files: list[str], errors: list[str]) -> None:
    for path in files:
        normalized = path.replace("\\", "/")
        basename = normalized.rsplit("/", 1)[-1]

        if normalized == ".env" or (
            normalized.startswith(".env.") and normalized != ".env.example"
        ):
            errors.append(f"environment secret file is tracked: {path}")
        if normalized.startswith(FORBIDDEN_PREFIXES):
            errors.append(f"local/build/data path is tracked: {path}")
        if basename.endswith(FORBIDDEN_SUFFIXES):
            errors.append(f"private/generated artifact is tracked: {path}")
        if fnmatch.fnmatch(basename, "*.new.md"):
            errors.append(f"temporary documentation file is tracked: {path}")


def active_markdown_files(files: list[str]) -> list[str]:
    excluded = ("docs/archive/", "docs/tasks/")
    return [
        path
        for path in files
        if path.endswith(".md") and not path.startswith(excluded)
    ]


def check_markdown_links(files: list[str], errors: list[str]) -> None:
    for relative in active_markdown_files(files):
        source = ROOT / relative
        try:
            text = source.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read {relative}: {exc}")
            continue

        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0].split("?", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (source.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"broken local Markdown link in {relative}: {raw_target}")


def check_adr_index(files: list[str], errors: list[str]) -> None:
    index = (ROOT / "docs/decisions/README.md").read_text(encoding="utf-8")
    decision_files = [
        path.rsplit("/", 1)[-1]
        for path in files
        if path.startswith("docs/decisions/")
        and path.endswith(".md")
        and not path.endswith("/README.md")
    ]
    for filename in decision_files:
        if filename not in index:
            errors.append(f"ADR is not listed in docs/decisions/README.md: {filename}")


def main() -> int:
    errors: list[str] = []
    files = tracked_files()
    file_set = set(files)

    check_required_files(file_set, errors)
    check_root_layout(files, errors)
    check_forbidden_tracked_paths(files, errors)
    check_markdown_links(files, errors)
    check_adr_index(files, errors)

    if errors:
        print("Repository hygiene: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Repository hygiene: PASS ({len(files)} tracked files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
