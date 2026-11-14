> Upstream: [examples/overlay-lab/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/examples/overlay-lab/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# Overlay lab

## Native layer-filter proof

`layer-filter-overlay` draws two static exiting-chip samples in a prewarmed native panel.
Both use a 400×40 pt capsule, nested dissolve/blur, sigma 1.5 pt and opacity .65. The upper
row is unmasked; the lower row uses `clip_rounded(20)`. Run from the repo root:

```sh
cargo build -p overlay-lab --bin layer-filter-overlay -j 2
python3 examples/overlay-lab/native/run-filter-probe.py crates/rune/artifacts/layer-filters/native-overlay
```

Run it on a GUI test Mac, never on a developer's desk display. The runner holds the host's GUI lock, waits for visible alpha and positive Metal presentation,
then captures that exact window with Cua. It closes the app's stdin to quit, ends the Cua
session and removes its diagnostic dylib. Evidence includes `native-overlay.png`, the
presentation log and Cua's valid-frame/window metadata. This proves Rune's native rendering
of a blurred, rounded capsule; the separate headless regression covers fully off-wall sources.

## Interactive lab

`cargo run -p overlay-lab` opens a transparent pill on the display under the pointer.
Only its chips intercept clicks; the background and hover label pass through. iPhone/Paste
change its contents inside a fixed maximum canvas. Area/Window/Screen open one picker per
display. Drag selects an area; Escape closes all pickers on platforms with overlay keys.

Headless stills use the same views, selected as the ordinary `lab` host:

```
cargo run -p overlay-lab -- --scene pill --snap pill.png
cargo run -p overlay-lab -- --scene expanded --snap expanded.png
cargo run -p overlay-lab -- --scene picker --size 960x600 --snap picker.png
```

Set `OVERLAY_LAB_SECONDS=15` for a bounded desktop probe with panel-ID/capture-request
logging. `OVERLAY_LAB_PICKER=1` opens the picker immediately. Run desktop probes in a GUI test
Mac's logged-in session, at normal priority, not on a developer's desk display.
`OVERLAY_LAB_UNDERLAY=1` runs a separate normal-window process that logs clicks, for
cross-process pass-through/focus checks. `OVERLAY_LAB_INCLUDE_IN_CAPTURE=1` disables the
capture request while grounding input coordinates; omit it for the exclusion check.

Linux capture exclusion is unavailable. Wayland only observes pointer movement inside its
input region, and the compositor chooses an output for UnderPointer. It cannot follow the
global pointer. OnDemand permits click-to-focus on layer-shell v4; Windows/X11 do not offer
nonactivating key focus. Capture requests on macOS must be supplemented with an explicit
ScreenCaptureKit window-ID filter when the OS capture path ignores NSWindow sharingType.
Wayland keeps all three levels on the compositor's overlay layer; it has no higher layer and
does not guarantee ordering among peers. Native status/status+1 levels are macOS-specific.

## Integrating an app's overlays

- The lab prewarms hidden hosts and logs `on_created` with the actual macOS CGWindowID.
  `window_number()` is available after that callback and stays stable through hide/show.
  Host creation happens on the event loop, not synchronously in `App::overlay`.
- Use `set_input(OverlayInput::All)` for selection and `set_input(OverlayInput::None)` for
  pass-through ink/glow on the same host. Mode changes wait for an owned drag's release.
  `Regions` uses `.hit()` geometry; `Legacy` restores the spec's `interactive` behavior.
- `set_follow_pointer(bool)` enables/disables following independently of placement/input.
  An app can keep it disabled and supply its own `Rect` and `set_display` requests.
- `ConfiguredOverlay::poll(fn(&mut T, f64, &mut Tx) -> bool)` overrides the app's poll.
  Overlays with the same state type inherit `AppSpec::poll`; different state types use the
  builder. Return true when state changed, and use `Tx::wake_after` for the next deadline.
  Hidden deadlines poll without drawing, matching the window host.
- `ConfiguredOverlay::compositor(...)` takes the same `Compositor<T>` as `App::compositor`.
  Call `frame.draw_ui()` and then `frame.rt.elements()` to trace each rendered overlay frame,
  including alpha-zero/offscreen prewarm. Runtime-only hidden updates do not call it.
  `animating()` keeps visible frames running; false allows them to go idle.
- Standalone modifier transitions (for example, pressing/releasing Shift without another
  key) are not delivered; the desktop and Wayland overlay callbacks have TODOs for a
  shared modifier-only key event. Pressed keys
  still carry modifier state, and Escape works.
- `Display::native_id()` maps to `DisplayTarget::Native`: macOS CGDirectDisplayID, Windows
  full-width HMONITOR, X11 RandR CRTC, Wayland wl_output registry name. X11 output IDs can
  also be targeted with `NativeDisplayId::X11Output`. `native_bounds()` is global top-left
  (macOS/Wayland points, Windows/X11 pixels); `scale` converts local lengths.
- The pill uses `AboveOverlays` (macOS 27), above the picker's `AboveStatus` (26). Both use
  CanJoinAllSpaces, FullScreenAuxiliary and Stationary. Wayland ordering remains compositor-owned.
- Desktop hide retains the native window, GPU surface and renderer. With `prewarm`, macOS
  renders a frame into the panel's actual surface at alpha zero, then orders it out.
  An unchanged show orders it back in and restores input and alpha; stale hidden changes render
   before reveal, preserving elapsed motion from hidden commits (see below).
   Hidden hosts have no pointer observers or draw loop. Wayland recreates its
  layer after hide.
- macOS Regions mode samples native pointer position/buttons at up to 120 Hz while visible.
   Monitors wake the loop; native local downs establish ownership through delivery of Up.
   Input changes also wait for native ownership when `.hit()` has no Runtime press handler.
   A known queued Up stays protected until dispatch. If no native Up was queued, 100 ms of
   observed button-up clears ownership and forwards one recovered release to Runtime at the
   first observed release position. Every Left Up acknowledges native ownership, even in None.
   None/All and hidden modes stop the polling deadline. Unchanged hover does not draw.
- Release measurements on a shared M2 Max: 30 retained re-shows reached the alpha setter in
  **0.369 ms median / 0.776 ms p95**. This is **not a presentation timestamp**. Alpha-only
  reveal reuses a drawable; Metal does not timestamp its compositor reveal. Opt-in diagnostic
  redraws reached positive `presentedTime` at **49.728 ms median / 75.907 ms p95**.
  **Sub-16 ms visible presentation remains unproven.**
- Ten-second idle intervals measured **0.044% CPU / 104 interrupt wakes/s** for a visible
  Regions pill with the pointer elsewhere and about **0.002% CPU** hidden. Neither interval
  produced drawable callbacks. All/None stopped polling and also produced no drawable callbacks.

The idle path filters outside-canvas motion and skips unchanged hover redraws. Windows hooks
run on a separate message-loop thread; X11 observes XI2 raw motion instead of polling. The
shared Wayland socket wakes its private queue; legacy noninteractive HUDs bind no seat and
reuse their empty input region.

## Commit an entrance, then show

For a prewarmed macOS overlay, initialize the view in its entry pose A (for example, a
collapsed capsule), then commit target B. Request `show()` in that poll or a later turn:

```rust,ignore
fn poll(s: &mut Capsule, _now: f64, tx: &mut Tx) -> bool {
    // Keep the app's existing wake scheduling here (Tx::wake_after, for example).
    let Ok(Command::Enter) = s.events.try_recv() else { return false; };
    s.expanded = true;                  // B: normal motion, not tx.instant().
    s.overlay.as_ref().unwrap().show(); // Reveal the current pose on the way to B.
    true
}

let configured = OverlaySpec::new("capsule", canvas_size, view)
    .options(OverlayOptions { prewarm: true, ..Default::default() })
    .poll(poll);
// Initialize expanded=false, install the returned OverlayHandle in the state,
// and let startup prewarm finish before accepting Enter commands.
```

No early show or delay is needed. Hidden transitions keep their own render-clock time:
show 16 ms after the commit and the entrance is near its start; show 2 s later and it is
already at rest. Rune catches motion up when polling or preparing the reveal, without a
hidden draw loop. Time before a commit is never charged to that new transition.

The revealed frame contains current content, geometry and live values, including instant
and text-only changes. Only motion keeps its original timing. Initial prewarm and
ordinary/unretained overlays still settle their first frame. Updates after `show()` can
also animate normally.

You can kick the first hidden poll with a queued `update()` or schedule it with
`tx.wake_after(..)`. A queued update makes the prepared frame stale, but refreshing it now
preserves the entry's elapsed motion instead of settling it.

## Native measurement harness (macOS)

Ordinary windows can opt into the same native switches without changing exhaustive
`WindowOptions` literals:

```rust
WindowSpec::from_app("capsule", app).configured_options(
    WindowOptions { transparent: true, borderless: true, ..Default::default() }
        .macos(MacWindowOptions::default()
            .shadow(false).level(27)
            .collection_behavior(1 | 16 | 64 | 256)
            .exclude_from_capture(true))
)
```

The mask above is CanJoinAllSpaces | Stationary | IgnoresCycle | FullScreenAuxiliary.
These settings apply at each native creation; other platforms ignore them. They do not
change an ordinary window into a nonactivating panel. Runtime `set_always_on_top` overrides
the configured native level, including after recreation. `OVERLAY_LAB_UNDERLAY=1` plus
`OVERLAY_LAB_NATIVE_WINDOW=1` exercises native options; `OVERLAY_PROBE_NATIVE_OPTIONS=1`
logs native readbacks when the diagnostic library is loaded.

Use `configured_options` for native builders; `options(WindowOptions)` remains concrete so
existing `.options(Default::default())` calls keep compiling.

`native/` contains diagnostic tools, loaded only into the lab process. Build them, then
copy the products into a fresh temporary directory on the GUI test host:

```sh
cargo build --release -p overlay-lab -j 2
xcrun clang -dynamiclib -fobjc-arc -framework AppKit -framework QuartzCore -framework Metal \
  examples/overlay-lab/native/presentation-probe.m -o presentation-probe.dylib
xcrun swiftc -parse-as-library examples/overlay-lab/native/capture-probe.swift -o capture-probe
```

Put `overlay-lab`, `presentation-probe.dylib` and `capture-probe` in that directory. Hold
the host's GUI lock file (`fcntl.LOCK_EX`), then run
`python3 examples/overlay-lab/native/run-native-probe.py <directory>` at normal priority.

`OVERLAY_LAB_CONTROL` names a unique Unix socket and starts the pill prewarmed but hidden.
Newline-terminated `show`, `hide`, `status`, `none`, `all`, `regions`, and `quit` commands are accepted. The driver
records the request's `CACurrentMediaTime` immediately before `handle.show()` and the
drawable's actual `presentedTime`, not queue submission or callback arrival time. Zero
timestamps are reported separately, with a two-second deadline for a positive timestamp.
It checks WindowServer identity before 31 shows (initial plus 30 re-shows). Set
`OVERLAY_PROBE_RETAINED=1` for alpha-zero hosts; the old order-out baseline omits it.
The retained run fails before showing if the pill has no alpha-zero `nextDrawable`
acquisition before `on_created`. This catches regressions in the wgpu occlusion override.
`python3 native/prewarm_trace.py <presentation.log>` checks every created overlay in a saved
trace; keep `prewarm_trace.py` beside the runner when copying the harness to another host.
`OVERLAY_PROBE_REDRAW=1` adds diagnostic redraws until a positive timestamp. Report this
endpoint separately from the alpha-only reveal; it includes work absent in normal showing.
`results.json` and `presentation.log` are the evidence; the lab has a bounded shutdown timer.

`run-idle-probe.py` samples process CPU and interrupt wake counters over ten-second intervals,
without redraw assistance, and counts drawable callbacks. `--modes` measures All/None/Regions.
`run-pill-probe.py <installed-binary> <directory>` runs 30 `lab pill tap-then-screen`
cycles of an installed reference app using the same diagnostic library without redraw
assistance. It measures native already-visible `orderFrontRegardless` entry to positive
presentation, not the beginning of the app's request.
`run-input-probe.py` drives an independent underlay and twenty raw-motion enter/click/leave/click
cycles. Build `mouse-path.swift`, copy it to a stable path and ad-hoc sign once before the
user grants Accessibility. Do not replace the granted binary. Point
`OVERLAY_MOUSE_HELPER` at it; the runner's default path is machine-specific. Set
`RUNE_OVERLAY_TRACE_INPUT=1` to log regions, monitor callbacks, polls, and native input flips.

`run-cua-input-probe.py <directory> prepare` drives the same checks through CuaDriver.
It holds the GUI lock file, starts two disposable lab processes, captures `grounding.png`,
then waits up to two minutes on `cua-control.sock`. After inspecting that screenshot and
its backing scale, send JSON `{"run":true,"scale":2}` over the socket. It verifies twenty
enter/click/leave/click cycles, hide-mid-press recovery, and `hit-only` → None during an
owned press; `hit-only` and `chips` control commands switch the fixture. The final None
assertion checks underlay delivery because None stops polling. `cycles:0,hide_case:false`
runs only the handlerless case. Preserve `actions.jsonl`, `steps.jsonl`, and both process
logs.

The capture helper uses ScreenCaptureKit with and without the exact CGWindowID in
`excludingWindows`. It checks permission first and exits 77 if unavailable. The probe does not change TCC;
an app verifies its own CGWindowID exclusion filter with its Screen Recording permission.

For click-through checks, use an independent underlay process. A coordinate-only synthetic
click does not establish that native mouse-move observation ran first. Check actual pointer
movement and both directions across the region boundary, and verify underlay/overlay logs.
