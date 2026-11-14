> Upstream: [crates/rune/README.md § Text fields](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#text-fields) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Text fields

`TextEdit::focused` is maintained by the runtime. Set it once to request focus, then
let the runtime clear it when another field takes focus; do not force it on every view rebuild.
A handler drops focus with `Tx::blur()` (Enter in an inspector field handing keys back to
the window, say); the field's `focused` turns false through its `on_edit` accessor.
A field the view builds only once it can read a rect (`Cx::layout`, on the commit's re-run)
still takes the focus it asks for in that commit.

Text fields support Cmd/Ctrl-Z and Cmd/Ctrl-Shift-Z. Consecutive typing is one undo
group; selection changes, navigation, paste, cut and IME commits separate groups.
Undo restores selection direction as well as text. History shares storage with view
snapshots and retains at most 128 edits / 1 MiB of text (oversized edits drop history).
Call `TextEdit::clear()` after submission to clear history while retaining focus;
call `break_history_group()` when setting a selection from custom pointer handling.

Use `TextEdit::new("").secure()` with `text_input(&edit, style).single_line()` for
passwords, or mark the element `.single_line().secure()`; kit's `TextInput::secure()`
passes it through. Each Unicode scalar displays as one bullet, with model-byte
selection and caret positions mapped to those bullets.
Secure fields have no undo, copy, cut, IME composition, or inspector text. macOS
Secure Event Input is held only while their native window is focused and visible.

An editor the app draws itself (not a `text_input`) gets the input method too: mark the caret
it draws with `.ime_cursor()` while the editor has the keyboard, and hear the events with
`App::on_ime(|s, ime, tx| ..)`. While that caret is drawn and no field has focus, the window
turns its input method on and places the candidate window at the caret. `Ime::Preedit` carries
the composition and its cursor range (draw it, don't insert it; empty ends it), `Ime::Commit`
the text to insert, and `Ime::Enabled` and `Disabled` the input method turning on and off.
Typing arrives once: a plain character is a key (`Key::Text` in `on_key`), and `Ime::Commit`
carries only what an input method composed (dead keys, CJK, the emoji picker, dictation). A
focused field takes the events instead, and a focused secure field keeps the input method off.
Model buffers and history wipe on drop; secure edits wipe replaced allocations.
Use `replace_text(..)` or `clear()` for programmatic replacement. Direct assignment
to the public `text: String` field bypasses replacement wiping.

For secure notes or keys, use `rune_kit::TextArea::new(&edit).secure()` or a multi-line
`text_input(&edit, style).secure()`. Enter inserts a newline; Cmd/Ctrl+Enter submits,
and paste preserves newlines. Hidden non-empty values show twelve bullets on one
line regardless of length. Navigation moves to the end (Shift selects all); typing
and paste append, or replace the whole value if selected, and Backspace deletes
at the end. `.revealed(true)` permits interior edits while retaining all secure
protections. Toggling alone preserves selection; hiding snaps geometry and resets
ancestor scrolling. `TextArea::max_height(..)` or `auto_grow(..)` bounds revealed
content. Revealed secure lines wrap long tokens automatically; other text can opt
in with `El::wrap_anywhere()` (add `.shrink()` for flex-row shrinking). Code that lays
out text itself passes `RichLayoutOptions::new().wrap_anywhere()` to
`TextSystem::layout_rich_with(..)` for the same breaks.

`tx.copy_secret(text, Duration::from_secs(30))` writes with the platform's clipboard
history-exclusion marker and expires on Rune's shared clipboard worker. Expiry
compares the current text and, on macOS/Windows, the clipboard revision; copying
something else cancels the old expiry. Linux's portable API exposes no revision,
so it compares text. Clipboard managers must honor the platform marker themselves.
On Windows, locking the session (Win+L) clears a secret still on the clipboard at once.

Put `.on_paste(|s: &mut State, text: &str, tx| { ... })` on the view root (or modal
root) to handle Cmd/Ctrl-V when no field is focused. `tx.request_paste()` requests
the same asynchronous clipboard read from a button, including in overlays.
Focused editors take precedence; late reads are discarded if the target changed.
Headless `--script` `paste` supplies text directly through the same routing and
records `paste window` or `paste field` in `--trace`, without recording contents.

#### Rich clipboard

A `ClipboardContent` is plain text plus, optionally, HTML and RTF. Copy formatted text with
`tx.copy_rich(ClipboardContent::new("Ship it").with_html("<b>Ship</b> it").with_rtf(rtf))`;
plain text is always written, so every app can paste it. `copy_secret` stays plain text only.

Pasting delivers the richest form the source offered. A field hears it before its editor with
`.on_input_paste(|s, content, tx| -> bool)`: return true when the app took the paste (say, a
rich composer parsing `content.html()` into its model), false to let the editor paste
`content.text()` as before. The root's `.on_paste_content(|s, content, tx| ..)` is `on_paste`
with every form. `tx.read_clipboard(|s, content, tx| ..)` reads without pasting; it always
answers, with empty content when there's nothing to read. A rich `TextEdit` copies and pastes
HTML without a hook (see Rich text editing below). Plain fields without a hook and text `on_paste`
handlers behave exactly as before, and a clipboard with HTML but no plain text
reaches only the rich hooks. Reads run on the clipboard worker, never the event thread.

Hooks also hear a pasted image (a screenshot, an image copied from a browser or an editor):
`content.image()` is a `ClipboardImage` holding PNG bytes (`png()`) and the pixel size
(`size()`), whatever form the clipboard held it in. Rune fetches it only for a target with a
hook (`on_input_paste`, `on_paste_content`, `read_clipboard`), so pasting text into other fields
never decodes one, and leaves out images over `clipboard::MAX_IMAGE_BYTES` (32 MiB as PNG).
An image alone, with no text, reaches only hooks. Copies don't write images yet.

```rust
text_input(&s.prompt, style).on_edit(|s: &mut S| &mut s.prompt).on_input_paste(|s: &mut S, content, _| {
    let Some(image) = content.image() else { return false };
    let id = s.attachments.add(image.png().to_vec());
    s.prompt.insert_pill(format!("image:{id}"), "Image");
    true
})
```

Clipboard HTML is another app's untrusted input. Rune runs it through `sanitize_html` before
any hook sees it: scripts, event handlers, frames, embeds, `javascript:` and other non-web
URLs, comments and CSS that loads anything are removed; text, tags, `class`,
inline styles and inert `<style>` stay. Treat the result as markup to parse into a model, not
to hand a web view as is. RTF is passed through untouched.

| Platform | Copy | Paste | Pasted image |
| --- | --- | --- | --- |
| macOS | text, `public.html`, `public.rtf` in one pasteboard change | HTML; else RTF converted to HTML (TextEdit, Notes, Pages); else text | `public.png` as is, else `public.tiff` converted to PNG |
| Windows | text and CF_HTML (`HTML Format`); no RTF | CF_HTML fragment, else text | `PNG`, else `CF_DIBV5`, through arboard, encoded as PNG |
| Linux (X11, Wayland data-control) | text and `text/html`; no RTF | `text/html`, else text | `image/png` through arboard, decoded and encoded again |
| Web | `text/plain` and `text/html` through the async Clipboard API; no RTF | `text/html` from the paste event or `navigator.clipboard.read()`, else text | `image/png` from the paste event's files or `navigator.clipboard.read()` |

On macOS the RTF conversion uses `NSAttributedString` on the worker; AppKit's RTF reader and
HTML writer don't need the main thread. In tests, `clipboard::memory()` keeps every form:
`set_content(ClipboardContent::new("Hi").with_html("<b>Hi</b>"))` stands in for another app's
copy and `content()` shows what Rune wrote. `Runtime::paste_content` and the script step
`{"paste": {"text": "Hi", "html": "<b>Hi</b>", "rtf": "…", "png": "shot.png"}}` (or
`{"paste": "Hi"}`; `png` is a file path) paste
several forms through the same routing, sanitised as a real paste is.

`tx.fly_text("prompt", "sent-text")` hands a visible plain-text field to a newly
mounted, uniquely keyed text node. The runtime captures its visible glyphs before
committing and measures the destination after growth/scroll each frame. One 0.32 s
growth-spring progress drives the screen-space handoff; reduced motion uses a
150 ms crossfade. `settle()` lands it immediately. Neither view code nor handlers
measure presentation geometry.
