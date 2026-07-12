---
name: no-yak-shaving
description: Keep code changes simple, direct, and proportionate. Use when implementing, refactoring, or reviewing code to prevent overengineering, speculative abstractions, unnecessary compatibility layers, defensive code for impossible states, and tests that only restate the implementation instead of protecting meaningful behavior.
---

# No Yak Shaving

Ship the smallest clear solution that fully handles the real requirement.

## Work from reality

- Inspect the actual call sites, constraints, and existing conventions before designing.
- Solve the requested problem, not hypothetical future variants.
- Prefer boring, readable code over clever machinery.
- Reuse an existing abstraction only when it genuinely fits. Do not add one merely to make a small change look architectural.
- Keep the diff narrow. Do not bundle unrelated cleanup.

## Refuse ceremonial complexity

- Do not introduce factories, registries, adapters, generic frameworks, configuration switches, or dependency injection for a single concrete use case.
- Do not add fallback paths for states the system cannot reach.
- Do not preserve obsolete behavior unless compatibility is an explicit requirement.
- Do not split straightforward logic across extra files or layers without a concrete readability or ownership benefit.
- Do not optimize before evidence identifies a real bottleneck.

If a direct function, explicit branch, or small data structure solves the problem cleanly, use it.

## Make tests earn their keep

Add or change a test only when it protects meaningful behavior or a realistic regression.

Good tests cover at least one of:

- A user-visible outcome or public contract.
- A bug that could realistically return.
- Important boundary behavior, error handling, state transitions, or integration seams.
- Logic with enough branching or subtlety that inspection alone is insufficient.

Skip tests that only:

- Assert a constant, default value, type declaration, or language behavior.
- Mirror the implementation line by line.
- Test private helpers with no meaningful behavioral distinction.
- Mock every dependency and prove only that mocks return configured values.
- Inflate coverage without increasing confidence.
- Lock down incidental formatting or implementation details that may safely change.

Do not delete valuable existing tests merely because they are simple. When behavior changes, update the narrowest relevant test. When no new test adds meaningful confidence, say so plainly and validate with the most relevant existing checks.

## Complexity checkpoint

Before finishing, ask:

1. Does every new abstraction have at least two real consumers or a strong present-tense reason to exist?
2. Can any layer, option, branch, helper, or test disappear without weakening correctness or clarity?
3. Does the code read naturally to the next person without an architectural tour?
4. Did validation target the actual risk of the change?

Simplify when any answer exposes ceremony. Stop once the requirement is met, the code is clear, and the real risks are covered.
