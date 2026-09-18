# State contract v1

## Storage and metadata

The helper needs Python 3.10+ on macOS/Linux and no third-party packages. Resolve `scripts/goal_state.py` relative to the installed skill, not the project. Always pass the absolute workspace root; pass `--state-dir` before the subcommand only when project guidance specifies a different directory.

Goal and memory files start with YAML frontmatter. The helper emits a deliberately small YAML subset: one key per line, with each value encoded as JSON. Strings, Unicode, and scientific notation are encoded to preserve their types and values in YAML 1.1/1.2 readers. The body is a generated view of that data. Do not hand-edit either half: use JSON input through the helper. It rejects duplicate keys, unknown versions, invalid records, or a body that disagrees with its metadata. A harness can use the helper's `read` output to avoid a YAML dependency.

The beginning of a goal record looks like this (remaining fields omitted here):

```yaml
---
schema_version: 1
kind: "goal"
id: "f8489b12-1ee7-459f-a18b-728d7839ae98"
previous_goal_id: null
title: "Fix refund rounding"
status: "active"
started: "2026-09-18T13:42:17.123456Z"
updated: "2026-09-18T13:46:02.123456Z"
finished: null
revision: 3
workspace: "/absolute/project"
agent: "codex"
run_id: null
stop_reason: null
criteria_done: 1
criteria_total: 2
---
```

All fields are required in stored records; defaults and derived fields come from the helper. Do not supply them in a start or checkpoint payload unless listed as editable below.

| Field | Type and meaning |
| --- | --- |
| `schema_version`, `kind` | Integer `1`; discriminator `goal` or `memory`. Unknown versions require migration, never blind rewriting. |
| `id` | Stable UUID for this goal, generated once. Resume preserves it. |
| `previous_goal_id` | UUID of the last retired goal, or `null`. A new goal after clear still links to the latest archive. |
| `started`, `updated`, `finished` | UTC ISO 8601 strings; started is immutable, updated changes on writes, finished exists only for completed goals. Migrated unknown start times are `null`. |
| `revision` | Positive integer, incremented on each checkpoint. Optimistic concurrency uses both goal ID and revision. |
| `workspace` | Absolute workspace root; rejects accidental reuse from another checkout. |
| `title`, `objective` | Nonempty strings. Editable. |
| `status` | `active`, `paused`, `blocked`, `completed`. Editable; only explicit user intent authorizes pause or replacement. |
| `agent`, `run_id` | Actual executor name and harness/session ID, or `null` if unknown. Editable; refresh on resume. They describe the last writer, not a lease or liveness signal. |
| `stop_reason` | String or `null`; e.g. `runtime_limit`, `context_limit`, `waiting_for_access`. Editable. Cleared on successful resume/completion. |
| `criteria` | Nonempty array of `{text: string, done: boolean, evidence: string[]}`. Editable. Each checked criterion requires evidence. |
| `criteria_done`, `criteria_total` | Derived integer counts for dashboards. |
| `constraints`, `progress` | String arrays. Editable. Progress summarizes durable results rather than the full transcript. |
| `next_action` | Nonempty, exact continuation instruction. Editable. Completed goals use “None; all acceptance criteria are verified.” |
| `blocker` | `null` or `{reason: string, attempts: string[], unblock_action: string}`. Editable; blocked goals require one. Name the unmet criterion in the reason. |
| `extensions` | Object for harness-specific values, e.g. observed native goal ID/status, external operation IDs, or resumed history source. Editable, shallow-replaced as a whole; preserve keys you did not change. Do not store secrets. |
| `archived`, `archive_reason` | `null` in current state. Archives have a UTC timestamp and `replaced` or `cleared`; the execution status is preserved. |

## Helper commands

