---
name: clean-codebase
description: Research and implement a comprehensive, evidence-first code-quality cleanup with exactly eight specialized subagents. Use when a user asks to clean up, simplify, modernize, de-slop, or improve an entire repository across duplication, shared types, unused code, dependency cycles, weak typing, defensive error handling, legacy paths, and low-value generated-looking code. Each subagent produces a critical assessment and recommendations, then implements only high-confidence changes after central conflict resolution.
---

# Clean Codebase

Run a repository-wide cleanup with eight specialized subagents. Preserve behavior unless the user explicitly requests a product or API change. Prefer deletion and direct code over new abstraction, but do not force uniformity where concepts only look similar.

Read [references/workstreams.md](references/workstreams.md) before creating subagents. Use its lane briefs verbatim enough that every agent receives the evidence standards and output contract.

## Establish the Baseline

1. Read repository instructions, manifests, workspace configuration, and the current Git status.
2. Identify generated, vendored, migration, fixture, snapshot, FFI, and compatibility surfaces that require special handling.
3. Record the repository's existing validation commands and run the cheapest useful baseline checks. Distinguish pre-existing failures from regressions.
4. Preserve unrelated dirty work. Never reset, overwrite, stage, commit, or reformat changes outside this cleanup.
5. Treat the whole repository as in scope only when the user did. Respect any narrower path, package, language, or validation boundary.

## Create Exactly Eight Subagents

Create one named subagent for each numbered workstream:

1. duplication and DRY
2. shared type definitions
3. unused code and dependencies
4. circular dependencies
5. strong types
6. justified error handling
7. deprecated, legacy, and fallback paths
8. AI slop, stubs, and comments

Do not merge lanes, omit a lane, or let agents create further subagents. When concurrency is limited, launch agents in batches while retaining a roster of exactly eight.

Use two turns with each subagent:

- **Research turn:** Inspect read-only. Produce a critical assessment, evidence, confidence-ranked recommendations, likely file ownership, and validation needs. Do not edit.
- **Implementation turn:** After central review, give the same agent an explicit set of approved recommendations and exclusive files or hunks. Require it to re-read the current files, implement only the still-valid high-confidence items, run targeted checks, and report its diff and residual concerns.

An agent with no evidenced high-confidence change must return a reasoned no-op assessment. Do not invent work to make every lane produce a diff.

## Reconcile Before Editing

Collect all eight research reports before authorizing implementation.

1. Merge duplicate findings and reject recommendations based only on naming, aesthetics, tool output, or speculation.
2. Resolve contradictory proposals using runtime behavior, public contracts, tests, call sites, persisted data, and package ownership.
3. Assign exclusive file or hunk ownership. Never allow concurrent edits to the same file.
4. Order implementation waves:
   - remove verified unused, obsolete, fallback, stub, and commentary-only code;
   - simplify duplication, shared types, and dependency direction;
   - strengthen types and error handling against the resulting structure.
5. Run agents sequentially when findings overlap. Before each implementation turn, include relevant earlier changes and require the agent to reassess stale recommendations.
6. Keep the coordinator responsible for cross-lane integration, small conflict fixes, and final validation.

## Confidence Standard

Implement a recommendation only when all of these hold:

- concrete source locations and affected behavior are understood;
- references, dynamic loading, framework conventions, generated consumers, and external/public use have been checked where relevant;
- the intended replacement or deletion is clearer than the current code;
- validation exists or a proportionate smoke check can be performed;
- compatibility and migration risks are either absent or explicitly handled.

Leave medium- and low-confidence recommendations in the final assessment. Do not turn a broad cleanup into speculative architecture work.

## Tool Use

- Prefer repository-provided scripts and already-installed tools.
- Use Knip, Madge, compiler diagnostics, linters, dependency graphs, and language-native equivalents as evidence generators, not as authorities.
- Do not add a permanent dependency solely to run an audit tool. Use an ephemeral invocation only when available and permitted; otherwise reproduce the relevant check with local manifests, compiler output, and targeted searches.
- Read tool configuration and package/workspace entrypoints before trusting results.
- Confirm every automated finding by inspecting definitions, imports, exports, call sites, tests, scripts, configuration, and dynamic conventions as applicable.
- For third-party types, inspect the installed package source and declarations first. Consult current official documentation when local contracts are insufficient.

## Validation

After each implementation wave:

1. inspect the combined diff for accidental churn, lost dirty work, and cross-lane contradictions;
2. run format or format-check only on touched files unless the repository expects a broader command;
3. run the narrowest relevant tests, type checks, lint checks, cycle checks, and unused-code checks;
4. rerun the repository's meaningful full validation when proportionate;
5. compare failures with the recorded baseline;
6. run a runtime, integration, or build smoke check when static checks cannot prove the affected behavior.

Do not claim the cleanup is safe based only on a successful build.

## Final Report

Lead with the implemented result. Include:

- one concise critical assessment per workstream, including justified no-op lanes;
- high-confidence changes implemented and their behavioral impact;
- medium- or low-confidence recommendations left untouched and why;
- validation commands and outcomes, including pre-existing failures;
- files or public contracts that deserve manual review;
- any residual cycle, type-boundary, dynamic-reference, compatibility, or migration uncertainty.

Do not commit, push, open a pull request, or change external systems unless the user explicitly asks.
