# Examples and anti-patterns

## Example 1: An authenticated dashboard in the in-app browser

**Request:** “Explore this dashboard and make its components, animations, colors, sizes, and fonts into a Paper UI kit.”

**Good execution:**

1. Select the referenced tab using the browser's documented workflow. Inspect home, settings, a table page, the account menu, dropdowns and a safe confirmation dialog.
2. Capture actual styles and states. Suppose the inspected source has a `#121212` shell, `#212121` canvas, 32 px fields and 150 ms control transitions: record those as this source's measurements, not universal defaults.
3. Check the actual source font and Paper's available fonts before building. If a substitute is needed, use one consistent family and label it.
4. Build editable foundations, controls, forms, overlays, data and icon boards. Bind repeated values to semantic tokens. Include the open account menu and the disabled confirmation button, using synthetic names.
5. Add a motion guide inside Paper with measured values and observed descriptions. Check every board visually and deliver the file link with coverage notes.

**Poor execution:** Copy the homepage into one large image, draw a few generic buttons, use an arbitrary font silently, and call it a complete design system.

## Example 2: “Copy all their icons as SVG”

**Good execution:** Inspect the agreed pages and open menus, extract original inline SVGs or accessible sprite symbols, deduplicate path content, and keep named variants. Save individual files and a manifest, import vectors into a labeled Paper grid, then inspect each rendering. Say “61 distinct icons from the inspected screens” if that is the verified count.

**Poor execution:** Replace source icons with emoji or a familiar icon library, count the same chevron twelve times, export screenshots with an `.svg` extension, or claim every icon on the website was collected after checking one page.

An example manifest entry (illustrative values):

```json
{
  "name": "copy",
  "file": "copy.svg",
  "sourceRoute": "/settings/example",
  "sourceState": "row action visible",
  "viewBox": "0 0 24 24",
  "evidence": "extracted original SVG"
}
```

## Example 3: Explain how the motion feels

**Request:** “Explain the animations in the UI kit.”

Add an annotated state pair and a short specification:

| Field | Example evidence |
| --- | --- |
| Trigger | Hover or keyboard focus on the card |
| Change | Action layer opacity 0 → 1, scale .98 → 1 |
| Timing | 150 ms, measured from the relevant CSS rule |
| Easing | Record the measured value; do not assume it |
| Appearance | Quick fade with a subtle expansion |
| Verification | Endpoint states observed; intermediate frames not captured |
| Representation | Static Paper specimens, not playable animation |

These numbers illustrate a possible inspection; remeasure the actual site. A declared transition does not prove it fired during the observed interaction.

**Do:** Explain what moves, when it moves, and what the viewer notices.

**Don't:** Say “the animation feels perfectly matched” from static screenshots, or add a bouncy spring to a source that only fades.

## Example 4: Paper is unavailable

**Request:** “Turn this site into a UI kit.”

**Good execution:** Discover that no usable Paper connection is available, state “Paper is unavailable here, so I’m creating a local HTML/CSS kit,” and continue. Create `index.html`, `styles.css`, original assets and evidence notes. Include navigation to foundations, controls, forms, overlays, icons and motion as relevant. Open it with an available browser and test the rendered kit at desktop and mobile sizes.

**Poor execution:** Stop with instructions for the user to install Paper, deliver only a Markdown palette, or scaffold a full application with a database for a static component reference.

## Example 5: An unseen error state

**Situation:** A settings field is visible, but inspecting its server error would require changing real account data.

**Do:** Capture the observed field. If a companion error specimen is useful, label it “Reconstructed error state; not observed on the source.” Keep the destructive flow at the safely inspectable confirmation screen and cancel.

**Don't:** Submit a real setting change to force an error, or describe an invented red alert as an extracted source component.

## Lightweight evidence template

Use this structure in the kit's coverage notes or a companion file. Keep private account values out.

| Family | Source route / state | Captured variants | Evidence | Gap |
| --- | --- | --- | --- | --- |
| Button | Settings / confirmation open | Default, disabled | Measured CSS + screenshot | Loading unseen |
| Dropdown | Header / account menu open | Selected, hover | Observed + measured | Mobile uninspected |
| Alert | No source example found | Error companion | Reconstructed | Source appearance unknown |

For each important component record: name, dimensions, token references, typography, states, behavior, source route and confidence. Do not turn every minor property into a paragraph; tables and compact annotations are easier to reuse.

## Do and don't summary

| Do | Don't |
| --- | --- |
| Use the agent's available browser and design tools | Assume a specific browser automation API exists |
| Inspect menus, settings and interaction states | Treat the first viewport as the entire component set |
| Preserve measured geometry and source character | Redesign the site with generic preferred defaults |
| Check font support and label substitutions | Mix fallback fonts across boards without explanation |
| Import original self-contained SVGs | Replace real icons with Unicode symbols |
| Use semantic tokens and editable specimens | Deliver flattened screenshots as the kit |
| Label estimates and reconstructed companions | Present invented states as observed behavior |
| Explain motion inside the deliverable | Leave important motion notes only in chat |
| Review every board and icon rendering | Infer visual quality from successful tool calls |
| Report inspected coverage and remaining gaps | Promise “all components” without a coverage inventory |
