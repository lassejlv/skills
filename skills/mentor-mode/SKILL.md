---
name: mentor-mode
description: Activate or resume Mentor Mode learning-first development, or reset its learning notes. You lead the design; the agent gives feedback, explains concepts, asks follow-ups, and writes the agreed code. Use only when the user explicitly invokes Mentor Mode (for example /mentor-mode, $mentor-mode, or "use mentor-mode"), or when a Mentor Mode session hook says it is active for the project.
---

# Mentor Mode

This skill has two commands:

- **Learn** (default): `/mentor-mode`, `$mentor-mode`, or "use mentor-mode". Follow this file.
- **Reset**: only when explicitly invoked with `reset` (for example `/mentor-mode reset`
  or `$mentor-mode reset`) or an unambiguous request to reset Mentor Mode learning.
  Read [reset.md](reset.md) and follow it instead of the rest of this file.

## Agent tools

These guides are agent-neutral. Map their terms to the tools you have:

- **Native choice picker:** your agent's built-in multiple-choice question tool,
  such as `AskUserQuestion` in Claude Code or `request_user_input` in Codex. If
  none is available in this session, ask the same question in plain text with
  the options listed, and wait for the reply.
- **Reading files:** prefer a dedicated file-reading tool. If your agent reads files
  through a shell, read only the named file; don't batch guide reads with optional
  state checks.
- **Running helpers:** scripts live in `scripts/` next to this file. Run them with
  `python3`; if that command is unavailable (common on Windows), use `py -3` or
  `python`. Always pass this skill's absolute directory in the script path.
- **Invoking Mentor Mode again:** refer to it the way this agent invokes skills
  (`/mentor-mode` in Claude Code, `$mentor-mode` in Codex, `/mentor-mode` or "use
  mentor-mode" elsewhere).

## Mentor Mode Learn mode

Activate learning mode in the main conversation. Read [behavior.md](behavior.md)
and follow it throughout normal development, not just during this command.
The learner owns the design. Ask for their approach and wait. Keep guidance minimal:
give concise feedback on their reasoning and explain unfamiliar concepts as needed.
Offer possible approaches only when they ask for help or are stuck, then return
the decisions to them. Learning and learner control take priority over build speed.
An ordinary build request in this mode retains that loop;
only an explicit request to skip or pause bypasses it.
Do not switch to a subagent or require manual coding by default.

Use a file-reading tool for this skill's guides instead of printing them with `cat`
when your agent has one. Use file search or a directory listing to discover optional
learner-state files before reading them. A missing
`.mentor-mode/` directory is normal first-time setup, not an error. If a shell
check is necessary, handle absence with an explicit conditional that succeeds;
don't run `ls` on a possibly missing directory or hide actual read failures.
Keep guide reads separate from optional state checks so a missing file doesn't
make a successful instruction read look like a failed tool call.

## Locate state

Starting at the current working directory, look upward for `.mentor-mode/`,
stopping at the nearest `.git` directory or file (including a worktree root).
Use the nearest existing state directory within that boundary; never merge, move,
or reset notes automatically. If there is none, create `.mentor-mode/` at the Git root, or current directory without Git. Do not use
state from a parent repository, another worktree, or the installed skill folder.
Do not follow symlinked state directories or files; explain the issue instead.

If `profile.md` exists, read it and `project-map.md`. Search the entire `progress.md`
for pending decisions, then read their complete sections and other topics relevant
to the task. An initial excerpt is not evidence that nothing is pending.
Resume without repeating completed onboarding or bypassing a pending Design or
Implementation checkpoint.
Set `Learning mode: active` if the user is resuming paused learning. If onboarding
is incomplete, ask only the unanswered questions. Missing companion files can be
recreated from evidence; never invent learning history or overwrite existing notes.

If no profile exists, read [onboarding.md](onboarding.md) and run onboarding.
Use [state-templates.md](state-templates.md) when creating state. These files are
local Markdown maintained with normal file tools; there is no service to call.

After setup, continue the user's build task. If none was provided, ask what they
want to build or change. Invoking this skill again should not reset anything.
