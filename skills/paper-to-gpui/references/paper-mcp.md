# Paper MCP extraction reference

Use this reference to obtain a complete, reproducible design contract from the
currently open Paper Desktop file. Tool schemas can evolve; inspect the exposed
MCP schema instead of guessing arguments.

## Contents

- [Connection and scope](#connection-and-scope)
- [Read-only extraction sequence](#read-only-extraction-sequence)
- [Tool selection](#tool-selection)
- [Evidence by node type](#evidence-by-node-type)
- [Tokens and themes](#tokens-and-themes)
- [Fonts](#fonts)
- [Assets](#assets)
- [Large designs](#large-designs)
- [Evidence record](#evidence-record)
- [Troubleshooting](#troubleshooting)
- [Primary sources](#primary-sources)

## Connection and scope

Paper Desktop starts its local MCP server when a file is open. The documented
Streamable HTTP endpoint is:

```text
http://127.0.0.1:29979/mcp
```

For Codex, prefer the official `paper-desktop` plugin when available. Manual
configuration is also supported in Codex under Settings → MCP Servers using the
endpoint above.

Before inspecting a design:

1. Confirm Paper Desktop is running.
2. Confirm the intended file is open and visible.
3. Confirm the `paper` MCP tools are exposed in the current agent session.
4. Call `get_basic_info`; quote the file and page names back to the user when
   ambiguity matters.
5. Call `get_selection`; resolve one selected artboard/frame or an exact node ID.

The server operates on the currently open file. A valid connection does not
prove that the correct document is open.

### Permissions

Classify calls before making them:

- **Read-only:** `get_basic_info`, `get_selection`, `get_node_info`,
  `get_children`, `get_tree_summary`, `get_screenshot`, `get_jsx`,
  `get_computed_styles`, `get_fill_image`, `get_font_family_info`, `get_guide`.
- **Local export:** `export` writes visual assets to a requested destination but
  does not redesign the Paper document.
- **Paper mutation:** `create_artboard`, `write_html`, `set_text_content`,
  `rename_nodes`, `duplicate_nodes`, `move_nodes`, `update_styles`,
  `delete_nodes`.

For design-to-code work, stay read-only in Paper unless the user explicitly asks
to change the design. Never use write tools merely to simplify extraction.

## Read-only extraction sequence

### Pass 1: establish the target

Call:

1. `get_basic_info`
2. `get_selection`
3. `get_node_info` for the selected root

Capture:

- File and page name
- Root node ID, name, type, width, and height
- Artboard association
- Visibility and lock state
- Parent and direct child count

If multiple selected nodes represent explicit breakpoints of the same view,
record each artboard separately and name the intended viewport for each. If they
are unrelated, ask the user to narrow the selection.

### Pass 2: capture the visual contract

Call `get_screenshot` for the root at 2x when supported. Keep this image
unaltered as the baseline.

Use 1x only for quick overview calls. Use 2x for typography, one-pixel borders,
small icons, and final comparison.

Record:

- Screenshot pixel dimensions
- Root logical width and height
- Requested capture scale
- Theme/mode represented by the artboard
- Any content that is intentionally clipped or outside the artboard

### Pass 3: capture hierarchy

Call `get_tree_summary` with enough depth to reveal the major regions. Use
`get_children` on structural containers when:

- sibling order affects layout;
- repeated rows or cards are collapsed in the summary;
- a node's child count suggests hidden detail;
- a large tree response was truncated.

Call `get_node_info` for structurally important descendants and any node whose
role is unclear.

Do not reproduce meaningless wrapper depth one-for-one. Preserve wrappers that
encode layout, clipping, stacking, scroll, hit area, or component boundaries.

### Pass 4: capture structure and computed styles

Call `get_jsx` on the smallest useful root. Request inline styles when that makes
computed values easier to trace; use Tailwind output only as a compact layout
hint.

Then call `get_computed_styles` in batches for:

- root and major layout containers;
- all text styles;
- interactive controls and their visible states;
- dividers and one-pixel geometry;
- nodes with radius, shadow, opacity, gradient, blur, transform, or clipping;
- repeated primitives, sampling one instance per visual variant.

Prefer computed values over class names. JSX can omit inherited values, flatten
design semantics, or make flexible layout look more deterministic than it is.

### Pass 5: fonts and assets

Call `get_font_family_info` for every non-system family and each required
weight/style. Capture availability before writing GPUI typography.

For asset nodes:

- Use `get_fill_image` to inspect an image fill.
- Use `export` for files that must enter the codebase.
- Prefer SVG for icons and flat vector artwork.
- Prefer PNG for alpha-heavy raster artwork and screenshots.
- Prefer JPG only for opaque photographic content where compression is wanted.
- Export raster assets at a scale sufficient for the target's highest expected
  device scale, normally 2x or higher.

Keep a node-ID-to-output-path map.

## Tool selection

| Tool | Use it for | Avoid using it as |
|---|---|---|
| `get_basic_info` | Verify document/page and list artboards | Detailed design extraction |
| `get_selection` | Resolve user intent and target IDs | Proof of descendant styling |
| `get_node_info` | Inspect one node's identity, bounds, text, parent, children | Full subtree traversal |
| `get_children` | Preserve direct order and inspect a container | Unbounded whole-file crawling |
| `get_tree_summary` | Understand hierarchy compactly | Source of exact styles |
| `get_screenshot` | Visual truth and comparison baseline | Only implementation input |
| `get_jsx` | Structural and CSS-like translation hint | Code to paste into Rust |
| `get_computed_styles` | Exact resolved layout/paint/type values | Semantic component model |
| `get_fill_image` | Retrieve image-fill data | Generic vector export |
| `get_font_family_info` | Verify fonts, weights, and styles | Proof the GPUI app bundles the font |
| `get_guide` | Load Paper-authored guided workflows | Replacement for direct evidence |
| `export` | Produce source assets | Screenshotting native controls or text |

## Evidence by node type

### Artboard or major frame

Capture:

- width, height, background;
- layout mode and primary/cross-axis alignment;
- padding and gap;
- clipping and scroll intent;
- fixed versus flexible children;
- titlebar or safe-area assumptions;
- breakpoint role.

### Text

Capture:

- exact content;
- font family and fallbacks;
- weight, style, size, line height, and letter spacing;
- text color and opacity;
- text alignment;
- fixed width, wrapping, number of lines, and truncation;
- transform such as uppercase;
- baseline relation to adjacent icons or controls.

Text mismatch often changes layout. Treat text metrics as geometry, not polish.

### Interactive control

Capture:

- visible bounds and intended hit area;
- padding and icon/text gap;
- fill, border, radius, shadow, and opacity;
- default, hover, active/pressed, focus, selected, and disabled variants;
- cursor and keyboard behavior inferred from role;
- label/icon alignment;
- tooltip or popover if shown elsewhere in the design.

Ask for missing states when they materially affect implementation. Do not invent
complex behavior from a static frame.

### Icon or illustration

Capture:

- logical size and bounding box;
- fill/stroke colors and opacity;
- stroke width and line caps if relevant;
- whether the icon is monochrome and should be tinted at runtime;
- export format and viewBox;
- optical alignment inside its container.

### Image fill

Capture:

- source aspect ratio;
- crop/fill/fit behavior;
- focal point or positioning;
- corner clipping;
- opacity, blend/effect, and overlay;
- required export resolution.

### Overlay, popover, or modal

Capture:

- anchor and stacking relationship;
- scrim opacity;
- offset from anchor;
- preferred width and maximum height;
- edge avoidance expected near window bounds;
- focus ownership and dismissal behavior.

## Tokens and themes

Paper currently supports MCP-created tokens for:

- color;
- font family;
- font weight;
- font size;
- line height;
- letter spacing;
- spacing;
- container;
- breakpoint;
- radius.

When the design uses repeated values:

1. Record the token name if the MCP response exposes it.
2. Record the resolved value because GPUI needs an actual runtime value.
3. Search the GPUI checkout for an equivalent project token.
4. Reuse a matching semantic token.
5. Add a narrowly named project token only when repetition and semantics justify
   it.

Do not generate a second set of tokens whose names mirror Paper mechanically if
the application already has a theme API. Preserve semantics such as
`surface_muted`, `text_secondary`, or `control_radius`.

Paper's theme roadmap can change. Always inspect the current design and MCP
schema before assuming mode or theme-class behavior.

## Fonts

Font availability must be proven twice:

1. Paper reports the intended family/weight/style.
2. The GPUI runtime resolves and renders that family/weight/style.

If Paper uses a system font, map it to the app's established platform font
policy. If it uses a bundled font:

- locate existing font files and registration code first;
- preserve license and attribution requirements;
- add only the formats the GPUI app can load;
- verify weight names against the actual font metadata;
- test glyph coverage for real content;
- recapture after registration.

Never compensate for a wrong font by distorting padding and width values.

## Assets

Use stable, descriptive file names in the target repo. Avoid Paper node IDs as
public filenames unless the project already uses generated IDs.

Recommended manifest during implementation:

| Paper node ID | Paper name | Export format | Scale | Target path | GPUI usage |
|---|---|---|---|---|---|

After export:

- inspect SVG viewBox and hardcoded fills;
- remove unnecessary canvas-sized whitespace only when that preserves intent;
- verify PNG dimensions and alpha;
- avoid duplicates already in the app;
- use the checkout's existing asset embedding/loading mechanism;
- render at the Paper logical size, not the export's raw pixel dimensions.

## Large designs

Paper's own guidance recommends breaking large, deeply nested work into smaller
parts. Use this sequence:

1. Capture one full-root screenshot and tree summary.
2. Identify 3–7 structural regions.
3. Extract and implement one region at a time.
4. Keep shared tokens and primitives in a central list.
5. Compare each region locally.
6. Reassemble and compare the full screen for cumulative drift.

Batch computed-style calls. Do not request styles for every repeated child when
one representative instance and its variants are sufficient.

## Evidence record

Keep this compact record in notes or the implementation report:

```text
Paper file:
Page:
Root node:
Logical viewport:
Capture scale:
Theme/state:

Regions:
- <id> <name>: <bounds> <layout summary>

Typography:
- <role>: <family> <weight> <size>/<line-height> <color> <wrap width>

Tokens:
- <Paper token/resolved value> -> <GPUI token or constant>

Assets:
- <node id> -> <repo path> at <logical size>

Unknowns:
- <property or behavior requiring re-query/user input>
```

## Troubleshooting

### No Paper tools in the session

- Verify the Paper Desktop app is open with a file loaded.
- Verify the official plugin or local MCP endpoint is configured.
- Restart the agent session so it discovers the server again.
- Restart Paper Desktop if the endpoint remains stale.

### Correct server, wrong design

Call `get_basic_info`. Paper acts on the currently open file. Have the user open
the intended file, then call it again.

### Tool parameter errors

Read the live MCP tool schema. Do not reuse remembered arguments. Long sessions
can hold stale tool definitions; restart the agent session when repeated valid
calls fail.

### Missing or truncated subtree

Use `get_children` and recurse through smaller structural regions. Keep depth
bounded and batch style requests.

### JSX conflicts with screenshot

Trust the screenshot for visible result and computed styles for resolved values.
Use node hierarchy to determine why JSX was misleading.

### Changes not appearing

For read-only work, this usually indicates the wrong file or node. For explicitly
authorized design mutations, verify returned node IDs and call
`finish_working_on_nodes` when the live tool workflow requires clearing working
indicators.

## Primary sources

Research checked 2026-07-29:

- Paper MCP documentation: https://paper.design/docs/mcp
- Paper tokens documentation: https://paper.design/docs/tokens
- Paper support and MCP troubleshooting: https://paper.design/docs/support
