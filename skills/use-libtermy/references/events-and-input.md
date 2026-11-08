# Events, protocol replies, input, search and links

Sources: https://termy.sh/docs/developer/libtermy/events.md,
https://termy.sh/docs/developer/libtermy/input.md

Output flows program → libtermy. Input flows host → program. Keep the
directions separate, especially in display-only sessions.

## Draining events

Rust: `terminal.drain_events(&mut reply_host)` → `(events, has_more)`.
C: `termy_terminal_drain_events` or the callback-enabled
`termy_terminal_drain_events_with_clipboard` → `TermyFfiEventBatch`.

Process the batch, keep `has_more`, free the batch, repeat. Under sustained
output, use a host time budget and reschedule rather than starving the UI.
Don't wait for a new wakeup when the batch said there's more.

C batches own every event `payload`; copy what you need before
`termy_event_batch_free`. Payloads have explicit lengths and are **not**
NUL-terminated.

| Kind | Event | Host action |
| --- | --- | --- |
| 1 | Wakeup | Schedule work/redraw |
| 2 | Title | Set title from UTF-8 `payload` |
| 3 | Reset title | Restore host fallback title |
| 4 | Bell | Apply bell/notification preference |
| 5 | Exit | Mark exited, apply close policy |
| 6 | Clipboard store | Apply policy to OSC 52 text |
| 7 | Shell prompt start | Prompt lifecycle |
| 8 | Shell command start | Command-input state |
| 9 | Shell command executing | Mark execution |
| 10 | Shell command finished | Read `exit_code` (`-1` = not supplied) |
| 11 | Progress | `progress_state`: 0 clear, 1 in progress, 2 error, 3 indeterminate, 4 warning; `progress_value` |
| 12 | Working directory | Update metadata from UTF-8 `payload` |
| 13 | Program status | **Replace** previous snapshot with JSON array in `payload` |
| 14 | Input dropped | Tell the user keys/paste were discarded (program's input backlog full) |

Use the `TERMY_FFI_EVENT_*` constants, not raw numbers. Shell lifecycle events
need shell integration sequences; not every session emits them. `Exit` is not
an exit-code API.

## Protocol replies (display-only)

Programs query capabilities, colors, cursor/size and clipboard. PTY-backed
terminals answer their own child. **Display-only hosts must forward reply
bytes to the external process.**

```rust
use termy_core::{TerminalClipboardTarget, TerminalReplyHost};

#[derive(Default)]
pub struct ReplyHost { pub pending_replies: Vec<u8> }

impl TerminalReplyHost for ReplyHost {
    fn load_clipboard(&mut self, _target: TerminalClipboardTarget) -> Option<String> {
        None // no clipboard access
    }
    fn protocol_reply(&mut self, bytes: &[u8]) {
        self.pending_replies.extend_from_slice(bytes); // send via transport after drain
    }
}
```

C: pass `protocol_reply_callback` to
`termy_terminal_drain_events_with_clipboard`; copy the borrowed slice into a
transport queue before returning. NULL callback drops replies.

- Never feed replies back into `feed_output`; they are input for the remote
  process.
- Replies without draining: `feed_output_with_replies` /
  `termy_terminal_feed_output_with_replies` returns all queued replies in
  engine order. Free with `termy_buffer_free`.

### Replicas

A display terminal mirroring output another terminal already answered must
not reply: `set_protocol_replies_enabled(false)` /
`termy_terminal_set_protocol_replies_enabled(t, false)`. Queries still parse;
replies are dropped. Start a replica with `termy_terminal_snapshot_encode` →
`termy_terminal_snapshot_decode`; feeding both the same bytes keeps them in
sync. Snapshot contents: [engine.md](engine.md#snapshots).

### tmux control-mode panes (Rust only)

tmux answers DA, cursor/status reports, XTVERSION, colors, sizes itself. Use
`set_protocol_replies(TerminalProtocolReplies::Passthrough)` so the terminal
answers only what tmux leaves: kitty graphics, kitty keyboard flags, OSC 52
and OSC 5522 clipboard, kitty paste-event mode. Send those to the pane
yourself (e.g. `send-keys -H`).

## Kitty OSC 5522 clipboard

Arbitrary MIME read/write. Host owns access and permission policy. Rust:
`TerminalReplyHost` clipboard methods. C: callback-enabled drain. Missing read
callback = deny; missing write callback = unsupported.

C callback rules:

1. Requests, MIME lists and write slices are borrowed for the callback only.
2. A read callback must call the supplied reply callback **before returning**
   (libtermy copies during that call).
3. A write callback returns `TermyFfiClipboardWriteResponse` directly.
4. Never keep the reply function or `reply_user_data`.
5. Never re-enter the same handle from a clipboard/reply callback.

Async permission prompt? Don't hold the callback open. Return denied/busy and
obtain permission separately for future requests. Marshal drains to the thread
your clipboard API requires.

Result codes (distinct from `TermyFfiStatus`): 0 success, 1 denied,
2 unsupported, 3 busy, 4 invalid data, 5 I/O error. Location: 1 clipboard,
2 primary selection.

Before an ordinary paste: if
`termy_terminal_kitty_clipboard_paste_events_enabled`, call
`termy_terminal_send_kitty_clipboard_paste_event` with available MIME types.
Rust display-only: `kitty_clipboard_paste_notification` returns bytes for your
transport. The notification does not replace the paste payload.

## Wakeups and scheduling

PTY wakeups are **coalesced**: one notification can cover many writes/events.

C PTY handles: `termy_terminal_wait_for_wakeup(timeout_ms)` blocks (0 polls),
reports via `out_woke`. Never block the UI thread on it. A dedicated waiter
posts to the serialized owner and checks a host shutdown flag after waking.

C display-only handles have **no** wake channel; schedule drains/frames after
feeding output. Rust has `new_display_with_wakeup_notifier` if you want
notifications.

Before freeing a C handle with a waiter: stop work, notify, join, then free
(details in [c-abi.md](c-abi.md#threading-and-shutdown)).

## Keyboard

Encode with the **current** mode every time; apps change it while running.
Never hardcode arrow-key escapes.

```rust
use termy_core::{Terminal, TerminalKeyEventKind, TermyKeystroke, keystroke_to_input};

pub fn send_key(terminal: &Terminal, key: &TermyKeystroke, kind: TerminalKeyEventKind) {
    if let Some(bytes) = keystroke_to_input(key, kind, terminal.keyboard_mode(), true) {
        terminal.write(&bytes); // display-only: send to transport instead
    }
}
```

`TermyKeystroke`: `key` logical name (`enter`, `backspace`, `left`,
`right`, ... see `crates/core/src/keyboard.rs`), optional `key_char`
produced text, `modifiers` (control, alt, shift, platform, function).

C: fill `TermyFfiKeystroke`, call `termy_terminal_encode_key` or
`termy_terminal_encode_key_with_options` (use options for macOS
Option-as-Alt). `event_kind`: 1 press, 2 repeat, 3 release. Returns owned
`TermyFfiBytes` → send, then `termy_buffer_free`. Empty is valid (e.g.
unreported release).

Don't add an unconditional ESC prefix for Alt; enhanced keyboard modes need
different bytes. Handle app shortcuts and IME composition in the host so
committed text isn't sent twice.

## Paste

Query `bracketed_paste_mode()` / `termy_terminal_bracketed_paste_mode` **at
paste time**. If on, wrap the approved payload in `\x1b[200~` … `\x1b[201~`;
otherwise send plain. `write` never adds markers. Decide newline/control-char
policy in the host, and send one consistently ordered paste. Kitty paste
notifications (above) don't replace the payload.

## Mouse

Convert pointer coords to **zero-based viewport cells** after subtracting
padding and chrome; clamp/reject outside the grid. libtermy encodes the
protocol coordinates.

Rust: `encode_mouse_report` with `terminal.mouse_mode()`, kind, position,
modifiers. C: `termy_terminal_encode_mouse` (reads mode internally).

| C `kind` | Meaning |
| --- | --- |
| 1 | Press |
| 2 | Release |
| 3 | Drag |
| 4 | Move |
| 5, 6 | Wheel up, down |
| 7, 8 | Wheel left, right |

`button`: 1 left, 2 middle, 3 right. Empty result = send nothing. The host
decides whether a gesture selects, scrolls history, or reports; mouse
reporting and local scrollback are separate actions.

## Scrollback and coordinates

`scroll_display(delta)` / `termy_terminal_scroll_display`: positive = older
history, negative = toward live. `scroll_to_bottom` returns to live. Repaint
when it reports a change.

| Coordinate | Meaning |
| --- | --- |
| Frame / dirty-span / mouse row | Zero-based visible viewport row |
| `display_offset` | Rows above the live bottom; 0 = live |
| `history_size` | Retained history rows |
| Search result `row` | Zero-based row over history + live screen, oldest first |
| Rust buffer-line visitors | Signed engine-neutral lines; see `line_bounds()` |

```text
viewport_row = result.row - (history_size - display_offset)
```

Compute in a signed type or bounds-check first. Highlight only visible rows.
Re-run searches after output, resize or trimming; rows aren't stable IDs.

## Search

`Terminal::search` / `termy_terminal_search` cover history **and** live
screen; default case-insensitive literal. `search_with_options` /
`termy_terminal_search_with_options` for case-sensitive or regex. Results:
buffer row, inclusive `start_col`/`end_col`, line text. Free with
`termy_search_batch_free`. Rust `search_shared_with_options` shares line
strings across matches on a row.

Empty queries and invalid regexes return no matches; validate patterns
separately if the UI must tell them apart. Matching is per row: no multiline
matches across wraps. Standalone `search_frame` helpers search only the frame
passed in.

## Links and selection

- `hyperlink_at(row, col)` / `termy_terminal_hyperlink_at`: OSC 8 only, at a
  **viewport** position. C reports "found" separately from status; free with
  `termy_hyperlink_free`.
- `link_at(row, col)` / `termy_terminal_link_at`: OSC 8 first, then URLs,
  domains, existing file paths (relative to the pane cwd, returned as
  `file://`), possibly wrapped. Free with `termy_link_free`. Touches the
  filesystem: call on modifier-hover or click, not every mouse move.
- Opening links is the host's job. Validate schemes against an allowlist.
  Never auto-execute based on a terminal-provided cwd or link.
- Selection gestures, highlight, copy and accessibility are host jobs.
  Preserve wide-cell and wrap info; never slice UTF-8 by column.
