# Paper-to-GPUI translation reference

Use this layer to turn one selected Paper.design frame or component into
maintainable native GPUI code. Paper supplies the visual contract; the target
checkout supplies the architecture and API contract.

## Contents

- [Required inputs](#required-inputs)
- [Build the evidence pack](#build-the-evidence-pack)
- [Separate design from architecture](#separate-design-from-architecture)
- [Map layout semantics](#map-layout-semantics)
- [Translate typography, paint, and material](#translate-typography-paint-and-material)
- [Translate assets and icons](#translate-assets-and-icons)
- [Add state and interaction](#add-state-and-interaction)
- [Handle responsive designs](#handle-responsive-designs)
- [Implement in fidelity passes](#implement-in-fidelity-passes)
- [Validate the native result](#validate-the-native-result)
- [Failure shields](#failure-shields)

## Required inputs

Do not begin a claimed one-to-one translation without:

- Paper Desktop running;
- intended Paper file open;
- Paper MCP tools connected;
- one exact selected artboard/frame/component or node ID;
- target GPUI checkout and owning surface;
- permission boundary: code edits versus design edits;
- target viewport(s), platform(s), and appearance(s).

If the request is an open implementation inspired by a Paper system, identify
the exact source components/tokens that still govern it. “Make it like the
design” is not enough when multiple frames conflict.

Run:

```sh
scripts/inspect_gpui_project.sh /path/to/project
```

Then read the target's manifests, root view, theme, components, assets, state,
actions, tests, and current GPUI dependency.

## Build the evidence pack

Follow [paper-mcp.md](paper-mcp.md). For the exact root capture:

1. File/page identity and selected node ID
2. 2x screenshot
3. Root bounds and hierarchy
4. JSX as a structural hint
5. Computed styles for major containers and representative descendants
6. Text content, family, face, size, line height, wrapping, and alignment
7. Tokens/variables and resolved values
8. Fill, border, radius, shadow, opacity, transform, clipping, and backdrop
   effects
9. Exportable icons/images
10. Known interactions and missing states

Record:

| Node | Semantic role | Bounds | Constraint/layout | Type | Paint/effect | Asset | State |
|---|---|---|---|---|---|---|---|

Resolve unknowns with narrower calls. Never replace an unknown with a plausible
Apple default and later call it exact.

Paper supports modern design data such as variables/tokens, constraints,
backdrop filters, variable fonts, and OpenType settings. Capture them, but map
only capabilities that exist in the pinned GPUI/platform path. Evidence of a
design effect is not proof of a native implementation capability.

## Separate design from architecture

Preserve:

- app startup and window ownership;
- domain state and persistence;
- typed actions and key contexts;
- existing component/theme systems;
- focus and overlay conventions;
- asset source;
- async and error behavior;
- platform support.

Translate Paper into five implementation layers:

1. **Window/chrome:** content bounds, titlebar relationship, minimum size.
2. **Regions:** navigation, toolbar, content, inspector, footer, overlays.
3. **Primitives:** buttons, fields, rows, chips, separators, empty states.
4. **Tokens:** semantic color, spacing, type, radius, shadow, motion, material.
5. **Behavior:** selection, input, loading, scrolling, resize, focus, shortcuts.

Do not create a Rust struct for each Paper node. Create a component when it
repeats, owns behavior/state, maps to an existing primitive, or makes fidelity
iteration materially clearer.

## Map layout semantics

Paper's JSX resembles web structure; GPUI should reproduce constraint intent,
not the DOM.

| Paper evidence | GPUI direction |
|---|---|
| Auto-layout row/column | flex row/column |
| Flex grow or fill container | `.flex_1()` or pinned equivalent |
| Fixed control/icon/sidebar | exact logical `px` dimension |
| Min/max constraint | pinned min/max style |
| Grid | GPUI grid when supported; otherwise semantic row composition |
| Gap/padding | exact `px` first, tokens after matching |
| Clip content | radius/overflow clipping on actual clipping owner |
| Overlay | anchored/deferred/project overlay layer |
| Absolute child | absolute only for genuine overlap |
| Scroll region | project/list/overflow scroll pattern |

Determine whether a width is:

- authored fixed size;
- min/max constraint;
- result of parent flex;
- intrinsic text/content size;
- screenshot-only outcome.

The biggest translation error is freezing screenshot outcomes into every child.
Match the design at the target viewport, then prove it at adjacent widths.

Maintain layer/paint order explicitly. Browser `z-index` does not map by copying
a number; use child/deferred/overlay order supported by the target.

## Translate typography, paint, and material

### Typography

Match in this order:

1. Runtime font family and fallback
2. Available face for weight/style/variable axis
3. Font size
4. Line height
5. Wrapping width and line count
6. Baseline/alignment
7. Letter spacing/OpenType behavior when supported
8. Truncation

If GPUI cannot express a Paper variable axis or feature, pick the nearest
available face only with an explicit delta. Do not silently bundle a
license-restricted font.

### Paint

Capture resolved:

- fills and gradients;
- opacity at node and paint level;
- border width/color/location;
- per-corner radii;
- shadow offset, blur, spread, alpha;
- clipping/mask behavior;
- transforms;
- background/backdrop effect.

Use exact values during first pass. Consolidate repetition into semantic tokens
after matching.

### Material

If Paper uses backdrop blur:

1. Determine whether it is window-wide or per-element.
2. Select a real target capability using [apple-glass.md](apple-glass.md).
3. Keep text and boundary readable over worst-case content.
4. Add opaque/reduced-transparency fallback.
5. Record any difference from Paper's browser-style effect.

Do not convert `backdrop-filter: blur(...)` into a translucent fill and claim
the blur matches. A GPUI approximation can preserve hierarchy but not sampling.

## Translate assets and icons

Export only actual assets:

- icons and vector illustrations as SVG when the target asset pipeline handles
  them;
- alpha-heavy raster art as PNG;
- photos as appropriately compressed raster;
- multiple scale variants only when the runtime needs them.

Keep:

- Paper node ID;
- export format/scale;
- logical size;
- destination path;
- runtime tint policy;
- license/source notes if relevant.

Do not export:

- text;
- standard controls;
- complete panels/screens;
- shadows or backgrounds that GPUI can render;
- multiple raster copies of a monochrome icon that should be tinted.

Inspect SVG viewBox and optical bounds. A 16×16 icon file can still look
misaligned if its paths have uneven internal whitespace.

## Add state and interaction

A static Paper frame usually shows one state. Define:

- default, hover, pressed, focus-visible;
- selected/checked;
- disabled;
- loading/error;
- keyboard activation;
- tooltip/help;
- overlay open/dismiss;
- scroll and resize;
- reduced-motion/material fallbacks.

Reuse existing product behavior. Ask or state assumptions when Paper has no
evidence for a materially important interaction.

Implement typed actions and stable element IDs. Keep source-anchored
presentations anchored to the invoking control. Restore focus on dismissal.

Do not let a visual translation turn a functioning button into a pointer-only
`div`.

## Handle responsive designs

If Paper provides multiple artboards:

- map each to logical bounds;
- identify what changes: visibility, order, size, density, navigation pattern;
- derive the smallest set of breakpoints;
- preserve shared components/state;
- test between authored widths.

If only one artboard exists:

- match it exactly;
- preserve existing app resize behavior;
- use sensible min/max/flex constraints from evidence;
- report unverified responsive behavior;
- do not invent a separate mobile UI.

Treat long content and localization as resize inputs. A design with one short
sample is not proof of fixed-size safety.

## Implement in fidelity passes

### Pass 1: geometry

- root content bounds;
- major region rectangles;
- layout direction;
- fixed/flexible sizing;
- gaps/padding;
- clipping and scroll.

### Pass 2: typography

- fonts and faces;
- size/line height;
- wrap/truncation;
- baseline.

### Pass 3: paint

- backgrounds;
- borders/radii;
- shadows/material;
- opacity.

### Pass 4: assets

- exact file;
- logical/optical size;
- tint;
- cropping.

### Pass 5: behavior

- states;
- pointer/keyboard/focus;
- loading/error;
- overlay/scroll/resize.

### Pass 6: extraction

Only now consolidate verified repeated values into existing tokens/components.
Do not introduce a parallel design system for one frame.

## Validate the native result

Use [visual-validation.md](visual-validation.md):

1. Build and test the owning crate.
2. Launch the real app.
3. Put it in the same state/content/theme.
4. Match logical viewport and scale.
5. Capture the native content.
6. Compare side-by-side, overlay, and targeted diff.
7. Fix capture, bounds, layout, typography, paint, assets, then polish.
8. Exercise interaction and resize.
9. Record expected native/platform variance.

Completion requires a final Paper screenshot and a final native screenshot at
matching logical bounds for one-to-one work.

## Failure shields

- Paper tools absent: stop extraction and connect Paper Desktop MCP.
- Wrong file open: have the user open it, then call `get_basic_info` again.
- No exact selection: request a selection or node ID.
- Huge tree: split by semantic region; retain a full-root screenshot.
- Missing font: verify, bundle/register only if authorized/licensed, recapture.
- Unsupported effect: implement honest nearest capability and record delta.
- Screenshot mismatch after equal values: inspect crop, scale, font metrics,
  border inclusion, opacity inheritance, clipping, and window activity.
- Existing dirty code: patch only requested files/hunks.
- Paper mutation not requested: remain read-only.

For a fully worked set of GPUI patterns, see
[worked-patterns.md](worked-patterns.md).
