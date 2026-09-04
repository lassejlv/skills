---
name: no-yak-shaving
description: Keep implementation, refactoring, and code review proportionate to the requested behavior. Use to avoid speculative abstractions, unrelated cleanup, and tests that mirror implementation while preserving necessary contracts and validation.
---

# No Yak Shaving

Deliver the smallest clear solution that fully meets the requirement. Minimize
unnecessary complexity, not functionality or evidence of correctness.

## Choose the scope

- Inspect the relevant call sites, contracts, and local conventions before editing.
- Separate work required for the requested outcome from adjacent improvements.
  Include a prerequisite only when the outcome depends on it.
- Reuse existing code when it fits. Prefer a direct function, explicit branch, or
  small data structure when no reusable mechanism is needed.
- Preserve unrelated changes. In a review, report actionable complexity with a
  concrete simplification; do not turn the review into an unsolicited rewrite.

## Make complexity justify itself

- Add a layer, dependency, option, or abstraction only for a current need, such as
  distinct callers, a real integration boundary, or clearer ownership. A second
  consumer is useful evidence, not a quota; small duplication can be clearer.
- Keep straightforward logic together unless splitting it improves navigation,
  ownership, or testing of meaningful behavior.
- Preserve compatibility when callers, persisted data, or rollout requirements
  depend on it. Verify obsolescence before removing old behavior.
- Validate untrusted inputs and handle failures that can occur. Omit defensive
  branches only when an enforced invariant makes the state unreachable.
- Optimize performance against a measured bottleneck or an explicit target.
  Avoid speculative tuning and general frameworks for imagined future variants.

## Validate the behavior

Use the narrowest checks that address the change's actual risk, including required
repository checks. Add or update tests for a public contract, a realistic
regression, consequential boundaries, or subtle branching and state transitions.

Do not add tests whose only evidence is that a private helper was called, a mock
returned its configured value, or the implementation matches a copied algorithm.
A simple assertion is still valuable when it protects a real contract, including
a consequential default value. Preserve valuable existing tests.

For a reversible, low-impact change, existing checks or direct inspection may be
enough. State what was verified and any material gap; do not claim tests ran when
they did not. Do not use simplicity as a reason to skip necessary integration or
user-visible verification.

## Stop at completion

Before finishing, remove anything introduced by this change that can disappear
without weakening the requirement, correctness, or clarity. Stop when the full
requested behavior works and relevant validation is complete. Report the result
and evidence briefly; mention a deferred improvement only if it matters to the user.
