# Workstream Briefs

Give every subagent the shared contract followed by its numbered lane brief.

## Shared Contract

Research the assigned lane across the user-scoped repository. Read actual implementations, consumers, tests, configuration, and package boundaries; do not rely on a search result or audit tool alone.

During the first turn, remain read-only and return:

1. **Assessment:** Critique the current design with concrete file and symbol evidence.
2. **Findings:** Rank each item as high, medium, or low confidence and explain the behavioral risk.
3. **Recommendations:** State the smallest sound change, expected benefit, affected files, and possible conflicts with other lanes.
4. **Validation:** Name the checks needed to prove each change.
5. **Ownership proposal:** List exact files or narrow hunks needed for high-confidence implementation.

During the implementation turn:

- re-read current files and discard findings invalidated by other agents;
- edit only the assigned files or hunks;
- implement all approved recommendations that remain high confidence;
- preserve public behavior and compatibility unless explicitly authorized otherwise;
- run targeted checks and inspect the diff;
- report changes, checks, remaining recommendations, and any unexpected overlap;
- do not stage, commit, push, or modify unrelated dirty work.

Do not create further subagents.

## 1. Duplication and DRY

Find repeated logic, data transformations, constants, protocol handling, validation, components, and near-copy implementations.

- Prove that candidates represent the same concept, have the same invariants, and should evolve together.
- Prefer consolidating behavior over merely sharing syntax.
- Avoid generic helpers, base classes, configuration machinery, or indirection that costs more than the duplication.
- Preserve intentionally separate domain behavior and platform-specific implementations.
- Check whether an existing abstraction can absorb the duplication before creating a new one.
- Measure success by reduced branching and maintenance surface, not line count alone.

## 2. Shared Type Definitions

Inventory type declarations, schemas, DTOs, enums, models, protocol shapes, generated types, and repeated anonymous object types.

- Consolidate only semantically identical types with shared ownership.
- Place shared types at the lowest stable dependency layer that owns the concept; avoid a global dumping-ground module.
- Keep transport, persistence, domain, and UI models separate when their contracts differ.
- Derive types from schemas or authoritative declarations where the stack supports it.
- Do not hand-edit generated types.
- Check that consolidation does not create cycles, broaden dependencies, or expose internal fields.

## 3. Unused Code and Dependencies

Use Knip or the repository's equivalent when suitable, then independently verify every candidate.

- Inspect package exports, binaries, scripts, tests, fixtures, configuration, plugins, reflection, dependency injection, code generation, lazy imports, string-based registration, and framework file conventions.
- Search all workspace packages and non-code consumers before deleting.
- Distinguish unused production code from intentionally public library API.
- Remove verified dead files, symbols, exports, dependencies, scripts, and configuration together with tests that only cover deleted behavior.
- Do not add Knip as a permanent dependency solely for the audit.
- Treat tool false positives and unresolved configuration as findings, not deletion authority.

## 4. Circular Dependencies

Use Madge, compiler/module diagnostics, or a language-native graph tool when suitable. Confirm reported cycles against the real resolver, aliases, conditions, and type-only edges.

- Distinguish runtime cycles from harmless or erased type-only relationships.
- Trace initialization order and concrete failure risk.
- Untangle cycles by restoring ownership and dependency direction: move a shared contract downward, inject behavior, split initialization from definition, or relocate orchestration upward.
- Do not hide a cycle with dynamic imports, service locators, duplicate types, or barrel-file shuffling.
- Check package-level as well as file-level cycles.
- Re-run graph checks and runtime initialization tests after changes.

## 5. Strong Types

Find unjustified `any`, broad objects, unchecked casts, placeholder generics, erased error types, stringly typed state, and language equivalents such as Python `Any`, Go `any`/`interface{}`, Swift `Any`, Rust `dyn Any`, or unstructured value containers.

- Research producers, consumers, tests, schemas, protocol documentation, and installed dependency declarations before choosing replacements.
- Model invariants with domain types, discriminated/tagged unions, enums, generics, validated schemas, or narrow interfaces.
- Remove casts by fixing the source type or adding runtime validation rather than asserting desired shapes.
- Preserve `unknown` or the language equivalent at genuinely untrusted boundaries until validation narrows it. Replacing boundary uncertainty with a confident but unchecked type is a regression.
- Preserve necessary type erasure at FFI, serialization, reflection, or heterogeneous container boundaries, but isolate and document it concisely.
- Run strict compiler/type checks and relevant runtime validation tests.

## 6. Justified Error Handling

Inventory `try`/`catch`, broad rescue/recover blocks, ignored results, silent defaults, catch-and-log flows, retry wrappers, and equivalent defensive patterns.

- Keep handling that validates or translates untrusted input, adds meaningful domain context, performs required cleanup, implements an explicit recovery policy, or presents an actionable boundary error.
- Remove catches that only hide failure, return unrelated defaults, duplicate logging, swallow cancellation, or immediately rethrow without useful context.
- Prefer direct propagation and typed/result-based errors where the language supports them.
- Keep cleanup safe with `finally`, defer/RAII, or structured resource management.
- Preserve deliberate resilience at process, job, request, plugin, or user-input boundaries; make the policy explicit and observable.
- Test failure paths, cancellation, cleanup, and user-visible errors rather than only the happy path.

## 7. Deprecated, Legacy, and Fallback Paths

Find deprecated APIs, compatibility branches, old feature flags, migrations, aliases, dual implementations, stale environment handling, fallback providers, and version-gated paths.

- Identify the original contract and prove the old path is no longer reachable or required.
- Check persisted data, deployed version skew, public API consumers, rollback expectations, migrations, serialization formats, feature flags, and supported platform versions.
- Remove the obsolete implementation and its tests, configuration, flags, adapters, dependencies, and comments as one coherent change.
- Prefer a single explicit path over silent fallback.
- Do not remove historical migrations, wire-format compatibility, or public deprecations without evidence that the compatibility window is closed.
- Treat “legacy” names and old-looking code as clues, not proof.

## 8. AI Slop, Stubs, and Comments

Find placeholder implementations, fake data, no-op wrappers, speculative abstractions, duplicated adapters, excessive delegation, tutorial narration, stale refactor notes, and comments that describe past or in-motion work instead of current constraints.

- Judge code by behavior and maintenance value, not by whether it looks machine-generated.
- Remove verified stubs, unreachable placeholders, redundant wrappers, needless pass-through layers, and comments that restate the code.
- Replace fake success, silent no-op, or “temporary” production behavior with the real implementation only when the intended contract is evidenced; otherwise surface it as an unresolved risk.
- Keep concise comments that explain non-obvious invariants, safety constraints, protocol quirks, performance reasons, or why a simpler-looking alternative is wrong.
- Replace stale transition commentary with present-tense explanations only when a comment remains necessary.
- Avoid broad rewriting, voice policing, or cosmetic churn.
