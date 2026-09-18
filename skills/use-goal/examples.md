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

The agent creates `.use-goal/current.md` through the state helper. Its YAML frontmatter includes the goal ID, start/update times, status, agent/run metadata, revision, criteria, and evidence. The agent inspects both paths, implements the coherent rule, runs focused tests, fixes failures, and continues until every criterion has evidence. Useful project learnings are saved in `.use-goal/memory.md` with provenance and validity conditions.

**Agent final response**

```text
Goal complete: Correct checkout tax rounding
Delivered: charges and refunds now share the currency rounding path, with regression cases for half-cent boundaries.
Verified: focused checkout tests and the package typecheck pass.
State: saved as completed; /use-goal clear archives it and removes the current checkpoint.
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

The saved `next_action` is specific, such as `Add the negative refund case in tests/refunds.test.ts and run the checkout test target.` The helper increments the revision while preserving the goal ID and start time.

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

Before replacement, the agent saves current progress and useful memory. The old checkpoint is written to `.use-goal/history/<old-goal-id>.md`, preserving its `active` status, evidence, and unfinished next action. Its `archive_reason` is `replaced`. The new checkpoint has a fresh ID and links to the old one through `previous_goal_id`. Existing tax edits remain. Reading `/use-goal previous` reports the old goal; it does not resume it automatically.

## Clear without undoing work

**User**

```text
delete goal
```

**Agent**

```text
Goal cleared: Restore the production health endpoint
The checkpoint was archived. Local memory, history, and existing workspace changes remain.
```

After a successful archive write, only `.use-goal/current.md` is deleted. Source edits, commits, artifacts, memory, previous goals, and remote state remain. A failed archive write leaves the current checkpoint intact.

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

The user explicitly requested publishing a package, but registry access is unavailable.

After completing all safe local preparation and validation, the agent checkpoints:

```text
Goal blocked: Publish the patched package
Blocked on: the tested package is ready, but the registry rejected authentication.
Need from you: restore registry access through the approved environment.
```

A failing local test is not handled this way: the agent diagnoses and fixes it, or proves that an unrelated environment failure makes further validation impossible.

The agent does not ask for publication permission again. If the user had asked only to prepare a package, it would not invent publication as an additional acceptance criterion or blocker.

## Stale writer and interrupted replacement

Agent A reads goal revision 4. Agent B checkpoints revision 5. A's update with `--expected-revision 4` fails without modifying the file. A re-reads, reconciles the newer work, and checks who owns execution before continuing; it does not blindly change the number and retry its old payload.

If a process stops after archiving a goal but before writing its successor, `current.md` remains authoritative. `history` excludes that provisional snapshot while the goal is still current. A later retirement refreshes the archive from the current checkpoint before switching goals. The agent never guesses that the replacement or an external operation succeeded.

## Resume with memory

An earlier goal saved a `refund-tests` note with the test target, source goal ID, observed evidence, and the condition “while checkout owns the money code.” On resume, the agent sees that money logic moved to a new package. It verifies the new test target and updates that entry by ID with fresh provenance. It preserves unrelated notes and does not treat the old note as an instruction to restore the former layout.

## Context limit

The agent reaches a runtime limit with one criterion still unmet. It saves `status: active`, `stop_reason: context_limit`, current evidence, and an exact next action. It reports that the goal remains incomplete. It does not mark the goal completed or paused, and does not claim it scheduled another run.
