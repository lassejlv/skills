"""Register (or remove) Mentor Mode's SessionStart restore hook for one agent.

The hook is a one-time opt-in per agent. Preview is the default; pass
--apply to write. Only Mentor Mode's own entry is added or removed; other settings
and hooks are preserved, and the previous file is kept as <name>.bak.
"""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile


SCRIPT = Path(__file__).resolve().parent / "session_start.py"
MARKER = "session_start.py"

# User-level config file for each agent. Every agent below also loads it in
# addition to project-level hooks, so the hook covers every project.
CONFIGS = {
    "claude": Path("~/.claude/settings.json"),
    "codex": Path("~/.codex/hooks.json"),
    "gemini": Path("~/.gemini/settings.json"),
    "cursor": Path("~/.cursor/hooks.json"),
}


def quote(path):
    # Forward slashes work in POSIX shells, cmd, and PowerShell on Windows.
    text = Path(path).as_posix()
    return '"{}"'.format(text) if " " in text else text


def command(agent, python=None):
    return "{} {} --agent {}".format(quote(python or sys.executable), quote(SCRIPT), agent)


def entry(agent, python=None):
    cmd = command(agent, python)
    if agent == "cursor":
        return {"command": cmd}
    handler = {"type": "command", "command": cmd}
    if agent == "gemini":
        # Gemini matches SessionStart sources exactly; no matcher means all of them.
        # Its timeouts are milliseconds.
        handler.update(name="mentor-mode-restore", timeout=5000)
        return {"hooks": [handler]}
    # Claude Code and Codex use regex matchers and timeouts in seconds.
    matcher = "startup|resume|clear|compact" + ("|fork" if agent == "claude" else "")
    handler["timeout"] = 5
    return {"matcher": matcher, "hooks": [handler]}


def is_ours(group):
    """True for a hook group whose commands run this skill's restore script."""
    if not isinstance(group, dict):
        return False
    commands = [group.get("command")]
    commands += [h.get("command") for h in group.get("hooks", []) if isinstance(h, dict)]
    return any(isinstance(c, str) and MARKER in c and "--agent" in c for c in commands)


def event_list(config, agent):
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("'hooks' in the config is not an object; edit it manually.")
    if agent == "cursor":
        config.setdefault("version", 1)
    groups = hooks.setdefault("sessionStart" if agent == "cursor" else "SessionStart", [])
    if not isinstance(groups, list):
        raise ValueError("SessionStart hooks are not a list; edit the config manually.")
    return groups


def load(path):
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    config = json.loads(text) if text.strip() else {}
    if not isinstance(config, dict):
        raise ValueError("{} does not contain a JSON object.".format(path))
    return config


def plan(agent, path, uninstall=False, python=None):
    """Return (before, after) configs without writing anything."""
    before = load(path)
    after = json.loads(json.dumps(before))
    groups = event_list(after, agent)
    groups[:] = [g for g in groups if not is_ours(g)]
    if not uninstall:
        groups.append(entry(agent, python))
    return before, after


def write(path, config):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.with_name(path.name + ".bak").write_bytes(path.read_bytes())
    fd, temp = tempfile.mkstemp(prefix=".mentor-mode-", dir=path.parent)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(config, stream, indent=2)
        stream.write("\n")
    os.replace(temp, path)


def installed(agent, path):
    try:
        config = load(path)
    except (OSError, ValueError):
        return False
    hooks = config.get("hooks")
    if not isinstance(hooks, dict):
        return False
    groups = hooks.get("sessionStart" if agent == "cursor" else "SessionStart")
    return isinstance(groups, list) and any(is_ours(g) for g in groups)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=sorted(CONFIGS))
    parser.add_argument("--config", help="Config file to edit (default: the agent's user config)")
    parser.add_argument("--python", help="Interpreter for the hook (default: this one)")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--status", action="store_true", help="Report whether the hook is installed")
    action.add_argument("--uninstall", action="store_true", help="Remove Mentor Mode's hook entry")
    parser.add_argument("--apply", action="store_true", help="Write the change (default: preview)")
    args = parser.parse_args(argv)
    path = Path(args.config).expanduser() if args.config else CONFIGS[args.agent].expanduser()

    if args.status:
        print(json.dumps({"agent": args.agent, "config": str(path),
                          "installed": installed(args.agent, path)}))
        return 0
    try:
        before, after = plan(args.agent, path, args.uninstall, args.python)
        changed = before != after
        if args.apply and changed:
            write(path, after)
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "error", "config": str(path), "message": str(error)}))
        return 1
    status = ("applied" if args.apply else "preview") if changed else "unchanged"
    print(json.dumps({"status": status, "agent": args.agent, "config": str(path),
                      "result": after}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
