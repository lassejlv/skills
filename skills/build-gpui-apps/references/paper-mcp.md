# Paper Desktop MCP reference

Use this layer to connect to the currently open Paper.design file and extract a
reproducible design evidence pack. Inspect the live MCP schemas because tool
arguments can evolve.

## Contents

- [Connect safely](#connect-safely)
- [Confirm scope](#confirm-scope)
- [Extract in passes](#extract-in-passes)
- [Choose tools](#choose-tools)
- [Capture tokens, type, and effects](#capture-tokens-type-and-effects)
- [Export assets](#export-assets)
- [Handle large designs](#handle-large-designs)
- [Record evidence](#record-evidence)
- [Permission boundary](#permission-boundary)
- [Troubleshoot](#troubleshoot)

## Connect safely

Paper Desktop documents a local Streamable HTTP MCP endpoint:

```text
http://127.0.0.1:29979/mcp
```

The target file must be open in Paper Desktop. A successful endpoint connection
does not prove the right document is active.

Before calls:

1. Confirm Paper Desktop is running.
2. Confirm the intended file/tab is open.
3. Confirm `paper` MCP tools exist in the current session.
4. Inspect current tool schemas instead of inventing arguments.
5. Stay read-only unless the user explicitly asked to edit Paper.

If a Paper plugin is unavailable, manual MCP configuration can use the endpoint
above. Do not install or modify global configuration unless authorized.

## Confirm scope

Call in order:

1. `get_basic_info`
2. `get_selection`
3. `get_node_info` for the selected root

Record:

- file and page name;
- artboard/frame/component name and ID;
- node type;
- logical width/height;
- parent/artboard;
- selection count;
- visibility/locked state if exposed.

Resolve ambiguity before implementation:

- one selected frame: proceed;
- several explicit breakpoints of the same screen: name each and proceed;
- unrelated nodes: ask for one target;
- empty selection: ask the user to select or supply exact ID;
- right name in wrong file: stop and correct the file.

Never infer selection solely from a familiar layer name.

## Extract in passes

### Pass 1: visual baseline

Call `get_screenshot` for the exact root, preferably at 2x.

Record:

- screenshot pixel dimensions;
- logical node dimensions;
- capture scale;
- appearance/theme;
- clipping;
- representative app state.

Keep the baseline unchanged.

### Pass 2: hierarchy

Call `get_tree_summary` at enough depth to expose major regions. Use
`get_children` for containers where:

- sibling order controls layout;
- repeated nodes are summarized;
- hidden/clipped children matter;
- the response was truncated;
- component boundaries are unclear.

Use targeted `get_node_info` calls for exact text, bounds, and metadata.

### Pass 3: structure

Call `get_jsx` for the smallest useful root. Treat output as:

- hierarchy hint;
- layout/constraint hint;
- compact view of repeated structure;
- source of candidate style nodes.

Do not paste JSX into Rust and do not treat wrapper count as architecture.

### Pass 4: resolved styles

Call `get_computed_styles` in batches for:

- root;
- structural containers;
- representative repeated rows/cards;
- every text style;
- controls and variants shown;
- dividers/one-pixel geometry;
- nodes with gradient, transform, opacity, shadow, radius, clipping, or
  backdrop effect.

Computed/resolved values beat class names or design intuition.

### Pass 5: fonts/assets

Call `get_font_family_info` for non-system families and relevant faces. Use
`get_fill_image` for image-fill content. Use `export` for actual source assets
when the tool is exposed and code edits are authorized.

## Choose tools

Current official Paper MCP documentation includes these relevant read/extraction
tools:

| Tool | Purpose |
|---|---|
| `get_basic_info` | Verify current document/page and top-level artboards |
| `get_selection` | Resolve current user selection |
| `get_node_info` | Inspect one node's identity, bounds, text, relations |
| `get_children` | Read direct ordered children |
| `get_tree_summary` | Compact subtree hierarchy |
| `get_screenshot` | Capture exact design appearance |
| `get_jsx` | Structural web-like representation |
| `get_computed_styles` | Resolved layout/type/paint values |
| `get_fill_image` | Retrieve an image fill |
| `get_font_family_info` | Inspect font availability/metadata |
| `get_guide` | Retrieve Paper-authored guided workflow |
| `export` | Export actual image/vector assets when available |

Paper can add or change tools. Use live discovery as the final authority.

Do not use `get_screenshot` as the only evidence. It hides constraints, font
metadata, exact values, and structure.

## Capture tokens, type, and effects

### Tokens and variables

Paper supports variables/tokens. Capture:

- token name and semantic role;
- supported category such as color, type, spacing, breakpoint, or radius;
- resolved value in the selected appearance;
- raw versus aliased value when the live schema exposes it;
- usage nodes;
- whether the target project already has an equivalent.

Paper's current tokens documentation lists multiple theme modes as roadmap
rather than a generally available capability. Do not invent a mode/collection
model when the open file and live tools do not expose one.

Map semantic intent before raw values. Reuse an existing `text_secondary` token
when it renders correctly; do not create `paper_gray_450` alongside the project
theme.

Keep resolved values for fidelity diagnostics even when code uses semantic
tokens.

### Constraints and layout

For each major node capture:

- auto-layout/flex direction;
- gap and padding;
- primary/cross-axis alignment;
- fixed, fill, hug/intrinsic behavior;
- min/max dimensions;
- grid/track behavior;
- absolute/overlay relation;
- clipping and scroll intent.

Distinguish authored constraint from screenshot outcome.

### Typography

Capture:

- exact text;
- family and fallbacks;
- face/weight/style;
- variable axes;
- size and line height;
- letter spacing;
- OpenType features;
- wrapping width, lines, alignment, truncation;
- transform such as uppercase.

Verify the face exists in the target runtime. Paper availability does not prove
the GPUI app can load it.

### Paint and effects

Capture:

- fill/gradient stops and opacity;
- border width/color;
- corner radii;
- shadow offset/blur/spread/color;
- node opacity;
- transform;
- clip/mask;
- background/backdrop filter.

For backdrop blur, record the exact design value but route implementation
through [apple-glass.md](apple-glass.md). GPUI's public per-element capability is
not equivalent.

## Export assets

Export only authorized real visual assets.

Recommended:

- SVG for monochrome/multicolor vector icons and illustration;
- PNG for raster alpha;
- JPG/WebP when the target pipeline supports it and opaque photo compression
  matters.

Record:

| Node ID | Name | Format | Scale | Logical size | Destination | Tint |
|---|---|---|---:|---:|---|---|

Before commit:

- inspect output visually;
- check SVG viewBox and unexpected embedded fonts/images;
- remove private metadata if project policy requires;
- use deterministic filenames;
- avoid duplicate exports;
- confirm asset license/source.

Export writes outside Paper but changes the code workspace. It is allowed only
when the user requested implementation or asset export.

## Handle large designs

Do not request an entire complex file repeatedly.

1. Keep one full-root screenshot and shallow tree.
2. Divide into major regions.
3. Extract one region's hierarchy/styles/assets.
4. Implement and compare that region.
5. Move to the next region.
6. Recheck global alignment after every region.

For repeated rows/cards:

- inspect one representative per variant;
- capture all unique content/state variants;
- infer repetition only after confirming structure/styles;
- do not make one MCP call per identical instance.

Keep a node-ID map so later queries are deterministic.

## Record evidence

Use a compact evidence pack:

```text
Paper file/page:
Root node:
Logical bounds:
Capture scale/theme:
Breakpoints:
Fonts:
Tokens:
Assets:
Material effects:
Missing states:
Known uncertainty:
```

Then the node table from [paper-to-gpui.md](paper-to-gpui.md).

Save only what helps implementation/review. Respect private designs and do not
send screenshots/code to external services without authorization.

## Permission boundary

Read-only extraction does not authorize Paper mutation.

Only use document-writing tools such as node creation, duplication, movement,
style/text updates, or deletion when the user explicitly requested design edits.
Before destructive design edits, resolve exact node IDs and preserve recovery
through the application's undo/version behavior where available.

Do not “clean up” the source design to make translation easier.

## Troubleshoot

### Tools missing

- Confirm Paper Desktop and file are open.
- Confirm endpoint `127.0.0.1:29979/mcp`.
- Refresh MCP/plugin connection.
- Inspect current tool discovery.
- Stop; do not recreate from memory.

### Wrong or stale file

- Bring intended Paper tab forward.
- Call `get_basic_info` again.
- Re-resolve selection and IDs.

### Empty/ambiguous selection

- Ask for one exact frame/component.
- Accept an exact node ID.
- Do not choose the first matching name.

### Truncated/huge response

- Reduce depth.
- Query direct children.
- Split by semantic region.
- Batch computed-style calls.

### Screenshot differs from computed values

Check inherited opacity, clipping, transforms, gradient, font face, variable
axes, backdrop effects, and nested layout outcomes. Use the screenshot as visual
truth and computed styles to locate the reason.

### Missing font or asset

Report it. Do not silently substitute or rasterize text. Ask for authorization
to add a licensed asset/font when needed.

See [sources.md](sources.md) for official Paper documentation.
