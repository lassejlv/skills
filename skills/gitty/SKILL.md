---
name: gitty
description: Use the gitty Rust CLI to inspect repository changes and generate repository-aware Git commit messages through Codex, Claude Code, or OpenCode. Use when an agent needs to preview staged or working-tree diffs, generate or refine Conventional Commit messages, select a provider or model, copy a message, configure gitty, create an authorized commit, or commit and push an authorized change.
---

# Gitty

Use `gitty` as the commit-message interface while keeping Git state changes within the user's authorization.

## Run the workflow

1. Confirm the working directory is the intended Git repository. Use `gitty -C <path> ...` when operating outside its root.
2. Run `gitty providers` if provider availability is unknown. Auto mode falls through installed Codex, Claude Code, and OpenCode providers when one fails; an explicit `--provider` does not fall back. If `gitty` is missing, tell the user and offer the installation command from [CLI reference](references/cli.md); do not silently install software.
3. Inspect the input with `gitty diff` before generation. Use `gitty diff --stat` for a compact view or `gitty diff --all` only when unstaged and untracked changes belong in scope.
4. Generate with `gitty gen`. Add constraints such as `--type`, `--scope`, `--hint`, `--style`, or `--provider` only when they reflect the repository or user request.
5. Return the generated message. Copy, commit, stage all changes, or push only when the user asked for that mutation.

## Preserve repository safety

- Treat plain `gitty gen` as read-only: it prints a message and does not modify the repository or remote.
- Prefer staged changes for an authorized commit. Run `gitty gen --commit` only after confirming the intended changes are staged.
- Use `--all` carefully because it includes and may stage staged, unstaged, and untracked changes. Inspect `gitty diff --all` first and exclude secrets, local configuration, generated artifacts, and unrelated user work.
- Use `--push` only when the user explicitly asked to push. It implies a commit and pushes the current branch to its configured upstream.
- Do not use `--commit`, `--all`, or `--push` merely because they are convenient. If authorization is ambiguous, generate the message and stop.
- Rely on default credential redaction and inspect the exact redacted provider payload with `gitty diff`. Use `--allow-secrets` only when the user explicitly authorizes sending the raw diff and understands which provider will receive it.
- Use `--dry-run` when the user wants to review the exact provider prompt. The prompt preserves the same default secret redaction.
- Never invent success. Verify the resulting commit with `git status --short` and `git log -1 --oneline`; verify a requested push from command output or the remote state.

## Choose inputs and output

- Let the default `auto` selection use staged changes when present and otherwise visible working-tree changes.
- Use `--changes staged` to force staged-only input.
- Use `--all` or `--changes all` for every visible change only after checking scope.
- Use `-i` for terminal-based selection, editing, regeneration, copy, commit, or push. Do not use interactive mode in a non-interactive shell.
- Use `--json` when another program will consume candidate messages and `-n 2` through `-n 5` when alternatives help. A non-interactive commit requires exactly one candidate.
- Use Conventional Commit `--type` and `--scope` only with `--style conventional`.

Read [CLI reference](references/cli.md) for installation, configuration, providers, flags, and common command recipes.
