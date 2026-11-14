> Upstream: [crates/rune-kit/README.md § Markdown](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-kit/README.md#markdown) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Markdown

Feature `markdown`: `Markdown::new(src).build(&kit)`, or without a kit
`Markdown::new(src).render(&MarkdownStyle::neutral(dark))`.
It renders CommonMark plus GFM tables, and is built for streaming: re-render with the longer
source each time, and earlier blocks stay mounted.

- **Tables** keep their header row, per-column alignment and inline formatting. Columns start
  at their content's width, so a table with room never wraps a cell, and shrink in proportion
  to their text when the table doesn't fit; text wraps inside a column down to its longest
  word (at most `table_min_column`, 120 points), then the cell clips. With
  `Markdown::scroll_wide(true)` columns keep their full width and a wide table scrolls sideways
  instead. While a row is still arriving (`Markdown::streaming(true)`) it doesn't resize the
  columns, and a header line alone already shows as a table. Cells set figures at one width (`tnum`) so numbers line up; turn
  that off with `table_tabular_figures(false)`. `table(border, header_fill)` sets the outline,
  row rules and header fill; `table_outline(None)`, `table_rules` and `table_header_text` give
  the look of a web table (no outline, a rule under every row, a dimmer header).
- **Code fences are syntax-coloured** in Rust, JavaScript/JSX, TypeScript/TSX, JSON, Python,
  Go, Swift, shell, SQL, HTML/XML, CSS and YAML (common aliases such as `ts`, `rs`, `py`,
  `golang`, `sh`, `yml` work). Other languages, and fences with none, stay plain. Colour is all
  that changes, never weight or style, so a fence streaming in draws its newest line plain and
  colours it in place when the line ends, with nothing moving. Token colours come from a
  `SyntaxTheme` that follows the kit's light or dark theme; override one with
  `syntax(Syntax::Keyword, color)`, all with `syntax_theme(theme)`, or turn colouring off with
  `syntax_highlight(false)`. Tabs in code line up at four-column stops and copy as tabs.
  [Light](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/markdown-code-light.png) and [dark](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/markdown-code-dark.png)
  stills: the gallery's `rune-markdown--code` scene.
- **Your own highlighter.** `Markdown::highlight(|lang, code| ...)` replaces the built-in one:
  it gets the fence's language as written (`None` for none) and returns
  `Vec<(Range<usize>, Paint)>`, where `Paint` is a token kind (`Syntax::Keyword`, coloured by the
  theme) or a `Color`. Fall back on `rune_kit::syntax::builtin(lang, code)` for the rest. Output
  is cached per highlighter, language and code; give a highlighter whose output depends on
  something it captures a `Highlighter::new(f).key(theme)`.
- **The same highlighting outside Markdown.** `rune_kit::syntax` doesn't need the `markdown`
  feature: `syntax::highlight(Some("rust"), code)` returns the cached ranges and
  `SyntaxTheme::from_kit(&k).spans(&ranges, offset)` turns them into colour-only `Span`s for
  any rich text, such as code in a composer. The built-in highlighter is OpenCode Desktop's own:
  Pierre's Highlights, 80 hand-written lexers (C, C++, C#, Java, Kotlin, Ruby, PHP, Lua,
  Dockerfile, Makefile and the rest) that `rune-highlights` translates from WebAssembly to Rust
  at build time, so tokens match Desktop's exactly. They run in linear time (0.1 to 0.6 ms per
  thousand lines); a block streaming in costs only its new lines; a block colours its first
  128 KiB (or 32,768 ranges) and draws the rest plain. `syntax::lang_for_path` names a file's
  language as Desktop's diffs do.
- **```` ```diff ````** (or `patch`) fences tint `+` and `-` lines edge to edge, and dim `@@`
  and file header lines. Set colours with `MarkdownStyle::diff` and `diff_hunk`. Line text
  keeps the body colour unless `diff_text(added, removed)` or `diff_text_tint(0.5)` (toward the
  theme's green and red) colours it.
- **```` ```mermaid ````** (feature `mermaid`, backed by `rune-mermaid`) draws flowcharts,
  sequence diagrams and state diagrams natively, with no JS or webview, themed through
  `MarkdownStyle::diagram*`. Layout runs once per source and is cached. Anything outside the
  supported subset (listed in `rune-mermaid`) shows as its plain code block. `rune_kit::mermaid::render(src, &style)` draws one on its own.
- **`selectable(true)`** lets people select and copy the text as one selection: a drag runs from
  a paragraph through list items into a code block, Shift-click extends, Cmd+A selects the
  whole Markdown and Cmd+C copies the text as drawn, as a web browser does: a newline between
  blocks, a tab between table cells, no list markers, fences or `**`. Links still open on a
  click, and a selection stays while the source streams on after it. The highlight is
  `k.selection()`; set another with `MarkdownStyle::selection`.
- **`highlights(..)` and `markdown::find(src, query, case)`** search and highlight the rendered
  text in source UTF-8 byte ranges across inline markers, tables and code blocks without
  reshaping text (`Highlight::new()` and `Highlight::current()`, scrolled to with
  `Tx::scroll_into_view` by `Markdown::highlight_key(index)` or `.key(..)`).

`Tooltip::label(..).render(&TooltipStyle::neutral(dark), &mut layer)` builds a tooltip without
a kit. `TooltipStyle::max_width(w)` caps its width; `label`, `text` and a `.wrap()` text `child` wrap at it. The
app owns `open`, so the hover delay is a `wake_after` in its hover handler; `El::help(text)` is
the delayed, self-dismissing system tooltip when the look needn't match. The gallery's `rune-markdown--walkthrough`, `rune-markdown--diagrams`,
`rune-markdown--table-styles` and `rune-markdown--code` scenes show every feature.
