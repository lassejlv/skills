# Worked GPUI patterns

These examples show the current GPUI 0.2.2/upstream shape reviewed on
2026-08-13. They are deliberately small. Adapt imports, result types, theme,
component library, and signatures to the target's pinned source.

For one compile-checked composition of the patterns, inspect
`../assets/reference-app/src/main.rs`. Its lockfile pins the exact upstream
revision. It is intentionally not a reusable framework and does not implement
a toy custom editor in place of a production text component.

## Contents

- [Open one root window](#open-one-root-window)
- [Build a stateful entity](#build-a-stateful-entity)
- [Build a value-like component](#build-a-value-like-component)
- [Create an accessible control](#create-an-accessible-control)
- [Observe and subscribe](#observe-and-subscribe)
- [Own a cancellable async request](#own-a-cancellable-async-request)
- [Choose material tokens](#choose-material-tokens)
- [Drive a spring](#drive-a-spring)
- [Virtualize a large list](#virtualize-a-large-list)
- [Test with GPUI](#test-with-gpui)
- [Apply a Paper frame](#apply-a-paper-frame)
- [Use the compile-checked fixture](#use-the-compile-checked-fixture)

## Open one root window

Current upstream examples construct an application with
`gpui_platform::application()` and return an `Entity<V>` from the window
builder.

```rust
use gpui::{
    App, AppContext, Bounds, Context, Render, Window, WindowBounds,
    WindowOptions, div, prelude::*, px, size,
};

struct RootView;

impl Render for RootView {
    fn render(
        &mut self,
        _window: &mut Window,
        _cx: &mut Context<Self>,
    ) -> impl IntoElement {
        div().size_full().child("Hello, GPUI")
    }
}

fn main() {
    gpui_platform::application().run(|cx: &mut App| {
        cx.open_window(
            WindowOptions {
                focus: true,
                window_bounds: Some(WindowBounds::Windowed(
                    Bounds::centered(None, size(px(960.0), px(640.0)), cx),
                )),
                ..Default::default()
            },
            |_, cx| cx.new(|_| RootView),
        )
        .expect("open main window");
    });
}
```

Before using:

- inspect current `gpui_platform` feature requirements;
- register assets/fonts/globals/actions first;
- use target error/log policy instead of unconditional `expect` where startup
  recovery matters;
- preserve existing window/titlebar ownership.

## Build a stateful entity

Actions express intent and `cx.notify()` invalidates rendered output:

```rust
use gpui::{
    App, Context, Render, Window, actions, div, prelude::*,
};

actions!(counter, [Increment, Reset]);

struct CounterView {
    count: u64,
}

impl CounterView {
    fn increment(
        &mut self,
        _: &Increment,
        _window: &mut Window,
        cx: &mut Context<Self>,
    ) {
        self.count += 1;
        cx.notify();
    }

    fn reset(
        &mut self,
        _: &Reset,
        _window: &mut Window,
        cx: &mut Context<Self>,
    ) {
        if self.count != 0 {
            self.count = 0;
            cx.notify();
        }
    }
}

impl Render for CounterView {
    fn render(
        &mut self,
        _window: &mut Window,
        cx: &mut Context<Self>,
    ) -> impl IntoElement {
        div()
            .id("counter-root")
            .on_action(cx.listener(Self::increment))
            .on_action(cx.listener(Self::reset))
            .child(format!("Count: {}", self.count))
    }
}
```

Bind keys at the appropriate app/key context. A root-level `Increment` binding
is probably too broad; scope it to the focused counter or its owning screen.

## Build a value-like component

Use `RenderOnce` for a configured component without independent state:

```rust
use gpui::{App, RenderOnce, SharedString, Window, div, prelude::*, px};

#[derive(IntoElement)]
struct StatusBadge {
    label: SharedString,
    emphasized: bool,
}

impl StatusBadge {
    fn new(label: impl Into<SharedString>) -> Self {
        Self {
            label: label.into(),
            emphasized: false,
        }
    }

    fn emphasized(mut self, emphasized: bool) -> Self {
        self.emphasized = emphasized;
        self
    }
}

impl RenderOnce for StatusBadge {
    fn render(self, _window: &mut Window, _cx: &mut App) -> impl IntoElement {
        div()
            .px(px(8.0))
            .py(px(3.0))
            .rounded(px(6.0))
            .when(self.emphasized, |this| this.font_weight(gpui::FontWeight::SEMIBOLD))
            .child(self.label)
    }
}
```

Colors are omitted on purpose: pull semantic values from the target theme. Do
not encode product colors in every primitive.

## Create an accessible control

Current GPUI's public accessibility surface uses AccessKit roles and actions.
This fragment follows the current accessibility example:

```rust
div()
    .id(("project-row", project.id))
    .focusable()
    .tab_stop(true)
    .role(gpui::Role::Button)
    .aria_label(format!("Open {}", project.name))
    .cursor_pointer()
    .border_1()
    .border_color(theme.border_subtle)
    .focus_visible(|style| style.border_color(theme.focus_ring))
    .hover(|style| style.bg(theme.control_hover))
    .on_click(cx.listener(move |view, _, window, cx| {
        view.open_project(project.id, window, cx);
    }))
    .child(project.name.clone())
```

`on_click` exposes accessible Click in the current implementation, but still
verify:

- Button role and label;
- Tab stop/focus;
- keyboard activation in the pinned version/component;
- disabled gating;
- accessible state;
- unique ID.

For increment/decrement/expand/collapse, add explicit `on_a11y_action` handlers
with the correct `AccessibleAction` and update the same semantic operation.

## Observe and subscribe

Hold lifecycle-bound subscriptions:

```rust
struct InspectorView {
    document: Entity<Document>,
    subscriptions: Vec<Subscription>,
}

impl InspectorView {
    fn new(document: Entity<Document>, cx: &mut Context<Self>) -> Self {
        let changed = cx.observe(&document, |this, _, cx| {
            this.rebuild_derived_state();
            cx.notify();
        });

        let events = cx.subscribe(&document, |this, _, event, cx| {
            this.handle_document_event(event);
            cx.notify();
        });

        Self {
            document,
            subscriptions: vec![changed, events],
        }
    }
}
```

If the exact callback types differ, copy a nearby pinned example. Do not create
these subscriptions in `render`.

Use observation for “this entity changed.” Use a typed event when the semantic
fact matters to consumers.

## Own a cancellable async request

Current `Context::spawn` passes a `WeakEntity<T>` and `AsyncApp`. Store the task
so replacing/dropping it cancels lifecycle-bound work:

```rust
enum SearchState {
    Idle,
    Loading,
    Ready(Vec<ResultRow>),
    Failed(SharedString),
}

struct SearchView {
    generation: u64,
    task: Option<Task<()>>,
    state: SearchState,
}

fn begin_search(
    &mut self,
    query: SharedString,
    cx: &mut Context<Self>,
) {
    self.generation += 1;
    let generation = self.generation;
    self.state = SearchState::Loading;
    cx.notify();

    self.task = Some(cx.spawn(async move |this, cx| {
        let result = search_service(query).await;
        this.update(cx, |view, cx| {
            if view.generation != generation {
                return;
            }
            view.state = match result {
                Ok(rows) => SearchState::Ready(rows),
                Err(error) => SearchState::Failed(error.to_string().into()),
            };
            cx.notify();
        })
        .ok();
    }));
}
```

If `search_service` blocks or is CPU-heavy, schedule the owned operation on the
background executor first. Keep GPUI entity/window access on the application
thread.

The generation protects against operations that complete despite cancellation.
For persistent writes, use storage-level revision safety too.

## Choose material tokens

Keep the selection pure and testable:

```rust
#[derive(Clone, Copy)]
enum MaterialRole {
    Toolbar,
    Popover,
    FloatingControl,
}

#[derive(Clone, Copy)]
struct DisplayPreferences {
    dark: bool,
    active_window: bool,
    reduce_transparency: bool,
    increase_contrast: bool,
}

fn material_tokens(
    role: MaterialRole,
    preferences: DisplayPreferences,
    theme: &Theme,
) -> MaterialTokens {
    if preferences.reduce_transparency {
        return theme.opaque_material(role, preferences);
    }

    let mut tokens = theme.translucent_material(role, preferences.dark);
    if !preferences.active_window {
        tokens = tokens.inactive();
    }
    if preferences.increase_contrast {
        tokens = tokens.high_contrast();
    }
    tokens
}
```

Native glass selection should happen at the material-host/platform boundary,
not inside this color function. GPUI fallback code renders these tokens; the
native host renders real material using the same semantic role.

Unit-test every preference combination.

## Drive a spring

Copy [spring.rs](../assets/spring.rs) into the target and hold it as entity
state. This fragment shows orchestration, not an exact callback API:

```rust
fn tick_motion(
    &mut self,
    now: Instant,
    window: &mut Window,
    cx: &mut Context<Self>,
) {
    if cx.reduce_motion() {
        self.spring.snap_to(self.spring.target);
        self.last_frame = None;
        cx.notify();
        return;
    }

    let dt = self.last_frame.replace(now)
        .map_or(0.0, |last| (now - last).as_secs_f32());

    if self.spring.step(dt, self.spring_config) {
        window.request_animation_frame();
    } else {
        self.last_frame = None;
    }
    cx.notify();
}
```

Use the pinned project callback that invokes `tick_motion` on an animation
frame. Do not start an application-thread sleep loop.

On a new press:

```rust
self.dragging = true;
self.grab_offset = pointer_position - self.spring.value;
self.last_frame = None;
```

During drag, update directly. On release, set spring velocity from the gesture
estimate and retarget to a bounded semantic stop.

## Virtualize a large list

Current upstream's data-table example uses `uniform_list` with a processor that
receives the visible `Range<usize>`:

```rust
uniform_list(
    "items",
    self.rows.len(),
    cx.processor(|this, range: std::ops::Range<usize>, _, _| {
        range
            .filter_map(|index| {
                this.rows
                    .get(index)
                    .map(|row| Row::new(row.id, row.clone()))
            })
            .collect::<Vec<_>>()
    }),
)
.size_full()
.track_scroll(&self.scroll_handle)
```

Use stable row IDs inside `Row`. Do not use this for variable-height rows unless
the pinned API explicitly supports the chosen behavior. Keep selection in the
owning model/view, not recycled row-local state.

## Test with GPUI

Current upstream shape:

```rust
#[gpui::test]
fn selection_changes(cx: &mut gpui::TestAppContext) {
    let model = cx.new(|_| Model::default());

    model.update(cx, |model, cx| {
        model.select(ItemId(7));
        cx.notify();
    });

    assert_eq!(model.read(cx).selected, Some(ItemId(7)));
}
```

For a window:

```rust
#[gpui::test]
fn reduced_motion_schedules_no_more_frames(cx: &mut TestAppContext) {
    cx.update(|cx| cx.set_reduce_motion(true));
    let window = cx.open_window(size(px(320.0), px(200.0)), |_, _| MotionView::new());
    cx.run_until_parked();

    let callbacks = window
        .update(cx, |_, window, cx| window.simulate_next_frame(cx))
        .unwrap();

    assert_eq!(callbacks, 0);
}
```

This follows current upstream tests but exact window helpers differ across
versions. Search the target's `TestAppContext`.

## Apply a Paper frame

Suppose Paper shows:

- 280 px fixed navigation;
- flexible content;
- 12 px gap;
- 16 px outer padding;
- 44 px toolbar;
- 8 px radius;
- 1 px border;
- backdrop blur on a floating control group.

First geometry pass:

```rust
div()
    .size_full()
    .flex()
    .flex_row()
    .child(sidebar.w(px(280.0)).flex_none())
    .child(
        div()
            .flex_1()
            .min_w_0()
            .p(px(16.0))
            .gap(px(12.0))
            .flex()
            .flex_col()
            .child(toolbar.h(px(44.0)).flex_none())
            .child(content.flex_1().min_h_0()),
    )
```

Then:

1. verify the actual pinned methods such as `min_w_0`/`min_h_0`;
2. add exact fonts and paint;
3. select an honest material tier for the floating group;
4. add states/focus/actions;
5. capture at the Paper logical bounds;
6. replace repeated exact values with existing semantic tokens only after the
   screen matches.

Do not turn the backdrop blur into a full-window blur unless the design and
capability both call for it.

## Use the compile-checked fixture

The bundled fixture combines:

- `gpui_platform::application()` startup and window creation;
- typed actions, key contexts, menus, and multi-window close policy;
- an entity-owned event subscription and cancellable async generation;
- stable IDs, roles, labels, tab stops, and focus-visible styling;
- `uniform_list` virtualization;
- semantic opaque/high-contrast material fallback;
- reduced-motion-aware spring orchestration;
- pure and `#[gpui::test]` coverage.

Run:

```sh
scripts/validate_reference_app.sh
```

Copy the smallest relevant pattern only after comparing the target revision,
theme, component library, and platform policy. For full custom text input,
clipboard, drag/drop, menus, and restoration, read
[input-windows.md](input-windows.md); those OS contracts do not belong in a
minimal visual example.
