> Upstream: [crates/rune/README.md § What exists](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#what-exists) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## What exists

- **View API** (`el.rs`): `fn view(s: &S, cx: &mut Cx<S>) -> El`, with `row()/col()/el()/text()`,
  `.key(..)`, layout and style methods, `.on_press(|s: &mut S| ..)`, `.on_press_tx(|s, tx| ..)` and
  `.on_drag(|s, drag, tx| ..)`. Handlers are queued and run between frames with `&mut S`. Then the view
  re-runs, and the diff retargets property tracks. Hover and press only retarget tracks; they never
  re-run the view.
- **Tokens** (`tok.rs`): colours in OKLCH (dark and light themes, six accents), plus space, radius, type
  and the motion palette (snappy .25/0, default .3/0, calm .4/0, a .2/0 lead, a .15 fade).
- **Layout**: Taffy 0.15 at the target state. Text sizes round up to whole device pixels, so layout
  stays on the pixel grid. Keyed nodes retain Taffy's constraint cache between commits; only changed
  styles, children or text measurements dirty it. Text colour does not invalidate measurement.
  Three gotchas, all CSS flexbox behaviour:
  - `.grow(g)` is `flex: g 1 0`: flex-basis 0, so the element is only as big as the free space its
    parent leaves. In an auto-height column there is none, and a grown `.scroll(..)` viewport
    collapses to 0 pt. Bound an ancestor's height (`.h(..)`, `.h_full()`) or set `.min_h(..)`.
  - Flex items default to a minimum of their content size, so a nested flex column overflows its
    parent instead of shrinking and the scroll inside never scrolls. Put `.min_h(0.0)` on each
    column between the bounded ancestor and the viewport.
  - `.virtualize(..)` only works on a growth stack: call `.growth(GrowthSpec)` on the same element,
    and make it the scroll viewport's first child.

  Debug builds warn once per call site when a scroll viewport inside a `.grow()` container
  resolves to 0 pt while its content is taller; `.virtualize` without `.growth` panics with the
  element's path.
- **Animation** (`rune-motion`, `runtime.rs`): analytic springs (`Spring::new(duration, bounce)`),
  tweens, decay and transitions driven through `rune_motion::Scene` and `AnimationStore`. Retargets
  keep exact position and velocity.
  - Layout animates per edge, so stationary edges never move.
  - `.lead(lead, trail)` makes the edge in the direction of travel lead; `.width_leads()` speeds up X
    by `0.78×`.
  - Children ride their parent's left edge. `.ride_trailing()` keeps an element against its parent's
    right edge instead while the parent's width animates, so right-aligned content holds still
    whatever springs the rows around it use (a trailing `RollingText` does this).
  - Presence (`Transition`): elements added or removed after the first frame animate in and stay drawn
    until their exit settles at opacity 0 (including `.transition(Transition::blur_replace())` and
    mid-flight revival).
  - Colours animate in premultiplied OKLab, and text colour leads its background (`0.5×` duration) so
    theme switches keep label contrast through the transition.
  - Nothing animates on the first frame.
  - `Tx::instant()` applies a change with no animation (drag moves are instant by default).
  - `El::instant_changes()` does the same for one subtree in any commit (a popup of search results),
    while the element's own entrance and exit and its colours keep their motion.
  - `Tx::color_motion(spring)` sets the spring for that change's colours (the theme switch uses calm).
  - In reduced motion, spatial travel snaps while opacity, presence and colour take `REDUCED_FADE`
    (`0.15 s`). Growth-stack rows also keep this fade on insertion/removal; closing gaps land after
    the exit fade instead of animating their height.
  - The animation clock has a time scale, which the Settings speed slider drives.
- **Renderer** (`render.rs`, `shader.wgsl`): one instanced uber-quad pipeline and one draw call per
  frame.
  - Kinds: rounded rects (per-corner radius, a border drawn over the fill as CSS draws one, per-side
    widths), analytic Gaussian shadows (outer and inset),
    vertical and angled linear gradients, circular and elliptical radial gradients (`KIND_RADIAL`),
    dashed border rings (`KIND_DASHED`), RGBA images, and glyphs from the atlas.
  - **Gradients** (`.gradient(top, bottom)`, `.radial_gradient(center, radius, stops)`,
    `.linear_gradient(angle, stops)`): painted over `.fill(..)` and under hover/press overlays and
    borders, clipped to `.radius(..)`, and composited with `.opacity(..)` and `.blur(..)`.
    `radial_gradient` takes normalized `center: [f32; 2]` (`[0.5, 0.5]` = element centre), `radius` in
    points (`f32` for a circle or `[rx, ry]` for an ellipse), and up to 8 `stops` as `(t, Color)` pairs in
    `0.0..=1.0` (inner radial bands shrink their quads to the band bounding box). `linear_gradient`
    takes `angle` in radians (CSS convention: `0.0` up, `PI / 2` right, `PI` down) and up to 8 `stops`.
    Stop colours spring in Oklab when changed and interpolate in premultiplied colour across the quad.
  - **Shadows** (`.shadow(y, blur, color)`, `.box_shadow(Shadow)`): `blur` follows CSS `box-shadow`
    (`blur = 2σ`, so the Gaussian standard deviation is `σ = blur * 0.5`). `CALayer.shadowRadius` and
    Sketch / Figma shadow blur specify `r ≈ σ`, so pass `blur = 2.0 * r` to match a `CALayer` shadow
    radius (whereas `.blur(sigma)` takes `σ` directly).
  - Vector shapes (`shape.rs`): `El::shape(Shape)` and `canvas(shape)` paint strokes (polylines,
    round or butt caps, open or closed) and fills (simple polygons, ear-clipped) in the element's own
    points, or in a `view_box` stretched to the element's size; `Path` flattens quadratic and cubic
    Béziers. Strokes are one analytic capsule/box per
    segment (`KIND_SEGMENT`); fills are triangles (`KIND_TRIANGLE`) antialiased only on polygon
    edges, so they have no seams. No atlas, so a shape can change every frame (`examples/shapes`).
    Translucent strokes blend twice where segments overlap at a joint; fills do not overlap.
  - Every instance has a soft-edge clip (`clip_soft`, `clip_fade`).
  - Windows blend in sRGB-encoded space by default, as Core Animation, CoreText and CSS do.
    `.srgb_blend(false)` on `App`, `WindowSpec` or `ConfiguredOverlay` opts out into linear-light
    blending (colour premultiplied in linear light, drawn into an sRGB target). sRGB blending
    encodes premultiplied colours in sRGB (`Color::premul_srgb`) and renders into a non-sRGB
    target view (`format.remove_srgb_suffix()`). With a `Compositor`, `Frame::srgb_blend()` and `Frame::format` tell it which encoding and view its own passes must match.
    A runtime the app draws itself (`Runtime::with_text`, a headless snapshot) opts in with
    `Runtime::set_srgb_blend(true)`, then draws with `Renderer::set_srgb_blend(true)` into a
    non-sRGB target cleared to `clear_color()`; hover and press tints follow the mode.
    A handler switches a running window with `Tx::set_srgb_blend(bool)`: the frame that switches
    reconfigures the surface and rebuilds the renderer once (the web canvas keeps its format and
    changes its view).
  - The Retina scale is applied throughout.
- **Text** (`text.rs`): Parley 0.12 lays out embedded Inter 4.1 (OFL, `assets/`). swash 0.2
  outlines are rasterised through a port of CoreGraphics' glyph pipeline into a 2048² R8 shelf
  atlas, at CoreGraphics' subpixel pen steps, with a 1 px zeroed border per glyph and
  pixel-snapped baselines.
  **Font smoothing** (`FontSmoothing`, `text/coretext_match.rs`) picks how glyphs are rasterised
  and placed, app-wide with `App::new(spec).font_smoothing(FontSmoothing::Off)` (or
  `WindowSpec::font_smoothing`), or while running with `Tx::set_font_smoothing(mode)`, which
  rasterises the new mode's glyphs on the next frame (each mode keeps its own atlas entries, so a
  switch back is free). Modes:
  - `On`, the default on macOS and in a Mac's browser: CoreText's text with font smoothing on.
    Apple's pipeline (pens floored to CoreGraphics' subpixel step, which depends on the ppem:
    fifths of a device pixel below 8⅓ ppem, quarters to 11.1, thirds to 16.7, halves to 33.3 and
    whole pixels above; coverage drawn as is; sRGB blending; CoreGraphics' curve flattening and
    its y autohinter at 7–18 ppem) plus font smoothing's outline dilation, a radius set by the
    ink's luminance and the device ppem (`text/macos/smoothing.rs`, `ApplePipeline::SMOOTHED`).
  - `Off`: what macOS browsers draw for `-webkit-font-smoothing: antialiased`, CoreText with font
    smoothing off. Apple's pipeline without the dilation
    (`ApplePipeline::UNSMOOTHED`); lighter than `On`. Coverage takes an exponent keyed to the
    ink's luminance, the curve of Skia's grayscale text gamma.
  - `DirectWrite`: Chromium's text on Windows. DirectWrite rasterises each
    glyph as Skia's `SkScalerContext_DW` asks it to (the rendering mode the `gasp` table picks,
    grid fitting on, grayscale antialiasing, the face at the run's variation coordinates, read in
    place from Parley's bytes), pens sit on Skia's quarter pixels, and Skia's gamma tables
    (sRGB, contrast 1, eight luminance buckets) weigh each mask by its ink
    (`text/windows/`). Off Windows it draws as `Off`.
  - `Windfoil`: Rune's own text with CoreText's weight, the same
    on every OS. Each glyph's exact pixel coverage from its outline, Windfoil's closed-form box filter over
    xy-monotone quadratics (DesLauriers 2026), with CoreText's dilation (times `TEXT_WEIGHT`,
    0.93, which puts its ink within 1% of CoreText's) and y autohint applied per pixel, pens on
    quarter pixels, coverage drawn as is (`text/outline/`, `text/windfoil.rs`, `outline.wgsl`).
    Masks at rest are filled on the GPU by the shader that draws text whose scale moves (a zoom,
    a presence scale, a text flight) straight from its outlines, at its resting pen and size
    magnified, so it stays sharp and lands on the mask it rests as. A text's raster path
    (`text/outline/path.rs`: still, moving, landing), each mask's residency (`text/atlas_fill.rs`:
    uploaded, pending, filled) and the renderer's shader (`render/variant.rs`: Classic, Windfoil,
    unavailable) are state machines. CJK faces up to 24 ppem draw their TrueType-hinted outlines
    from whole-pixel pens, at half the dilation, so dense ideographs stay legible at 1x. Renderers
    start with the Windfoil shader everywhere but macOS, where the Classic shader keeps drawing
    until text asks for outlines; where it can't be built, the CPU fills the same masks
    (`text/outline/cover.rs`) and moving text draws from them.
  - `WindfoilChromium`, the default everywhere but macOS and a Mac's browser, then `Slug`,
    `HintedGpu` and `Hinted`: the other ways to draw from the outline store. Each takes Chromium's weight (no dilation, Skia's text gamma):
    Windfoil's box coverage of the design outline, Slug's two-ray winding (`outline_slug` in
    `outline.wgsl`), the outline after skrifa's light autohint, and that autohinted outline on
    whole-pixel pens, which is Chromium's text on Linux. `FontSmoothing::ALL` lists every mode and
    `FontSmoothing::support` says whether this machine draws one as named (`text/support.rs`).
  - `WindfoilRgb` and `ClearType` (Windows): subpixel text. Masks hold three coverages a pixel
    (Windfoil's box about each subpixel, or DirectWrite's `CLEARTYPE_3x1`), and the window draws
    them with a dual-source pipeline that blends each channel by its own (`render/variant.rs`,
    `Lcd`). Layers draw them grayscale; without dual-source blending they draw as
    `WindfoilChromium` and `DirectWrite`.
  `On` and `Off` work on every OS, since they are arithmetic on outlines. Blending is separate
  (`srgb_blend`).
  `cargo run -p rune --example coretext_compare [-- --smoothing on|off]` measures
  each mode against CoreText references (`tests/coretext/`, `scripts/coretext-reference.sh`). The
  atlas recycles a two-page steady ping-pong pool across frames without zeroing 4 MiB buffers,
  spills to overflow pages when a single frame exceeds one page, and never caches an allocation
  failure as an empty glyph. Colors share the same atlas masks.
  The [CoreText comparison and phase sweep](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/research/23-text-quality.md) measure weight,
  structural similarity and motion brightness variation at 1×/2×.
