# Use Goal Examples

These examples show lifecycle behavior. The agent still adapts acceptance criteria and validation to the actual project.

## Start and complete

**User**

```text
/use-goal Fix checkout tax rounding and prove the total is correct for refunds.
```

**Agent progress update**

```text
Goal started: Correct checkout tax rounding
Done when: charges and refunds use the same rounding rule, regression coverage passes, and the checkout validation is green.
Working now: trace the charge and refund calculation paths.
```

The agent creates `.use-goal/current.md`, inspects both paths, implements the coherent rule, runs focused tests, fixes failures, and continues until every criterion has evidence. It does not stop after the progress update or first edit.

**Agent final response**

```text
Goal complete: Correct checkout tax rounding
Delivered: charges and refunds now share the currency rounding path, with regression cases for half-cent boundaries.
Verified: focused checkout tests and the package typecheck pass.
State: saved as completed; use /use-goal clear to remove it.
```

## Pause and resume

**User**

```text
pause goal
```

**Agent**

```text
Goal paused: Correct checkout tax rounding
Checkpoint: shared rounding is implemented; refund boundary coverage and package validation remain.
Resume with: /use-goal resume
```

The saved `Next action` is specific, such as `Add the negative refund case in tests/refunds.test.ts and run the checkout test target.`

Later:

**User**

```text
/use-goal resume
```

The agent reads the state, checks the live repository for intervening changes, and responds:

```text
Goal resumed: Correct checkout tax rounding — 2/4 criteria complete.
Working now: add the remaining refund boundary case against the current calculation API.
```

It then continues execution in the same turn.

## Resume after external changes

The checkpoint names `src/tax.ts`, but another contributor refactored the logic into `src/money/tax.ts`.

The agent must not restore the old path or blindly replay a patch. It inspects version-control status and current call sites, updates the checkpoint to the new ownership boundary, preserves compatible external work, and continues against the live code.

## Replace an active goal

**User**

```text
/use-goal new Restore the production health endpoint before returning to tax work.
```

**Agent progress update**

```text
Goal started: Restore the production health endpoint
Replaced: Correct checkout tax rounding
Done when: the endpoint returns the required status and its deployment-facing check passes.
Working now: reproduce the failing health request and trace its route.
```

The old goal state is replaced. Existing tax edits remain unless the new request explicitly asks to revert them.

## Clear without undoing work

**User**

```text
delete goal
```

**Agent**

```text
Goal cleared: Restore the production health endpoint
Existing workspace changes were left intact.
```

Only `.use-goal/current.md` is deleted. Source edits, commits, artifacts, and remote state are untouched.

## Missing goal

**User**

```text
resume goal
```

**Agent**

```text
No saved goal exists in this workspace. What objective should I start?
```

The agent does not infer an old objective from repository changes or conversation fragments.

## Real blocker

The goal requires publishing a package, but publishing needs explicit approval and credentials.

After completing all safe local preparation and validation, the agent checkpoints:

```text
Goal blocked: Publish the patched package
Blocked on: the tested package is ready, but publishing is an external mutation requiring your approval and registry access.
Need from you: confirm that I should publish version 2.4.1 and provide registry access through the approved environment.
```

A failing local test is not handled this way: the agent diagnoses and fixes it, or proves that an unrelated environment failure makes further validation impossible.