All successful commands print JSON to stdout and exit 0. Missing read-only state returns `null` or `[]` without creating files. Errors print `{"error":"..."}` to stderr and exit nonzero (argument errors use argparse's stderr/exit 2). Inspect the error; never claim a write succeeded after failure. `--input -` reads JSON from stdin; file inputs avoid shell-escaping mistakes.

Resolve these example paths to actual paths before running them:

```sh
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project read
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project memory
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project history
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project previous
```

`history` returns newest archives first, excluding any provisional archive of the still-current goal. `previous` returns its first item, or `null`. Neither resumes work or rewrites state.

For `start`, supply only editable fields. Required in practice are `title`, `objective`, `criteria`, and `next_action`; the others have empty/null defaults and status defaults to `active`:

```json
{
  "title": "Fix refund rounding",
  "objective": "Charges and refunds follow the same currency rounding rule.",
  "agent": "codex",
  "run_id": null,
  "criteria": [
    {"text": "The shared rule handles negative half-cent refunds.", "done": false, "evidence": []},
    {"text": "The checkout package validation passes.", "done": false, "evidence": []}
  ],
  "constraints": ["Preserve unrelated checkout edits."],
  "next_action": "Inspect the charge and refund calculation call sites."
}
```

```sh
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project start --input /tmp/goal-start.json
```

Record the returned ID and revision. For `checkpoint`, supply only changed editable fields. Arrays and `extensions` replace their entire old values, so read them first and retain unrelated entries. Use this for normal progress, pause, resume, blocker, and completion:

```json
{
  "progress": ["Charges and refunds now call the shared currency function."],
  "criteria": [
    {"text": "The shared rule handles negative half-cent refunds.", "done": true, "evidence": ["Focused refund boundary test passed against the changed implementation."]},
    {"text": "The checkout package validation passes.", "done": false, "evidence": []}
  ],
  "next_action": "Run the checkout package validation target."
}
```

```sh
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project checkpoint --goal-id f8489b12-1ee7-459f-a18b-728d7839ae98 --expected-revision 1 --input /tmp/goal-update.json
```

The sample ID is illustrative: always use the ID and revision actually returned. Goal IDs prevent a late checkpoint for an old goal from corrupting its successor even when their revision numbers match. Completed goals reject further checkpoints. Resume a paused goal to active before doing more work. The helper checks structural evidence, while the agent remains responsible for checking that the evidence proves the user's criteria.

After an explicit user request to replace or clear, first save any outstanding progress/memory, then use the latest revision:

```sh
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project new --goal-id f8489b12-1ee7-459f-a18b-728d7839ae98 --expected-revision 2 --input /tmp/goal-new.json
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project clear --goal-id f8489b12-1ee7-459f-a18b-728d7839ae98 --expected-revision 2
```

These are alternative examples, not a sequence: after `new` the old ID is invalid for `clear`. `new` also works without ID/revision when there is no current goal. Repeated `clear` when no current state remains is a no-op. Neither command deletes memory/history or changes project files.

## Memory input

`memory.md` has `schema_version: 1`, `kind: "memory"`, its own `revision`, `workspace`, `updated`, and `entries`. Each entry has these fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable lowercase slug, at most 80 characters, used to merge updates without duplicating a note. |
| `kind` | `fact`, `decision`, `preference`, or `pitfall`. |
| `text` | Concise note, including rationale for decisions. |
| `source_goal_id` | Set by the helper from the current goal. |
| `evidence` | Nonempty array of concrete observations or user statements supporting the note. |
| `valid_when` | Scope/conditions under which the note still applies, to guide revalidation. |
| `recorded` | UTC time set by the helper when this entry is saved. |
| `verified` | Actual last verification time, or `null` if unknown. Never infer it from the file timestamp. |

Send an array containing only new or changed entries. The helper merges by ID, preserves unrelated entries, and sets provenance. Updating a matching entry replaces that entry; goal history retains earlier checkpoints, not a full memory audit log.

```json
[
  {
    "id": "checkout-validation",
    "kind": "fact",
    "text": "The checkout package owns refund boundary coverage.",
    "evidence": ["Inspected the package test target and ran its refund boundary cases."],
    "valid_when": "The checkout package still owns the money calculation code.",
    "verified": null
  }
]
```

```sh
python3 /installed/use-goal/scripts/goal_state.py --workspace /absolute/project remember --goal-id f8489b12-1ee7-459f-a18b-728d7839ae98 --expected-revision 0 --input /tmp/goal-memory.json
```

For `remember`, `--expected-revision` refers to the memory revision, using `0` only when `memory.md` is absent. The current goal ID is also checked. Save useful learnings before replacement/clear. Never write these notes to global assistant memory without separate explicit user authorization.

## Failure recovery and legacy migration

Writes use a short, nonblocking OS lock, a same-directory temporary file, fsync, and atomic rename. The OS releases the lock after a process crash; the remaining `.lock` file is not a stale-lock problem. Never delete a lock file to bypass another writer. Reads observe whole files; there is no transaction spanning a harness's separate reads of current state and memory. Re-read revisions when a consistent view matters. `updated` is a checkpoint timestamp, not a heartbeat.

Retirement writes an archive before replacing or unlinking current state. If interrupted between writes, current state remains authoritative. Its provisional archive is excluded from history listings and can be refreshed by the next retirement attempt. Once the goal is no longer current, the helper never changes its archive. A leftover `.tmp-*` file is not a checkpoint and must not be automatically promoted. If current disappeared during clear, history is the recovery record; do not resume it without user intent. Filesystem guarantees depend on the underlying filesystem; this is a local store, not a distributed coordinator.

For a recognized old `# Current Goal` document without frontmatter:

1. `status` may inspect the legacy file as-is; it must not migrate as a side effect. Before mutating/resuming, read the exact file and its SHA-256.
2. Map objective, status, criteria, constraints, progress, evidence, next action, and blocker into a normal goal input JSON. Preserve the status and all relevant context. Associate old evidence with the criteria it actually proves. If completed criteria lack evidence, establish that evidence or leave migration pending; never manufacture results to pass validation.
3. Run `migrate --expected-sha256 <observed-sha256> --input <mapped-json>` with the same workspace. The helper accepts only the original skill's known heading structure and checks the hash before writing.
4. The exact old file is saved to `history/legacy-<sha256>.md` before current state is replaced. A new ID/revision is generated; `started` is `null` because the original format did not track it. For a legacy completed goal, `finished` is the migration observation time and `extensions.timestamps_inferred` is `true`. `extensions.legacy_sha256` links the raw backup. Do not claim these are original execution times.

Malformed files, unknown versions, unrelated contents, or unsupported manual YAML formatting require reconciliation, not automatic deletion or reinitialization. Keep the originals and explain what needs resolution. If Python or filesystem guarantees are unavailable, report that durable state automation is unavailable and retain a conversation checkpoint; do not silently fall back to unsafe overwrites.
