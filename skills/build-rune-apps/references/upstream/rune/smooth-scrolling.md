> Upstream: [crates/rune/README.md § Smooth scrolling](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#smooth-scrolling) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Smooth scrolling

A scroll costs Rune no commit: it moves the content, mounts `virtual_rows` and paints `El::hover` styles without
running `view`. A frame that commits while a viewport scrolls is the app's, and on a long page each one can cost
more than the 8 ms a 120 Hz frame has. Before and after code is in "Smooth scrolling" on the docs site's
Fast apps page (`site/src/FastApps.tsx`); `scripts/app-audit <repo>` greps for the patterns below.

- **`poll` returns true only when visible state changed.** To act on where a scroll stops (loading the next page,
  saving the position), wait until it has been still a moment with `Tx::wake_after`; follow it frame by frame with
  `El::on_scroll_offset` and live values.
- **Paint hover with `El::hover`, `hover_group` and `group_*` styles**, not state set from `on_hover_change`: a
  hover handler on each row commits the view for every row the pointer crosses, and a scroll moves rows under a
  still pointer.
- **Layout handlers that follow a scroll say `Tx::live_only`.** `on_layout` and `on_drawn_layout` report every
  frame of a scroll for an element inside it; their `_tx` forms can say `live_only` when the handler only moves
  live values or bookkeeping.
- **Read `Cx::layout_size` or `Cx::layout`, not `Cx::window_layout`,** unless the view needs where the window
  shows the element; then read `window_layout_with` and only what it decides.
- **Glide with `Tx::scroll_to_with(key, x, y, spring)`**, on Rune's clock, rather than an instant scroll stepped by a
  `wake_after` loop, which commits every frame.
- **Keep the reading position with `El::scroll_anchor()`.** On a scroll viewport it holds the row at the top of
  the view when a commit changes the content above it (rows inserted, grown or reflowed by a new width), like CSS
  `overflow-anchor`. It holds only while the viewport is still, off its top and not following its bottom.
  `virtual_rows` lists already keep their first visible row. For one commit, `Tx::keep_on_screen(key)` holds a
  chosen element instead.

Debug builds name the source when one keeps committing through a scroll: `poll`, a handler with its element and
where it was set, or the layout read that moved. Each warns once, on stderr, when it commits on 6 or more frames
and a quarter of a scroll's frames; `RUNE_PERF_WARN=0` silences them. They also warn when an app steps a viewport
with an instant scroll on 8 committing frames in a row, and when one hover handler commits for 8 different elements:

```text
rune: `on_layout_tx` on "#0/feed/rows/r3" (set at src/feed.rs:43:35) committed the view on 6 of 7 frames of a
scroll: when the handler only moves live values or bookkeeping, say `Tx::live_only` [...]
```

`RUNE_COMMIT_BUDGET_MS=N` prints a line for each commit over `N` ms, in any build, with where its time went and
what made the frame commit, at most once a second:

```text
rune: commit took 14.2 ms, over RUNE_COMMIT_BUDGET_MS=8: view 9.0, layout 3.0 (text 1.0), apply 1.5 ms; most in
the view (63%); committed for poll
```
