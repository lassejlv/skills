# macOS Swift Host Reference

Source basis: `macos/` in Termy main at commit `4be935f5647c05f2ab53dd2ad723ab7bdec6d2d0`. Re-check current sources before editing.

Relevant source files:

- `macos/Package.swift`
- `macos/Sources/CTermy/CTermy.h`
- `macos/Sources/CTermy/module.modulemap`
- `macos/Sources/TermySwift/Support/TermyFfiBridge.swift`
- `macos/Sources/TermySwift/Services/LibTermyTerminal.swift`
- `macos/Sources/TermySwift/Services/TerminalViewModel.swift`
- `macos/Sources/TermySwift/Models/TerminalFrameStore.swift`
- `macos/Sources/TermySwift/Views/TerminalRenderPlan.swift`
- `macos/Sources/TermySwift/Views/TerminalGridView.swift`
- `macos/Sources/TermySwift/Services/DisplaySyncedRefreshDriver.swift`
- `macos/Sources/TermySwift/Services/NativeRenderMetrics.swift`

## Contents

- SwiftPM And Linking
- Swift FFI Wrapper Shape
- Wakeup Monitor
- Frame And Render Loop
- Rendering Architecture
- Cadence, Resize, And Occlusion
- Input And Safety
- Config And Appearance
- Display-Only And tmux
- Validation

## SwiftPM And Linking

Build `termy_ffi` before Swift:

```sh
cargo build -p termy_ffi
TERMY_FFI_LIBRARY_PATH="$PWD/target/debug" swift test --package-path macos
```

The package uses a `CTermy` system library target whose header includes `../../../crates/ffi/include/termy.h`. Link with `-ltermy_ffi` and an `-L` path from `TERMY_FFI_LIBRARY_PATH`, falling back to `target/debug` in development.

For app bundles, copy `libtermy_ffi.dylib` into `Contents/Frameworks`, set its install name to `@rpath/libtermy_ffi.dylib`, rewrite the app binary's linked path to `@rpath/libtermy_ffi.dylib`, and sign the dylib with the app. The existing DMG scripts show the exact bundle packaging flow.

## Swift FFI Wrapper Shape

Centralize all C calls behind a small Swift wrapper like `LibTermyTerminal`.

Use a tiny bridge layer for common operations:

- `requireOK(operation, status)` to throw on non-OK `TermyFfiStatus`.
- `string(from:)` to decode `TermyFfiBytes` while respecting byte length and nil pointers.

In the terminal wrapper:

1. Load default config unless explicitly disabled.
2. Read render config before terminal creation so cell metrics, colors, font, padding, cursor, scroll, and opacity match the config.
3. Create with `termy_terminal_new_with_options` for normal shells or `termy_display_terminal_new` for display-only terminals.
4. Store the terminal handle and config handle as private optionals.
5. In `deinit`, stop the wakeup monitor first, then free terminal, then free config.
6. If initialization throws after acquiring config but before object initialization completes, free config explicitly because `deinit` will not run.

Do not expose raw pointers outside the wrapper unless the caller owns the full FFI lifecycle.

## Wakeup Monitor

Use a dedicated background queue/thread blocked in `termy_terminal_wait_for_wakeup`. On wake, hop to `MainActor` and ask the view model to poll. Use a long timeout as a safety net; output and stop should wake immediately.

Stop sequence:

1. Mark the monitor as not running.
2. Call `termy_terminal_notify_wakeup(handle)`.
3. Wait for the monitor to exit.
4. Then allow `termy_terminal_free(handle)`.

Do not free while the wait thread is blocked.

## Frame And Render Loop

The production loop should:

1. Drain events with `termy_terminal_drain_events`.
2. Handle metadata events: title, reset title, bell, exit, progress, working directory, clipboard store, and shell lifecycle.
3. Call `termy_terminal_take_frame_update(handle, forceFull, &update)`.
4. Apply the update to a retained `TerminalFrameStore`.
5. Publish only lightweight state plus a render revision.
6. Update a retained `TerminalRenderPlanCache`.
7. Invalidate only dirty rects in an AppKit grid view.

Use `snapshot()` only for simple one-off full reads, diagnostics, or test helpers. A hot render loop should use `frameUpdate(forceFull:)`.

