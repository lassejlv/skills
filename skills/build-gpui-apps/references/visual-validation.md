# Visual validation reference

Use this layer to compare a GPUI runtime to Paper, a product baseline, or a
design spec without confusing capture noise with implementation error.

## Contents

- [Define the contract](#define-the-contract)
- [Normalize captures](#normalize-captures)
- [Compare in the right order](#compare-in-the-right-order)
- [Use overlays and diffs](#use-overlays-and-diffs)
- [Diagnose common mismatch patterns](#diagnose-common-mismatch-patterns)
- [Validate states and responsiveness](#validate-states-and-responsiveness)
- [Set acceptance criteria](#set-acceptance-criteria)
- [Evidence record](#evidence-record)

## Define the contract

Record before capture:

- source design/baseline and exact node/version;
- GPUI commit/build profile;
- logical content width and height;
- OS and version;
- display scale;
- app appearance and active-window state;
- font families/weights available;
- deterministic content/state;
- whether window chrome is included;
- expected dynamic/native-material differences.

For Paper, preserve:

- root node ID;
- 2x screenshot;
- logical artboard bounds;
- theme;
- exported assets;
- computed style evidence.

For an existing app regression, record the baseline origin and why a baseline
change is expected.

## Normalize captures

Two screenshots are comparable only when their coordinate systems match.

1. Match logical content bounds.
2. Match scale factor or resample deliberately once.
3. Crop both to the same semantic region.
4. Exclude OS chrome only if excluded from both.
5. Use the same appearance, activation, data, and scroll offset.
6. Ensure fonts finished loading.
7. Wait for intended async state and animations to settle.
8. Keep image color profiles consistent when tooling permits.
9. Do not resize screenshots by eye.

If the design artboard is 1200×800 logical points captured at 2x, compare it to
a 2400×1600-pixel native content capture at a 2x scale, or normalize both to
the same logical pixel grid with a documented resample.

Native glass and font rasterization can vary by OS/display. Compare structure
and perceptual behavior rather than demanding identical noise/blur kernels.

## Compare in the right order

Fix high-leverage mismatches first:

1. **Capture:** crop, scale, chrome, theme, data
2. **Bounds:** window/content/major region rectangles
3. **Layout:** direction, fixed/flexible size, gaps, padding, alignment
4. **Typography:** family, face, size, line height, wrapping, baseline
5. **Paint:** fills, borders, opacity, radius, shadow, material
6. **Assets:** correct icon/image and optical size
7. **Interaction states:** hover, pressed, focus, selected, disabled
8. **Polish:** one-pixel optical corrections

Do not nudge child margins to compensate for a wrong root crop or font.

Use guide lines for:

- outer content edges;
- columns and repeated row baselines;
- toolbar/sidebar boundaries;
- text cap/baseline relationships;
- concentric radii;
- overlay anchors.

## Use overlays and diffs

### Side by side

Best for semantic hierarchy, missing elements, and state differences.

### Alpha overlay

Place one image over the other at roughly 50% opacity. Double edges reveal:

- translation;
- wrong scale;
- width/height drift;
- radius mismatch;
- baseline misalignment.

### Absolute difference

Compute per-channel difference and amplify for inspection. Use a mask to exclude
known nondeterministic regions such as timestamps, caret blink, live avatars, or
native blur noise. Keep masks small and justified.

### Edge comparison

Edges are useful when color/material differs by platform but geometry should
match. They reveal incorrect silhouettes, separators, icons, and text blocks.

Do not reduce acceptance to one global percentage. A tiny missing focus ring can
matter more than a large, harmless native blur difference.

## Diagnose common mismatch patterns

| Pattern | Likely cause |
|---|---|
| Everything uniformly shifted | Crop/chrome/safe inset mismatch |
| Everything uniformly scaled | Logical versus device pixel mismatch |
| Right edge drifts while left aligns | Wrong flexible width or font metrics |
| Rows drift progressively | Gap/line-height/row-height mismatch |
| Text starts right but wraps differently | Family/weight/width/line height |
| Borders appear two pixels | Scale or inside/center border assumption |
| Shadow clipped | Ancestor overflow or capture crop |
| Icons centered geometrically but look off | SVG/viewBox optical bounds |
| Only native glass differs | Dynamic background/material/rendering variation |
| Hover/focus absent | State not triggered or element lacks stable ID/focus |
| High-DPI only mismatch | Asset resolution, pixel snapping, scale conversion |
| Resize breaks after matching one frame | Screenshot dimensions copied instead of constraints |

When exact style values still look wrong, inspect:

- backend font substitution;
- glyph hinting/subpixel behavior;
- implicit line height;
- border inclusion;
- child opacity compositing;
- parent clipping;
- window active state;
- material sampling;
- scale rounding.

## Validate states and responsiveness

Capture a state matrix relevant to the component:

| Dimension | States |
|---|---|
| Appearance | light, dark |
| Window | active, inactive |
| Control | default, hover, pressed, focus, disabled, selected |
| Data | loading, empty, error, typical, long |
| Geometry | minimum, target, wide; 1x/high-DPI |
| Accessibility | reduced motion, opaque/reduced transparency, high contrast |
| Overlay | closed, open, edge repositioned |

For each breakpoint, verify the design intent rather than preserving every pixel
from the desktop artboard. Record which source frame defines each breakpoint.

Use real long strings and localization fixtures. A view matching only short
English mock content is not stable.

For motion, inspect video/frame sequence or interact live. A static endpoint
cannot prove anchoring, velocity continuity, input responsiveness, or reduced
motion.

## Set acceptance criteria

Classify differences:

- **Blocker:** wrong hierarchy, unusable control, clipped content, incorrect
  asset, inaccessible interaction, unsupported material claim.
- **Major:** visible geometry/type mismatch, broken resize, wrong state.
- **Minor:** small optical spacing/radius/shadow difference.
- **Expected platform variance:** font antialiasing, native blur grain, system
  control rendering with the same semantic role.

For one-to-one design work, completion requires:

- matching major geometry;
- correct fonts/assets;
- states implemented;
- runtime launch;
- final captures;
- no unexplained blocker/major differences;
- remaining minor/platform deltas listed.

If numeric image metrics are used, pair them with regional inspection and
semantic assertions. Save the command/tool version used to produce the metric.

## Evidence record

Keep a compact table:

| Capture | Source | Logical bounds | Scale | State | Result | Notes |
|---|---|---:|---:|---|---|---|
| baseline | Paper node `abc` | 1200×800 | 2x | dark/default | reference | exact frame |
| native-01 | GPUI commit | 1200×800 | 2x | dark/default | major delta | sidebar +6 px |
| native-final | GPUI commit | 1200×800 | 2x | dark/default | pass | native blur variance |

Store only durable, useful evidence according to repository policy. Avoid
committing huge transient diffs or screenshots containing private data.
