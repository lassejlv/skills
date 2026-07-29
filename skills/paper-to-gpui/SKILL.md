---
name: paper-to-gpui
description: Translate Paper.design artboards, selected frames, components, tokens, computed styles, and exported assets into faithful native Rust interfaces built with GPUI. Use when Codex must inspect a Paper file through the Paper Desktop MCP server, implement or update a GPUI view to match it closely, map web-style layout and typography to GPUI elements, preserve an existing GPUI app's architecture and design system, or run a screenshot-driven visual fidelity pass.
---

# Paper to GPUI

Turn a selected Paper design into maintainable GPUI code, then prove the native
result against the design at the same viewport. Treat Paper as the visual
contract and the current Rust checkout as the implementation contract.

## Non-negotiable rules

1. Inspect before editing. Verify the Paper file, selected node, GPUI version,
   existing components, theme, assets, and dirty worktree first.
2. Use Paper MCP evidence, not a screenshot alone. Capture hierarchy, computed
   styles, text, fonts, assets, and a 2x screenshot of the exact target.
3. Treat Paper JSX as a structural hint, never as GPUI code or unquestioned
   truth. Computed styles and the screenshot settle ambiguity.
4. Preserve the app shell, state model, component conventions, and platform
   behavior. Replace only the visual surface in scope.
5. Prefer GPUI layout over coordinate transcription. Use flex/grid for normal
   structure and absolute positioning only where the design genuinely overlaps.
6. Do not rasterize text, controls, panels, or whole screens to fake fidelity.
   Export only real visual assets such as icons, illustrations, textures, and
   photos.
7. Validate the native runtime. `cargo check` is necessary but does not prove
   fonts, window chrome, scale factor, focus, hover, clipping, or pixel fidelity.
8. Work in small regions. Large artboards must be translated and compared
   section by section before the whole screen is judged.

## Workflow

### 1. Establish both contexts

Run the read-only project inspector:

```sh
scripts/inspect_gpui_project.sh /path/to/gpui-project
```

Then inspect the checkout directly:

- Confirm the repository root, branch, dirty state, and requested surface.
- Read the relevant `Cargo.toml`, lockfile entry, app entrypoint, root view,
  theme/tokens, reusable components, asset source, and nearby tests.
- Identify whether the project uses published `gpui`, a Git revision, a
  workspace checkout, a fork, or a wrapper component library.
- Follow the pinned checkout's APIs when they differ from examples. GPUI is
  pre-1.0 and changes frequently.

Use the Paper MCP server:

1. Call `get_basic_info` to verify the currently open file and artboards.
2. Call `get_selection` to resolve the target.
3. If the selection is empty or includes unrelated nodes, ask the user to select
   one artboard or frame. Do not guess from names when multiple targets fit.
4. Default to read-only Paper tools. Do not change the design unless the user
   explicitly asks for design edits.

Read [paper-mcp.md](references/paper-mcp.md) before extracting a non-trivial
design or troubleshooting Paper connectivity.

### 2. Capture a design evidence pack

Acquire evidence in this order:

1. `get_screenshot` at 2x for the selected root.
2. `get_node_info` and `get_tree_summary` for dimensions and hierarchy.
3. `get_jsx` for a compact structural interpretation.
4. `get_computed_styles` in batches for the root, layout containers, text,
   controls, separators, and visually distinct descendants.
5. `get_font_family_info` for every non-system family and used weight/style.
6. `get_fill_image` or `export` for real image/vector assets.
7. `get_children` plus targeted subtree calls when a large design exceeds tool
   limits or loses detail.

Record a compact evidence table before coding:

| Paper node | Role | Bounds | Layout | Spacing | Type | Paint/effects | Asset | Behavior |
|---|---|---|---|---|---|---|---|---|

Include exact values where they affect fidelity. Do not fill unknowns with
plausible defaults. Re-query the node or label the uncertainty.

### 3. Build a translation plan

Map the design into these layers:

1. **Window and chrome** — viewport, titlebar, background, safe inset, minimum
   size, and platform-specific frame.
2. **Structural regions** — sidebar, toolbar, content columns, inspector, footer,
   modal, or overlay.
3. **Reusable primitives** — button, icon button, field, row, badge, separator,
   list item, empty state, and section heading.
4. **Tokens** — color, spacing, typography, radius, border, shadow, and
   breakpoint constants.
5. **State and behavior** — selection, hover, pressed, focus, disabled, loading,
   scrolling, shortcuts, and resize behavior.

