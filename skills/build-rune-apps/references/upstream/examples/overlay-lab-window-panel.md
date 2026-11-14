> Upstream: [examples/overlay-lab/window-panel.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/examples/overlay-lab/window-panel.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# Ordinary quick panels

## Cached launcher panels

Launcher-style apps can use a retained quick panel:

```rust,ignore
WindowSpec::from_app("quick", App::new(spec).keep_running())
    .configured_options(WindowOptions::launcher_panel())
    .on_focus(|_, focused, tx| { if !focused { tx.close_window(); } })
    .on_ready(|window| {
        // Hidden, with a completed cached frame. Register your shortcut here.
        assert!(window.is_ready());
    })
```

For a single-window app, use `App::configured_options(WindowOptions::launcher_panel())`.
Keep using accessory launch policy as described below. The preset is initially hidden,
borderless, transparent and non-resizable, with no inherited minimum size. AppSpec sets its
size. On macOS it prepares even with `App::windowless()`. `on_created` still means native
creation; `on_ready` means the first surface frame completed on the GPU, not merely submission.
Both callbacks run on the event thread. Readiness is per native lifetime, not a freshness
guarantee for later state updates. Headless rendering does not invoke native callbacks.

`WindowHandle::set_visible(true)`/`show()` and `AppHandle::show()`/`open()` reveal cached
pixels and take keys without app activation. A show before readiness waits behind the
first-frame fence; hide cancels that pending show. Hide leaves the panel ordered in at
alpha zero, ignores mouse input, and returns keys through AppKit. It retains the surface
even when `release_gpu_when_closed()` is set. Use `keep_running()` if closing should hide
rather than end this host. Ordinary non-launcher windows keep their existing show semantics.

The reveal itself does no settling, layout, surface configuration or drawable acquisition.
Queued state updates, focus handlers and later input can draw fresh frames normally.
Hidden updates, and `poll` changes after `AppHandle::wake()`, render at alpha zero: the first
after a quiet spell at once, later ones at most every 250 ms; hidden animations do not drive a
continuous loop. A shown launcher redraws on every wake. A show whose state changed since the
cached frame (an `update()` in the same turn, or one still waiting for that pace) first renders
one fenced hidden frame, so it never reveals stale pixels. That frame commits the new state
without settling it: content is fresh on reveal and the update's motion runs on from there.
First preparation retries unavailable drawables for at most two seconds, then reports through
`AppHandle::window_error()` and remains hidden; a later show retries preparation. A late
successful frame still completes readiness. Other platforms use an ordinary hidden
window; their `on_ready` fires after the first shown frame completes on the GPU.

The implementation ports the spike's retained reveal and uses a GPU fence for hidden preparation
(a never-shown alpha-zero layer need not emit a positive `presentedTime`). Existing spike
measurements (cached alpha 7.9/12.7 ms; native 6.2/15.8 ms) describe that experiment, not a new
benchmark of this API. `WINDOW_PANEL_LAUNCHER=1` selects the launcher in the native fixture;
its `visible`/`invisible` commands exercise WindowHandle directly.

## Ordinary panels and focus

`AppSpec`, `WindowSpec`, `WindowOptions` and `OverlaySpec` literals retain their fields.
Configure focus callbacks on `App::on_focus`, `WindowSpec::on_focus`, or
`ConfiguredOverlay::on_focus`. Each callback takes `fn(&mut S, bool, &mut Tx)`.
Repeated focus notifications are deduplicated per runtime. Callbacks run on the event
thread even when the window is hidden/occluded, before requiring a drawable.
`Tx::close_window()` dismisses a keep-running ordinary window or hides an overlay.

```rust,ignore
let quick = App::new(spec).windowless().on_focus(|_, focused, tx| {
    if !focused { tx.close_window(); }
});
let handle = quick.handle();
let window = WindowSpec::from_app("quick", quick).configured_options(
    WindowOptions { borderless: true, ..Default::default() }
        .macos(MacWindowOptions::default().nonactivating_panel(true))
);
// From a shortcut callback on any thread:
handle.place(DisplayTarget::UnderPointer, OverlayPlacement::Edge {
    edge: ScreenEdge::Top, margin: 160.0, align: Align::Center, inset: 0.0,
});
handle.open();
```

The macOS panel takes keys without activating its application. `show()` does not take
keys; `open()`/`focus()` do. Hiding lets AppKit return keys to the prior application.
For a single-window app use `App::macos_window(...)`. Use `App::accessory()` or
`run_windows_with(RunOptions { accessory: true }, ...)` to prevent launch activation too.
Panel policy is ignored on other platforms; poll, scenes, on_key and headless tooling
remain ordinary-window features.

Both AppHandle and WindowHandle have `place(display, placement)`. UnderPointer samples
at the calling thread, not after a delayed event-loop wake. Placement is retained across
recreation and re-resolved on open and scale changes; disconnected display IDs fall back
to primary. Rect and FullScreen resize as well as place; Edge uses the current window size.
Coordinates are display-local points, as for overlays. Wayland ignores placement requests.
`set_position` replaces a pending/retained display placement, and vice versa.

Headless runs resolve `AppHandle::place` against displays a `--script` object declares,
`{"displays":[{"id":1,"frame":[0,0,1512,982],"scale":2,"primary":true}],"pointer":[800,400],"events":[]}`
(frames and pointer in global points; ids match `DisplayTarget::Native`). Without them there is
one 1920x1080-pixel primary display, which `run_windows` factories also receive. Each
placement prints `rune-placed {"t":…,"display":1,"frame":[x,y,w,h]}` and the latest one
appears as `"placed"` in `--tree`. The headless viewport keeps its size.

Headless scripts accept `{"t": 0.1, "focus": false}` (time defaults to zero), delivering
the same app callback as native input. Existing root `El::on_window_focus` callbacks also
receive the queued focus event when Runtime next advances.

`cargo run -p rune --example window-panel --release` supplies two independent windows with
the same state type. `WINDOW_PANEL_SOCKET` enables the fixture's open/focus/hide/status/quit
commands. `native/run-window-panel-probe.py` holds the GUI test host's lock for a bounded Cua proof.
