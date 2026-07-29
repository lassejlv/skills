# GPUI translation reference

Use this reference after extracting the Paper evidence pack. It targets the
current public GPUI `0.2.2` shape as of 2026-07-29, but the target checkout's
pinned dependency and source always take precedence.

## Contents

- [Version and architecture shields](#version-and-architecture-shields)
- [Translation strategy](#translation-strategy)
- [Paper and CSS to GPUI mapping](#paper-and-css-to-gpui-mapping)
- [Typography](#typography)
- [Color, borders, radii, and effects](#color-borders-radii-and-effects)
- [Assets](#assets)
- [Components and state](#components-and-state)
- [Responsive and window behavior](#responsive-and-window-behavior)
- [Custom drawing boundary](#custom-drawing-boundary)
- [Performance and maintainability](#performance-and-maintainability)
- [Primary sources](#primary-sources)

## Version and architecture shields

GPUI is pre-1.0 and can break between releases. Before copying any API:

1. Inspect every relevant `Cargo.toml`.
2. Inspect `Cargo.lock` or the Git revision.
3. Search the checkout for a similar, currently compiling component.
4. Prefer the target repo's wrapper component library and prelude.
5. Use documentation matching the pinned version when available.

Current standalone GPUI applications use `gpui_platform::application()` and
open a root `Entity<V>` through `App::open_window`. Existing projects may use an
older `Application::new()` path or a wrapper. Do not rewrite app startup during a
screen translation unless startup itself is in scope.

Current `Render` has this shape:

```rust
impl Render for MyView {
    fn render(
        &mut self,
        window: &mut Window,
        cx: &mut Context<Self>,
    ) -> impl IntoElement {
        div().child("Hello")
    }
}
```

GPUI has three useful levels:

- **Entity state:** application-owned mutable state and communication.
- **Views/components:** declarative element trees built during `Render` or
  `RenderOnce`.
- **Elements/custom paint:** lower-level layout and rendering for behavior that
  ordinary elements cannot express efficiently.

Use the highest level that can faithfully express the design.

## Translation strategy

### Separate visual structure from data

Do not encode every Paper node as a Rust struct. Create a component when at least
one is true:

- the pattern repeats;
- it has independent state or behavior;
- it is already a project component;
- it has multiple visual variants;
- isolating it materially improves the screenshot iteration loop.

Keep decorative wrappers inline when they only contribute local spacing or
paint.

### Preserve project ownership

Before implementing:

- find the root screen/view entity;
- find its state and event flow;
- find theme access and semantic colors;
- find asset loading;
- find reusable controls;
- find window/titlebar ownership;
- find focus and action registration.

The Paper frame specifies appearance. It does not authorize replacing correct
data flow with hardcoded mock state.

### Use exact values first

During the first pass, translate resolved Paper values directly:

```rust
div()
    .w(px(280.0))
    .h(px(40.0))
    .px(px(12.0))
    .gap(px(8.0))
    .rounded(px(6.0))
```

After the screen matches, replace repeated literals with existing semantic
tokens. Convenience methods such as `.gap_2()` are useful only when their value
matches the design.

## Paper and CSS to GPUI mapping

Exact availability varies by pinned version. Search the local `Styled` trait or
existing code when a method fails.

| Paper/computed style | GPUI direction | Notes |
|---|---|---|
| `display: flex` | `.flex()` | GPUI elements use web-like layout through Taffy |
| `display: grid` | `.grid()` plus `.grid_cols(n)` / `.grid_rows(n)` | Confirm complex track behavior in the pinned version |
| `flex-direction: row` | `.flex_row()` | Row is often the default, but state intent explicitly in fidelity work |
| `flex-direction: column` | `.flex_col()` | |
| `flex-wrap: wrap` | `.flex_wrap()` | Verify the narrowest supported viewport |
| `gap: Npx` | `.gap(px(N))` | Prefer exact gap during first pass |
| row/column gap | `.gap(...)` or axis-specific helper if present | Inspect pinned API before assuming separate gap methods |
| `align-items: flex-start` | `.items_start()` | |
| `align-items: center` | `.items_center()` | |
| `align-items: flex-end` | `.items_end()` | |
| `align-items: stretch` | `.items_stretch()` | |
| `justify-content: flex-start` | `.justify_start()` | |
| `justify-content: center` | `.justify_center()` | |
| `justify-content: flex-end` | `.justify_end()` | |
| `space-between` | `.justify_between()` | |
| fixed width/height | `.w(px(...))`, `.h(px(...))` | Keep logical pixels, not device pixels |
| equal width/height | `.size(px(...))` | For non-square dimensions, use width/height separately or the pinned size API |
| full parent size | `.size_full()`, `.w_full()`, `.h_full()` | Confirm parent has definite bounds |
| min/max size | `.min_w(...)`, `.max_w(...)`, `.min_h(...)`, `.max_h(...)` | Avoid hard width where Paper describes a flexible container |
| flex grow/shrink | `.flex_1()`, `.flex_grow(...)`, `.flex_shrink(...)` | Match Paper's fixed/flexible intent |
| padding | `.p(...)`, `.px(...)`, `.py(...)`, or side helpers | Use exact `px(...)` |
| margin | `.m(...)`, `.mx(...)`, `.my(...)`, or side helpers | Negative values need explicit checking |
| `position: absolute` | `.absolute()` plus inset helpers | Parent must establish intended coordinate context |
| inset/top/right/bottom/left | `.top(...)`, `.right(...)`, `.bottom(...)`, `.left(...)` | Use only for real overlays |
| hidden overflow/clipping | `.overflow_hidden()` | Required for rounded image clipping |
| scrolling | `.overflow_scroll()` or axis-specific scrolling | Track scroll state when behavior requires it |
| hidden display | `.hidden()` | Different from opacity zero |
| opacity | `.opacity(f32)` | Paper percentages map to 0.0–1.0 |
| aspect ratio | `.aspect_ratio(value)` / `.aspect_square()` | Preserve image/icon proportions |
| background | `.bg(rgb(...))`, `.bg(rgba(...))`, or a fill | Prefer semantic theme colors after matching |
| border | `.border_1()` or exact border helper plus `.border_color(...)` | Check whether Paper border is inside/centered when diagnosing 1px drift |
| dashed border | `.border_dashed()` | |
| radius | `.rounded(px(...))` or corner-specific helpers | Avoid scale shortcuts when radius is exact |
| standard shadow | `.shadow_sm()`, `.shadow_md()`, `.shadow_lg()` | Use only if it matches |
| custom shadow | project/pinned `BoxShadow` and shadow API | Preserve offset, blur, spread, and alpha |
| text color | `.text_color(...)` | Cascades to children |
| font family | `.font_family(...)` | Must exist in the runtime |
| font weight | `.font_weight(FontWeight(...))` | Reuse the project's weight constants where available |
| font size | `.text_size(px(...))` | Use exact size before scale shortcuts |
| line height | `.line_height(px(...))` or relative value | Explicit line height prevents metric drift |
| text align | `.text_left()`, `.text_center()`, `.text_right()` | |
| nowrap | `.whitespace_nowrap()` | |
| ellipsis | `.truncate()`, `.text_ellipsis()`, or line clamp | Match Paper's line count and width |
| hover state | `.hover(|style| ...)` | Add an element ID when stateful interactivity requires it |
| click | `.on_click(...)` | Keep hit area and semantic action correct |
| focus | `.track_focus(...)` and focused styling | Implement for keyboard-accessible controls |

### Fixed versus flexible dimensions

This is the most common translation failure.

- Use a fixed `px` width when Paper shows a fixed sidebar, icon, field, or
  explicit artboard-aligned control.
- Use `.flex_1()` when the content region consumes remaining space.
- Use min/max bounds when Paper has a preferred width but must resize.
- Use intrinsic content sizing for labels and compact buttons.
- Do not assign every Paper node its screenshot width. Many widths are outcomes
  of parent layout rather than authored constraints.

### Absolute positioning

Use absolute positioning for:

- badges over thumbnails;
- overlay controls;
- deliberate visual overlap;
- anchored decoration;
- custom chrome;
- stack layers.

Do not use it for ordinary rows, columns, grids, lists, or form layout. A
coordinate dump can match one screenshot and fail immediately on text or window
changes.

### DOM concepts without direct native equivalents

- `z-index`: GPUI paint order generally follows element/deferred structure.
  Model overlays with appropriate element ordering, `deferred`, anchored UI, or
  the project's overlay system.
- CSS pseudo-elements: use explicit decorative child elements.
- media queries: branch on current window/content bounds using the project's
  established resize pattern.
- browser default controls: build or reuse native GPUI controls; never assume
  browser padding or focus rings.
- DOM accessibility roles: use the current GPUI accessibility APIs and existing
  component patterns.

## Typography

Typography is a first-order layout input.

### Match in this order

1. Font family and fallbacks
2. Actual available face for the requested weight/style
3. Font size
4. Line height
5. Wrapping width and number of lines
6. Alignment and baseline
7. Letter spacing, if the pinned GPUI text system exposes it
8. Truncation and text transform

GPUI's current public `Styled` surface includes `font_family`, `font_weight`,
`font`, `text_size`, `line_height`, text alignment, whitespace, ellipsis, and
line clamp. Letter-spacing support may differ by version or require lower-level
text shaping. Do not claim exact tracking when the target API cannot express it;
inspect the pinned text APIs or record the limitation.

### Font registration

Reuse the app's current asset/font registration. For standalone current GPUI,
platform text setup can depend on `gpui_platform` features. The current upstream
README notes that macOS needs `font-kit` for glyph rasterization; without it,
layout may occur while glyphs do not render.

Verify font fidelity in the actual app, not only through successful layout or
tests.

### Text antialiasing

Paper and native GPUI screenshots can differ slightly because of platform text
rasterization. Judge:

- family and weight shape;
- baseline;
- line breaks;
- advance widths;
- line height;
- overall tone.

Do not chase subpixel antialias noise with incorrect colors or dimensions.

## Color, borders, radii, and effects

### Color

Paper hex values map naturally:

```rust
rgb(0x1f2328)
```

For alpha, use the target version's `rgba`/`hsla` constructors and verify channel
ordering from local docs or source. Prefer the existing theme:

```rust
.bg(cx.theme().surface)
.text_color(cx.theme().text)
```

Exact theme access is project-specific. Do not introduce hardcoded colors into a
themed app just because Paper returns hex.

### Borders

One-pixel drift commonly comes from:

- Paper's border placement versus GPUI's box model;
- fractional coordinates;
- device-scale rounding;
- a separator modeled as a border in one system and a 1px child in the other.

When a border refuses to align, test an explicit 1px separator child before
moving surrounding geometry.

### Radius and clipping

Radius alone does not guarantee child clipping. Add `.overflow_hidden()` to the
container when an image or fill must be clipped to the rounded bounds.

### Shadows

Match custom shadows by:

- x/y offset;
- blur;
- spread;
- color and alpha;
- whether the shadow is inset.

If the pinned GPUI API cannot represent inset shadow, use a deliberate
approximation such as an inner border/gradient or a custom element. Record the
remaining delta.

### Gradients and blur

Current GPUI exposes fill and gradient primitives, but their exact construction
can vary. Search the pinned checkout for `linear_gradient`, `Fill`, and existing
usage.

Backdrop blur, complex blend modes, masks, filters, and shader effects may not
have a direct high-level equivalent. Prefer a maintainable native substitute.
Use `canvas` or a custom element only when the effect is visually important and
cannot be expressed by ordinary elements.

## Assets

### SVG

Current GPUI provides:

```rust
svg()
    .path("icons/search.svg")
    .size(px(16.0))
```

The application must provide an `AssetSource` that can load the path. Reuse its
conventions. GPUI's SVG renderer rasterizes through the configured asset source;
verify gradients, masks, text-in-SVG, and runtime tinting visually.

Prefer SVG for:

- monochrome icons;
- logos;
- simple vector illustrations;
- shapes with precise edges.

### Raster images

Reuse the app's `img`/`ImageSource` and cache policy. Render a 2x export at its
logical Paper dimensions rather than its raw pixel width. Match fill/fit/crop and
rounded clipping.

### Do not flatten

Never replace these with screenshots:

- text;
- buttons;
- fields;
- list rows;
- panels;
- window chrome;
- icons that need tint or interaction;
- states that change.

Flattening hides layout bugs and breaks accessibility, theming, scaling, and
interaction.

## Components and state

### Render versus RenderOnce

Use a `Render` view/entity when the component owns mutable state, subscriptions,
focus, or long-lived behavior. Use a `RenderOnce` component for reusable
data-driven visual recipes that do not need independent entity state.

Follow the target repo's component conventions instead of introducing
`RenderOnce` solely because the upstream API supports it.

### Events

Current event callbacks receive both `Window` and `App` contexts. A view-owned
handler commonly uses `cx.listener`:

```rust
.on_click(cx.listener(|this, _event, _window, cx| {
    this.selected = true;
    cx.notify();
}))
```

Use actions for commands and keyboard shortcuts when the app already does so.
Preserve focus:

- store or obtain a `FocusHandle`;
- apply `.track_focus(...)`;
- expose the view through `Focusable` when appropriate;
- style focus visibly;
- test keyboard activation and escape/dismissal paths.

Static Paper frames rarely define every state. Reuse the existing design system
state behavior before inventing new colors or motion.

## Responsive and window behavior

Desktop GPUI does not mean one fixed screenshot size. Determine:

- minimum supported content size;
- window chrome and titlebar height;
- fixed versus resizable window;
- sidebar collapse or hiding behavior;
- toolbar wrapping/truncation;
- scroll ownership;
- modal edge avoidance;
- platform-specific titlebar insets.

Paper may contain multiple selected artboards representing breakpoints. Treat
them as explicit layout states and map each to a window-width condition. Keep the
content and component model shared.

Do not assume a web breakpoint helper exists. Read the current window bounds
through the project's established pattern and render the appropriate structure.
Test at the exact artboard widths and at one width between each pair to catch
threshold discontinuities.

## Custom drawing boundary

Stay with `div`, text, `svg`, images, gradients, and project components for most
UI.

Use `canvas(prepaint, paint)` for small custom drawing that depends on final
bounds. Implement a custom `Element` only for:

- specialized high-performance layout;
- non-standard hit testing;
- advanced vector drawing;
- an effect unavailable from ordinary elements;
- very large/virtualized rendering where per-child views are too costly.

Do not jump to custom paint to avoid understanding flex geometry.

## Performance and maintainability

- Avoid file-system reads and asset decoding inside `render`.
- Reuse `SharedString` and existing assets.
- Keep lists lazy/virtualized when the app already supports that.
- Do not create new entities for decorative leaves.
- Keep expensive layout-independent calculations out of every frame.
- Call `cx.notify()` when owned state changes and the view must rerender.
- Preserve subscriptions so they are not dropped immediately.
- Avoid cloning large state merely to satisfy closure ownership; follow existing
  entity update patterns.
- Keep target-specific pixel constants centralized enough to review, but do not
  build a generic styling framework for one design.

## Primary sources

Research checked 2026-07-29:

- GPUI official site and current example: https://gpui.rs/
- GPUI crate documentation: https://docs.rs/gpui/latest/gpui/
- `Render` trait: https://docs.rs/gpui/latest/gpui/trait.Render.html
- `Styled` trait: https://docs.rs/gpui/latest/gpui/trait.Styled.html
- `Svg` element: https://docs.rs/gpui/latest/gpui/struct.Svg.html
- Upstream GPUI README:
  https://github.com/zed-industries/zed/blob/main/crates/gpui/README.md
- Upstream current `hello_world` example:
  https://github.com/zed-industries/zed/blob/main/crates/gpui/examples/hello_world.rs
- Upstream current styling source:
  https://github.com/zed-industries/zed/blob/main/crates/gpui/src/styled.rs
