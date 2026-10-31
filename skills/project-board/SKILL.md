---
name: project-board
description: Keep a private working board for a project - one local Markdown file (.board/BOARD.md), only for the agent, that holds the current state, open work, waiting items, findings, environment notes and every rule the user and others have given, so nothing is lost between sessions or after a compact. Use this whenever the user mentions a board, brief room, "boardet" or a work log for the agent; whenever a session starts or resumes in a folder with a .board/ directory; after a compact; when the user asks where things stand ("hvor kom vi til", "what's next", "hvad mangler vi"); when the user gives a standing rule that must survive the session; and when a long multi-session project has no board yet. Not for task lists the user reads, team trackers (Linear, Jira, GitHub Projects) or documents meant for other people.
---

# Project board

A board is the agent's own notebook for one project. Long projects outlive any single session, and compacts and new sessions drop detail: which PR waits for whom, what was tested and what was not, the rule the user gave three days ago. The board keeps one current picture in one file, so the next session starts where the last one stopped.

It only works if it stays three things:

- **Private.** It is for the agent. It never reaches a repository or another person, so it can hold blunt notes.
- **Current.** A stale board is worse than none, because it gets believed.
- **Short.** A board nobody can read in one go gets skimmed, and the rule on line 400 gets missed.

`scripts/board.py` (next to this file) does the mechanical parts. Run it with `python3 <skill dir>/scripts/board.py <command>`.

## At the start of every session and after every compact

1. Run `board.py path` to find the board. It walks up from the current folder.
2. Read the whole **Rules** section and the **Now** section before doing anything else. Rules bind every step, and Now says where to pick up. Read other sections when the task touches them.
3. Run `board.py check` and fix what it reports.
4. Treat the board as a lead, not as proof. It says what was true when it was written. Before you act on a claim that can have changed (a branch, a PR, a ticket, a running server), look at the source, and correct the board if it was wrong.

If the user asks where things stand, answer from the board plus that check, not from the board alone.

## Setting up a board

Do this when the user asks for one, or offer it in one line when a project clearly spans several sessions.

1. Run `board.py init --name "<project>"`. It picks the folder, creates `.board/BOARD.md` from the template and protects it. Pass `--root <dir>` when you know better: for several repos under one folder, the board belongs in that folder, above the repos.
2. Fill in what you already know. Delete the sections the project will not use; add one if the project needs it.
3. Put the rules the user gave so far into **Rules**. Then read `references/starter-rules.md` and add the ones that fit this project.
4. Make the next session find it. A skill does not start by itself, so add a line to the agent's persistent memory: "Read `<path>` at the start of every session and after every compact; update it after each step that changes state; never commit it." If there is no memory, use a file that stays local, such as `CLAUDE.local.md`. A committed `CLAUDE.md` or `AGENTS.md` would reveal the board to everyone, so leave those alone.

## What goes where

| Section | Holds |
| --- | --- |
| Now | Where things stand and the exact next step. What the next session must do first. |
| Overview | What the project is, the repositories, the people and who decides what. Who tests, reviews and merges. |
| Work | One row per ticket or task: state, owner, branch or PR. |
| Waiting for | What is stuck on whom, and what happens when it arrives. |
| Findings | Bugs and problems noticed on the way that are not being worked on yet. |
| Log | What was done, newest first, one or two lines each, with the decisive detail: the commit, the cause, the result. |
| Environment | Paths, versions, commands that work, what is running, and what broke and how it was fixed. |
| Time and billing | Only when the project has it: rates, limits, how hours are reported. |
| Rules | Every standing rule, by source. See below. |
| Process | The repeatable steps per ticket, when the project has a fixed flow. |

Keep the headings **Now** and **Rules**; `check` looks for them.

## Updating the board

Update after each step that changes something the board states: a ticket moved, a PR pushed, a review arrived, a rule was added, a server started or stopped, something was found. Do it as part of the step, not at the end, because a session can be cut off at any point. Then run `board.py touch "<what changed>"` so that the date on top stays true.

Write it so a stranger could act on it:

- **Absolute dates.** "Today" and "tomorrow" mean nothing next week. Write `2026-10-30`, or `30/10` once the year is clear.
- **Exact references.** Commit hashes, PR numbers, branch names, file paths, comment ids.
- **State, not story.** "Pushed `d262881`, waiting for the bot" beats a paragraph about how it went.
- **Say what was not done.** Note what is unpushed, untested or not yet posted. A later session will assume the opposite. "Jest only, not checked in a browser" is worth a line.
- **Correct, do not append.** When something on the board turns out wrong, change it where it stands. Two contradicting lines cost more than one wrong one.

Do not narrate board updates to the user, and do not ask before making them. The board is routine bookkeeping.

## The Rules section

This is what makes the board worth keeping: rules are what a new session is most likely to get wrong.

- **Record every standing rule** when it is given, the moment it is given. Group by source: the user, then each other person or team, then project docs.
- **Keep the source and the date**: `- Max 40 h per week (Patrick, 2026-10-28).` A rule without a source cannot be weighed later.
- **Keep strong wording.** When someone is emphatic, quote them. "ikke MERGE!!!!" carries information that "avoid merging" loses.
- **Add the reason when it was given.** It tells you how to handle the edge case nobody listed.
- **One rule, one place.** When a rule changes, replace it and note the date. Do not leave the old version further down.
- **A one-off instruction is not a rule.** "Don't push this one yet" belongs in Now. "Never push without asking" belongs in Rules.

A permission covers what it was given for. Do not turn "yes, push this" into a standing rule.

## Keep it short

The board is a working surface, not an archive. Aim for under 300 lines and a Now section under 40 lines; `check` warns above that.

- **Now holds the present.** When an item is finished, move one line about it to the Log and delete the rest. Now is not a diary. Long sessions tend to pile entry on entry here, and this is the first thing to prune.
- **Newest first** in Now and Log, so the top of the section is always the current one.
- **Archive instead of growing.** When the Log gets long, move older entries to `.board/archive/YYYY-MM.md`. The archive is read only when needed.
- **Prune at the start of a session** when `check` warns, before the new work adds more.

## What stays off the board

- **Secrets and credentials**: tokens, passwords, keys, test logins, even from a ticket. Write where they live instead: "token in env `API_TOKEN`". The board is a plain file on disk, and a pasted key outlives the moment it was needed. `check` scans for the common forms.
- **Personal or customer data** that the work does not need.
- **What the code or git already records.** Point to it. The board holds what cannot be derived: state, decisions, reasons and rules.

## Keeping it private

- Never commit, push, upload, paste or attach the board, or any part of it. Lasse's wording: "du skal ikke commits!!".
- `init` adds `.board/` to `.git/info/exclude`, which works without changing any tracked file. Do not add it to `.gitignore`: that file is committed, so it would announce the board to everyone.
- Stage files by name near a board, not with broad commands, unless `check` has confirmed that it is ignored.
- Do not mention the board in commits, pull requests, comments, messages or reports to other people. It is not a source for them; cite the primary source instead.
- Subagents do not edit the board. Give them what they need in their brief and update the board yourself from their results.

## Before you stop

Whenever a session or a turn ends with work still open, make sure the top of Now says what comes first next time, specifically enough to act on without rereading the session: the exact step, the branch, and what it waits for. If the user decides to pause something, write the decision and the date, so the next session does not reopen the question.
