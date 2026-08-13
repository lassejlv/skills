# Apple glass and material reference

Use this layer for Apple-polished hierarchy, macOS translucency, Liquid Glass,
window blur, and cross-platform material fallbacks. The goal is functional
depth and clarity, not a glossy effect pasted onto every rectangle.

## Contents

- [Start with hierarchy](#start-with-hierarchy)
- [Choose an honest capability tier](#choose-an-honest-capability-tier)
- [Use native Liquid Glass](#use-native-liquid-glass)
- [Use legacy or whole-window translucency](#use-legacy-or-whole-window-translucency)
- [Build a GPUI approximation](#build-a-gpui-approximation)
- [Shape and layer materials](#shape-and-layer-materials)
- [Handle appearance and accessibility](#handle-appearance-and-accessibility)
- [Build a narrow AppKit bridge](#build-a-narrow-appkit-bridge)
- [Validate materials](#validate-materials)
- [Anti-patterns](#anti-patterns)

## Start with hierarchy

Apple's current design guidance treats glass as a functional layer for controls
and navigation above content. Apply this order:

1. Establish content hierarchy and layout.
2. Decide what belongs to the content layer.
3. Identify the few controls or navigation surfaces that float above it.
4. Select native material or fallback capability.
5. Add restrained motion and depth cues.
6. Verify legibility in real content, both appearances, inactive windows, and
   accessibility modes.

Keep document, editor, list, form, and media content mostly solid or quietly
tinted. Appropriate glass candidates include:

- titlebar-adjacent controls;
- compact toolbars;
- source-anchored inspectors or popovers;
- navigation rails;
- floating control clusters;
- a transient search/command surface.

Glass is a poor default for dense text, large data tables, stacked cards,
background decoration, or every nested panel.

## Choose an honest capability tier

Select the highest tier the target can really support:

| Tier | Capability | Use |
|---|---|---|
| 1 | Existing project/system component | First choice; preserves integration and tested behavior |
| 2 | macOS 26+ `NSGlassEffectView` | True native Liquid Glass for a bounded control/navigation surface |
| 3 | `NSVisualEffectView` | Older macOS vibrancy/translucency with explicit blending semantics |
| 4 | GPUI `WindowBackgroundAppearance::Blurred` | Whole-window blur where supported by the backend |
| 5 | Pure GPUI material approximation | Cross-platform tint, border, highlight, shadow, and opacity |
| 6 | Opaque surface | Accessibility, unsupported backend, inactive, or performance fallback |

Current GPUI 0.2.2 has a whole-window blurred appearance but no public,
arbitrary per-element backdrop-filter API. Do not claim a GPUI panel is blurring
the content behind it unless a native bridge or target-specific renderer
actually does that.

In the pinned snapshot, any non-opaque window background also disables GPUI's
subpixel text-rendering path. Keep an opaque window for an isolated Tier 5
toolbar/panel unless the whole-window material is intentional and the text
tradeoff has been inspected.

Windows Mica variants in `WindowBackgroundAppearance` are Windows backdrop
capabilities, not portable Apple glass. Keep platform naming honest.

## Use native Liquid Glass

Apple introduced `NSGlassEffectView` and `NSGlassEffectContainerView` for macOS
26. The SDK exposes a content view plus material controls including style,
corner radius, and tint. The container can coordinate nearby effects and their
spacing.

Use native Liquid Glass when all are true:

- macOS 26 is available at runtime;
- the target can safely host/manage an AppKit view relative to GPUI content;
- the surface is a control or navigation layer;
- its bounds and lifetime can track the GPUI element/window;
- accessibility preferences and opaque fallback are wired;
- other platforms have a deliberate fallback.

Choose style:

- **Regular:** default for most floating controls; stronger legibility.
- **Clear:** only over visually rich content when the composition stays
  legible. Add dimming or a stronger fallback when content makes it noisy.

Use tint to communicate semantic grouping or accent, not to color every
surface. Avoid tint values that make text contrast depend on the background
image.

Use `NSGlassEffectContainerView` for multiple nearby glass shapes that should
behave as a coordinated group. Its spacing is part of visual merging behavior,
not a substitute for GPUI layout gap. Keep related controls close enough to read
as one cluster; separate unrelated actions.

Do not rely on beta-only AppKit properties without checking the installed SDK,
deployment target, and current Apple documentation. This suite intentionally
does not require experimental interactive-effect APIs.

## Use legacy or whole-window translucency

### NSVisualEffectView

Use `NSVisualEffectView` when supporting older macOS versions or when its
vibrancy model matches the product. Decide:

- material;
- blending mode;
- emphasized/active state;
- behind-window versus within-window sampling;
- opaque fallback.

`behindWindow` samples content outside/behind the app window and is appropriate
for window backgrounds. `withinWindow` blends with content from the same window
and fits bounded in-window composition. Test inactive windows; vibrancy can
change when key status changes.

Do not market this fallback as Liquid Glass. It is native macOS translucency
with different behavior.

### GPUI whole-window blur

Use `WindowBackgroundAppearance::Blurred` only when the intended material is the
window background and the current backend supports it. The enum documentation
explicitly notes that blur is not always supported.

Whole-window blur requires:

- a transparent/semitransparent GPUI root where the effect should show;
- legible opaque/tinted content surfaces above it;
- backend/runtime verification;
- a solid fallback when unsupported.

Do not use whole-window blur to pretend individual cards have independent
backdrop filtering.

Whole-window blur is also not a harmless cosmetic toggle: recheck text
rendering because the pinned `Window::should_use_subpixel_rendering` rejects
non-opaque window backgrounds.

## Build a GPUI approximation

When native per-element material is unavailable, build a coherent visual
approximation from semantic tokens:

- translucent surface tint;
- subtle light-facing inner/highlight border;
- low-alpha outer border;
- restrained ambient and key shadow;
- content-aware opacity chosen per appearance;
- optional gradient that implies illumination;
- clear opaque fallback.

Example token model:

```rust
struct MaterialTokens {
    fill: Hsla,
    border: Hsla,
    highlight: Hsla,
    shadow: Hsla,
    text: Hsla,
    text_secondary: Hsla,
    focus_ring: Hsla,
}
```

Keep the component API semantic:

```rust
enum MaterialRole {
    Toolbar,
    FloatingControl,
    Popover,
    NavigationRail,
}
```

Derive tokens from role, appearance, active-window state, and accessibility
preferences. Never let callers improvise five unrelated alpha values.

An approximation should be described as “translucent material” or
“Apple-inspired surface,” not native blur.

## Shape and layer materials

### Concentric geometry

Nested rounded surfaces should have related radii. A practical starting rule:

```text
inner_radius = max(0, outer_radius - inset)
```

Then correct optically for border thickness, visual weight, and asymmetric
insets. Concentricity matters more than applying the same radius everywhere.

Use:

- rounded rectangles for dense desktop controls;
- capsules for standout actions, segmented clusters, and compact floating
  controls;
- circles for icon-only controls when the symbol and hit target fit;
- consistent silhouette across hover/pressed state.

### Layering

Keep a simple depth order:

1. canvas/content;
2. solid/elevated content surface;
3. glass navigation/control layer;
4. temporary menu/dialog/tooltip;
5. focus and system feedback.

Avoid glass-on-glass. Nested transparent layers compound contrast, blur, and
GPU cost while making ownership unclear.

Use shadows to establish elevation, not as a glow. Keep dark-mode shadows
subtle and rely more on border/highlight separation. In light mode, avoid gray
mud from excessive ambient shadow.

Use scroll-edge effects or an explicit separator when content moves behind a
toolbar. The boundary should respond to scroll state rather than being a
permanent decorative line when the content is at rest.

## Handle appearance and accessibility

Materials must adapt to:

- light and dark appearance;
- active and inactive window;
- reduced transparency;
- increased contrast;
- differentiate without color;
- reduced motion;
- display scale and HDR/content brightness where relevant.

For reduced transparency, swap native/translucent material for an opaque
surface that preserves hierarchy. Do not merely increase alpha from 0.55 to
0.65 and hope contrast passes.

For increased contrast:

- strengthen border and text separation;
- avoid meaning encoded only in slight tint changes;
- preserve focus ring visibility;
- remove background-dependent text color.

For differentiate without color, add shape, icon, label, stroke, or state text
to selected/error/success states.

Reduced motion applies to material transitions too. Snap or crossfade simply
instead of morphing multiple glass shapes.

## Build a narrow AppKit bridge

Native glass is a platform integration, not a Rust styling helper. Keep it
behind a capability interface and a macOS module.

The bridge must own:

- runtime `@available(macOS 26.0, *)` checking in Objective-C/Swift or the
  equivalent guarded Rust/ObjC call path;
- creation and main-thread destruction of native views;
- containment relative to the GPUI rendering view;
- logical-to-backing coordinate conversion;
- window resize, scale, visibility, occlusion, and z-order updates;
- input policy so the native layer does not steal GPUI events unexpectedly;
- accessibility ownership without duplicate semantics;
- fallback selection;
- cleanup when the entity/window closes.

Prefer a target-provided native-view hook. If GPUI does not expose safe subview
hosting at the pinned revision, adding it is platform/framework work and should
be scoped and tested separately. Do not reach into unstable private window
internals from every component.

A good shared API describes capability:

```rust
trait MaterialHost {
    fn set_surface(&mut self, id: SurfaceId, bounds: Bounds<Pixels>, role: MaterialRole);
    fn remove_surface(&mut self, id: SurfaceId);
    fn capabilities(&self) -> MaterialCapabilities;
}
```

The exact implementation may live in the platform crate; GPUI view code should
not name AppKit classes.

## Validate materials

Capture the running app with real content:

- light and dark;
- active and inactive window;
- plain and visually busy background;
- reduced transparency;
- increased contrast;
- 1x and high-DPI display;
- resized and scrolled states;
- macOS 26 native path and oldest supported macOS fallback;
- non-macOS opaque/approximation path.

Inspect:

- text/icon contrast over worst-case content;
- boundary separation;
- child/parent radii;
- shadow clipping;
- native view alignment while moving/resizing;
- frame pacing during scroll/resize;
- click, hover, focus, and accessibility hit targets;
- cleanup after closing/reopening the window.

## Anti-patterns

- Calling any alpha fill “Liquid Glass”
- Glass as a full-content background behind long text
- Glass stacked inside glass
- Every control independently tinted
- Clear glass over uncontrolled busy imagery
- Blur used to hide weak spacing or hierarchy
- Native views added without availability or lifetime cleanup
- A macOS-only material silently breaking Linux/Windows builds
- Reduced transparency implemented as a tiny alpha adjustment
- Shadows/radii copied from iPhone onto dense desktop controls
- Visual screenshots accepted without interaction and resize checks

See [sources.md](sources.md) for Apple and GPUI primary sources.
