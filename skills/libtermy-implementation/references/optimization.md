# libtermy Optimization Reference

Use this when performance, responsiveness, memory, or rendering correctness is part of the task.

## Contents

- Fast Path
- FFI Marshaling
- AppKit Rendering
- Cadence And Wakeups
- Resize
- Memory
- Instrumentation And Gates
- Review Checklist
- Implementation Bias

## Fast Path

The desired frame path is:

1. Drain events.
2. Take `frame_update(false)`.
3. Patch a retained frame store.
4. Rebuild only dirty row render plans.
5. Invalidate only dirty rects.
6. Present only when damage, metadata, or cursor blink requires it.

Force full updates only for initial seeding, startup refresh windows, dimension changes, render-config changes, display-offset/history metadata that invalidates the viewport, or explicit full refresh operations.

Do not call full snapshot APIs on every tick, keystroke, scroll event, or wakeup. That serializes the grid across FFI and defeats dirty rendering.

## FFI Marshaling

Reduce crossing cost:

- Use `termy_terminal_take_frame_update`, not `termy_terminal_snapshot`, in hot loops.
- Keep `TermyFfiCell` compact and position-free.
- For partial updates, send only dirty-span cells.
- Decode FFI arrays once into host frame/update types.
- Free FFI buffers immediately after copying.
- Keep search, input encoding, link lookup, config parsing, and terminal mode handling in Rust.

Avoid adding ABI calls that return large JSON or full grids for hot-path work. If a feature needs repeated render-time data, add a typed, damage-aware surface.

## AppKit Rendering

Use a retained row renderer:

- Convert cells into row render plans: background runs, text segments, block glyphs, stroke glyphs.
- Rebuild rows only when damage covers those rows.
- Reuse unchanged row plans.
- Keep the plan out of SwiftUI diffing and `@Published`.
- Publish a revision counter for redraw coordination.

Cache:

- `NSFont` objects by font key.
- `NSColor` by packed color and alpha.
- shaped `CTLine` or equivalent text layout by text/color/weight key.

Invalidate:

- Full redraw when dimensions, render config, display offset, selection, search state, hovered link, or focus semantics require it.
- Dirty span rects for partial terminal damage.
- Cursor cell only for blink toggles.

Clear backing stores and shaped-line caches when windows are occluded or geometry changes.

## Cadence And Wakeups

Use display link while active, not timers. Gate over-rate display-link callbacks before they hop to the main queue.

When idle:

- Use blink cadence only when a focused cursor is blinking.
- Use inert idle cadence otherwise.
- Wake from libtermy's wake channel when output arrives.

Coalesce wakeups. Do not schedule one main-thread poll per PTY chunk while the display link is already active.

For suspended or occluded panes, keep draining events to prevent child process backpressure, but skip rendering.

## Resize

Resize is two costs:

- Cheap: update FFI/PTY size every step to keep child programs correct.
- Expensive: force full frame update, rebuild plan, redraw.

Run the cheap path every step. Coalesce the expensive forced refresh to frame cadence and ensure a trailing refresh after a drag finishes.

## Memory

Respect core clamps, but still manage host memory:

- Apply active and inactive scrollback limits through `termy_terminal_set_scrollback_history`.
- Shrink inactive tabs if the config has an inactive limit.
- Avoid retaining old full frames, plans, search results, or line caches after they become stale.
- Drop hidden grid layer contents and line caches.
- Keep debug metrics disabled unless the overlay is visible.

When changing scrollback, preserve cursor defaults and verify shrinking actually releases history rows. Core has logic for this; avoid host-side hacks.

## Instrumentation And Gates

Use metrics that prove the partial path holds:

- frame updates
- full vs partial frame updates
- presented frames
- skipped presents
- full vs partial render-plan rebuilds
- patched cells
- rebuilt rows
- render-plan build p50/p95/p99
- CPU and RSS in launch or workload gates

Relevant commands:

```sh
cargo test -p termy_core
cargo test -p termy_ffi
cargo build -p termy_ffi
TERMY_FFI_LIBRARY_PATH="$PWD/target/debug" swift test --package-path macos --filter NativeRenderMetricsGateTests
macos/scripts/check-performance-gates.sh --native-render-metrics
macos/scripts/check-render-perf.sh
macos/scripts/check-launch-gate.sh --app /path/to/Termy.app
cargo run -p xtask -- benchmark-compare --baseline-root /path/to/baseline --candidate-root "$PWD" --output target/macos-performance-gate --duration-secs 5
cargo run -p xtask -- benchmark-gate --summary target/macos-performance-gate/summary.json
```

Use `check-render-perf.sh` for gross native render regressions. It expects the benchmark to stay mostly partial and checks render-plan p95 against a ceiling.

## Review Checklist

Flag these as performance regressions:

- A render loop uses `snapshot()` instead of frame updates.
- Input, wakeup, or scroll forces full refresh by default.
- SwiftUI `Canvas` or large `@Published` arrays return to the hot path.
- Dirty spans are collapsed to full redraw without a clear reason.
- Host code guesses cell metrics instead of using render config.
- FFI buffers are leaked or freed through the wrong owner.
- A wakeup thread can outlive the terminal handle.
- A hidden tab keeps presenting frames.
- Search or link detection scans all rows every frame.
- Debug metrics run syscalls while the overlay is off.

## Implementation Bias

Prefer small, typed APIs over broad host-side workarounds. If the host needs performance-critical data that core already knows, expose it through `termy_core` and `termy_ffi` with tests rather than deriving it repeatedly in Swift.
