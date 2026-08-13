# Components and layout reference

Use this layer for view trees, reusable controls, themes, typography, overlays,
responsive behavior, collections, and the decision to use custom drawing.

## Contents

- [Choose the rendering level](#choose-the-rendering-level)
- [Build semantic components](#build-semantic-components)
- [Translate layout intent](#translate-layout-intent)
- [Use stable identity](#use-stable-identity)
- [Create a semantic theme](#create-a-semantic-theme)
- [Handle typography and assets](#handle-typography-and-assets)
- [Build controls and overlays](#build-controls-and-overlays)
- [Scale lists and responsive views](#scale-lists-and-responsive-views)
- [Cross the custom-element boundary carefully](#cross-the-custom-element-boundary-carefully)
- [Review checklist](#review-checklist)

## Choose the rendering level

Start high and descend only when evidence requires it:

1. Ordinary GPUI elements and `Styled` methods
2. A `RenderOnce` value-like reusable component
3. A stateful `Entity<T>` implementing `Render`
4. `canvas` for a bounded custom paint interaction
5. A custom `Element` with explicit request-layout, prepaint, and paint phases
6. A narrow native platform bridge

Ordinary element trees should handle most application layout: rows, columns,
grid, clipping, scrolling, text, images, borders, shadows, input handlers, and
focus.

Choose a custom `Element` only when you need unusual layout participation,
high-volume specialized painting, or behavior that ordinary elements cannot
express. Custom elements assume responsibility for lifecycle, layout,
prepainting, hit testing, and painting; they are not a shortcut around learning
the standard APIs.

## Build semantic components

A useful component owns a repeatable contract:

- role and semantics;
- content slots;
- variants and size;
- enabled/selected/loading state;
- interaction callback or action;
- focus behavior;
- theme roles;
- stable identity.

Prefer:

```rust
Button::new(("save", document_id), "Save")
    .variant(ButtonVariant::Primary)
    .disabled(!can_save)
    .on_click(cx.listener(|view, _, window, cx| {
        view.save(window, cx);
    }))
```

over a generic `PanelBuilder` with dozens of unrelated flags.

Make invalid combinations difficult to construct. Distinguish semantic variants
such as primary, secondary, destructive, toolbar, and quiet instead of exposing
raw colors to every caller.

Use `RenderOnce` for configured leaf or composition components. Use an entity
when the component independently owns state, tasks, subscriptions, or focus
lifetime.

## Translate layout intent

GPUI's style vocabulary is web-like and backed by layout machinery, but it is
not a browser. Match constraints, not DOM wrapper count.

| Intent | GPUI direction |
|---|---|
| Horizontal group | `.flex().flex_row()` |
| Vertical stack | `.flex().flex_col()` |
| Remaining space | `.flex_1()` |
| Fixed logical dimension | `.w(px(...))` or `.h(px(...))` |
| Bounded fluid area | min/max size plus flex behavior |
| Repeated tracks | `.grid()` and pinned grid helpers |
| Rounded clipping | radius plus `.overflow_hidden()` |
| Scrollable region | pinned overflow/list pattern with owned state if needed |
| Real overlap | `.relative()` parent and `.absolute()` child |

Rules:

- Use logical pixels and let GPUI/backend scale for the display.
- Make the parent constraint definite before relying on full-size children.
- Give fixed dimensions to icons, controls, sidebars, and authored chrome only
  when they are truly fixed.
- Let content regions flex.
- Use min/max bounds for resizable panels and readable text measures.
- Keep alignment and gaps on the parent.
- Clip only where the design requires it; hidden overflow can silently cut
  focus rings, shadows, menus, and long text.
- Test the smallest and largest supported window.

Absolute positioning is valid for badges, source-anchored overlays, layered
decoration, and custom chrome. It is fragile for normal forms and lists.

## Use stable identity

Interactive or stateful elements need IDs stable across renders. Good IDs come
from domain identity plus local role:

```rust
div()
    .id(("sidebar-row", item.id))
    .on_click(...)
```

Avoid:

- current list index when rows can reorder;
- random IDs generated during render;
- the same static ID repeated in a loop;
- IDs derived from localized display text;
- source-location convenience IDs for repeated macro expansion.

Stable identity protects hover/active state, focus, list behavior,
accessibility, and test targeting.

Current GPUI accessibility code also requires unique global accessibility IDs.
The `text!` macro can use source location as identity; repeated expansion in a
loop can therefore create duplicates. Use explicitly identified text/elements
for repeated accessible rows and verify the tree.

## Create a semantic theme

Keep appearance policy in semantic roles:

```rust
struct Theme {
    canvas: Hsla,
    surface: Hsla,
    surface_elevated: Hsla,
    control_fill: Hsla,
    text_primary: Hsla,
    text_secondary: Hsla,
    border_subtle: Hsla,
    accent: Hsla,
    danger: Hsla,
    focus_ring: Hsla,
}
```

Add state roles rather than opacity math at call sites:

- hover, pressed, selected, disabled;
- active/inactive window;
- elevated material;
- opaque accessibility fallback;
- high-contrast border/text;
- light and dark appearances.

Theme values should describe roles, not component names like
`settings_sidebar_gray`. Keep spacing, radii, typography, shadows, and motion
tokens nearby when the project benefits.

For Apple-style materials, theme policy should decide whether a surface is
native glass, legacy vibrancy, whole-window blur, an approximation, or opaque.
See [apple-glass.md](apple-glass.md).

## Handle typography and assets

Text is geometry. Specify and verify:

- actual runtime family and fallback;
- available weight/style;
- logical size and line height;
- wrapping width and line limit;
- alignment and truncation;
- text color and disabled contrast;
- baseline with adjacent icons;
- localization expansion.

On macOS, prefer system font roles unless the product brand requires a bundled
face. Do not hardcode “SF Pro” as an arbitrary downloaded asset; use the system
font path established by the target.

Load fonts and assets through the project's asset source. Keep identifiers
typed or centralized. Prefer vectors for icons when the renderer supports the
format reliably, and supply high-DPI raster data for photos/illustration.

Do not rasterize native controls or text for screenshot fidelity. Ensure icons
have consistent optical size, not merely identical file bounds.

## Build controls and overlays

Every control needs:

- adequate visual and hit bounds;
- hover, pressed, focus-visible, disabled, and selected states as applicable;
- a semantic role and accessible label;
- keyboard activation;
- cursor behavior;
- typed intent;
- predictable focus after activation or dismissal.

Respond visually on press/down. Commit the action according to the expected
control semantic. Do not lock the whole UI during decorative animation.

For a popover, menu, sheet, or dialog:

1. Store the anchor/source identity.
2. Mount it in the project's overlay/deferred layer.
3. Establish focus scope and initial focus.
4. Handle Escape and outside dismissal in a defined order.
5. Keep pointer events from leaking to obscured content.
6. Return focus to the source when dismissed.
7. Reposition or dismiss on resize/anchor loss.
8. Give the presentation an accessibility role and label.

Avoid drawing a menu as an absolutely positioned child inside a clipped
scrolling container.

## Scale lists and responsive views

Use ordinary child iteration for small bounded groups. Use `list` or
`uniform_list` for large collections. The exact API varies by revision, so copy
a pinned example.

List rules:

- keep row keys stable;
- keep row render pure and cheap;
- keep selection in a clear owner;
- preserve keyboard navigation and focus visibility;
- avoid one subscription/task per visible row when a model-level operation can
  serve all rows;
- test insertion, deletion, reordering, empty state, and restoration;
- verify variable-height assumptions before choosing `uniform_list`.

Responsive behavior should be an explicit policy:

- identify breakpoints from usable geometry, not device marketing names;
- collapse secondary panels before crushing primary controls;
- keep keyboard focus on surviving content;
- preserve selection when a panel moves;
- avoid maintaining unrelated desktop/mobile trees if composition can change;
- test text enlargement and localization at every breakpoint.

## Cross the custom-element boundary carefully

Before creating a custom `Element`, prove:

- normal flex/grid cannot express the layout;
- `canvas` is not sufficient;
- the expected performance or precision benefit matters;
- hit testing and accessibility have a plan;
- scale-factor and clipping behavior are understood;
- tests can cover pure geometry and GPUI interaction.

A custom element's phases must remain coherent:

1. Request layout using stable constraints.
2. Prepaint derived geometry and hit regions.
3. Paint without mutating product state.
4. Route input to the correct entity/action.
5. Expose accessibility semantics outside or alongside custom paint.

Never put blocking work, nondeterministic domain mutation, or unbounded
allocation in paint.

## Review checklist

- [ ] Correct rendering level chosen
- [ ] One source of truth for durable state
- [ ] Flexible and fixed constraints match intent
- [ ] Interactive IDs stable across reorder and rerender
- [ ] Semantic theme roles cover state and accessibility variants
- [ ] Font faces and metrics verified at runtime
- [ ] Controls support pointer, keyboard, focus, and accessibility
- [ ] Overlays own focus/dismissal/positioning
- [ ] Large collections are virtualized
- [ ] Small and large windows exercised
- [ ] Custom drawing justified and accessible
