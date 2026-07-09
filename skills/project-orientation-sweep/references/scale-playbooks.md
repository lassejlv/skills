# Scale Playbooks

Read this when the repo is medium or large, the ownership boundary is unclear, or the user asks for broad project exploration.

## Table of Contents

- [Scale Signals](#scale-signals)
- [Small Project Playbook](#small-project-playbook)
- [Medium Project Playbook](#medium-project-playbook)
- [Large Repo and Monorepo Playbook](#large-repo-and-monorepo-playbook)
- [Task Lanes](#task-lanes)
- [Subagent Lanes](#subagent-lanes)
- [Confidence Labels](#confidence-labels)

## Scale Signals

Treat scale as a working hypothesis, not a rigid classification.

- Small: one obvious manifest, under a few hundred relevant files, one app/library, simple test surface.
- Medium: several packages or services, mixed stacks, multiple manifests, but the user's task likely belongs to one surface.
- Large: monorepo workspaces, many packages/apps, generated code, many owners, multiple deploy targets, or no obvious task surface.
- Noisy: vendored dependencies, generated clients, build outputs, fixture dumps, or checked-in artifacts dominate file counts.

Use cheap facts first: manifest counts, top-level directory counts, lockfiles, workspace config, CI config, deployment config, and exact symptom searches.

## Small Project Playbook

Explore directly and avoid ceremony.

1. Read the main manifest and scripts.
2. Read the main entrypoint, config loader, route/app shell, and nearest tests.
3. Run or identify the narrow validation command.
4. Return a concise map, then make a narrow fix if requested.

Good small-project outputs include exact commands, the main data/control flow, and one or two risks. Avoid creating a research plan unless the repo is deceptive.

## Medium Project Playbook

Find the likely surface before reading deeply.

1. Inventory manifests, workspace files, top-level packages, and CI/deploy config.
2. Search exact task signals: error text, UI labels, route paths, exported symbols, table names, endpoint names, package names, or log strings.
3. Pick one or two likely surfaces and read entrypoints, local dependencies, and tests there.
4. Identify cross-cutting contracts: shared packages, generated clients, migrations, auth/session code, build config, and environment variables.
5. Validate with the nearest package/app check before broader checks.

If multiple surfaces remain plausible, present the fork explicitly with evidence and choose the most likely one if the user asked you to proceed.

## Large Repo and Monorepo Playbook

Do not try to understand everything. Build a map that is useful for the user's question.

1. Establish the repo boundary and workspace model:
   - Workspaces: `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`, `rush.json`, `bun.lock`, root `package.json`.
   - Rust: root `Cargo.toml` workspace members and crate graph.
   - Go: `go.work`, `go.mod`, `cmd/`, `internal/`, service directories.
   - Swift: `Package.swift`, Xcode projects/workspaces, app targets, package targets.
   - Python: `pyproject.toml`, `uv.lock`, `poetry.lock`, app package roots, service entrypoints.
2. Build a package/app inventory from manifests and top-level counts.
3. Identify deployable surfaces: apps, services, CLIs, workers, functions, mobile/desktop targets, infra modules.
4. Search from the user's symptom or goal into the inventory instead of reading package by package.
5. Read only the chosen lane deeply: entrypoints, local dependency edges, adjacent tests, configs, and generated-code boundaries.
6. Keep generated/vendor/client code out of the main reasoning unless it is the suspected source or sink.
7. Run targeted validation in the selected package/app. Escalate to whole-repo validation only after targeted checks pass or when the repo's normal workflow requires it.

Large-repo outputs should include a high-level map plus the chosen lane. Name omitted areas that were intentionally not explored.

## Task Lanes

Use these lanes to decide what evidence to gather.

- Architecture map: manifests, entrypoints, deployment targets, data stores, shared libraries, test strategy, and risky boundaries.
- Feature prep: owning app/package, extension points, existing similar feature, data model/API contract, tests, and validation command.
- Bug triage: exact error/UI/log search, failing path, source-to-sink trace, regression candidates, and the smallest reproduction or check.
- Performance: hot path, repeated work, IO/network/database calls, render/update loop, caching boundaries, and measurement command.
- Cleanup/refactor: current call graph, public API surface, tests that protect behavior, and compatibility risks.
- CI/build failure: failing job command, package manager, lockfile/toolchain versions, local reproduction, and smallest failing target.

For explicit security review, use the relevant security skill instead of turning this skill into an ad hoc security scan.

## Subagent Lanes

Use subagents only when the environment supports them and lanes are genuinely independent. Do not delegate final synthesis.

Good lanes:

- One agent maps deployable apps/services.
- One agent maps tests and validation commands.
- One agent traces a specific error string or route.
- One agent inspects one isolated package or language stack.

Bad lanes:

- Multiple agents reading the same files without distinct questions.
- Asking agents to "review the whole repo" with no boundary.
- Passing your intended answer or unverified theory as fact.

Ask for concise evidence: files read, commands run, confidence level, and open questions.

## Confidence Labels

Use explicit confidence when the repo is broad.

- Confirmed: directly supported by a manifest, code path, test, command output, or documentation in the repo.
- Likely: supported by naming and nearby code, but not fully traced.
- Unclear: plausible but not enough evidence; state the next command or file that would resolve it.

Do not hide uncertainty behind polished prose. A precise uncertainty is useful.
