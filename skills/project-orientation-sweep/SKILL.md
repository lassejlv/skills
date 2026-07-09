---
name: project-orientation-sweep
description: Explore an unfamiliar or recently changed local project before implementation, from tiny repos to large monorepos. Use when Codex needs to map architecture, identify active surfaces, find relevant files for a bug or feature, assess repo health, performance, or errors, choose validation commands, or ground future work in the current checkout before editing.
---

# Project Orientation Sweep

Use this skill to build a repo-grounded map before changing code. Scale the sweep to the user's request and the repository size: quick and direct for small projects, lane-based and evidence-driven for large projects.

## First Moves

1. Establish boundaries:
   - Run `pwd`, `git rev-parse --show-toplevel`, `git status --short --branch`, and `git remote -v` when inside a git repo.
   - If the current directory is not a repo, identify nearby independent repos instead of assuming a monorepo.
   - Preserve unrelated dirty work.

2. Capture a cheap inventory:
   - Prefer `scripts/project_inventory.sh [path]` when available, then follow up with targeted reads.
   - Otherwise use `rg --files`, `git ls-files`, top-level manifests, and shallow directory counts.
   - Exclude generated or vendor-heavy directories such as `node_modules`, `target`, `dist`, `build`, `.next`, `.turbo`, `.venv`, and `vendor`.

3. Classify scale:
   - Small: one app/library, one main stack, a few obvious entrypoints.
   - Medium: several packages/services or mixed stacks, but one likely task surface.
   - Large: monorepo, many apps/packages, many manifests, generated code, or unclear ownership.
   - For medium or large projects, read `references/scale-playbooks.md` before deeper exploration.

4. Identify the stack:
   - Read manifests first: `Cargo.toml`, `Package.swift`, `Package.resolved`, `bun.lock`, `package.json`, `go.mod`, `pyproject.toml`, `requirements*.txt`, `Dockerfile`, `justfile`, `Makefile`, `railway.json`, `wrangler.toml`.
   - Prefer `rg --files` and targeted `rg` searches over broad filesystem walking.
   - For JS/TS projects, prefer Bun commands when the repo supports them. Respect the existing package manager when only npm, pnpm, or yarn lockfiles/scripts are present.

5. Map active surfaces:
   - Find entrypoints, route files, app shells, services, migrations, config loaders, scripts, and tests.
   - For user-visible bugs, search exact UI/log/error text first.
   - For performance work, identify the hot loop or refresh path before editing.
   - For native apps, separate host UI ownership from core/runtime libraries.
   - For broad requests, map ownership boundaries before reading implementation details.

6. Decide the output shape:
   - If the user asked only to understand the project, return a compact architecture map, main workflows, validation commands, and risks.
   - If the user asked to fix obvious issues, make only high-confidence, low-blast-radius fixes after the map is clear.
   - If the surface is broad, split research lanes or use subagents only when their scopes are disjoint or research-only.

7. Validate:
   - Run the narrowest meaningful checks for touched areas.
   - Rust: `cargo fmt --check`, `cargo check`, targeted `cargo test`, or repo `just` tasks.
   - SwiftPM/macOS: `swift build`, existing build/run scripts, and smoke checks where available.
   - Bun/TS: `bun run` scripts, typecheck/lint/build, and live HTTP smoke tests for web apps.
   - Go: `go test ./...` unless the repo has a narrower test target.
   - Shell/Python utility repos: `bash -n`, `python3 -m compileall`, and endpoint/file smoke tests.
   - Large repos: prefer the nearest package/app validation first. Run whole-repo checks only when they are known to be reasonable or the user asked for a broad pass.

## Exploration Depth

Use the lightest pass that can answer the user:

- Orientation only: map boundaries, stack, entrypoints, data flow, commands, risks.
- Feature prep: map the relevant surface, adjacent tests, extension points, and likely implementation files.
- Bug/performance investigation: start from symptoms, logs, UI text, traces, or failing checks, then trace source to sink.
- Broad audit: inventory first, split into lanes, sample representative modules, and label confidence.
- Fix request: orient enough to avoid accidental damage, then implement the narrowest credible change.

## Output

Lead with the concrete result:

- Map: repo boundary, scale classification, stack, important entrypoints, and current branch/dirty state.
- Active surfaces: files/directories that matter for the request and why.
- Findings: only evidenced issues or risks, ordered by impact and labeled when inferred.
- Changes: files touched, if any.
- Verified: commands and smoke tests run.
- Next: one or two genuinely useful follow-ups.

## Guardrails

- Do not invent architecture from filenames alone; label inferences when direct file evidence is missing.
- Do not read the whole repo when a manifest, route, test, or error string can identify the relevant surface.
- Do not turn an orientation request into a large refactor.
- Do not run expensive full-repo commands before identifying the stack and likely blast radius.
- Do not push unless the user asks.
- Do not delete or rename files unless the user explicitly requested that operation or the issue is unambiguously stale and validated.
