> Upstream: [crates/rune/README.md § Selectable text](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#selectable-text) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Selectable text

`text(..).selectable(true)` lets people select and copy read-only text, as SwiftUI's
`.textSelection(.enabled)`: drag across it, double-click a word, triple-click a paragraph,
shift-click to extend. Cmd+C (Ctrl+C off macOS) copies and Cmd+A selects all of it while it holds
the selection; a right-click opens a native Copy menu on macOS unless the element has its own
`on_secondary_press`. It shows the I-beam (a link inside it keeps the pointing hand and opens on
click), isn't a Tab stop, and a press anywhere else clears it. One text (or selection group) holds
the selection at a time. It works across spans, wrapped lines and bidi runs. Cmd+C and Cmd+A are the plain chords
only: with Shift, Option or Control added they go to the app. A click on the text makes it the
holder, so Cmd+A selects all of it, as in an AppKit text view; Cmd+C with nothing selected goes to
the app. A view that changes the selected text, removes it or turns `selectable` off drops its
selection; text appended after it (a message streaming in) keeps it.

`El::selection_group(true)` makes the selectable texts inside an element one selection, as a web
page's are: a drag crosses from one into the next in tree order, Shift-click extends into any of
them, Cmd+A selects them all and Cmd+C joins them with a newline, or a tab between texts side by
side (table cells). Double- and triple-clicks still take a word or paragraph of one text, and
non-selectable text inside (a list marker) is left out. Texts whose boxes overlap vertically (a
table row's cells) select as a row, and a drag into a gap stops where the pointer is. A group
inside a group is its own. Kit's `Markdown::selectable` is one. `El::uncopied(range)` marks
bytes that draw but aren't copied, such as padding characters; a double-click's word stops at
them. An elided text (`max_lines`, `truncate`) selects through its ellipsis and copies whole,
and a virtual row scrolling out drops the selection it holds.

Inside a row that handles input, the row keeps it: an unmoved click on the text presses (and
double-presses) the nearest ancestor with a handler, hover and press paint reach that ancestor,
and its `on_secondary_press` wins over the Copy menu. A drag that selects text doesn't press.
Inside a draggable row (`on_drag` or `drag_out`), dragging drags the row and double- and
triple-clicks still select words and lines. Text with its own handlers keeps them.

The selection lives in the runtime, so selecting never re-runs the view or re-lays out the text.
`El::selection_color` sets the highlight for selectable text and text fields alike, and both draw
it the same way; kit's `k.selection()` is the colour its `TextInput` uses, so pass it to match.
`Runtime::text_selection()` and `selected_text()` read the selection; `--tree` marks the text's
node `selected` with the selected string, and scripts gain a `triple-click` event.

```rust
text(&command).font(k.ty.mono).selectable(true).selection_color(k.selection())
```

A handler reads the selection with `tx.text_selection()`, a `TextSelection` of the selected
texts (path, key, byte range, whether all of it is selected) and the text copying takes. It sets
the selection by key with `tx.select_text(key, range)` (a byte range of one text, clamped to its
characters), `tx.select_all_text(key)` (a text, or every text of the selection group inside an
element) and `tx.clear_text_selection()`. These apply after the handler's change is built, so a
text the same change adds can be selected, and before a key later in the same frame, so a
handler can select and the next Cmd+C copies it. The last call wins.

`El::selection_copy(|sel| ..)` on an element decides what copying a selection inside it takes,
for Cmd+C and the Copy menu: it sees every selectable text it could reach (paths relative to it,
unselected texts with an empty range), and returning `None` copies the text as drawn. The nearest
one around both ends of the selection answers. An app that wants Cmd+C or Cmd+A for something
else takes it in `on_key`, which sees it before the selection does.

`El::on_selection_change(|s, change, tx| ..)` hears the selection start, change, leave the
element or clear, however it happened: a drag (from its first selected character), a double- or
triple-click, Cmd+A, a click elsewhere, or `tx.select_text`. `change.selection()` is the whole
selection while any of it is inside the element, and `change.started()` and `change.cleared()`
say which edge it was. It runs at most once a frame during a drag, before the frame's commit; a
press that leaves only a caret isn't heard. Call `tx.live_only()` in it when the view reads
nothing it changed.

```rust
col().key("note").selection_group(true).children(paragraphs)
    .selection_copy(move |sel| sel.texts().iter().all(|t| t.is_whole()).then(|| source.clone()))

// Select a note's text from code, then read it back in a later handler.
tx.select_all_text("note");
let picked = tx.text_selection().map(|s| s.text().to_owned());

// Drop the app's own highlight once people start selecting.
col().key("note").selection_group(true)
    .on_selection_change(|s: &mut Notes, change, _| if change.started() { s.highlight = false });
```
