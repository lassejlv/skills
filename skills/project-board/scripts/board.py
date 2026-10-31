#!/usr/bin/env python3
"""Mechanical parts of the project board: find it, create it, keep it private, keep its date true.

Standard library only, so that it runs in any project.

  board.py path                     print the board of this folder, or exit 1
  board.py init [--name N] [--root DIR]
                                    create .board/BOARD.md and keep it out of git
  board.py check                    report privacy, secrets, size and freshness problems
  board.py touch "what changed"     set the Last update line to today
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

BOARD = Path(".board") / "BOARD.md"
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "BOARD.template.md"
MAX_LINES = 300
MAX_NOW_LINES = 40
MAX_AGE_DAYS = 14
REQUIRED_SECTIONS = ("Now", "Rules")
LAST_UPDATE = re.compile(r"^Last update: (\d{4}-\d{2}-\d{2})?.*$", re.MULTILINE)

# Names only in the report: a check must never print the secret it found.
SECRETS = [
    ("private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("JWT", r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    ("GitLab token", r"\bglpat-[A-Za-z0-9_-]{20}"),
    ("AWS key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("Slack token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    ("API key", r"\bsk-[A-Za-z0-9_-]{20,}"),
    ("bearer token", r"\b[Bb]earer\s+[A-Za-z0-9._~+/-]{20,}"),
    ("assigned credential", r"(?i)\b(passwor[dt]|kennwort|adgangskode|secret|api[_-]?key|token)\s*[:=]\s*[\"']?(?!\$|<|\(|`)[^\s\"'`*<>()\[\]]{6,}"),
]


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def repo_root(path):
    result = git(path, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()) if result.returncode == 0 else None


def find_board(start):
    """The nearest board at or above this folder; a board above a repo covers every repo in that folder."""
    current = Path(start).resolve()
    for folder in (current, *current.parents):
        if folder == Path.home() or folder == folder.parent:
            break
        if (folder / BOARD).is_file():
            return folder / BOARD
    return None


def default_root(start):
    """The repo root, or the folder above it when that folder holds several repos and is no repo itself."""
    start = Path(start).resolve()
    root = repo_root(start)
    if root is None:
        return start
    parent = root.parent
    siblings = [d for d in parent.iterdir() if d.is_dir() and (d / ".git").exists()]
    if len(siblings) > 1 and repo_root(parent) is None:
        return parent
    return root


def exclude_from_git(root):
    """Uses .git/info/exclude: it needs no tracked file, so the board stays invisible to everyone else."""
    if repo_root(root) is None:
        return None
    path = Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude").stdout.strip())
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text() if path.exists() else ""
    if ".board/" not in text.splitlines():
        path.write_text(text + ("" if text.endswith("\n") or text == "" else "\n") + ".board/\n")
    return path


def privacy_problems(board):
    """Failures when the board is tracked or could be staged, in any repo that contains it."""
    folder = board.parent
    if repo_root(folder) is None:
        return []
    if git(folder, "ls-files", "--error-unmatch", board.name).returncode == 0:
        return ["the board is tracked by git: remove it from the index and the history"]
    if git(folder, "check-ignore", "-q", board.name).returncode != 0:
        return ["the board is not ignored: run init, or add .board/ to .git/info/exclude"]
    return []


def secret_problems(text):
    problems = []
    for number, line in enumerate(text.splitlines(), 1):
        for name, pattern in SECRETS:
            if re.search(pattern, line):
                problems.append(f"line {number}: {name}; remove it and say where it lives instead")
    return problems


def section_lines(text, title):
    match = re.search(rf"^## (?:\d+\.\s*)?{re.escape(title)}\b.*$", text, re.MULTILINE)
    if match is None:
        return None
    rest = text[match.end():]
    end = re.search(r"^## ", rest, re.MULTILINE)
    return len((rest[: end.start()] if end else rest).strip().splitlines())


def size_and_age_warnings(text, today):
    warnings = []
    lines = len(text.splitlines())
    if lines > MAX_LINES:
        warnings.append(f"{lines} lines (aim for {MAX_LINES}): move older Log entries to .board/archive/")
    now = section_lines(text, "Now")
    if now is not None and now > MAX_NOW_LINES:
        warnings.append(f"Now has {now} lines (aim for {MAX_NOW_LINES}): move finished items to the Log")
    for title in REQUIRED_SECTIONS:
        if section_lines(text, title) is None:
            warnings.append(f"no '## {title}' section")
    match = LAST_UPDATE.search(text)
    if match is None or match.group(1) is None:
        warnings.append("no dated 'Last update:' line: run touch")
    else:
        age = (today - datetime.date.fromisoformat(match.group(1))).days
        if age > MAX_AGE_DAYS:
            warnings.append(f"last update is {age} days old: check the board against the real state")
    return warnings


def cmd_path(_args):
    board = find_board(Path.cwd())
    if board is None:
        print("no board here or above; create one with: board.py init", file=sys.stderr)
        return 1
    print(board)
    return 0


def cmd_init(args):
    root = Path(args.root).resolve() if args.root else default_root(Path.cwd())
    board = root / BOARD
    exclude = exclude_from_git(root)
    if board.exists():
        print(f"{board} exists, left as it is")
        return 0
    board.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    board.write_text(TEMPLATE.read_text().replace("{{name}}", args.name or root.name).replace("{{date}}", today))
    print(board)
    if exclude is not None:
        print(f"kept out of git through {exclude}")
    return 0


def cmd_check(_args):
    board = find_board(Path.cwd())
    if board is None:
        print("no board here or above", file=sys.stderr)
        return 1
    text = board.read_text()
    failures = privacy_problems(board) + secret_problems(text)
    warnings = size_and_age_warnings(text, datetime.date.today())
    for line in failures:
        print(f"FAIL {line}")
    for line in warnings:
        print(f"warn {line}")
    if not failures and not warnings:
        print(f"ok {board}")
    return 1 if failures else 0


def cmd_touch(args):
    board = find_board(Path.cwd())
    if board is None:
        print("no board here or above", file=sys.stderr)
        return 1
    text = board.read_text()
    line = f"Last update: {datetime.date.today().isoformat()} ({args.note})"
    if LAST_UPDATE.search(text):
        text = LAST_UPDATE.sub(lambda _: line, text, count=1)
    else:
        parts = text.split("\n", 1)
        text = f"{parts[0]}\n\n{line}\n{parts[1] if len(parts) > 1 else ''}"
    board.write_text(text)
    print(line)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("path").set_defaults(run=cmd_path)
    init = commands.add_parser("init")
    init.add_argument("--name")
    init.add_argument("--root")
    init.set_defaults(run=cmd_init)
    commands.add_parser("check").set_defaults(run=cmd_check)
    touch = commands.add_parser("touch")
    touch.add_argument("note")
    touch.set_defaults(run=cmd_touch)
    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