Reuse existing tokens and components when their rendered result matches. Extend
them narrowly when they do not. Do not create a parallel design system for one
screen.

Read [gpui-translation.md](references/gpui-translation.md) before implementing.
It contains the detailed Paper/CSS-to-GPUI mapping and the boundaries where GPUI
needs a custom element, canvas, or deliberate approximation.

### 4. Implement from geometry inward

Use this order because it minimizes rework:

1. Match window/content bounds and large background regions.
2. Match flex direction, fixed/flexible dimensions, gaps, padding, alignment,
   wrapping, overflow, and clipping.
3. Match typography: actual family, available weight, size, line height,
   wrapping width, alignment, truncation, and baseline.
4. Match fills, borders, radii, opacity, shadows, gradients, and separators.
5. Add exported assets at their intended logical size.
6. Add interaction states and focus behavior.
7. Extract reusable GPUI components only after the repeated visual pattern is
   confirmed.

Keep exact Paper pixels as `px(...)` during the first fidelity pass. Consolidate
repeated values into project tokens after the screen matches. Avoid premature
rounding to GPUI convenience scales such as `.gap_3()` when Paper specifies an
off-scale value.

### 5. Validate behavior and visual fidelity

Run the nearest repository checks first:

```sh
cargo fmt --check
cargo check -p <owning-crate>
cargo test -p <owning-crate>
cargo clippy -p <owning-crate> --all-targets -- -D warnings
```

Adapt commands to the repository. Do not claim checks that were unavailable or
unreasonably broad.

Then launch the real app and compare:

1. Reproduce the Paper artboard's logical viewport inside the GPUI content area.
2. Confirm OS scale factor, theme, font availability, and window chrome.
3. Put the app in the same state and use the same content as Paper.
4. Capture the GPUI window or content region without resizing the result.
5. Compare side by side, overlay at partial opacity, and use a difference image
   when tooling is available.
6. Fix mismatches in this order: bounds, layout, typography, paint, assets,
   interaction polish.
7. Repeat until further changes are below the agreed tolerance.

Read [fidelity-validation.md](references/fidelity-validation.md) for capture
normalization, diff techniques, tolerances, and mismatch diagnosis.

### 6. Prove completion

Do not call the work complete until:

- The exact Paper file and target node are identified.
- The relevant GPUI crate builds and targeted tests pass.
- The native app has been launched at least once.
- A final Paper screenshot and GPUI screenshot exist at matching logical bounds.
- Major structure, typography, colors, radii, and assets have been visually
  compared.
- Hover, active, focus, scrolling, resizing, and keyboard behavior relevant to
  the screen have been exercised.
- Remaining deltas and platform limitations are stated plainly.

## Reference routing

- Read [paper-mcp.md](references/paper-mcp.md) for connection setup, safe tool
  sequencing, node extraction, tokens, fonts, assets, and Paper failure modes.
- Read [gpui-translation.md](references/gpui-translation.md) for current GPUI
  architecture, styling APIs, property mapping, components, assets, state, and
  version shields.
- Read [fidelity-validation.md](references/fidelity-validation.md) for the
  screenshot loop, visual tolerances, diff workflow, responsive checks, and
  native acceptance.
- Read [worked-example.md](references/worked-example.md) when starting a new
  translation or when Paper's JSX/CSS structure does not map cleanly to GPUI.

## Failure shields

- If Paper tools are absent, stop and explain how to connect Paper Desktop MCP.
  Do not reconstruct a design from memory.
- If Paper reports the wrong file, have the user open the intended file and call
  `get_basic_info` again.
- If no single target is selected, ask for a selection or an exact node ID.
- If a Paper subtree is huge, split by structural region and keep one screenshot
  of the full target for global alignment.
- If an exact font is unavailable to GPUI, do not silently substitute it. Report
  the missing family/weight, add or register the font if authorized, then
  recapture.
- If a Paper effect has no direct GPUI equivalent, preserve hierarchy and
  interaction, implement the nearest maintainable native effect, and document
  the delta. Consider `canvas` or a custom `Element` only after ordinary GPUI
  styling is proven insufficient.
- If screenshots differ despite equal CSS-like values, inspect content bounds,
  device scale, text metrics, default line height, border inclusion, and OS
  window chrome before nudging arbitrary pixels.

## Final response

Report:

- Paper file, artboard/frame, and viewport used.
- GPUI files and reusable components changed.
- Assets and fonts added or reused.
- Build, test, launch, and screenshot checks performed.
- Remaining visual or behavioral deltas.
- Any assumptions that still require user confirmation.
