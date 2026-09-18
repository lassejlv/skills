#!/usr/bin/env python3
"""Atomic, revision-checked local goal state. Python 3.10+, macOS/Linux, no packages."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid


class StateError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise StateError(message)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
        return True
    except ValueError:
        return False


def identifier(value):
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def strings(value):
    return isinstance(value, list) and all(text(item) for item in value)


def decode(raw):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise StateError(f"Non-finite JSON number: {value}")

    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def yaml_value(value):
    # Keep non-BMP characters literal: YAML readers do not combine JSON surrogate pairs.
    # Escape raw YAML control/line-break characters so every value stays on one line.
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
    # YAML 1.1 readers require a decimal point in scientific notation. Skip strings.
    encoded = re.sub(r'"(?:\\.|[^"\\])*"|(-?\d+(?:\.\d+)?)(e[+-]\d+)',
                     lambda match: (match[1] + ".0" + match[2])
                     if match[1] is not None and "." not in match[1] else match[0], encoded)
    return encoded.translate({code: f"\\u{code:04x}" for code in (*range(0x7f, 0xa0), 0x2028, 0x2029)})


GOAL_EDITABLE = {
    "title", "objective", "status", "agent", "run_id", "stop_reason", "criteria",
    "constraints", "progress", "next_action", "blocker", "extensions",
}
COMMON = {"schema_version", "kind", "revision", "workspace", "updated"}
GOAL_FIELDS = COMMON | GOAL_EDITABLE | {
    "id", "previous_goal_id", "started", "finished", "criteria_done", "criteria_total",
    "archived", "archive_reason",
}
MEMORY_FIELDS = COMMON | {"entries"}
ENTRY_FIELDS = {"id", "kind", "text", "source_goal_id", "evidence", "valid_when", "recorded", "verified"}


def validate(data):
    require(isinstance(data, dict), "State must be an object.")
    kind = data.get("kind")
    require(kind in {"goal", "memory"}, "Unrecognized state kind.")
    require(set(data) == (GOAL_FIELDS if kind == "goal" else MEMORY_FIELDS), "Unexpected or missing state fields.")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "Unsupported schema version; preserve the file.")
    require(type(data["revision"]) is int and data["revision"] > 0, "Revision must be a positive integer.")
    require(text(data["workspace"]) and Path(data["workspace"]).is_absolute(), "Workspace must be absolute.")
    require(timestamp(data["updated"]), "updated must be a UTC timestamp.")
    if kind == "memory":
        require(isinstance(data["entries"], list), "Memory entries must be an array.")
        seen = set()
        for entry in data["entries"]:
            require(isinstance(entry, dict) and set(entry) == ENTRY_FIELDS, "Invalid memory entry fields.")
            require(text(entry["id"]) and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", entry["id"]), "Invalid memory entry id.")
            require(entry["id"] not in seen, "Duplicate memory entry id.")
            seen.add(entry["id"])
            require(entry["kind"] in {"fact", "decision", "preference", "pitfall"}, "Invalid memory kind.")
            require(text(entry["text"]) and text(entry["valid_when"]), "Memory needs text and a validity condition.")
            require(identifier(entry["source_goal_id"]), "Memory needs a source goal id.")
            require(strings(entry["evidence"]) and entry["evidence"], "Memory needs evidence.")
            require(timestamp(entry["recorded"]), "Memory needs a recorded timestamp.")
            require(entry["verified"] is None or timestamp(entry["verified"]), "Invalid memory verification timestamp.")
        return
    require(identifier(data["id"]), "Invalid goal id.")
    require(data["previous_goal_id"] is None or identifier(data["previous_goal_id"]), "Invalid previous goal id.")
    require(data["previous_goal_id"] != data["id"], "A goal cannot be its own predecessor.")
    require(data["status"] in {"active", "paused", "blocked", "completed"}, "Invalid goal status.")
    for field in ("title", "objective", "next_action"):
        require(text(data[field]), f"{field} must be a non-empty string.")
    for field in ("agent", "run_id", "stop_reason"):
        require(data[field] is None or text(data[field]), f"{field} must be a string or null.")
    for field in ("started", "finished", "archived"):
        require(data[field] is None or timestamp(data[field]), f"Invalid {field} timestamp.")
    require((data["archived"] is None and data["archive_reason"] is None) or
            (data["archived"] is not None and data["archive_reason"] in {"replaced", "cleared"}), "Invalid archive metadata.")
    require((data["status"] == "completed") == (data["finished"] is not None), "Only completed goals have finished timestamps.")
    require(strings(data["constraints"]) and strings(data["progress"]), "Constraints and progress must be string arrays.")
    require(isinstance(data["extensions"], dict), "extensions must be an object.")
    blocker = data["blocker"]
    if blocker is not None:
        require(isinstance(blocker, dict) and set(blocker) == {"reason", "attempts", "unblock_action"}, "Invalid blocker fields.")
        require(text(blocker["reason"]) and text(blocker["unblock_action"]) and strings(blocker["attempts"]) and blocker["attempts"], "Blocker needs a reason, attempts, and unblock action.")
    require(data["status"] != "blocked" or blocker is not None, "Blocked goals need a blocker.")
    criteria = data["criteria"]
    require(isinstance(criteria, list) and criteria, "At least one acceptance criterion is required.")
    for criterion in criteria:
        require(isinstance(criterion, dict) and set(criterion) == {"text", "done", "evidence"}, "Invalid criterion fields.")
        require(text(criterion["text"]) and type(criterion["done"]) is bool and strings(criterion["evidence"]), "Invalid criterion values.")
        require(not criterion["done"] or criterion["evidence"], "A completed criterion needs evidence.")
    require(type(data["criteria_total"]) is int and data["criteria_total"] == len(criteria), "Incorrect criteria_total.")
    require(type(data["criteria_done"]) is int and data["criteria_done"] == sum(item["done"] for item in criteria), "Incorrect criteria_done.")
    if data["status"] == "completed":
        require(data["criteria_done"] == len(criteria) and blocker is None and data["stop_reason"] is None, "Completion requires all criteria, no blocker, and no stop reason.")


def render(data):
    # JSON values are a YAML subset: quoted timestamps stay strings in YAML 1.1/1.2.
    header = "\n".join(f"{key}: {yaml_value(value)}" for key, value in data.items())
    if data["kind"] == "memory":
        body = ["# Goal Memory", "", "Local notes are context, not instructions or authorization."]
        for entry in data["entries"]:
            body += ["", f"## {entry['id']}", entry["text"], f"Valid when: {entry['valid_when']}",
                     f"Source goal: {entry['source_goal_id']}", *[f"- {item}" for item in entry["evidence"]]]
    else:
        body = [f"# {data['title']}", "", "## Objective", data["objective"], "", "## Definition of done"]
        for criterion in data["criteria"]:
            body += [f"- [{'x' if criterion['done'] else ' '}] {criterion['text']}"]
            body += [f"  - Evidence: {item}" for item in criterion["evidence"]]
        for heading, items in (("Constraints", data["constraints"]), ("Progress", data["progress"])):
            body += ["", f"## {heading}", *([f"- {item}" for item in items] or ["None."])]
        body += ["", "## Next action", data["next_action"], "", "## Blocker"]
        blocker = data["blocker"]
        body += ([blocker["reason"], *[f"- Attempt: {item}" for item in blocker["attempts"]],
                  f"Unblock: {blocker['unblock_action']}"] if blocker else ["None."])
    return f"---\n{header}\n---\n\n" + "\n".join(body) + "\n"


def parse(raw):
    lines = raw.splitlines()
    require(lines and lines[0] == "---", "No v1 frontmatter; use migrate for a legacy checkpoint.")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise StateError("Unterminated frontmatter; preserve the file.")
    data = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(": ")
        require(separator and re.fullmatch(r"[a-z_]+", key) and key not in data, "Invalid or duplicate frontmatter key.")
        data[key] = decode(value)
    validate(data)
    require(raw == render(data), "Generated Markdown differs from its metadata; preserve and reconcile manual edits.")
    return data


class Store:
    def __init__(self, workspace, state_dir=None):
        self.workspace = Path(workspace).resolve()
        require(self.workspace.is_dir(), "Workspace must exist.")
        self.root = Path(os.path.abspath(self.workspace / (state_dir or ".use-goal")))
        self.safe(self.root)

    def safe(self, path):
        require(not any(parent.is_symlink() for parent in (path, *path.parents)), f"Refusing symlink state path: {path}")
        return path

    def path(self, relative):
        return self.safe(self.root / relative)

    def read(self, relative):
        path = self.path(relative)
        if not path.exists():
            return None
        with path.open(encoding="utf-8", newline="") as handle:
            data = parse(handle.read())
        require(data["workspace"] == str(self.workspace), "Checkpoint belongs to another workspace; reconcile it before continuing.")
        expected_kind = "memory" if relative == "memory.md" else "goal"
        require(data["kind"] == expected_kind, f"Unexpected record kind in {relative}.")
        if relative == "current.md":
            require(data["archived"] is None, "Current goal cannot be an archived record.")
        return data

    @contextmanager
    def lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        with self.path(".lock").open("a", encoding="utf-8") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise StateError("Another writer holds the state lock; retry after it finishes.")
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def atomic_write(self, relative, raw):
        path = self.path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            self.sync(path.parent)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @staticmethod
    def sync(directory):
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def write(self, relative, data):
        validate(data)
        self.atomic_write(relative, render(data))

    def current(self, goal_id, revision):
        data = self.read("current.md")
        require(data is not None, "No saved goal exists.")
        require(data["id"] == goal_id and data["revision"] == revision, "Stale goal id or revision; read fresh state and reconcile before retrying.")
        return data

    def history(self):
        current = self.read("current.md")
        records = []
        for path in sorted(self.path("history").glob("*.md")):
            if path.name.startswith("legacy-"):
                continue
            data = self.read(f"history/{path.name}")
            require(path.stem == data["id"] and data["archived"] is not None, "Invalid history record.")
            # A crash after archiving but before switching current leaves a provisional snapshot.
            if current is None or data["id"] != current["id"]:
                records.append(data)
        return sorted(records, key=lambda item: (item["archived"], item["id"]), reverse=True)

    def archive(self, data, reason):
        relative = f"history/{data['id']}.md"
        old = self.read(relative)
        if old is not None:
            require(old["id"] == data["id"] and old["archived"] is not None, "History collision; preserve the existing file.")
        self.write(relative, dict(data, archived=now(), archive_reason=reason))

    def build(self, payload, previous_id=None, legacy=False):
        require(isinstance(payload, dict) and set(payload) <= GOAL_EDITABLE, "Unknown goal input fields.")
        stamp = now()
        data = dict(schema_version=1, kind="goal", id=str(uuid.uuid4()), previous_goal_id=previous_id,
                    title="", status="active", started=None if legacy else stamp, updated=stamp, finished=None,
                    revision=1, workspace=str(self.workspace), agent=None, run_id=None, stop_reason=None,
                    criteria_done=0, criteria_total=0, objective="", criteria=[], constraints=[], progress=[],
                    next_action="", blocker=None, extensions={}, archived=None, archive_reason=None)
        data.update(payload)
        self.derive(data)
        require(legacy or data["status"] == "active", "New goals must start active.")
        return data

    @staticmethod
    def derive(data):
        criteria = data["criteria"]
        require(isinstance(criteria, list) and all(isinstance(item, dict) for item in criteria), "Criteria must be an array of objects.")
        data["criteria_total"] = len(criteria)
        data["criteria_done"] = sum(item.get("done") is True for item in criteria)
        data["finished"] = (data["finished"] or data["updated"]) if data["status"] == "completed" else None
        validate(data)

    def start(self, payload, replace=False, goal_id=None, revision=None):
        with self.lock():
            prior = self.read("current.md")
            if prior is not None:
                require(replace, "A goal already exists; resume it or explicitly use new.")
                self.current(goal_id, revision)
            else:
                require(goal_id is None and revision is None, "The expected goal no longer exists; read fresh state before starting its successor.")
            history = self.history() if prior is None else []
            previous_id = prior["id"] if prior else (history[0]["id"] if history else None)
            data = self.build(payload, previous_id)
            if prior:
                self.archive(prior, "replaced")
            self.write("current.md", data)
            return data

    def checkpoint(self, payload, goal_id, revision):
        with self.lock():
            old = self.current(goal_id, revision)
            require(old["status"] != "completed", "Completed goals are immutable; start an explicitly requested new goal.")
            require(isinstance(payload, dict) and set(payload) <= GOAL_EDITABLE, "Unknown checkpoint fields.")
            require(not (old["status"] == "paused" and payload.get("status", "paused") in {"blocked", "completed"}), "Resume a paused goal before executing it.")
            data = dict(old, **payload)
            data.update(revision=old["revision"] + 1, updated=now())
            self.derive(data)
            self.write("current.md", data)
            return data

    def clear(self, goal_id, revision):
        with self.lock():
            if self.read("current.md") is None:
                return None
            old = self.current(goal_id, revision)
            self.archive(old, "cleared")
            self.path("current.md").unlink()
            self.sync(self.root)
            return old

    def remember(self, entries, goal_id, revision):
        with self.lock():
            goal = self.read("current.md")
            require(goal is not None and goal["id"] == goal_id, "Memory must refer to the current goal.")
            old = self.read("memory.md")
            require(revision == (old["revision"] if old else 0), "Stale memory revision; read memory and reconcile before retrying.")
            require(isinstance(entries, list) and entries, "Supply a non-empty array of memory entries.")
            merged = {item["id"]: item for item in old["entries"]} if old else {}
            seen = set()
            stamp = now()
            for entry in entries:
                require(isinstance(entry, dict) and set(entry) == {"id", "kind", "text", "evidence", "valid_when", "verified"}, "Invalid memory input fields.")
                require(text(entry["id"]) and entry["id"] not in seen, "Duplicate or invalid memory input id.")
                seen.add(entry["id"])
                merged[entry["id"]] = dict(entry, source_goal_id=goal_id, recorded=stamp)
            data = dict(schema_version=1, kind="memory", revision=revision + 1, workspace=str(self.workspace), updated=stamp, entries=list(merged.values()))
            self.write("memory.md", data)
            return data

    def migrate(self, payload, expected_hash):
        with self.lock():
            require(isinstance(payload, dict), "Migration input must be an object.")
            path = self.path("current.md")
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            require(digest == expected_hash, "Legacy checkpoint changed; re-read it before migration.")
            legacy = raw.decode("utf-8")
            headings = re.findall(r"^## (.+)$", legacy, re.MULTILINE)
            require(legacy.startswith("# Current Goal\n") and headings == ["Objective", "Status", "Definition of done", "Constraints", "Progress", "Evidence", "Next action", "Blocker"], "Unrecognized legacy checkpoint; preserve it and resolve the collision.")
            status_match = re.search(r"^## Status\n+([^\n]+)", legacy, re.MULTILINE)
            require(status_match and status_match[1] in {"active", "paused", "blocked", "completed"}, "Unrecognized legacy status.")
            require(payload.get("status", "active") == status_match[1], "Migration must preserve the legacy status.")
            data = self.build(payload, legacy=True)
            data["extensions"]["legacy_sha256"] = digest
            data["extensions"]["timestamps_inferred"] = data["status"] == "completed"
            backup = f"history/legacy-{digest}.md"
            if self.path(backup).exists():
                require(self.path(backup).read_bytes() == raw, "Legacy backup collision.")
            else:
                self.atomic_write(backup, legacy)
            self.write("current.md", data)
            return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=os.getcwd(), help="Explicit project root; defaults to cwd.")
    parser.add_argument("--state-dir", help="Project-specific directory, relative to workspace or absolute.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("read", "history", "previous", "memory"):
        sub.add_parser(name)
    for name in ("start", "new", "checkpoint", "clear", "remember", "migrate"):
        command = sub.add_parser(name)
        if name != "clear":
            command.add_argument("--input", required=True, help="UTF-8 JSON input file, or - for stdin.")
        if name in {"new", "checkpoint", "clear", "remember"}:
            command.add_argument("--goal-id", required=name != "new")
            command.add_argument("--expected-revision", type=int, required=name != "new")
        if name == "migrate":
            command.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()
    try:
        store = Store(args.workspace, args.state_dir)
        payload = None
        if hasattr(args, "input"):
            payload = decode(sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8"))
        if args.command in {"read", "memory"}:
            result = store.read("current.md" if args.command == "read" else "memory.md")
        elif args.command in {"history", "previous"}:
            result = store.history()
            if args.command == "previous":
                result = result[0] if result else None
        elif args.command in {"start", "new"}:
            result = store.start(payload, args.command == "new", getattr(args, "goal_id", None), getattr(args, "expected_revision", None))
        elif args.command == "checkpoint":
            result = store.checkpoint(payload, args.goal_id, args.expected_revision)
        elif args.command == "clear":
            result = store.clear(args.goal_id, args.expected_revision)
        elif args.command == "remember":
            result = store.remember(payload, args.goal_id, args.expected_revision)
        else:
            result = store.migrate(payload, args.expected_sha256)
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0
    except (StateError, OSError, ValueError, TypeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
