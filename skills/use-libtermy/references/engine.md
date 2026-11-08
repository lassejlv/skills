# libtermy_engine: engine-only C library

Source: https://termy.sh/docs/developer/libtermy/engine.md

The VT parser, screens, scrollback, protocol state and input encoders as a
standalone C library. **No** PTY, config files, threads, timers, keyring,
fonts or network code. Use it when the host owns the process and transport:
a multiplexer client mirroring panes, a session recorder, or a server holding
the authoritative terminal per pane. If libtermy should launch the shell, use
[c-abi.md](c-abi.md) instead.

Header: `crates/engine_ffi/include/termy_engine.h` (authoritative). At startup
check `termy_engine_abi_version() == TERMY_ENGINE_ABI_VERSION`. Build both
sides of a connection from the same revision when you can; snapshots from one
version may be rejected by another.

## Build and package

```sh
cargo build --release -p termy_engine_ffi --lib
# -> target/release/libtermy_engine.a (+ shared lib, skipped on musl)

scripts/package-libtermy-engine.sh x86_64-unknown-linux-musl aarch64-unknown-linux-musl
scripts/package-libtermy-engine.sh aarch64-apple-darwin
# -> dist/libtermy-engine-<target>.tar.gz (static lib, header, module map, link flags)
# macOS also -> dist/TermyEngine.xcframework (usable as a SwiftPM binaryTarget)
```

When linking the `.a` yourself, add the system libs from the package's
`lib/link-flags.txt`.

## Server and replicas

Authoritative terminal: replies enabled (default). Replies to DA, DSR,
DECRQM, color reports come back from `termy_engine_feed` immediately and in
byte order; write them straight to the program.

```c
TermyEngineOptions options = termy_engine_options_default();
options.cols = 120;
options.rows = 40;

TermyEngine *server = NULL;
termy_engine_new(&options, &server);

TermyEngineBytes replies = {0};
termy_engine_feed(server, pty_bytes, pty_len, &replies);
write_to_pty(replies.ptr, replies.len);
termy_engine_bytes_free(&replies);
```

Replica: parses the same bytes, never answers (the server already did). Start
from a server snapshot, then feed every byte the server receives afterwards.

```c
TermyEngineBytes snapshot = {0};
termy_engine_snapshot_encode(server, &snapshot);
send_to_client(snapshot.ptr, snapshot.len);
termy_engine_bytes_free(&snapshot);

/* Client */
TermyEngine *replica = NULL;
TermyEngineStatus status = termy_engine_snapshot_decode(
    snapshot_ptr, snapshot_len, TERMY_ENGINE_REPLIES_DISCARD, &replica);
if (status == TERMY_ENGINE_UNSUPPORTED_SNAPSHOT_VERSION) { /* see Versions */ }
termy_engine_feed(replica, output_ptr, output_len, NULL);
```

`termy_engine_set_reply_mode` switches an existing handle between modes.

**Synchronized output (`?2026`)** buffers until the program ends the update.
There is no timer: poll `termy_engine_synchronized_deadline` and call
`termy_engine_tick` after the deadline so an unterminated update still commits.

## Snapshots

Contain everything that affects how the terminal reacts to later output: both
screens and all scrollback (graphemes, styles, OSC 8, underline colors, wrap
flags), cursor state and DECSC saves, scroll region/margins/origin/tab stops,
charsets and every DEC/ANSI mode (mouse, bracketed paste, focus, alternate
scroll, DECCKM, DECKPAM, kitty keyboard flag stacks), OSC 4/10/11/12
overrides, title + title stack, OSC 7 cwd, OSC 7501 status, the parser's
in-progress sequence, a pending synchronized update, scrollback/payload
limits, and (v2+) kitty graphics including chunked uploads. OSC 1337 inline
images are stored as kitty images.

Decode + feed B == original + feed B, including which scrollback rows evict.
Snapshots **exclude**: queued replies and events (drain first), render damage
(a decoded engine starts with a full frame), and an OSC 1337 multipart image
still receiving parts.

Format: magic `TRMYSNAP` + version, little-endian; portable Linux ↔ macOS.
`termy_engine_snapshot_peek_version` reads the version without decoding.
~16 MiB scrollback encodes in tens of ms (release). Images stored as PNG.

### Versions

Each release decodes every version from `termy_engine_snapshot_min_version()`
to `termy_engine_snapshot_version()` and can encode any of them with
`termy_engine_snapshot_encode_version`. The **newer side adapts**: a newer
client decodes older snapshots as-is; a newer server encodes for an older
client after learning its `termy_engine_snapshot_version()` in the attach
handshake.

