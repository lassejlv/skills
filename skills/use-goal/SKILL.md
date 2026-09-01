---
name: use-goal
description: Runs durable, completion-driven goal sessions with explicit acceptance criteria and checkpointed state. Use when the user invokes /use-goal, asks the agent to keep working until an objective is finished, or says resume goal, pause goal, new goal, goal status, clear goal, or delete goal.
---

# Use Goal

Treat a goal as a committed outcome, not a plan or a list of tasks. Persist its state, work autonomously through recoverable failures, and do not conclude while its definition of done remains unmet.

## Command contract

Recognize these slash-command forms and equivalent natural language:

| Command | Behavior |
| --- | --- |
| `/use-goal <objective>` | Create a goal when none exists. |
| `/use-goal` | Resume the current goal; if none exists, ask for the objective. |
| `/use-goal resume` | Load, reconcile, and continue the current goal now. |
| `/use-goal pause` | Reach a safe boundary, save an exact checkpoint, and stop. |
| `/use-goal status` | Report progress, evidence, blockers, and the next action without doing more work. |
| `/use-goal new <objective>` | Replace the saved goal and start the new one now. |
| `/use-goal clear` | Delete only the saved goal state. Do not undo completed work. |
| `/use-goal delete` | Alias for `clear`. |

Also accept phrases such as `resume goal`, `pause goal`, `new goal: ...`, `clear goal`, and `delete goal`.

Rules for ambiguous commands:

- A bare `/use-goal` resumes when state exists.
- Text that is not a lifecycle command is the objective when no goal exists.
- When a goal exists, do not replace it with a different objective unless the user says `new`, `replace`, `clear`, or `delete`.
- `new` without an objective requires one focused question.
- `resume` with no saved goal must say that no goal exists and ask for the objective. Never reconstruct one from guesses.

## Durable state

Use project guidance when it specifies a goal-state location. Otherwise store the current goal at:

```text
<workspace-root>/.use-goal/current.md
```

Keep this file local state:

- Do not edit `.gitignore` to hide it.
- Do not stage or commit it unless the user explicitly asks.
- Read it fresh before every resume or lifecycle operation.
- Delete only `current.md` for `clear` or `delete`; never recursively delete `.use-goal`.
- If `current.md` already contains unrelated or unrecognized data, do not overwrite it. Explain the collision and ask for a state location.
- If no writable workspace exists, keep the same structure in conversation state and warn that cross-session resume is unavailable.

Use this compact format:

```markdown
# Current Goal

## Objective
[One observable outcome.]

## Status
active

## Definition of done
- [ ] [Observable acceptance criterion.]
- [ ] [Required validation or delivered artifact.]

## Constraints
- [User constraints, safety boundaries, and explicit non-goals.]

## Progress
- [Completed work that matters to the definition of done.]

## Evidence
- [Command, test, inspection, or artifact and its result.]

## Next action
[One exact action from which another agent can continue.]

## Blocker
None.
```

Allowed statuses are `active`, `paused`, `blocked`, and `completed`.

The state is a checkpoint, not a transcript. Replace stale progress and next-action text instead of appending every command. Update it:

1. Immediately after creating or replacing a goal.
2. After a definition-of-done item is proven.
3. After a consequential decision changes the execution path.
4. Before pausing, reporting a blocker, or yielding because of a hard runtime or context limit.
5. Immediately before reporting completion.

## Start a goal

1. Read the user's full objective and applicable project instructions.
2. Inspect only enough of the current workspace to make the goal actionable.
3. Write one observable objective and a small definition of done. Infer criteria from the request and repository; do not expand the product scope.
4. Ask one focused question only when a missing answer would make execution unsafe or lead to materially different outcomes. Otherwise choose a reasonable reversible path and begin.
5. Save `current.md` before implementation.
6. Send the `Goal started` progress response, then continue working in the same turn.

A strong definition of done covers the requested outcome and the evidence needed to trust it. It does not contain vague criteria such as “code looks good,” “all edge cases,” or “production ready” unless the request defines them.

## Execution loop

While the goal is active:

1. Select the highest-value unmet criterion.
2. Inspect the relevant current state; do not trust stale assumptions.
3. Perform the next coherent unit of work.
4. Validate the behavior in the way it will actually be used.
5. Record proven progress and the exact next action.
6. Continue immediately to the next unmet criterion.

Keep going through ordinary friction:

