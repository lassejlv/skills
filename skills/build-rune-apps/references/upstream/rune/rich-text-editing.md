> Upstream: [crates/rune/README.md § Rich text editing](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#rich-text-editing) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Rich text editing

`TextEdit` holds an attributed rich-text model alongside plain `edit.text`. Formatting keys,
soft breaks and rich paste are opt-in with `TextEdit::new(text).rich()` (`from_html` and
`from_parts` turn it on); without it a field keeps `⌘B`/`⌘I`/`⌘U` for the app, inserts a plain
newline on `Shift+Return` and pastes plain text. The mark and block methods work either way.

- **Inline marks** (`Mark::Bold`, `Italic`, `Underline`, `Strike`, `Code`, `Link(url)`): stored as
  sorted byte ranges (`MarkRange { start, end, mark }`) on `edit.text`. Insertions and deletions
  shift and split ranges automatically. Typing inherits the marks of the character before the caret
  (following AppKit's rules: never extending backwards from the start of a link or code mark's
  run). `edit.toggle_mark(mark)`, `set_mark`, `remove_mark` and `set_link(Some(url))` apply or
  remove marks on a selection, or arm a pending typing style when the selection is empty (cleared
  when the caret moves). In a rich field `⌘B`, `⌘I` and `⌘U` (`Ctrl` on Windows/Linux) toggle
  bold, italic and underline. Query `edit.has_mark(&Mark::Bold)`, `edit.active_marks()` and `edit.active_link()` to
  drive a formatting bar's pressed state.
- **Paragraph block attributes** (`Block::Paragraph`, `Bullet(level)`, `Numbered(level)`, `Quote`,
  `Code`): one `Block` per `\n`-delimited paragraph (`edit.blocks()`, `edit.paragraphs()`,
  `edit.active_block()`, `edit.set_block(block)`, `edit.toggle_block(block)`). Bullet and numbered
  list markers (`0..=3` nesting levels), quote bars and code-block backgrounds are drawn as
  decorations (never inserted into `edit.text`), and Parley indents each paragraph's lines by
  `Block::indent_pt`. By default (overridable via `.on_input_key`):
  - `Return` in a non-empty list item starts a new item at the same level; `Return` in an empty
    list item or quote, or on a blank last line of a code block, resets the paragraph to
    `Block::Paragraph`, leaving the list, quote or code block.
  - `Down` or `Right` at the very end of a field that ends in a code block or quote adds an
    empty paragraph after it, so the caret can always get out.
  - In a rich field, `Shift+Return` inserts a soft line break (`edit.soft_breaks()`) that stays inside the current
    list item or quote without drawing a second marker.
  - `Backspace` at the start of a list item outdents it (`level > 0`) or converts it to
    `Block::Paragraph` (`level == 0`).
  - `Tab` and `Shift+Tab` inside a list item indent or outdent its nesting level instead of moving
    focus.
  - Inside `Block::Code`, `Return` elsewhere inserts a newline (never submits), inline marks do not apply,
    and a typed or pasted `\t` inserts a literal tab byte that advances to the next 4-column stop
    (one byte, so offsets and copy/paste keep the tab).
  - Code blocks and `Mark::Code` runs draw in the mono slot (name a monospaced family in
    `AppSpec::families`; the default is Inter) without ligatures.
- **Inline pills** (`Mark::Pill(id)`, for `@file`, `@agent` or attachment mentions): an atomic
  run whose label is the text under the mark and whose id is the app's. The caret steps over a
  pill in one move, a selection that reaches into one grows to cover it, `Backspace`/`Delete`
  remove it whole, typing and IME composition never land inside it, and undo restores it with
  its id. Pills are only made by the app: `edit.insert_pill(id, label)` at the caret, or
  `edit.replace_with_pill(range, id, label)` to swap a typed `@query` for one (one undo step;
  wrap multi-part edits like `replace_with_pill` + `insert(" ")` in `edit.undo_group(|e| ..)`).
  `edit.pills()` lists `(range, id)` for each. The field draws each pill as a rounded chip
  (`.pill_style(|id| PillStyle::default().bg(..).fg(..).icon(..))`, or `.pill_colors(bg, fg)`
  and `.pill_icon(|id| ...)`), and a chip never splits across lines. Copy writes the label as
  plain text and `<span data-pill="id">label</span>` as HTML; pasting that into a rich field
  of the same app restores the pill, while HTML from elsewhere never makes one (an
  `on_input_paste` hook can call `insert_pill` itself).

  ```rust
  // `@que` typed before the caret becomes a file pill.
  let (caret, _) = edit.range();
  if let Some(at) = edit.text[..caret].rfind('@') {
      edit.replace_with_pill(at..caret, "file:src/main.rs", "main.rs");
  }
  ```
- **Per-frame decorations** (`.spans(spans)` / `.decorations(spans)` on `text_input`, `TextInput`
  and `TextArea`): paint caller-supplied `rune::Span`s (such as `SyntaxTheme::from_kit(&k).spans(&ranges, offset)`
  from `rune_kit::syntax::highlight`) over the editor without mutating `TextEdit`. Byte offsets are
  relative to `edit.text` and shift automatically across any active IME preedit, so syntax and
  mention highlights hold through IME composition and undo/redo.
- **HTML paste and export, and data out**: `TextEdit::from_html(html)` and
  `edit.paste_html(html, plain)` parse a safe HTML subset (`b`/`strong`, `i`/`em`, `u`,
  `s`/`del`/`strike`, `a[href]`, `code`, `pre`, `ul`/`ol`/`li`, `blockquote`, `p`/`div`/`br`, and
  `style` attributes for `font-weight`, `font-style`, `text-decoration`; `<script>`/`<style>` are
  dropped and links keep only `http`, `https`, `mailto`, `tel` and scheme-less URLs). A plain
  field, a code block, or HTML with no formatting the model keeps (a code editor's coloured copy)
  pastes the plain text. `edit.to_html()` and `edit.selected_html()` serialize back to HTML
  alongside plain `edit.text`. A focused rich field uses the rich clipboard on its own: `⌘C` / `⌘X`
  write `selected_html()` beside the text, and paste goes through `paste_html` unless an
  `on_input_paste` hook takes it. Construct or inspect the model directly with
  `TextEdit::from_parts(text, marks, blocks)`, `edit.marks()`, `edit.blocks()` and
  `edit.paragraphs()`, adding soft breaks with `.with_soft_breaks(edit.soft_breaks().to_vec())`
  (or `set_soft_breaks`) and dropping undo/redo stacks with `edit.clear_history()`. Accessibility
  roles (`textbox`) and plain-text values are unchanged.
- **Undo history past a restart**: `edit.history_json(max_steps, max_bytes)` gives the newest
  undo and redo steps (each the document before and after it: text, selection, marks, blocks)
  as JSON for the app to store, and `edit.restore_history_json(&v)` takes them back when they
  lead to the field's document; a history stored a few keystrokes early gets one step from where
  it ends to the document. A secure field gives and takes none. `edit.history_len()` (undo, redo)
  changes when the history moves, so an app can store it only then.
- **Allowed formatting**: `.allow_marks([Mark::Bold, Mark::Italic, ..])` and
  `.allow_blocks([Block::Bullet(0), ..])` keep a field to what its app can store (Markdown has no
  underline, say). The field never holds the rest: its shortcut (`⌘U`) goes on to the app's key
  handlers, `toggle_mark`, `set_mark`, `toggle_block` and `set_block` skip it, paste drops it
  (a pasted disallowed block becomes a paragraph), and marks or blocks the field already had
  are removed. Kinds match whatever they carry (any `Mark::Link` allows links, any
  `Block::Bullet` level allows bullets); `Block::Paragraph` is always allowed.
  `edit.allows_mark(&mark)` and `allows_block(block)` tell a formatting bar which buttons to show.
