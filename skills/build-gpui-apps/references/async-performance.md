# Async, lifecycle, and performance reference

Use this layer for loading, persistence, background computation, cancellation,
subscriptions, large collections, frame demand, and render-path performance.

## Contents

- [Keep the application thread responsive](#keep-the-application-thread-responsive)
- [Choose the executor](#choose-the-executor)
- [Own task lifetime](#own-task-lifetime)
- [Reject stale results](#reject-stale-results)
- [Own subscriptions](#own-subscriptions)
- [Keep render and paint cheap](#keep-render-and-paint-cheap)
- [Scale collections and assets](#scale-collections-and-assets)
- [Control frame demand](#control-frame-demand)
- [Measure before optimizing](#measure-before-optimizing)
- [Review checklist](#review-checklist)

## Keep the application thread responsive

The application thread owns entity mutation, window/input handling, render
orchestration, and frame delivery. Never block it with:

- filesystem reads/writes;
- network calls;
- process execution;
- sleeps;
- large JSON/database parsing;
- image decoding;
- expensive syntax/graph/layout computation;
- a mutex held across slow work;
- synchronous waiting for a background task.

Split work:

1. Snapshot the smallest owned input from app/entity state.
2. Run I/O or CPU work on an appropriate background executor/service.
3. Return owned data or a typed error.
4. Update a live entity on the application thread.
5. Notify and expose completion/error state.

Do not move GPUI `Entity` internals, `Window` references, or mutable app context
to a background thread. Use the framework's async context and weak handles.

## Choose the executor

At the current upstream snapshot:

- `cx.spawn`/`cx.spawn_in` orchestrate futures on GPUI's foreground/application
  executor and provide an async app/window context;
- `cx.background_spawn` or the background executor runs `Send` work away from
  the application thread;
- returned `Task<R>` represents lifetime and result.

Pinned signatures vary. Search the target for a nearby task of the same kind.

Use foreground orchestration for:

- awaiting an already asynchronous operation without blocking;
- updating entities/windows;
- sequencing UI states;
- timers that integrate with test executors;
- coordinating background results.

Use background work for:

- blocking library calls;
- CPU-heavy transforms;
- large parsing/decoding;
- filesystem/process work without an async adapter.

If a library is async but internally blocks, it still belongs off the
application thread.

## Own task lifetime

Current GPUI requires a returned task to be held or detached. Make the choice
semantic:

| Lifetime | Ownership |
|---|---|
| Search/query tied to current entity state | Store task; replacement/drop cancels |
| Save tied to a document/window | Store task and expose pending/error state |
| App service loop | App/service owns it; detach only if intended |
| Fire-and-forget telemetry | Detach only with bounded work and error handling |
| Test-controlled operation | Hold/await so the test observes completion |

Example shape:

```rust
struct SearchView {
    query: SharedString,
    generation: u64,
    task: Option<Task<()>>,
    state: SearchState,
}

fn search(&mut self, query: SharedString, cx: &mut Context<Self>) {
    self.generation += 1;
    let generation = self.generation;
    self.state = SearchState::Loading;
    cx.notify();

    self.task = Some(cx.spawn(async move |view, cx| {
        let result = fetch(query).await;
        view.update(cx, |view, cx| {
            if view.generation != generation {
                return;
            }
            view.state = SearchState::from_result(result);
            cx.notify();
        })?;
        anyhow::Ok(())
    }));
}
```

Adapt result types and APIs to the target. Do not hide a meaningful error with
`.ok()` merely to satisfy a detached future.

Dropping a view should cancel lifecycle-bound work without a callback trying to
resurrect it. Weak handles make that policy explicit.

## Reject stale results

Cancellation may be cooperative or unavailable. Use a generation/token when:

- query text changes quickly;
- a selected document changes;
- pagination overlaps;
- an old network response can finish after a new one;
- a save result belongs to a specific revision.

Increment generation before starting work. Compare it before applying any
result. For domain writes, use revision/optimistic concurrency at the
persistence boundary as well; a UI generation alone does not protect storage.

Keep separate:

- user-cancelled;
- superseded/stale;
- failed;
- empty;
- successful.

Avoid updating loading state to false from an old request while a newer request
is still running.

## Own subscriptions

`cx.observe` and `cx.subscribe` return `Subscription` values. Store them in the
owner whose lifetime defines the relationship.

Create subscriptions during construction/setup, not during every render.
Repeated render-time subscription creates duplicate callbacks and leaks
behavior until owners drop.

Use:

- observation for dependent entity change/invalidations;
- subscription for typed emitted events;
- global/application observations only when the relationship is truly global.

Detach a subscription only when GPUI's entity-lifetime behavior is exactly the
desired owner. Prefer explicit fields for relationships important enough to
review.

Callback work should stay small. If one model event causes heavy derived
computation, schedule/cancel that computation rather than blocking notification
delivery.

## Keep render and paint cheap

Render should:

- read already available state;
- derive bounded presentation values;
- build the element tree;
- attach handlers using stable captures.

Render should not:

- access disk/network/database;
- decode assets;
- sort/filter huge collections repeatedly;
- compile regexes or parse formats;
- start subscriptions/tasks on every pass;
- mutate domain state;
- allocate large cloned models for callbacks;
- create unstable IDs.

Move expensive derivation to:

- mutation time;
- a cached model field;
- background work;
- a virtualized row provider;
- a pure memo keyed by explicit revision.

Do not add caching until ownership and invalidation are clear. Stale caches are
correctness bugs with a performance justification attached.

Custom element prepaint/paint must also be bounded and deterministic. Cache
stable GPU/asset resources through project facilities rather than recreating
them per frame.

## Scale collections and assets

For collections:

- use `uniform_list` for many rows with genuinely uniform height;
- use `list` for virtualized collections needing the pinned API's flexibility;
- keep stable domain keys;
- store selection outside recycled rows;
- precompute search/sort results;
- batch model updates;
- avoid N tasks/subscriptions for N visible rows.

For assets:

- centralize asset identifiers and loading;
- decode/cache outside render;
- use correct logical dimensions;
- avoid loading multiple copies of identical images;
- define eviction for unbounded user content;
- verify failure/placeholder states;
- size raster assets for expected scale without decoding enormous originals
  into small thumbnails.

For text:

- avoid reshaping unbounded hidden content;
- clamp/virtualize long logs;
- use project text/editor primitives for editing rather than rebuilding a text
  system;
- profile font fallback and emoji-heavy paths when relevant.

## Control frame demand

Idle windows should become idle.

Request an animation frame only while:

- a finite animation remains active;
- a spring remains unsettled;
- direct manipulation is updating;
- a renderer/service has new visual content.

Stop requesting when:

- the value is within settled thresholds;
- reduced motion snaps the result;
- the entity/window is hidden or gone;
- the animation is cancelled;
- no presentation state changed.

Current GPUI test support can simulate frames and assert callback counts. Add a
test that an idle animation schedules zero further frames.

Avoid permanent polling for state that can notify. Avoid `cx.notify()` loops
that wake a clean window without new output.

## Measure before optimizing

Measure:

- input-to-feedback latency;
- frame duration and missed frames;
- app-thread blocking spans;
- render count for an isolated action;
- list row construction;
- allocations and retained entities;
- asset decode/upload time;
- startup and first-window time;
- task concurrency and stale completion.

Test release-like builds with production-like content. Debug mode, an empty
list, and a static background can hide real bottlenecks.

Optimize in this order:

1. Remove blocking app-thread work.
2. Stop unnecessary rerenders/frame loops.
3. Virtualize unbounded collections.
4. Remove repeated heavy derivation/allocation.
5. Cache with explicit invalidation.
6. Specialize paint/layout only after profiling.

## Review checklist

- [ ] No blocking I/O/CPU work on application thread
- [ ] Foreground/background executor matches the operation
- [ ] Every task is intentionally held or detached
- [ ] Weak entity used for lifecycle-bound long work
- [ ] Stale results rejected
- [ ] Errors and cancellation visible
- [ ] Subscriptions created once and owned
- [ ] Render/prepaint/paint bounded and deterministic
- [ ] Large collections virtualized
- [ ] Assets decoded/cached outside render
- [ ] Idle windows stop requesting frames
- [ ] Performance claims backed by production-like measurement
