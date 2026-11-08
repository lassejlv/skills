# Configuration, sizing and resize

Source: https://termy.sh/docs/developer/libtermy/configuration.md

Two consumers: the **runtime** (shell, env, scrollback, query colors) and the
**renderer** (fonts, colors, cursor, dimensions). Loading config does not
apply every setting to an existing terminal or your UI.

## Load

| Source | Rust | C |
| --- | --- | --- |
| User default path | `load_config_from_default_path` | `termy_config_load_default` |
| Explicit file | `load_config_from_path` | `termy_config_load_path` |
| In-memory text | `load_config_from_contents` | `termy_config_from_contents` |

Missing default config → defaults, no file created. Missing explicit path →
error. In-memory load never writes. Rust `LoadedTermyConfig` has `app_config`,
`runtime_config`, `diagnostics`, `path`, `loaded_from_disk`.

A successful load can still have diagnostics; **show them** instead of
silently using fallbacks. C: `termy_config_diagnostics`, free with
`termy_config_diagnostics_free`.

| Kind | Meaning |
| --- | --- |
| 1 | Unknown section |
| 2 | Unknown root key |
| 3 | Unknown color key |
| 4 | Invalid syntax |
| 5 | Invalid value |
| 6 | Duplicate root key |

Accepted keys: https://termy.sh/docs/reference/configuration-reference. An
embedder need not implement Termy's tabs, updater or other app settings just
because the parser exposes them.

## Measure cells

- Rust: `measure_cell_from_config(&loaded.app_config)` or
  `measure_cell(font_family, font_size, line_height)`.
- C: `cell_width` / `cell_height` in `TermyFfiRenderConfig` from
  `termy_config_render_config_for_appearance`.

Use the same metrics for the grid **and** drawing. Changing font or size
without remeasuring misaligns text, mouse hit testing and size replies.

```text
cols = floor(content_width  / cell_width)
rows = floor(content_height / cell_height)
```

`content_*` is after subtracting chrome and padding. Require finite positive
cell sizes; clamp rows/cols to `>= 1` and to `u16`. Don't resize while the
view has no usable size. Keep metrics and content in one coordinate space;
apply logical→device scaling consistently.

## Appearance and colors

C: `termy_config_render_config_for_appearance(config, appearance, &out)`,
`0` light, `1` dark. `termy_config_render_config` assumes dark. Free with
`termy_render_config_free` (never free nested strings).

Render config includes fg, bg, cursor color, font family/size, line height,
padding, opacity, cursor style/blink, and measured cells. Some extra fields
describe optional host UI behavior; they are not a renderer.

Updating a live terminal's **query colors** (what programs see when they ask):

- C: `termy_terminal_apply_config_colors_for_appearance`. Resolving a render
  config alone does not update the terminal.
- Rust: build runtimes with `runtime_config_from_app_config_with_theme` for a
  `SystemAppearance`. For a live terminal: `resolve_theme_colors_from_app_config`
  → `terminal_query_colors_from_resolved_theme` → `set_query_colors`.

On any visual config change, refresh drawing resources and force a full
frame. Apply the same resolved appearance to runtime **and** renderer, or
programs that detect light/dark backgrounds pick wrong colors.

## Live resize

On window resize or font/scale change:

1. Resolve current cell metrics and content area.
2. Compute new nonzero grid.
3. `Terminal::resize` (needs `&mut`) / `termy_terminal_resize`.
4. Display-only: also resize the remote PTY through the transport (libtermy
   can't resize a PTY it doesn't own).
5. Replace the retained buffer from a **forced full frame**, then repaint.

Update image and glyph transforms with text metrics. Never patch a partial
update into a buffer sized for other dimensions.

## Settings persistence

`termy_settings_*` are conveniences for Termy's **own** user config and write
to disk. Use your own persistence for independent embedder settings; never
call setters as a side effect of showing a preview.
