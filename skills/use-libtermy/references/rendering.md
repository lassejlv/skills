# Rendering and damage

Source: https://termy.sh/docs/developer/libtermy/rendering.md

libtermy returns terminal **state, not pixels**. The renderer retains a grid,
patches updates, shapes ordinary text, draws terminal geometry and images, and
owns cursor/selection overlays. Get full frames right first, then add
incremental updates.

## Full frames vs partial updates

`Terminal::snapshot()` / `termy_terminal_snapshot`: full compact frame.
`frame_update(force_full)` / `termy_terminal_take_frame_update`: cells +
damage. Force full on init, dimension change, or cache recovery.

| Damage | Rust | C `damage_kind` | Cell layout |
| --- | --- | --- | --- |
| None | `Partial` with empty spans | `0` | Nothing to patch |
| Full | `Full` | `1` | `rows * cols` cells, row-major |
| Partial | `Partial(spans)` | `2` | Concatenated cells per span, in span order |

Span = `(row, left_col, right_col)`, columns **inclusive**:
`len = right_col - left_col + 1`. Cells carry no coordinates.

Example, 80 cols, spans `(2, 3, 5)` and `(7, 10, 11)`: 5 source cells. Copy
the first 3 to retained indices 163–165, the next 2 to 570–571. Never index
the 5-cell source by absolute grid index.

## Patch a retained frame (Rust)

```rust
use termy_core::{TerminalDamageSnapshot, TermyFrame, TermyFrameUpdate};

pub fn apply_update(retained: &mut Option<TermyFrame>, update: TermyFrameUpdate) {
    let TermyFrameUpdate { cols, rows, cells, cursor, display_offset, history_size, damage } = update;
    match damage {
        TerminalDamageSnapshot::Full => {
            assert_eq!(cells.len(), usize::from(cols) * usize::from(rows));
            *retained = Some(TermyFrame { cols, rows, cells, cursor, display_offset, history_size });
        }
        TerminalDamageSnapshot::Partial(spans) => {
            let frame = retained.as_mut().expect("request a full frame first");
            assert_eq!((frame.cols, frame.rows), (cols, rows));
            let mut source = 0;
            for span in spans {
                assert!(span.row < usize::from(rows));
                assert!(span.left_col <= span.right_col);
                assert!(span.right_col < usize::from(cols));
                let count = span.right_col - span.left_col + 1;
                let destination = span.row * usize::from(cols) + span.left_col;
                frame.cells[destination..destination + count]
                    .copy_from_slice(&cells[source..source + count]);
                source += count;
            }
            assert_eq!(source, cells.len());
            // Copy metadata even when no cells changed.
            frame.cursor = cursor;
            frame.display_offset = display_offset;
            frame.history_size = history_size;
        }
    }
}
```

The asserts surface integration bugs during bring-up. In production, recover
from a lost cache or dimension mismatch by requesting a new full frame. C
hosts run the same algorithm over `cells_ptr`, `spans_ptr`, `damage_kind`,
then `termy_frame_update_free` after copying.

**Damage reads consume damage.** Calling `take_damage_snapshot` /
`termy_terminal_take_damage` and then `frame_update(false)` loses that damage.
Use one consuming path per render cycle.

Cursor movement, host selection, focus, blink and animation need repaints
without new text. Track old + new cursor rects. A host timer may repaint with
no PTY wakeup.

## Compact cells

| Field | Meaning |
| --- | --- |
| Rust `char` / C `codepoint` | One Unicode scalar, **not** a full grapheme |
| `fg`, `bg` | Resolved RGBA |
| `uses_terminal_default_bg` | Default background vs explicit cell bg |
| `render_text` | Whether to draw the text; bg painting is independent |
| `wide_character_spacer` | Trailing half of a wide char; draw no second glyph |
| `bold`, `italic`, `underline`, `strikethrough` | Compact style flags |
| `line_wrapped` | Keep for selection/copy |

C cursor styles on current revision: `1` bar, `2` block (check the header for
your revision). Respect cursor visibility, including hidden while viewing
history.

Compact cells cannot represent all combining text or underline variants. If
needed, use rich Rust reads, or document the C limitation.

## Rich Rust rendering

`Terminal::render_read(force_full)` → coherent `TerminalRenderRead`: viewport
metadata, live palette, rich cells, damage, scroll operations, generation.
**Its `cells` is always a full row-major viewport**, even with partial damage
(unlike `frame_update(false)`).

`TerminalRenderCell`: full cell text, indexed/default/RGB colors, underline
color + style, dim/inverse/hidden, wide flags. Resolve `TerminalRenderColor`
with the read's palette and configured fallbacks. A palette revision change
can alter cached cells' appearance.

Damage-first renderer:

1. `take_render_damage_snapshot` → damage + generation.
2. Apply ordered viewport scroll ops and palette revision changes.
3. `visit_viewport_ranges_at_generation` for affected spans.
4. If it returns `false`, discard and take a fresh coherent read (forced full
   read is the simple recovery).

`visit_viewport_cells` / `visit_viewport_ranges_at_generation` allow reentrant
callbacks. `_locked` variants and `visit_line_cells` hold the backend lock:
**no** re-entry into the same terminal from their callbacks.

## Special-glyph geometry

Box drawing, block elements, sextants, Braille, rounded corners, diagonals.

Rust: `terminal_glyph_plan` with `TerminalGlyphMetrics` and
`TerminalGlyphNeighbors`; no plan → shape normally.
`TerminalGlyphNeighbors::from_row` keeps the long-Braille-run vs short-spinner
distinction.

C:

1. Patch the retained full row-major buffer.
2. `termy_cells_build_glyph_render_plan(buffer, dims, metrics, dirty spans)`.
3. Draw entries by absolute `cell_index`, ranges into rect/stroke arrays.
4. `termy_glyph_render_plan_free`.

- **Zero spans = full plan**, not empty. Skip the call on updates with no
  cell damage unless you want a full rebuild.
- Keep full row context; invalidate neighbors when a change can affect a
  context-sensitive run (rebuilding the row is simple).
- Coordinates are normalized to a cell; transform and snap in device pixels.
  Rect snap kinds: `1` nearest, `2` outward. Stroke width is a fraction of
  cell width.
- Don't also font-shape a glyph that has a geometry plan.

## Kitty graphics

Images are separate from cells. Rust: `kitty_graphics_snapshot` (revision +
placements). C: `termy_terminal_kitty_graphics_revision`,
`termy_terminal_kitty_graphics_placements`, free with
`termy_kitty_graphics_batch_free`.

Placements: PNG bytes, image id/generation, source crop, display size,
viewport position, offsets, z-order, clipping, virtual-cell coordinates,
`next_frame_delay_ms`.

- Keep viewport/column offsets **signed** when clipping; casting a negative to
  unsigned puts the image far off-screen.
- Respect transform and clip fields; don't stretch each PNG over its cells.
- Nonzero `next_frame_delay_ms` → host timer to refetch placements and
  redraw, even with no new text. Zero = static.
- The batch owns PNG buffers; copy bytes before freeing if decoding async.