| Version | Adds |
| --- | --- |
| 1 | First format |
| 2 | Scrollback byte limit (and >20,000 rows), payload limits, kitty graphics |

Encoding v1 keeps the newest 20,000 rows, drops kitty graphics, and gives the
client default limits. Identical eviction is only guaranteed on the same
release.

### Scrollback limit

History keeps at most `scrollback_rows` rows and `scrollback_bytes` (16 MiB
default), whichever binds first. `TERMY_ENGINE_SCROLLBACK_UNLIMITED` rows =
bound by bytes only. Charges are by value so server and replicas evict the
same rows. **Don't** call `termy_engine_compact_history` on a server or its
replicas (it changes how later rows are stored). Packed rows at 120 cols cost
~650 B, so 16 MiB ≈ 25,000 rows. Live changes:
`termy_engine_set_scrollback`, `termy_engine_set_scrollback_bytes`.

### Payload limits

OSC/DCS strings over `max_string_bytes` (64 KiB default) and OSC 52 writes
over `max_clipboard_bytes` (8 MiB) are dropped whole. Defaults are maxima: you
can lower, not raise. `termy_engine_set_payload_limits` on a live handle.
Server and replicas should match; snapshots carry them. Kitty/OSC 1337 images
have their own limit.

## Frames

`termy_engine_frame` returns changes since the last frame. Full on first call,
on `force_full`, and whenever size, active screen, viewport scroll, palette or
reverse video changed; otherwise spans list every changed cell (including
scrolled rows). Frame pointers **borrow handle-owned buffers** valid until the
next frame or line read on that handle: no allocation, nothing to free.

`TermyEngineCell`:

- first scalar of the grapheme cluster (rest in the frame's grapheme array)
- width role: narrow, wide, spacer tail, spacer head (wide glyph wrapped)
- raw colors: `0` default, `0x01000000 | n` palette `n`, `0x02RRGGBB` RGB
- all SGR attributes, underline style + color, hyperlink index
- `STYLED` and `BLANK` flags so renderers can skip plain blanks

Cursor: shape, blink, visibility, in-viewport, on-right-half-of-wide-glyph.
Resolve colors with `termy_engine_effective_colors` after
`termy_engine_set_default_colors`. `termy_engine_read_lines` reads any lines,
scrollback included, in the same format.

## State and queries

- `termy_engine_mode`: DECRQM-style; 0 unknown, 1 set, 2 reset, 3 permanently set.
- `termy_engine_get_state`: size, cursor, mouse tracking/encoding, focus
  reporting, alternate scroll, bracketed paste, keypad/cursor-key modes, kitty
  flags, scrollback counts.
- `termy_engine_title`, `termy_engine_working_directory` (a snapshot-restored
  replica has them without seeing events).
- `termy_engine_scrollbar`, `termy_engine_scroll_viewport` (top/bottom/row).
- `termy_engine_next_event`: bell, title, cwd, progress, clipboard, program
  status, one at a time.

## Encoders (return bytes, never write)

- `termy_engine_encode_key`: legacy, DECCKM, DECKPAM, all kitty flags. If the
  host reports which Option key is held, only configured sides act as Alt;
  pass composed text in `text` (legacy sends it as-is, Space included, e.g.
  macOS Option+Space → U+00A0) unless Control/Command is held.
- `termy_engine_encode_mouse`: X10/normal/button/any-event tracking;
  X10/UTF-8/SGR/SGR-pixel encodings; buttons 1–11. SGR pixel (`?1016`) needs
  `pixel_mouse_reports` in options.
- `termy_engine_encode_paste`: line endings → CR, strips dangerous control
  chars, adds bracketed markers when `bracketed` is passed.
- `termy_engine_encode_focus`: `CSI I` / `CSI O`; send only when focus
  reporting is on.

## Text and selection

`termy_engine_read_text` returns a range (or whole buffer for NULL) as plain
text, VT text with SGR + OSC 8, or HTML; options join soft wraps and trim
trailing blanks. The host owns the selection state machine.
`termy_engine_select_word` / `termy_engine_select_line` give the word/logical
line under a cell across soft wraps. Anchor selections with
`scrolled_into_history` from state; resize reflows without updating it, so
reset anchors on resize.

## Not included

- Kitty graphics placements in frames (parsed, stored, snapshotted, but not
  exposed by the C API yet).
- Platform keycodes: keys use Termy key names.
