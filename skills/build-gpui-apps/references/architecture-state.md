# Architecture and state reference

Use this layer to decide what owns state, how views communicate, when to notify,
and how tasks and subscriptions follow entity lifetime.

## Contents

- [Mental model](#mental-model)
- [Choose state ownership](#choose-state-ownership)
- [Use contexts deliberately](#use-contexts-deliberately)
- [Model actions and events](#model-actions-and-events)
- [Update and notify correctly](#update-and-notify-correctly)
- [Own tasks and subscriptions](#own-tasks-and-subscriptions)
- [Represent product states](#represent-product-states)
- [Set module boundaries](#set-module-boundaries)
- [Review smells](#review-smells)

## Mental model

GPUI combines retained application state with declaratively rebuilt element
trees:

- `App` owns application-wide facilities, entities, globals, executors, windows,
  and registrations.
- `Entity<T>` is a cloneable handle to application-owned mutable `T`.
- `Context<T>` mutates the currently owned entity and connects it to the app.
- `Render` rebuilds a view's element tree from current state.
- `RenderOnce` consumes a value-like component to produce an element.
- `Window` supplies window-local input, focus, layout, and frame facilities.
- `WeakEntity<T>` observes ownership without keeping an entity alive.

The element tree is not the state model. Render it from durable state and let
GPUI reconcile layout, paint, and interaction.

## Choose state ownership

Use the narrowest owner that preserves truth:

| State | Good owner |
|---|---|
| Hover/pressed state expressible by element styling | Element state |
| Open/closed, selection, draft text, scroll relationship | Owning view entity |
| Shared documents, sessions, workspaces, or caches | Model entity |
| Process-wide service or immutable configuration | App global/service |
| Derived text, enabled state, visibility | Compute from source state |
| Temporary async result | Owning entity plus generation/cancellation state |

Keep one writer or explicit command boundary for each value. Do not duplicate
“selected item” in a list row, parent view, and model unless synchronization is
formal and tested.

Create an `Entity<T>` when the value:

- changes independently;
- is observed by multiple owners;
- survives element rebuilds;
- owns tasks/subscriptions;
- emits domain events;
- needs focused GPUI tests.

Use `RenderOnce` when a component is configured by value, has no independent
lifetime, and delegates behavior through callbacks/actions. Avoid entities for
decorative wrappers.

## Use contexts deliberately

Current GPUI exposes related context types with different capabilities. Exact
methods vary by pinned version.

| Context | Typical work |
|---|---|
| `App` | globals, registration, entities, executors, windows |
| `Context<T>` | mutate `T`, notify, emit, spawn, observe, subscribe |
| `Window` | focus, input, window state, frame/layout interaction |
| `AsyncApp` | access app state from async application-thread work |
| `AsyncWindowContext` | async work that also needs a specific window |

Do not smuggle a mutable app/window reference into background work. Move owned
data across the boundary, compute, then update through the supported async
context.

Use the weak handle supplied by current `Context::spawn` in long-running work:

```rust
let task = cx.spawn(async move |view, cx| {
    let result = load_data().await;
    view.update(cx, |view, cx| {
        view.finish_loading(result);
        cx.notify();
    })?;
    anyhow::Ok(())
});
```

This is the current shape, not a guaranteed signature for every revision. Copy
a compiling local sibling and propagate errors according to project policy.

## Model actions and events

Use typed actions for user intent that participates in:

- keyboard bindings;
- menus and command palettes;
- reusable input routing;
- focus-scoped behavior;
- testable application commands.

Use key contexts to scope bindings. A generic `Enter` or `Escape` handler should
not fire everywhere because a descendant forgot to stop propagation.

Use emitted events for child-to-owner domain communication:

- selection changed;
- submitted;
- dismissed;
- requested deletion;
- navigation requested.

Prefer semantic intent over pointer mechanics. Emit `Submit`, not
`MouseWasReleasedAt(x, y)`.

Use direct callbacks when the relationship is local and value-like. Use actions
when behavior should be remappable or routed. Use events when an entity exposes
a stable outward contract.

Document propagation policy for nested shortcuts:

1. Which focus/key context receives the action?
2. When does the handler stop propagation?
3. What is the parent fallback?
4. What happens while a modal or menu is open?

## Update and notify correctly

Mutating state does not help if observers or rendering never learn about it.

- Call `cx.notify()` after a mutation changes this entity's rendered output.
- Emit a typed event when another owner must respond.
- Let observed entities trigger dependent updates through an owned observation.
- Avoid redundant notifications inside tight loops; batch related mutation.
- Do not notify after calculating an identical value unless downstream behavior
  relies on it and that contract is explicit.

Keep a transition centralized:

```rust
fn select(&mut self, id: ItemId, cx: &mut Context<Self>) {
    if self.selected == Some(id) {
        return;
    }

    self.selected = Some(id);
    cx.emit(SelectionChanged(id));
    cx.notify();
}
```

When a callback updates another entity, make the ownership path obvious. Deeply
nested `update` calls are a sign that domain operations may belong on a shared
model.

## Own tasks and subscriptions

Current GPUI lifecycle behavior is important:

- a returned `Task` must be held or detached;
- dropping a held task cancels its work;
- detaching deliberately lets it continue;
- a held `Subscription` is cancelled when dropped;
- detached subscriptions follow entity-lifetime semantics supported by GPUI.

Store lifecycle-bound work:

```rust
struct SearchView {
    query: SharedString,
    search_task: Option<Task<()>>,
    subscriptions: Vec<Subscription>,
}
```

Replace a held task to cancel stale work. For requests that cannot be cancelled
reliably, add a monotonically increasing generation and discard results from an
older generation.

Detach only for deliberate app-lifetime work such as telemetry flushing or a
background service. Observe failures; `.detach()` must not become shorthand for
“ignore the result.”

Use `cx.observe` for entity invalidation/dependency relationships and
`cx.subscribe` for typed emitted events. Hold the returned subscription in the
owner whose lifetime defines the relationship.

## Represent product states

Avoid parallel booleans such as `is_loading`, `has_error`, and `has_data` that
can create impossible combinations. Prefer an enum:

```rust
enum LoadState<T> {
    Idle,
    Loading { generation: u64 },
    Ready(T),
    Empty,
    Failed { message: SharedString, retryable: bool },
}
```

Represent interaction state explicitly when it changes behavior:

- disabled and why;
- pending operation and cancellation;
- selection;
- open overlay and focus return target;
- validation errors;
- drag phase and active pointer/touch;
- animation target and velocity.

Derive visuals from the state machine. Do not use an animation completion
callback as the only source of product truth.

Errors should be:

- actionable to the user when recovery is possible;
- recorded for developers with relevant context;
- preserved across rerenders;
- cleared by a defined event;
- testable.

## Set module boundaries

Organize by ownership, not by one file per type:

- domain model: operations, invariants, persistence boundary;
- view entity: orchestration, focus, actions, state mapping;
- components: reusable appearance and local interaction contract;
- theme: semantic roles, platform/material policy;
- platform bridge: availability checks and native ownership;
- pure modules: parsing, reducers, geometry, springs;
- tests close to the behavior plus integration coverage where needed.

Keep public constructors small. Prefer a builder only when optional
configuration is numerous and callers benefit. Validate invariants once rather
than sprinkling defensive checks through render code.

## Review smells

- Render-local variables pretend to be durable state.
- Multiple entities own unsynchronized copies of one domain value.
- A mutation changes output without `cx.notify()`.
- A task is created and immediately dropped.
- Every task is detached, including stale queries.
- Subscriptions are accumulated after every render.
- Pointer callbacks bypass typed actions and keyboard access.
- A child knows the entire parent implementation.
- App globals are used for screen-local state.
- Errors become `unwrap()` or disappear inside detached work.
- A model performs window/input work.
- A visual refactor silently changes domain ownership.

For async details, continue with [async-performance.md](async-performance.md).
For complete patterns, continue with [worked-patterns.md](worked-patterns.md).
