# Native fidelity validation

Use this reference to compare a Paper artboard with a real GPUI window. Build and
unit-test success do not prove visual fidelity.

## Contents

- [Define the comparison](#define-the-comparison)
- [Capture both sides](#capture-both-sides)
- [Comparison methods](#comparison-methods)
- [Mismatch diagnosis](#mismatch-diagnosis)
- [Tolerance](#tolerance)
- [Behavioral acceptance](#behavioral-acceptance)
- [Responsive acceptance](#responsive-acceptance)
- [Final report](#final-report)

## Define the comparison

Write down these values before comparing:

```text
Paper root node:
Paper logical width x height:
Paper screenshot scale:
GPUI content width x height:
OS display scale:
Window chrome included: yes/no
Theme:
Content/state:
Font families and weights:
```

The images are not comparable until their logical content bounds represent the
same rectangle.

### Content bounds versus window bounds

Paper artboards usually represent content, while native screenshots can include:

- titlebar;
- traffic lights or system caption buttons;
- borders and shadows;
- transparent window margins;
- menu bar;
- screen background.

Either:

- set the GPUI content region to the artboard's logical size and crop exactly to
  content; or
- make the Paper frame include the intended native chrome.

Never “fix” a constant vertical offset in inner layout before checking titlebar
ownership.

## Capture both sides

### Paper baseline

Use `get_screenshot` at 2x for the exact root node. Preserve the original.

Name it clearly:

```text
paper-<screen>-<width>x<height>-2x.png
```

Record the MCP-reported logical and pixel dimensions. Do not crop, resize, or
color-correct the baseline.

### GPUI baseline

Launch the real target binary using its normal development path. Set:

- the same logical content dimensions;
- the same light/dark theme;
- the same data and selection state;
- the same scroll position;
- the same overlay/modal state;
- the same font availability.

Capture the window with the platform's normal screenshot facility or an existing
repository capture tool. Crop only to the agreed content/window bounds. Do not
rescale after capture to make dimensions line up.

Name it:

```text
gpui-<screen>-<width>x<height>-<scale>.png
```

If the repository already has screenshot/golden tests, reuse them only after
confirming they render with the real font and platform backend.

### Stabilize dynamic content

Before capture:

- stop caret blinking when practical;
- wait for fonts and images;
- freeze time-dependent labels;
- wait for animation to settle;
- use deterministic fixture data;
- hide debug overlays unless they are part of the target;
- keep mouse hover state intentional.

Document any region that cannot be stabilized.

## Comparison methods

Use more than one method.

### Side by side

Best for:

- hierarchy;
- visual balance;
- missing elements;
- wrong assets;
- general typography.

Inspect at 100% zoom and fit-to-screen. 100% reveals one-pixel geometry; fit view
reveals balance.

### Alpha overlay

Place one capture over the other at roughly 50% opacity. This exposes:

- translated edges;
- wrong panel widths;
- baseline shifts;
- icon misalignment;
- radius mismatch;
- line-wrap changes.

Use an image editor or ImageMagick when available:

```sh
magick paper.png gpui.png -compose blend -define compose:args=50,50 -composite overlay.png
```

Both inputs must already have identical pixel dimensions. Do not let the command
implicitly resize.

### Difference image

When ImageMagick is available:

```sh
magick compare -metric AE paper.png gpui.png diff.png
```

Or:

```sh
magick paper.png gpui.png -compose difference -composite diff.png
```

Interpret the result carefully:

- text antialiasing can create noisy halos;
- native shadows can vary slightly by backend;
- color profiles can cause low-level differences;
- large solid regions make raw percentages look better than important small
  controls actually are.

A low aggregate error does not excuse a visibly wrong toolbar.

### Measurement spot checks

For high-value geometry, record:

- root content bounds;
- major panel boundaries;
- toolbar height;
- sidebar width;
- primary padding/gaps;
- control height;
- icon box and optical center;
- text baseline and wrap width;
- modal bounds.

Use Paper computed styles and GPUI debug/inspector bounds when available. GPUI
elements provide debug styling and current versions expose debug-selector support
for visual tests; follow the pinned checkout's approach.

## Mismatch diagnosis

Fix in this order. Later categories often resolve when earlier geometry is fixed.

### 1. Global bounds

Symptoms:

- everything is uniformly offset;
- all dimensions scale together;
- bottom/right content is clipped;
- large background regions do not align.

Check:

- content versus window bounds;
- titlebar/safe inset;
- logical versus device pixels;
- OS display scale;
- capture crop;
- root padding;
- min/max window size.

### 2. Structural layout

Symptoms:

- cumulative drift down a list;
- wrong column widths;
- unexpected empty space;
- controls spread or compress.

Check:

- fixed versus flexible children;
- parent flex direction;
- gap versus child margins;
- padding included twice;
- `flex_shrink` on fixed controls;
- wrapping;
- scrollbars taking layout space;
- hidden nodes still occupying space.

### 3. Typography

Symptoms:

- many unrelated widths are slightly wrong;
- labels wrap early;
- row heights drift;
- icons appear vertically wrong beside text.

Check:

- actual resolved font;
- requested weight mapped to a real face;
- font size;
- explicit line height;
- wrap width;
- fallback glyphs;
- uppercase transform;
- letter spacing support;
- baseline alignment.

Do not adjust every row's padding before fixing the font.

### 4. Paint

Symptoms:

- geometry matches but the screen feels heavier/lighter;
- borders glow in the diff;
- cards look too raised;
- rounded images leak square corners.

Check:

- alpha channel;
- theme color resolution;
- border placement and width;
- radius plus clipping;
- shadow offset/blur/spread;
- opacity inheritance;
- gradient direction and stops.

### 5. Assets

Symptoms:

- icon looks blurry or too heavy;
- illustration is cropped differently;
- transparent padding shifts optical alignment.

Check:

- SVG viewBox;
- raster logical size versus pixel size;
- fill/fit/crop;
- tint or hardcoded SVG fill;
- duplicate padding inside the file;
- transform and rotation;
- device-scale choice.

### 6. State

Symptoms:

- correct static screenshot but wrong app experience.

Check:

- hover/pressed/focus/selected/disabled;
- keyboard focus order;
- scroll and clipping;
- resize;
- modal anchoring and dismissal;
- loading/empty/error content;
- theme change.

## Tolerance

Agree on the quality bar. Suggested design-to-native targets:

- major regions and control bounds: exact or within 1 logical px;
- repeated gaps/padding: exact; never allow cumulative drift;
- one-pixel borders/separators: visually aligned at target scale;
- icon logical bounds: exact; allow optical centering adjustments;
- typography: same family/face, line breaks, baseline, and line height;
- colors: exact token/resolved value unless native material deliberately differs;
- shadows: visually equivalent when platform rasterization prevents exact pixels;
- text antialiasing: allow platform-level subpixel differences only after metrics
  match.

For a user request to “match closely,” do not settle for merely similar
composition. The implementation should survive overlay inspection.

## Behavioral acceptance

Exercise only behavior relevant to the target, but do it in the native app:

- hover every interactive control;
- press/click primary controls;
- tab through focusable controls;
- trigger expected keyboard actions;
- test selected and disabled states;
- scroll each scroll region to both ends;
- resize to minimum and normal sizes;
- open/close overlays and modals;
- switch theme when supported;
- confirm text remains selectable/editable where intended.

Verify hit areas independently of visible bounds. Paper may show a 16px icon
inside a 28–32px button.

## Responsive acceptance

For multiple Paper artboards:

1. Capture each artboard separately.
2. Run the GPUI app at each exact width.
3. Compare each breakpoint.
4. Test a width halfway between adjacent artboards.
5. Test just below and above every layout switch.
6. Confirm no transient overlap, clipping, or unreadable truncation.

Desktop resize behavior can use:

- fluid flex growth;
- fixed sidebars plus flexible content;
- min/max constrained panels;
- explicit compact layout branches;
- hiding secondary controls;
- scroll rather than destructive compression.

Choose based on Paper evidence and existing product behavior.

## Final report

Report with evidence:

```text
Paper:
- file/page/root node
- logical viewport and capture scale

GPUI:
- owning crate/view
- runtime and OS scale

Verified:
- fmt/check/test/clippy
- native launch
- matching-state screenshot
- overlay/diff
- interaction/resize states

Remaining:
- exact visual deltas
- unavailable font/effect/API
- untested platform or state
```

Do not call “build passes” visual acceptance.