For partial updates, validate cell count against dirty spans. Full updates must have `cols * rows` cells. Partial updates must have the sum of each span width.

## Rendering Architecture

Use AppKit for the terminal grid hot path:

- `NSViewRepresentable` wraps a custom `NSView`.
- `TerminalGridNSView.update(...)` compares frame dimensions, display offset, render config, selection, search state, hovered link, focus, and damage.
- Full changes set `needsDisplay = true`.
- Partial changes call `setNeedsDisplay` for each dirty span rect.
- Drawing uses retained row render plans: background runs, text segments, block glyphs, and stroke glyphs.

Cache expensive drawing objects across frames:

- fonts keyed by family/size
- colors keyed by packed RGBA
- alpha colors
- shaped text lines keyed by text, color, and weight

Pixel-snap cell rects. Draw block and box glyphs as snapped geometry where appropriate so terminal UI characters tile cleanly.

Keep large render plans out of `@Published` state. Publish a revision counter, and let the view read the retained plan.

## Cadence, Resize, And Occlusion

Use display-synced polling only while active. When idle:

- Drop to blink cadence if the focused pane has cursor blink enabled.
- Drop to inert idle cadence if nothing needs animation.
- Let the FFI wake channel schedule immediate polling for new output.

Coalesce wakeup polls. While the display link is active, ignore plain wakeups because the display link already polls at frame cadence.

Resize handling:

- Send every size step to FFI so PTY winsize stays correct.
- Throttle forced full refreshes to about 60 Hz during continuous resize.
- Always schedule a trailing forced refresh after resize coalescing.

When a pane/window is occluded or suspended:

- Stop visual refresh polling.
- Keep draining PTY events on wake so child processes do not block on full PTY buffers.
- Lower scrollback for inactive tabs if config provides an inactive limit.
- Drop layer contents and shaped-line caches for hidden grids to reduce RSS.

## Input And Safety

Use libtermy input encoders:

- `termy_terminal_encode_key`
- `termy_terminal_encode_mouse`

Write returned bytes with `termy_terminal_write` and free the returned `TermyFfiBytes`.

For paste:

1. Query `termy_terminal_bracketed_paste_mode`.
2. If disabled, write raw UTF-8 bytes.
3. If enabled, strip embedded bracketed-paste start/end markers from the payload, then wrap with bracketed-paste delimiters before writing.

For links:

- Prefer `termy_terminal_hyperlink_at` for OSC 8 links.
- Fall back to host-side text detection only when no OSC 8 link exists.
- Validate URL schemes before calling `NSWorkspace.open`.

## Config And Appearance

Use `termy_config_render_config_for_appearance` so system light/dark appearance resolves the same theme values as the Rust side. On settings or appearance changes, reload render config, reload terminal colors with `termy_terminal_reload_default_config_colors`, and force a full refresh.

Use FFI config helpers for native settings, safety settings, tmux binary, UI font family, window size, working directory, tasks JSON, keybinds JSON, settings schema, and diagnostics. Free returned byte buffers.

## Display-Only And tmux

Use display-only terminals for tmux control-mode pane output:

- Construct with `termy_display_terminal_new`.
- Feed `%output` bytes through `termy_terminal_feed_output`.
- Render with the same frame update path as a PTY-backed terminal.
- Treat `write` as a no-op for display-only terminals unless routing input back through tmux control is implemented separately.

## Validation

Run targeted Swift tests for the layer touched:

```sh
cargo build -p termy_ffi
TERMY_FFI_LIBRARY_PATH="$PWD/target/debug" swift test --package-path macos
```

Useful focused filters:

- `DisplayTerminalTests`
- `TerminalFrameStoreTests`
- `TerminalRenderPlanCacheTests`
- `DisplaySyncedRefreshDriverTests`
- `NativeRenderMetricsGateTests`
- `TerminalKeyboardInputViewTests`
- `TerminalIMEInputTests`
- `TerminalLinkAllowlistTests`

Use `macos/scripts/check-config-matrix.sh`, `macos/scripts/stress-native.sh`, and `macos/scripts/check-release-readiness.sh` for app-wide changes.
