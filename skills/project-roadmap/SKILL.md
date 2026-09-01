---
name: project-roadmap
description: Create or refresh a detailed, simple, and well-organized Markdown roadmap from the current project. Use when the user asks what to build next, where to start, how to prioritize a repository, for project ideas or direction, or for a ROADMAP.md grounded in the checkout's code, documentation, tests, history, constraints, and unfinished work.
---

# Project Roadmap

Create a roadmap from the project that exists now, not from a generic product checklist. Inspect the checkout, decide what matters, and write the result to a Markdown file.

## Deliverable

- Write `ROADMAP.md` at the repository root unless the user names another path.
- If that file already exists, read it first. Preserve still-valid decisions and human-authored commitments; revise stale or unsupported material rather than replacing it blindly.
- Do not modify implementation code unless the user separately asks for implementation.
- In the final response, state the file written, the recommended starting point, and the evidence used to validate the roadmap.

## Workflow

### 1. Establish the project boundary

1. Confirm the repository root and inspect `git status --short --branch`.
2. Preserve unrelated work and note when the checkout is dirty.
3. Inventory tracked files without descending into generated, dependency, build, or vendor directories.
4. Classify the project as a single app, library, service, multi-package repository, or monorepo.

### 2. Understand the current project

Read the smallest useful set of sources:

- `README*`, contribution guides, architecture notes, product specs, changelogs, and an existing roadmap.
- Manifests, workspace files, lockfiles, build configuration, deployment configuration, and environment examples.
- Main entrypoints, routes, public APIs, schemas, core modules, and representative tests.
- `TODO`, `FIXME`, `HACK`, skipped tests, placeholders, deprecated paths, and issue references.
- Recent git history when available, to identify active areas and direction.
- Existing validation scripts and CI workflows.

Determine:

- What the project does and who it serves.
- What is implemented, partial, missing, fragile, or undocumented.
- The current maturity: prototype, early product, growing product, or mature system.
- Important technical, product, operational, security, and usability constraints.
- Which opportunities are evidenced and which are informed recommendations.

Do not infer feature completeness from filenames alone. Read representative code and tests before making a claim.

### 3. Build a priority model

Evaluate candidate work using:

- **Impact:** user, product, reliability, security, maintainability, or operational value.
- **Urgency:** active breakage, blocked workflows, deadlines documented in the repo, or compounding risk.
- **Effort:** relative implementation and validation cost.
- **Confidence:** strength of repository evidence.
- **Dependency order:** foundations that must precede later work.

Prefer work that is high-impact, well-supported, and unblocks other work. Treat reliability and security issues as prerequisites when they threaten the usefulness of later features.

Do not present every possible improvement as a priority. Move speculative or low-confidence ideas to “Later” or “Open questions.”

### 4. Choose where to start

Select one concrete first milestone. Explain:

- Why it is the best starting point now.
- What evidence supports it.
- What it unlocks or de-risks.
- The first three actions.
- What “done” means in observable terms.

If evidence is insufficient to select one direction, make discovery the first milestone and list the exact questions or experiments needed. Do not invent product strategy.

### 5. Organize the roadmap

Use outcome-based phases, not arbitrary dates. Use calendar dates only when the repository or user provides real scheduling constraints.

For every phase include:

- **Outcome:** the capability or condition achieved.
- **Why now:** its value and ordering rationale.
- **Scope:** a short checklist of concrete work.
- **Dependencies:** earlier work or external decisions.
- **Exit criteria:** observable evidence that the phase is complete.

Keep phases sequential and understandable. Put optional ideas outside the committed path so readers can distinguish priorities from possibilities.

### 6. Write the Markdown file

Use this structure, adapting labels only when the project genuinely needs it:

```markdown
# Project Roadmap

## Project snapshot
[Purpose, users, maturity, current capabilities, and constraints.]

## Where to start
### [First milestone]
**Why this first:** [...]

**First actions**
1. [...]
2. [...]
3. [...]

**Done when**
- [...]

## Roadmap
### Phase 1 — [Outcome]
**Outcome:** [...]
**Why now:** [...]

**Scope**
- [ ] [...]

**Dependencies**
- [...]

**Exit criteria**
- [...]

### Phase 2 — [Outcome]
[Repeat as needed.]

## Good ideas
### Now
- **[Idea]:** [value, evidence, and rough effort.]

### Next
- **[Idea]:** [value, evidence, and rough effort.]

### Later
- **[Idea]:** [why it is promising and why it should wait.]

## Project guidelines
- [Project-specific product, architecture, quality, security, UX, or delivery rule.]

## Risks and dependencies
- **[Risk]:** [effect and mitigation.]

## Open questions
- [Decision that requires product, user, or technical evidence.]

## Evidence reviewed
- `[path or command]` — [what it established.]
```

The final document should be detailed enough to guide implementation but simple enough to scan. Prefer short paragraphs, checklists, explicit outcomes, and plain language. Use repository-relative paths in backticks.

## Quality Rules

- Separate observed facts from recommendations.
- Give each recommendation a reason tied to project evidence.
- Use rough effort labels such as small, medium, or large only when useful; do not fabricate time estimates.
- Make exit criteria testable through behavior, tests, metrics, documentation, or deployment evidence.
- Derive guidelines from the project's actual constraints and conventions. Avoid generic advice such as “write clean code.”
- Include product ideas only when they fit the project's apparent users and direction.
- Call out assumptions and unresolved product decisions.
- Keep the committed roadmap short enough to execute. A detailed roadmap is not a backlog dump.
- Do not claim a command passed unless it was run successfully.

## Validation

Before finishing:

1. Re-read `ROADMAP.md` as a new contributor.
2. Confirm the first milestone is singular, concrete, and justified.
3. Confirm each phase has an outcome and exit criteria.
4. Confirm “Now,” “Next,” and “Later” are clearly distinct.
5. Confirm important claims trace to files or commands in “Evidence reviewed.”
6. Confirm no existing commitments were silently discarded.
7. Check Markdown headings, lists, checkboxes, and local path references for clarity.
