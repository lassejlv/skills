# Gitty CLI reference

## Install

```sh
cargo install --git https://github.com/lassejlv/gitty
```

Installation requires Rust and Cargo. Authentication and model configuration remain owned by the selected AI CLI.

## Inspect

```sh
gitty providers
gitty diff
gitty diff --stat
gitty diff --all
gitty diff --all --stat
gitty config show
```

`gitty diff` uses staged changes when they exist; otherwise it includes working-tree changes and readable untracked text files. `--all` includes staged, unstaged, and untracked changes.

Potential credentials are redacted by default before a diff reaches an AI provider. `gitty diff` displays the same redacted payload used for generation. `--allow-secrets` disables redaction for the current command and must only be used after explicit user authorization to send the raw diff.

## Generate

```sh
gitty gen
gitty gen --provider claude
gitty gen --provider opencode --model anthropic/claude-sonnet-4-5
gitty gen --type feat --scope cli
gitty gen --style detailed --hint "fixes the startup race"
gitty gen -n 3
gitty gen --interactive
gitty gen --json
gitty gen --copy
gitty gen --dry-run
gitty -C /path/to/repo gen
```

Provider auto-detection tries Codex, Claude Code, then OpenCode. If an installed provider fails or is unauthenticated, auto mode falls through to the next installed backend; choosing `--provider codex`, `claude`, or `opencode` disables fallback. Supported styles are `conventional`, `plain`, and `detailed`. Candidate counts range from 1 through 5.

## Mutate Git state

```sh
gitty gen --commit
gitty gen --all --commit
gitty gen --all --push
```

`--commit` commits staged changes. `--all --commit` stages every visible change after generation and commits it. `--push` implies commit and requires a branch with a configured upstream. These commands require user authorization and a post-command Git verification.

## Configure

```sh
gitty config init
gitty config init --global
gitty config show
```

Configuration loads in increasing precedence from `~/.config/gitty/config.toml`, `.gitty.toml`, environment variables, and CLI flags. Useful environment variables are `GITTY_PROVIDER` and `GITTY_MODEL`.

```toml
provider = "codex"
style = "conventional"
language = "English"
candidates = 1
max_diff_bytes = 120000
allowed_types = ["feat", "fix", "docs", "refactor", "test", "chore"]
allowed_scopes = ["cli", "config", "providers"]
```

Generate completions with `gitty completions bash`, `elvish`, `fish`, `powershell`, or `zsh`.