- Diagnose and fix test, lint, build, or runtime failures caused by the work.
- Try a different evidence-based approach when the first approach fails.
- Use existing repository patterns and narrow validation before inventing new machinery.
- Treat a progress update as an update, not permission to stop.
- Do not stop after planning, after the first edit, after one passing test, or after reporting partial progress.
- Do not ask “should I continue?” while safe, in-scope work remains.
- Do not mark a criterion complete without evidence.

Do not simulate background work, waiting, or future continuation. Work with the tools and time available now.

## Resume safely

On `resume`:

1. Read `current.md`.
2. Re-read applicable project instructions.
3. Reconcile the checkpoint with the live workspace: inspect version-control status and the files or artifacts relevant to the next action.
4. Preserve compatible external work. If the workspace invalidates an assumption, update the checkpoint rather than blindly replaying old steps.
5. Recheck a prior result only when it may be stale or the resumed work depends on it.
6. Change `paused` or `blocked` to `active` when continuation is now possible.
7. Send the `Goal resumed` progress response, then execute the next action in the same turn.

If the saved status is `completed`, report the completion evidence. Do not redo the goal unless the user explicitly reopens or replaces it.

## Pause, replace, and clear

### Pause

Finish or revert any partial write that would leave the workspace malformed. Set the status to `paused`, record current evidence and one exact next action, then stop. Pausing does not undo work.

### New goal

An explicit `new` or `replace` command authorizes replacing `current.md`, even if the prior goal is active. State which goal was replaced, create the new checkpoint, and begin the new execution loop in the same turn. Do not undo prior workspace changes unless the new objective asks for that.

### Clear or delete

An explicit `clear` or `delete` command authorizes deletion of `current.md` only. It does not authorize reverting commits, edits, generated artifacts, remote operations, or user data. If no state exists, say so.

## Legitimate stop conditions

An active goal may stop only when one of these is true:

1. **Completed:** Every acceptance criterion is satisfied and supported by current evidence.
2. **Paused or replaced:** The user explicitly requested the lifecycle change.
3. **Blocked:** Progress requires unavailable credentials or access, explicit approval for a destructive or external action, or a product decision with materially different valid outcomes.
4. **Hard execution limit:** The runtime or context cannot continue. Leave the status `active`, save an exact checkpoint, and clearly say that the goal is not complete.

Before declaring a blocker, investigate reasonable alternatives. Ordinary uncertainty, a failed command, a missing optional tool, or a fixable test failure is not a blocker.

For a real blocker, record:

- The unmet criterion.
- What was attempted and observed.
- Why safe autonomous alternatives are exhausted.
- The single action or answer needed from the user.
- The exact next action after unblocking.

Never bypass security, consent, destructive-action, or publishing requirements in order to “keep going.”

## Completion gate

Before setting `completed`:

1. Re-read the objective and every definition-of-done item.
2. Inspect the final diff, artifacts, or live behavior relevant to the goal.
3. Run the narrowest sufficient validation, including negative or boundary behavior when it is part of the risk.
4. Separate failures introduced by the goal from pre-existing unrelated failures.
5. Check every criterion and add concise evidence.
6. Set the status to `completed` and set `Next action` to `Clear the saved goal when its record is no longer needed.`

Keep completed state until the user clears it or starts a new goal.

## Response protocol

Use these forms so the lifecycle is obvious:

```text
Goal started: <title>
Done when: <short criteria summary>
Working now: <next action>
```

```text
Goal started: <new title>
Replaced: <prior title>
Done when: <short criteria summary>
Working now: <next action>
```

```text
Goal resumed: <title> — <completed>/<total> criteria complete.
Working now: <next action>
```

```text
Goal status: <title> — <status>, <completed>/<total> criteria complete.
Evidence: <most relevant current evidence>
Next: <next action or unblock requirement>
```

```text
Goal paused: <title>
Checkpoint: <what is complete and what remains>
Resume with: /use-goal resume
```

```text
Goal blocked: <title>
Blocked on: <specific reason>
Need from you: <one action or answer>
```

```text
Goal complete: <title>
Delivered: <outcomes>
Verified: <evidence>
State: saved as completed; use /use-goal clear to remove it.
```

```text
Goal cleared: <title>
Existing workspace changes were left intact.
```

Starting and resuming responses are progress updates. Immediately continue with tool use and execution; do not return them as the final response while actionable work remains.

## Examples

Read [examples.md](examples.md) when command handling, interruption recovery, or blocker behavior is unclear.