- **Input**: hit-testing on presented rects, pointer capture, hover and press overlays, press on
  release inside the element, and drags with a per-gesture scratch value.
  `.on_secondary_press(|s: &mut App, point, tx| ..)` receives window-point coordinates on
  right-click (also control-click on macOS), without invoking primary actions;
  `.on_secondary_press_local` gives the element's own points too (see
  [coordinate spaces](canvas-handlers.md#canvas-handlers-live-only-events-and-coordinate-spaces)). Scripts accept
  `secondary-down`, `secondary-up`, and `secondary-click`.
- **Naming elements**: `Cx::layout`, `Tx::fly_text` and the `Tx` scroll requests
  (`scroll_into_view`, `scroll_to_bottom`, `scroll_page`, `scroll_to`, `scroll_to_with`,
  `scroll_to_instant`, `scroll_to_x`, `scroll_to_y`) take a key, which
  matches the first element with it in tree order, or a key path such as `"inspector/label"`
  whose leading keys are the element's nearest keyed ancestors. Keys are one namespace, and
  rune-kit keys its parts (`label`, `value`, `icon`, `control`, …), so scope an app's own keys
  with a path or a prefix.
- **Inert subtrees**: `.inert()` draws and lays out an element and everything inside it, but
  presses, hovers, cursors, scrolls, drops and tooltips go to whatever is under it, nothing inside
  takes focus, and `ElementInfo::inert` reports it (a document drawn under an editor's canvas).
- **Cursors**: `.cursor(Cursor::Pointer)` and the other system shapes; children inherit their
  nearest ancestor's. `Cursor::Image(CursorImage::png(include_bytes!("pencil.png"), [2.0, 30.0]))`
  shows an app's own PNG, drawn at 2x, with its hot spot in points from the top-left. The OS
  draws it, so it keeps up with the pointer and reaches the window's edge, where a view drawn
  after the pointer lags a frame and is clipped (`examples/sketch`). A PNG that doesn't decode
  shows the arrow. The web host sets no cursors yet.
- **Double press**: `.on_double_press(|s: &mut S| ..)` (or `_tx`) runs when a second press on
  the element lands within the double-click interval of the first and within 4 pt of it, and
  releases inside. `on_press` still runs for every press, the first one right away, so a row
  selects on the first click and opens on the second, as in AppKit; there's no delay to wait
  out a possible second click. A third press starts a new pair, and a press anywhere else breaks
  one. Only clicks pair: a press that travels more than 4 pt, or is held past the interval, is
  neither half of one. The interval is the system setting on macOS and Windows and 0.5 s
  elsewhere. Headless runs use the virtual clock, so a script's `double-click` (or two `click`s inside 0.5 s) is
  deterministic. Pointer only: the keyboard runs `on_press` (Space, and Return on a row).
- **Click count in a drag**: `Drag::clicks` says which click of a run an `on_drag` press is, on
  every phase: 1, then 2, 3 and on for presses on the element each within the double-click
  interval and 4 pt of the one before, as AppKit's `clickCount`. A press that drags past 4 pt
  ends the run. An app-drawn text view selects by words on 2 and lines on 3 and extends by them
  as the drag moves; `on_double_press` keeps pairing as before. A script's `double-click`,
  `triple-click` and `down`/`move`/`up` drive it on the virtual clock.
- **Press scale**: `.press_scale(0.97)` shrinks an element (and its children) about its centre
  while a press on it is held, following the pointer in and out like an iOS tile, and springs back
  with a slight bounce on release. Interrupting a spring retargets it without a jump. Layout and
  hit testing keep the resting size, so a press near the edge stays inside and keeps its hover.
  Scrolling the list under a held press (wheel or fling) cancels it, as a `UIScrollView` cancels
  its content's touches: the element springs back and the release doesn't press. Elements without
  it pay nothing, and Reduce Motion turns it off. rune-kit's `Button` and `IconButton` don't use
  it: they follow `@opencode/ui` and AppKit, whose buttons don't scale.
- **Scale, rotation and origin**: `.scale(0.5)` draws an element and everything in it at half size
  about its `.origin(x, y)` (default centre `(0.5, 0.5)`), like SwiftUI's `scaleEffect`. Changes
  spring on the element's layout spring or `.scale_motion(anim)` (landing at once on mount, in an
  instant transaction and under Reduce Motion). `.rotate(radians)` turns the element and its
  subtree clockwise about the same origin on the layout spring or `.rotate_motion(anim)`, drawing
  into a layer whose composite turns; hit testing follows the turned box while reported rects use
  its upright bounds. Layout keeps the unscaled upright size, so siblings don't move. `scale`
  multiplies with `press_scale`, `live_scale` and scale transitions (`origin` applies to all of
  them; `offset` ignores it), and nested scales and turns compose. Under all of them, text, icons
  and images transform with their box (link hit boxes and a text field's caret follow). Text under
  a still scale rasterizes at the scaled size, so it stays crisp. While a scale springs (or a
  presence transition runs), text samples glyphs rasterized at its nearest still ancestor's
  scale (1, or an app's zoom), filtered, and turns crisp when the spring settles. That way a
  spring doesn't rasterize a glyph at every frame's size, and text that only fades or slides
  inside a zoomed window draws exactly as it will at rest. Text under an actively moving
  `live_scale` rasterizes at logarithmic $2^{1/4}$ scale buckets and re-rasterizes crisp at the
  exact resting scale once it holds still for 0.1 s; a changing `scale` samples rest-size glyphs
  while moving and re-rasterizes crisp at the resting scale after 0.1 s. A matched flight's own
  label keeps its rest size so it doesn't pop when it lands.
- **Cached subtrees** (`.cache()`, `.cache_key(u64)`): rasterizes a settled subtree once into an
  offscreen `Rgba16Float` layer texture (reusing the isolated-layer compositor in `render/layers.rs`) and
  composites that single quad on subsequent frames without re-emitting or re-drawing its
  descendants, including while an ancestor's `live_offset` or `live_scale` moves or scales it.
  - **Invalidation:** derived automatically from the subtree's relative draw output (primitives,
    text, layout, hover/focus/selection, theme and scale) with an optional `.cache_key(u64)` hint.
  - **Live fallback:** while any node inside the subtree animates (springs, transitions, loops,
    growth, word reveals, flights) or hosts a live compositor `El::effect` slot, `NativeSurface`,
    native `SystemMaterial`, image pixels or focused text input, the subtree bypasses the cache and draws live,
    then re-caches once settled.
  - **Scale and budget:** while an ancestor's live scale or scale spring is changing without view
    commits, the existing cached texture is composited with clamped bilinear filtering and
    re-rasterized at the new device-pixel resolution once the scale holds still for 0.1 s.
    Scale changes through view commits draw live until settled: a commit may also change content.
    Textures are capped at `4096×4096` device pixels and managed under a configurable LRU byte
    budget (`Renderer::set_cache_budget`, `layers::DEFAULT_CACHE_BUDGET` = 64 MiB). Hit testing,
    accessibility, `elements()` and `on_layout` are unchanged.
- **Focus and modals**: `.focusable(true)`, `.tab_index(n)` (positive overrides, 0 document order,
  negative pointer-only), `.focus_group()` for arrow-key roving (Up/Down only, plus type-select,
  for roles `menu`, `listbox`, `list` and `tree`; Left/Right too for other groups such as
  segments and tabs; `list`, `tree` and `grid` stop at their ends while menus and segments wrap), `.focus_follows()` to press each item it
  reaches, `.focus_selected(on)` for a group's initial Tab stop, `.focus_ring(width, offset,
  color)` for keyboard-only rings, and `.focus_highlight(color)` for a menu row's shared pointer
  and keyboard highlight. Enter/Space
  activates non-text controls. `.modal(click_outside, close)` traps Tab, handles Escape, makes the
  background inert and restores the opener. Nested modals restore in stack order. Inspector tree
  flags (`focusable`, `focused`, `focusVisible`, `inert`) are the future platform AX hook.
- **Key routing**: a key the OS delivers to the window goes to the first of these that takes it.
  Global shortcuts and native menu key equivalents are handled before the window sees the key.
  1. Return and Escape while a field composes (IME preedit), or while `App::on_ime`'s editor
     does, go to the composition and no further.
  2. Return, with no modifiers, presses the window's (or open modal's) `default_button()`
     unless the focused element takes Return (see the table below).
  3. Nothing focused: the window's `on_key`, with `tx.focused()` `None`.
  4. The focused field's `on_input_key`.
  5. Focus navigation: Escape dismisses the open modal, Tab and Shift-Tab move focus, a
     focused slider's arrows and Page Up and Down step it (`on_step`) and Home and End take it
     to its ends (`on_step_limit`), arrows, Home, End and type-select move inside a
     `focus_group`, Space or Up and Down open a focused popup button (role `combobox`), Space
     presses the focused control, and Return presses a focused row or link. Past Tab, keys
     with Shift do none of this (typed capitals still type-select); they go on.
  6. The focused text field's editor.
  7. The window's `on_key` again, now with `tx.focused()` naming the focused element (or link), for keys
     the focused control passed on.
  8. Selected text, for its copy keys (plain Cmd+A and Cmd+C): an app's `on_key` that takes
     them wins, as a menu key equivalent wins over an AppKit text view. A focused text field
     keeps its own at step 6.
  9. Page Up, Page Down, Home and End scroll the nearest scroll view around the focused
     element, else around the pointer, else the first in the tree, skipping any whose content
     fits: a chat's short composer passes them to the message list beside it. A view that
     overflows keeps them, even at the edge a key moves toward (where it does nothing), as an
     NSTextView does. To page another view, route the keys yourself with
     `tx.scroll_page(key, pages)`.

  Return follows AppKit, where it belongs to the default button and Space presses the focused
  one:

  | Focused | Return |
  | --- | --- |
  | Nothing, a button, checkbox, switch, radio, segment, popup button or slider | The default button, else `on_key` |
  | A text field with `on_submit` | `on_submit` (in a multi-line field Shift- or Option-Return types a newline) |
  | A text field without `on_submit` | The default button |
  | A row of a `menu`, `listbox`, `list`, `tree` or `grid` group, or a `focus_highlight` row | Presses the row |
  | A link in text | Opens the link |

  A field's `on_input_key` sees Return before any of these.

  A handler's `KeyEvent` carries the character the key types, and with Shift held that moves
  between keyboard layouts: `⌘⇧7` arrives as `Key::Command('&')` on a US layout and
  `Key::Command('/')` on a German one. `tx.physical_key()` names the key itself
  (`Some(PhysicalKeyCode::Digit7)` on both), so match shifted shortcuts on it. It is `None` for a
  key with no physical origin: `Runtime::key`, or a script `"key"` without a `"code"`.
  `tx.key_base()` is the character the key types under the current layout with no modifiers
  (`Some('a')` for ⌥A, which types `å`), for bindings by letter that follow the layout, as
  macOS's key bindings do; `None` where winit can't say (the web, iOS) and with no physical
  origin.

  `Mods::cmd` is the primary shortcut modifier, reported with its key: ⌘ on macOS (with
  `logo`), Ctrl elsewhere (with `ctrl`). So Ctrl+W on Windows is `{ cmd, ctrl }`, and a test
  such as `cmd && !ctrl` never passes there. Bind shortcuts with a `Chord` instead, which
  resolves both sides to the keys held on the platform:

  ```rust
  let reopen = Chord::parse("mod+shift+t")?;          // ⇧⌘T on macOS, Ctrl+Shift+T elsewhere
  let next = Chord::parse("ctrl+tab")?;               // ⌃⇥ on macOS (a literal Control), Ctrl+Tab elsewhere
  let home = Keybind::new("mod+b").on(KeyPlatform::Windows, "alt+home");
  if reopen.matches_tx(ev, tx) { /* … */ }
  reopen.label();                                     // "⇧⌘T" or "Ctrl+Shift+T"
  ```

  `mod` is the primary modifier; `ctrl`, `alt`, `shift` and `super` (`cmd`, `win`) are keys.
  Off macOS Ctrl is the primary, so "mod+b" and "ctrl+b" are the same chord there
  (`Chord::same_keys` finds such clashes); give one of them another chord on that platform
  with `Keybind::on`. A character chord names the key unshifted ("mod+shift+[") and
  `matches_tx` follows the layout through `tx.key_base()`; on a layout whose keys type no
  ASCII (Cyrillic, Greek) an ASCII chord falls back to `tx.physical_key()`. A chord on a
  shifted character ("mod+plus") matches with or without the Shift that types it.
  `matches_on` and `Shortcut::parse_on` take the platform explicitly, for tests and keymap
  pickers. `Display` writes the canonical string back for settings files; `Keybind` parses
  alternatives ("mod+t, mod+n") and `Keybind::spec_on(platform)` writes one platform's chords.

  A text field's edit commands (copy, cut, paste, select all, undo, redo, and Ctrl+Y redo
  off macOS) take only the plain chord: Ctrl+Alt+V, Ctrl+Shift+V or ⌃⌘C reach `on_key`.
  On Windows, Left Ctrl + Left Alt is AltGr, so a character typed with both inserts, and
  Home and End move to the line's edge in a multi-line field (Ctrl+Home and Ctrl+End to
  the text's ends).
- **Periodic motion**: `.looping(rune_motion::LoopSpec::opacity(..))` or `LoopSpec::rotation(period)`
  (icon quads). Tracks use animation time, preserve phase when retimed and only request frames
  while visible through ancestor clips. Removal uses the existing spring presence fade. Reduced
  motion holds the first pose; time scale 0 pauses. Occluded windows stop drawing and building.

Commit layout runs through a `Measurement` capability that can access text/layout
caches and virtual geometry, but cannot access the scene, animation tracks, draw
instances, or mutable app state. It finishes all measurement retries before
returning an owned `Measured` result. Scene mutation consumes that result; motion
policy changes are applied in the same mutation phase.
