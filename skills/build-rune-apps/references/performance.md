# Performance: launch, idle, scrolling and commits

Rune's frame is cheap (well under a millisecond of CPU for a settings window);
what makes an app slow is the app's own commits, blocking work on the UI thread
and drawing when nothing changed. Upstream:
[launching fast](upstream/rune/launching-fast.md),
[smooth scrolling](upstream/rune/smooth-scrolling.md),
[canvas handlers](upstream/rune/canvas-handlers.md),
[Latest](upstream/rune/requests-off-the-main-thread.md),
[logging frame timing](upstream/rune/logging-frame-and-input-timing.md),
[rune-perf](upstream/rune-perf.md), and the performance rules in
[Rune's agent rules](upstream/agents.md).

## Launch

- `rune::prewarm_gpu()` first in `main`.
- Keep `init`, the first `view` and `on_window` cheap: on macOS the first frame
  is drawn during window creation.
- Start everything slow (network, indexing, Chromium, status items, secondary
  windows) from `App::on_ready`, through `handle.update(..)`.
- Keep the first second still: land post-launch state with `tx.instant()`.
- Re-summoned windows: `keep_running()` plus `AppHandle::hide/show/open`, so a
  second open is a show, not a launch.

## Idle

- `poll` returns true only when visible state changed. A `wake_after` that finds
  nothing new returns false and the window draws nothing.
- Loops stop asking for frames when their work ends; looping animations pause
  while hidden on their own.
- No file I/O on the UI thread during frames, input or animation; no repeating
  log or diagnostics writes while idle. Persist on close, quit or a debounced
  wake, and write off-thread.

## Commits

Every handler that changes state re-runs the view, diffs and lays out. Keep
that rare during continuous input:

- Hover: `.hover(..)`, `hover_group` and `group_*` styles, not
  `on_hover_change` state on every row.
- Scroll-following handlers (`on_layout`, `on_drawn_layout`) use their `_tx`
  form and `tx.live_only()` when they only move live values.
- Read `Cx::layout_size`/`layout` in views, not `window_layout`, so a scroll
  doesn't rebuild.
- Glide with `tx.scroll_to_with(key, x, y, spring)`, not an instant scroll
  stepped by `wake_after`.
- Pan, zoom and other camera handlers set `Live` values and call
  `tx.live_only()` (on 2,000 cards that cut 13.7 ms to 2.0 ms a frame).
- Values that change every frame are `Live<T>` / `LiveText`, never state.

## Long content

- `virtual_rows` builds only mounted rows; build row content inside its closure.
- `memo(id, version, || ..)` reuses rows that rarely change; key the version on
  what the row shows.
- `.cache()` rasterizes a settled subtree into a layer.
- Bound every cache in entries and in bytes, counting decoded pixels.

## Background work

`rune::Latest` for request-per-keystroke work (newest wins, optional debounce,
up to four shared workers), `rune::task::spawn` for one-offs, `setup`'s `Waker`
or `AppHandle::update` for threads that push data. Debug builds warn when a
handler or `poll` blocks for 8 ms.

## Finding the cause

- Debug builds name the source when something commits through a scroll and when
  one hover handler commits for many elements. `RUNE_PERF_WARN=0` silences them.
- `RUNE_COMMIT_BUDGET_MS=8` prints each commit over budget with where the time
  went (view, layout, text, apply) and what triggered it, in any build.
- `scripts/app-audit <repo>` (in the Rune checkout at the pinned rev) greps an
  app for the slow patterns; findings are places to look, not verdicts.
- Headless runs print per-frame CPU time, instance counts, layout nodes and
  glyphs; compare before and after on the same script.
- Measure with a `[profile.perf]` copied from Rune's root `Cargo.toml` (release
  codegen, not incremental) and paired, alternating runs by median.
  Headless numbers leave out GPU upload and presentation; say so.
- `App::on_frame_encoded(..)` and `--native --trace` give real-window timing.
