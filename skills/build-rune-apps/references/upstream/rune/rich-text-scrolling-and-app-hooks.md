> Upstream: [crates/rune/README.md § Rich text, scrolling and app hooks](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#rich-text-scrolling-and-app-hooks) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Rich text, scrolling and app hooks

![session](https://raw.githubusercontent.com/anomalyco/rune/65f8eb43f710e078f92cb82039212de50cb03113/demo/opencode/session-bottom.png)

- **Rich text** (`rich(text, spans)`): per-range weight, colour, family, background and underline
  (`Span`), wrapping with absolute line height and letter spacing, `.truncate()` with an ellipsis, and
  inline-code backgrounds that merge where they touch. `.align(..)` and `Node` insets keep text inside
  padding and borders.
- **Fonts as data**: `AppSpec::fonts` embeds faces and `AppSpec::families = (ui, mono)` names them.
  `TextStyle` picks a `Family`.
- **Icons** (`icon(&Icon, size)`): SVG icon bodies (as in `@opencode/ui`'s catalog) rasterised into
  the glyph atlas.
- **Themes as data** (`theme.rs`): `Theme::from_json(src, dark)` reads named tokens (hex, rgba or
  references, plus numbers). `"blend": {"mode": "srgb", "over": token}` says translucent tokens are
  authored for a browser's sRGB blending: they resolve as authored in a window that blends in sRGB
  (the default) and re-solved over `over` in one that blends in linear light, following the mode
  of the window building the view (`theme::blends_srgb`, `theme::for_blend`, `Theme::alpha`). An app's own theme lives
  in the app; core ships only the format.
- **Scrolling** (`.scroll(ScrollSpec { stick_bottom })`): a runtime-owned fractional offset, wheel 1:1,
  fling decay, and follow-the-end. A new viewport opens at its end on its first frame.
- **Virtual rows** (`.virtualize(estimated_row_height)` on a growth stack directly inside a scroll
  viewport): only an overscanned window has Taffy, shaped text and scene nodes. Rows need unique
  keys and internal vertical padding rather than margins or stack gaps. Unvisited heights are
  estimates; measured corrections preserve the visible key and the bottom stays exact. Historical
  rows remount settled. The measurement pass expands the window before drawing if estimates leave
  a gap. Render coordinates are rebased near the window and scroll extents use double precision.
  View construction still visits every row; a lazy view API is a remaining optimization.
  `tx.scroll_into_view(key)` reveals a row, including one outside the realized window.
  `tx.scroll_page(key, pages)` pages the viewport keyed `key` (or containing it) by `pages` × 90%
  of its height, as Page Up and Page Down do; a `stick_bottom` viewport that lands on its end
  follows it again.
  `.scroll_edge_fade(w)` fades a viewport's top and bottom only while content is hidden under
  them (strength = hidden extent / 15 pt), and `.scroll_margin(pts)` stops revealed rows clear of it.
- **Sticky headers and bars** (`.sticky_top(inset)`, `.sticky_bottom(inset)`, `.stuck_shadow(shadow)`,
  `tx.keep_on_screen(key)`, `runtime/scroll/sticky.rs`): an element inside a vertical scroll viewport pins to the
  nearest scroll viewport's top or bottom edge (offset inward by `inset`) while its parent stays in
  view, and is pushed out by its parent's content box (inside the parent's padding) as the parent
  scrolls away, as CSS `position: sticky` does. Sticky children draw and hit-test above later normal
  siblings of their parent and below `.above()` / `.modal()` overlays, move in the same frame as the
  scroll offset without re-running Taffy, and report their vertical stuck displacement on
  `ElementInfo::stuck` (`stuck` in `--tree` JSON when non-zero) and in `.on_drawn_layout(|s, r|)`'s
  drawn rect. `.stuck_shadow(Shadow)` appends shadows (such as a 1 pt hairline divider and a soft
  drop shadow) whose alpha scales linearly over the first 8 pt of `stuck.abs()`. When clicking a
  stuck header collapses or expands its section, `tx.keep_on_screen(key)` adjusts the enclosing
  scroll viewport's offset each frame so the header stays under the pointer while layout and
  growth springs run, remounting virtual rows if needed. Explicit scroll requests and subsequent
  wheel input win. In `virtual_rows`, put the header and its section in the same row: a header in
  a separate row disappears when that row is unmounted. Horizontal-only ancestors are skipped;
  without a vertical scroll ancestor sticky positioning is a no-op. Cached subtrees containing
  sticky content draw live rather than reusing a raster at a stale offset.
  `tx.scroll_into_view(key)` clears headers stuck at the edge it reveals to, and
  `El::anchored(key, ..)` follows a sticky target's drawn rect. See
  `cargo run -p rune --example sticky` ([still](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/sticky-headers.png)).
- **Horizontal scrolling** (`.scroll_x()`, `.scroll_xy()`): a filmstrip, a wide code block or table,
  a tab strip that overflows. The content (the first child) takes its natural width, unwrapped, and
  at least the viewport's, unless it sets a width other than `w_full`; `.scroll_xy()` also scrolls
  vertically and needs a bounded height like `.scroll`. Each axis has its own offset, momentum and
  clamping, and on the web its own rubber band. A wheel or trackpad gesture moves one axis, picked
  by its first delta and held to its end (momentum included), as AppKit's predominant-axis scrolling
  does: mostly horizontal goes to the innermost horizontal viewport under the pointer, anything else
  to the innermost vertical one, so a vertical swipe over a filmstrip scrolls the page around it and
  a diagonal never moves both. On the web a touch pan does the same from its first 8 pt. A gesture
  keeps its axis wherever the pointer ends up, as AppKit latches a gesture to the view it began on.
  Without phases, a mouse wheel tick wholly on the other axis picks afresh, so Shift + wheel and
  then the plain wheel each scroll at once. Shift with a mouse wheel scrolls horizontally on
  Windows, Linux and the web; macOS turns the delta itself. `tx.scroll_into_view(key)` scrolls both
  axes, `.scroll_edge_fade(w)` fades the left and right edges, `tx.scroll_to(key, x, y)` glides a
  viewport to an offset (clamped, rechecked as virtual rows measure, taken over by the wheel),
  `tx.scroll_to_with(key, x, y, spring)` glides there on the app's spring, and
  `scroll_to_instant`, `scroll_to_x` and `scroll_to_y` jump there. A request sent mid-glide keeps
  its speed, so key repeat moving a selection a row at a time scrolls as one motion. A still
  pointer's hover holds while an app steps its own glide with `scroll_to_instant` each frame,
  and resolves once after. Left and Right arrows don't scroll a viewport (text fields own them), and
  Page Up and Page Down stay vertical; AppKit scrolls an `NSScrollView` with Left and Right only
  when nothing focused takes them. Virtual rows are vertical only. Platforms report wheels through
  `Runtime::wheel_xy` with `wheel_began` and `wheel_ended` around trackpad gestures, or
  `Runtime::wheel_event` with modifiers and phases; `Runtime::wheel` stays the vertical path.
- **Canvas input** (`input/canvas_input.rs`): what an infinite canvas, map or image viewer needs.
  `.on_wheel(|s, e: WheelEvent, tx| -> bool)` hears wheel and trackpad deltas over the element
  before any scroll view does, innermost first up to the nearest scroll view, with `dx`, `dy`,
  the pointer in the element's own layout points (under any `live_scale`), `mods`, `phase`, `momentum` and `precise`.
  Returning true takes the delta, and the element then hears the rest of that gesture, its
  momentum included, wherever the pointer goes; false lets it scroll, and a gesture that
  scrolled stays a scroll. `.on_magnify(|s, e: MagnifyEvent, tx| -> bool)` hears trackpad
  pinches (scale by `1 + delta`) at the pointer: macOS reports them, and on Windows, Linux and
  the web a pinch arrives as Ctrl + wheel, which goes to `on_magnify` (`-dy / 200` per point)
  when one is under the pointer. `.on_rotate` and `.on_smart_magnify` (a two-finger double tap)
  are macOS only. `.pointer_buttons([PointerButton::Middle])` lets the middle (or back,
  forward) button press and drag the element through its own `on_press` and `on_drag`, from
  anywhere inside it; `tx.button()` says which button. Without it those handlers stay
  primary-only. `.on_key_up(|s, e: &KeyEvent, tx| -> bool)` hears releases with the same
  logical keys `on_key` sees: the focused element's first, then its ancestors', and with
  nothing focused the root's, so a handler on a window's root hears every release. A focused
  `on_physical_input` that takes a release keeps it from `on_key_up`. Hosts map releases to
  logical keys only while some element has `on_key_up`. Under a camera (`live_offset` and
  `live_scale` on the world), hit tests follow the drawn rects, `Drag` points and the pointer
  in these events are in the element's own (unzoomed) points, and `.on_drawn_layout(|s, r|)`
  reports where an element shows in the window, on each frame a pan or zoom moves it. A
  handler that moves only the camera says `tx.live_only()`, and its event doesn't re-run the
  view (see [below](canvas-handlers.md#canvas-handlers-live-only-events-and-coordinate-spaces)).
  `cargo run -p rune --example canvas_input` drives a canvas through all of it headlessly:
  wheel pan, pinch about the pointer, Space + drag, middle drag and a Focus button.
- **Timeline growth** (`.growth(GrowthSpec { spring, edge })`, `growth.rs`): rows of a stack ease
  their heights render-side on `GROWTH` (0.32 s, bounce 0) in fixed 1/240 s substeps, so 30, 60 and
  120 fps give the same curve. Desktop's per-frame caps are per-second here (start, ramp, max, long,
  carrying-tail, near-target), and every row eases into its target. Positions come from the presented
  heights above, on the 1/64 px grid. Leaving rows close after 0.15 s and fade in place.
  `.streaming(true)` marks the growing tail. Its last wrapped line holds back up to .52 line heights
  (one line) or .82 (multiple lines), proportional to unfilled width. Measurement reuses Parley's
  shaped layout. A width rewrap can shrink the row; completion lands at its full measured height.
- **Stream edges** (`edge::{FEATHER, FAST_FEATHER, NO_MASK, WORD_FADE}`): the feather mask under a
  growing row and the word-fade duration. `.reveal(word_fade)` fades appended words in, staggered from
  20 ms down to 5.5 ms as a backlog builds.
- **Settling** (`Tx::settle()`): no animation, every track lands, and removed nodes unmount at once.
  Opening a session lands at the bottom on its first frame with nothing animating in.
- **Turn actions**: a transcript view can reserve a stable tail and crossfades Working into the
  Desktop copy icon over .34 s, without removing and re-adding the tail's height. `Tx::copy(text)`
  requests a shell clipboard write. Requests follow handler order; headless runs never write the
  system clipboard.
- **Text input** (`text_input(&edit, style)`, `edit.rs`): caret, selection, word and line motion,
  select all, copy, cut and paste, undo, and IME preedit through winit (see [Text fields](text-fields.md#text-fields)). `.on_edit(..)` binds the `TextEdit` in app
  state and `.on_submit(..)` runs on Enter.
- **App hooks**: `AppSpec::setup` (once, with a `Waker` for background threads), `poll(state, clock,
  tx)` before every frame, `on_key`, and `extra_args()` for the app's own flags, ready before
  `run` (to choose the file a window opens).
  `tx.wake_after(Duration::from_millis(250))` schedules a poll on the unscaled app clock,
  even when poll returns false. Equal deadlines coalesce; the shell sleeps until the earliest
  deadline without a timer thread. Every deadline due by a frame collapses into that frame's
  one poll, so a poll that asks for a wake each time it runs costs one poll a frame, never
  more. Coarse headless steps stop at deadlines at least a frame interval apart. For debounce, store
  the latest due time in state and reschedule its remainder when an older wake arrives.
- **Modifier keys alone**: `App::modifier_keys()` (also on `WindowSpec` and `ConfiguredOverlay`)
  sends Shift, Control, Option/Alt, Command/Super and Fn going down and up on their own to
  `on_key` and the focused field's key handler, as `Key::Modifier { modifier, pressed }`, with
  the side (`Modifier::AltRight.side() == Some(KeySide::Right)`). `mods` hold the state after
  the change, as AppKit's flagsChanged does. Off by default; they never type, select, move focus
  or fire shortcuts, and a chord still arrives as before. Fn reaches macOS windows and overlays
  only: Windows and Linux keyboards handle Fn in firmware and never report it.
- **Tooling**: scripts gain `type`, `key`, `paste`, `scroll` (`dy`, and `dx` for a horizontal
  swipe) and `fling` (`v`, and `vx`). Traces carry motion-trace
  intents (settle cuts, growing rows, word reveals) and clipped visible rects.
