> Upstream: [crates/rune/README.md § Canvas handlers: live-only events and coordinate spaces](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#canvas-handlers-live-only-events-and-coordinate-spaces) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Canvas handlers: live-only events and coordinate spaces

Every event a handler hears re-runs the view, diffs and lays it out. A canvas camera lives in
[`Live`](high-frequency-values.md#high-frequency-values) values (`live_offset` and `live_scale` on the world), which
the frame draws without any of that, so a pan or pinch handler that only sets them can say so
with `tx.live_only()`:

```rust,ignore
.on_magnify(|s: &mut Canvas, e, tx| {
    s.zoom_about(e.x, e.y, 1.0 + e.delta); // sets s.cam_pan and s.cam_zoom, Live values
    tx.live_only();
    true
})
```

That event then skips the view, the diff and layout. The frame still draws the new live
values, hit tests against where they put elements, and reports `on_drawn_layout`; whatever
else the handler asked of its `Tx` (a scroll, a copy, `wake_after`) still happens. It works in
`on_wheel`, `on_magnify`, `on_rotate`, `on_smart_magnify`, `on_drag`, `on_pointer_move_local`,
`on_key`, `on_key_up`, a field's key handler, `on_physical_input`, the press and hover handlers,
`on_layout_tx` and `on_drawn_layout_tx`, so a toolbar that floats over the selection by its own live offset
follows a pan with no view re-run either. A handler that declines its event (returns false)
takes its `live_only` back, and an event several handlers take is live-only only if each says
so. It's the handler form of `Runtime::update_if` returning false, and the same rule holds:
change state the view reads and call `live_only`, and the screen stays stale until something
else commits. Debug builds look for that. A live-only event a quarter second or more after the
last commit re-runs the view anyway, and if the elements, layout, text or colours it builds
differ from what's on screen, Rune prints the handler. `rt.check_live_only(false)` turns the
check off for a test that counts commits; `rt.live_only_events()` counts the events that
skipped the view.

The debug check compares committed targets, not animated pixels or caret paint, and ignores
retained exits. It is a heuristic: a view that reads a clock or external state can differ
without a handler changing it; disable the check for such a view. Release builds compile it
out. Other model changes in the same frame still commit normally. Editing, paste and file-drop
actions always commit Rune's own changes, even if a callback calls `live_only`.

Virtual rows select their mounted window from the scroll offset and viewport height, not
from an independently transformed content stack. Transform the scroll viewport together
with its rows; use scrolling, rather than `live_offset` on the virtual stack alone, to move
which rows are visible.

On 2,000 cards (about 6,000 elements) at 2×, a 120-frame pinch with a toolbar following the
selection, on Apple silicon (`--profile perf`, `cargo run --profile perf -p rune --example
pinch_bench --features frame-profile`; thread CPU per frame, median of 7 runs):

| | view runs per frame | CPU per frame | allocations per frame |
| --- | --- | --- | --- |
| Handlers re-run the view | 1.0 | 13.7 ms | 42,124 |
| `tx.live_only()` | 0 | 2.0 ms | 78 |

Where each handler's points are measured from. *Local* is the element's own layout points: from
its top-left as drawn (after scrolling, `live_offset`, `live_scale` and `El::scale`), divided by
any scale it draws at, so they hold on a zoomed canvas. *Window* is points from the window's
top-left, which is what popups and context menus anchor to.

| Handler | Point it gives | Space |
| --- | --- | --- |
| `on_drag` | `Drag::x`, `y`; `start_x`, `start_y`, `w`, `h` captured at press | local |
| `on_drag` | `Drag::dx`, `dy` (travel since the press) | window |
| `on_wheel` | `WheelEvent::x`, `y` (`dx`, `dy` are the scroll in points) | local |
| `on_magnify`, `on_rotate` | `MagnifyEvent::x`, `y`, `RotateEvent::x`, `y` | local |
| `on_smart_magnify` | `x`, `y` | local |
| `on_pointer_move_local`, `on_secondary_press_local` | `PointerEvent::x`, `y` | local |
| | `PointerEvent::window_x`, `window_y`, `window()` | window |
| `on_pointer_move`, `on_secondary_press` | `PointerPress::x`, `y` | window |
| `on_layout`, `on_layout_tx` | `[x, y, w, h]`, as laid out, after scrolling (before live values) | window |
| `on_drawn_layout`, `on_drawn_layout_tx` | `[x, y, w, h]`, as drawn | window |
| `on_screen_layout` | `[x, y, w, h]` | primary display |
| `Cx::layout`, `layout_with`, `layout_size`, `memo::layout` (view reads) | `[x, y, w, h]`, as laid out, every scroll viewport at its origin, so a scroll doesn't re-run the view | window |
| `Cx::window_layout`, `window_layout_with`, `memo::window_layout` | `[x, y, w, h]`, as laid out, after scrolling | window |
| `context_menu`, `PopupAnchor::from(PointerPress)` | the anchor they take | window |

`on_press`, `on_double_press`, `on_hover`, `on_hover_change`, `on_drop_files` and
`on_drop_hover` give no point; a tooltip (`El::help`) anchors itself to the element as drawn.
`on_pointer_move` and `on_secondary_press` stay in window points, as apps written against
them expect.
