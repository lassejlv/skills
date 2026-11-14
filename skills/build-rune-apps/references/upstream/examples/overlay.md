> Upstream: [examples/overlay/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/examples/overlay/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# Display overlays

One normal control window and one transparent, borderless, always-on-top overlay
per display. The overlays pass clicks through by default. “Test overlay input”
enables hit-testing; clicking any overlay restores click-through on all of them.
This keeps the normal control window reachable. Each overlay draws a stroke and shares one
background-driven `Live<[f32; 2]>` remote cursor. Updates stop after four seconds.

```rust
rune::run_windows(|displays| {
    displays.iter().enumerate().map(|(i, display)| {
        rune::WindowSpec::new(format!("overlay-{i}"), app_spec())
            .options(rune::WindowOptions::overlay(display))
            .on_created(|window| {
                // CGWindowID on macOS; retain these for ScreenCaptureKit exclusions.
                let number = window.window_number();
                // window.set_click_through(false)?;
            })
    }).collect()
});
```

`WindowSpec::state(state)` supplies distinct initial state while sharing services
or Live handles. The factory runs once after monitor enumeration. Display origins
and `WindowOptions::position/physical_size` are physical pixels, including negative
origins; `AppSpec::size` and view layout use logical points.

Use `WindowSpec::from_app(key, App::new(spec).keep_running())` when a window must
retain its state after closing. The App's handle opens/activates/updates that window;
`WindowHandle::open` can also reopen a retained host. Default hosts are removed on
close, and the last host ends the loop. Any `AppHandle::quit` or `Tx::quit` quits the
whole loop. The outer tooling arguments apply to all specs; `App::args` is ignored
inside `run_windows`. `App::accessory` is a process launch option for `App::run`,
not a per-window option; `run_windows` starts with regular activation policy.
Use `run_windows_with_args(RunOptions { accessory: true }, [], factory)`
for a menu-bar app whose command-line flags belong to its host, not Rune.
An AppHandle's `set_dock_icon` still changes the whole process at runtime.

```sh
cargo build --release -p overlay
target/release/overlay --list-windows
target/release/overlay --window controls --snap controls.png
target/release/overlay --window overlay-0 --snap overlay.png --at 2
target/release/overlay --window overlay-0 --trace overlay.jsonl --frames 720 --fps 120
```

Headless tools select one window by its stable key and use one virtual display
(1920×1080 physical pixels, 2× scale by default). They create no native windows;
`on_created` does not run. `--size` and `--scale` override the selected capture.
Overlay PNGs retain transparency. A stroke is an SVG icon rasterized by Rune;
an interactive drawing editor is outside this example.

## Native boundaries

Windowed paths are compile-checked, not exercised on a desktop. Window-manager support
for transparency, topmost placement and click-through varies. Monitor placement
is a startup snapshot; hot-plug reconciliation is the app's next integration step.
The native window-number accessor supplies the macOS CGWindowID that a host app can
match to `SCWindow` for `SCContentFilter`; ScreenCaptureKit itself stays in the host app.
It can initially be `None` until AppKit registers the window; retain the handle
and query again. The native reference refreshes if a retained host is recreated.
Borrow raw-window-handles only through the handle's callback while the native
window is alive, on a platform-appropriate thread.

These are winit windows, not non-activating `NSPanel`s. Non-activating panels,
all-Spaces/fullscreen-space behavior and a status item still require Rune's own
Mac shell. This example does not implement them.

All windows share a GPU device. Unsupported transparency uses opaque rendering
with a diagnostic, and unsupported click-through reports the platform error.
Metal surfaces stay premultiplied for Core Animation; PNG exports are straight alpha.
