# Layout, style, colour, text and lists

Rune's layout is Taffy's flexbox and grid, in points, with CSS's defaults and
CSS's surprises. The full method list is in
[What exists](upstream/rune/what-exists.md) and
[rich text and scrolling](upstream/rune/rich-text-scrolling-and-app-hooks.md).

## Building blocks

- `row()`, `col()`, `el()`, `text(..)`, `rich(text, spans)`, `icon(&Icon, size)`,
  `grid(..)`, `spacer()`, `rule()`, `canvas(shape)`, `text_input(&edit, style)`.
- Size: `.w`, `.h`, `.size(w, h)`, `.w_full()`, `.h_full()`, `.min_w`, `.max_w`,
  `.min_h`, `.aspect_ratio`. Space: `.padding`, `.px`, `.py`, `.pt`, `.pb`, `.gap`.
  Flex: `.grow(g)`, `.shrink()`, `.center()`, `.center_y()`. Position:
  `.absolute(x, y)`, `.above()`, `.anchored(key, ..)`.
- Paint: `.fill`, `.radius`, `.border`, `.shadow(y, blur, color)`,
  `.box_shadow(Shadow)`, `.gradient`, `.linear_gradient`, `.radial_gradient`,
  `.opacity`, `.blur`, `.clip_rounded`, `.clip_fade`, `.hover(..)` styles.
- Text: `.font(TextStyle)`, `.color`, `.wrap()`, `.truncate()`, `.align(..)`,
  `.selectable(true)`.
- Accessibility on any element: `.role(..)`, `.label(..)`, `.checked(..)`,
  `.focusable(true)`, `.help(..)`; see [input and windows](input-windows.md).

## Three flexbox traps (all CSS behaviour)

1. `.grow(g)` is `flex: g 1 0`: basis 0, so the element only gets free space.
   In an auto-height column there is none, and a grown `.scroll(..)` viewport
   collapses to 0 pt. Bound an ancestor (`.h(..)`, `.h_full()`) or set `.min_h`.
2. Flex items default to a minimum of their content size, so a nested column
   overflows instead of shrinking and its scroll never scrolls. Put `.min_h(0.0)`
   on each column between the bounded ancestor and the viewport. The reference
   app's list is `list.scroll(..).shrink().min_h(0.0)` inside a `.h_full()` window.
3. `.virtualize(..)` works only on a growth stack (`.growth(GrowthSpec)`) that is
   the scroll viewport's first child. Debug builds warn about a 0 pt viewport and
   panic on `virtualize` without `growth`.

Read the `--tree` rects when a layout looks wrong; they are the laid-out truth.

## Keys

- `.key("name")` gives identity across commits: animation, presence, focus,
  scroll requests, tests and scripts all use it.
- Keys are one namespace; the first match in tree order wins. Reach nested
  elements with paths of keyed ancestors (`"inspector/label"`,
  `"task-3/check"`). rune-kit keys its own parts (`label`, `value`, `icon`,
  `control`), so prefix or path app keys.
- Rows from data: `format!("task-{id}")`. Never the index.

## Colour

- `rune::Color` is **linear sRGB with straight alpha**. A design hex value is
  sRGB: convert it with `rune::color::hex("#1f6feb")` (returns `Option<Color>`)
  or decode it yourself, never `Color { r: 0x1f as f32 / 255.0, .. }`.
- `oklch(l, c, h)` / `oklcha(..)` author colours perceptually; colours animate
  in OKLab, and text colour leads its background so contrast holds mid-theme.
- Windows blend in sRGB-encoded space by default, as browsers and Core
  Animation do, so translucent design tokens look as designed.
  `.srgb_blend(false)` on `App`, `WindowSpec` or an overlay opts into
  linear-light blending; rune-kit and
  `Theme::from_json` follow the window's mode.
- Shadows: `blur` is CSS `box-shadow` blur (σ = blur/2). A Figma, Sketch or
  `CALayer` shadow radius is about σ, so pass `blur = 2 × radius`. `.blur(σ)`
  on an element takes σ directly.

## Tokens and themes

- Core tokens: `rune::tok::theme(dark)` (`bg`, `card`, `text`,
  `text_secondary`, `separator`, `control_off`, `knob`, `hover`, `press`, …),
  `tok::accent(i, dark)` (six accents), `tok::space::S1..S6`,
  `tok::radius::SM/MD/LG`, `tok::type_::BODY/LABEL/TITLE/SECTION`,
  `tok::motion::*` springs.
- An app with its own design keeps one typed palette struct built from
  `rune::Theme::from_json(src, dark)` or from hex constants through
  `color::hex`, resolved once per view, and passes it down (`Paint { t, accent, hair }`
  in `examples/settings`).
- With rune-kit, the `Kit` is the token set: `k.c.*` colours, `k.ty.*` text
  styles, `k.radius`, `k.motion`, `k.elevation`. Use `k.c.page` for the window
  background; `bg_base` is a card on it (an off switch vanishes on `bg_base` in
  light mode).
- Follow the system appearance with `cx.system_dark()` unless the app has its
  own setting; render both with `--theme light|dark`.
- Hairlines: `1.0 / cx.env().scale` points.

## Text and fonts

- Inter is embedded by default. `AppSpec { fonts: &[include_bytes!(..)], families: ("Name", "Mono"), .. }`
  replaces it; `TextStyle::new(size, weight).family(Family::Named("Anton"))`,
  `.lh(line_height)`, `.tracking(..)`, `.features("'tnum' 1")`,
  `.variations("'wght' 500")`. `Family::SystemMono` uses SF Mono and peers
  without bundling them.
- Text sizes round to whole device pixels; numbers that change every frame use
  `LiveText` ([high-frequency values](upstream/rune/high-frequency-values.md)).
- Font smoothing defaults match the platform (CoreText-like on macOS); change it
  only with a reason ([what exists](upstream/rune/what-exists.md), "Text").

## Icons and images

- `icon(&Icon, size)` draws an SVG body (`Icon { name, view, body }`) through the
  glyph atlas; `currentColor` takes the element's colour. rune-kit ships
  `rune_kit::glyphs::*`.
- Raster and SVG images: one `ImageCache::new(waker)` made in `setup`, kept in
  state; `cache.load(bytes)`, `cache.svg(bytes, size_pt, scale)`,
  `cache.file(path, ..)`; draw with `el().w(..).h(..).pixels(image.pixels())` or
  `.pixels_fit(..)`. Decoding runs on worker threads; never decode in `view`.

## Scrolling and long lists

- `.scroll(ScrollSpec { stick_bottom })` for vertical; `.scroll_x()`,
  `.scroll_xy()` for the other axes. Offsets are the runtime's; ask with
  `tx.scroll_into_view(key)` and friends.
- Long lists: `virtual_rows(count, estimated_height, key_fn, build_fn)` on a
  growth stack inside the viewport builds only mounted rows. Handlers inside
  rows find their item by id, never by index. Wrap rarely-changing rows in
  `memo(id, version, || ..)`.
- `.sticky_top(inset)` headers, `.scroll_edge_fade(w)`, `.scroll_anchor()` to
  hold the reading position while content above changes.
- See [smooth scrolling](upstream/rune/smooth-scrolling.md) before adding any
  handler that runs during a scroll.

## Effects, materials and drawing

Vector shapes (`canvas`, `El::shape`), subtree blur, backdrop blur, system
materials (Liquid Glass on macOS 26+), isolated opacity, and the compositor hook
for `rune-fx`/`rune-light` shaders are in the bundled index. Use a native system
material only where the platform has it and give every material an opaque
fallback; never call a translucent fill "glass".
