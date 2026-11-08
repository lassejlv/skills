# libtermy C ABI: build, bindings, ownership, threading

Sources: https://termy.sh/docs/developer/libtermy/c.md,
https://termy.sh/docs/developer/libtermy/reference.md

The C ABI lives in `termy_core`. Public header:
`crates/core/include/termy.h` (authoritative for every signature and layout).
Generate bindings from it; never reconstruct structs from prose. Field order,
`bool`, `size_t`, alignment and pointer width are all ABI. No prebuilt native
SDK is distributed: build `termy_core` and vendor the header from the same
checkout.

## Build

```sh
cargo build --release -p termy_core --lib
```

| Platform | Shared library |
| --- | --- |
| macOS | `target/release/libtermy_core.dylib` |
| Linux | `target/release/libtermy_core.so` |
| Windows | `target/release/termy_core.dll` |

`--target` adds a triple directory; `CARGO_TARGET_DIR` changes the base. Match
the host's architecture. Artifacts: `rlib`, `cdylib`, `staticlib`
(`libtermy_core.a` / `termy_core.lib`). Static linking also needs Rust std's
system libs:

```sh
cargo rustc --release -p termy_core --lib --crate-type staticlib -- --print native-static-libs
```

Host owns PTY and only needs parser/screens/encoders? Use the engine-only
library instead: [engine.md](engine.md).

## Deterministic example

```c
#include "termy.h"
#include <stdio.h>

int main(void) {
    int result = 1;
    TermyFfiTerminal *terminal = NULL;
    TermyFfiFrameUpdate update = {0};
    TermyFfiSize size = termy_size_default();
    size.cols = 80;
    size.rows = 24;

    TermyFfiStatus status = termy_display_terminal_new(size, &terminal);
    if (status != TERMY_FFI_OK) goto cleanup;

    const uint8_t output[] = "\x1b[32mhello from libtermy\x1b[0m\r\n";
    status = termy_terminal_feed_output(terminal, output, sizeof(output) - 1);
    if (status != TERMY_FFI_OK) goto cleanup;

    status = termy_terminal_take_frame_update(terminal, true, &update);
    if (status != TERMY_FFI_OK) goto cleanup;
    if (update.damage_kind != 1 || update.cells_len != 80 * 24) goto cleanup;

    // ASCII only here; a real renderer must handle Unicode scalars.
    for (size_t col = 0; col < sizeof("hello from libtermy") - 1; ++col)
        putchar((int)update.cells_ptr[col].codepoint);
    putchar('\n');
    result = 0;

cleanup:
    if (status != TERMY_FFI_OK) fprintf(stderr, "libtermy status: %d\n", status);
    termy_frame_update_free(&update);
    termy_terminal_free(terminal);
    return result;
}
```

```sh
cc -std=c11 -Wall -Wextra example.c \
  -I crates/core/include -L target/release -ltermy_core \
  -Wl,-rpath,"$PWD/target/release" -o example
./example
```

The absolute rpath is for local dev only. Distribution: ship the library with
the app and set the platform runtime search path. Windows: use the import lib
from your toolchain and ship the matching DLL.

## PTY with configuration

```c
#include "termy.h"

TermyFfiStatus create_terminal(TermyFfiTerminal **out_terminal) {
    TermyFfiConfig *config = NULL;
    TermyFfiRenderConfig render = {0};
    TermyFfiStatus status = termy_config_load_default(&config);
    if (status != TERMY_FFI_OK) return status;

    status = termy_config_render_config_for_appearance(config, 1 /* dark */, &render);
    if (status == TERMY_FFI_OK) {
        TermyFfiSize size = termy_size_default();
        size.cols = 100;
        size.rows = 30;
        size.cell_width = render.cell_width;
        size.cell_height = render.cell_height;

        TermyFfiTerminalOptions options = {0};
        options.config = config;
        // Optional: UTF-8 working directory, startup command, env overrides.
        status = termy_terminal_new_with_options(size, &options, out_terminal);
    }
    termy_render_config_free(&render);
    termy_config_free(config);
    return status;
}
```

- Appearance `0` light, `1` dark; pass the real system appearance.
- The constructor copies launch data; inputs only need to live for the call.
- Env entries are separate key/value pointers + byte lengths, **not**
  `KEY=value` strings.
- Constructors without a config use runtime defaults; they do not load the
  user's settings implicitly.
- Writing input then immediately snapshotting does not wait for the child.
  Drain events and take frames after output arrives.

## Display-only scheduling

`termy_display_terminal_new` has **no wake channel**. Schedule from the
transport's output callback: feed bytes → drain replies → request an update.
Never loop on `termy_terminal_wait_for_wakeup` for a display handle.

PTY handles: one dedicated waiter thread may call
`termy_terminal_wait_for_wakeup(timeout_ms)` (0 polls; result in `out_woke`)
and marshal the notification onto the thread that serially drives the handle.

## Binding from Swift / Go / Python / C++

macOS: prefer the Swift SDK ([swift.md](swift.md)). To bind yourself, use a
bridging header or a Clang module next to a vendored `termy.h`:

```text
module CLibTermy {
    header "termy.h"
    link "termy_core"
    export *
}
```

Wrap the opaque handle in **one owner** that serializes calls and runs the
shutdown sequence before release. For any language:

- Keep borrowed input bytes alive for the whole call. Lengths are **byte**
  counts; buffers are not NUL-terminated.
- Copy returned data into host storage before calling its free function, or
  keep the owning batch alive until consumed.
- Preserve the full pointer/length/capacity tuple until freeing.
- Keep callbacks and their user-data alive through the synchronous drain.
- Free with `termy_*_free` only, never the host allocator.

## API map

| Task | Rust | C |
| --- | --- | --- |
| Load user config | `load_config_from_default_path` | `termy_config_load_default` |
| Parse config text | `load_config_from_contents` | `termy_config_from_contents` |
| Launch PTY | `Terminal::new` + variants | `termy_terminal_new_with_options` |
| Parser without PTY | `Terminal::new_display` | `termy_display_terminal_new` |
| Deliver process output | `feed_output` | `termy_terminal_feed_output` |
| Output + ordered replies | `feed_output_with_replies` | `termy_terminal_feed_output_with_replies` |
| Mirror without replying | `set_protocol_replies_enabled(false)` | `termy_terminal_set_protocol_replies_enabled` |
| Multiplexer pane passthrough replies | `set_protocol_replies(TerminalProtocolReplies::Passthrough)` | none |
| Save full state | `encode_snapshot` | `termy_terminal_snapshot_encode` |
| Restore full state | `restore_snapshot` | `termy_terminal_snapshot_decode`, `termy_terminal_snapshot_restore` |
| Input to owned PTY | `write` | `termy_terminal_write` |
| Resize | `resize` | `termy_terminal_resize` |
| Full compact frame | `snapshot` | `termy_terminal_snapshot` |
| Consume compact update | `frame_update` | `termy_terminal_take_frame_update` |
| Consume damage only | `take_damage_snapshot` | `termy_terminal_take_damage` |
| Rich text + palette | `render_read`, visitors | none |
| Encode key | `keystroke_to_input_with_options` | `termy_terminal_encode_key_with_options` |
| Encode mouse | `encode_mouse_report` | `termy_terminal_encode_mouse` |
| Drain events + replies | `drain_events` + `TerminalReplyHost` | `termy_terminal_drain_events_with_clipboard` |
| Search | `search_with_options` | `termy_terminal_search_with_options` |
| OSC 8 link at cell | `hyperlink_at` | `termy_terminal_hyperlink_at` |
| Any link (OSC 8, URL, path) | `link_at` | `termy_terminal_link_at` |
| Scroll viewport | `scroll_display`, `scroll_to_bottom` | `termy_terminal_scroll_display`, `termy_terminal_scroll_to_bottom` |
| History limit | `set_scrollback_history` | `termy_terminal_set_scrollback_history` |
| Clear history | `clear_scrollback` | `termy_terminal_clear_scrollback` |
| Special-glyph plan | `terminal_glyph_plan` | `termy_cells_build_glyph_render_plan` |
| Image placements | `kitty_graphics_snapshot` | `termy_terminal_kitty_graphics_placements` |

## Allocation ownership

Zero-initialize output structs; check status before reading. Free a previous
successful result before reusing its output variable; the next call does not
free it for you.

| Owned result | Free with | Nested data it owns |
| --- | --- | --- |
| `TermyFfiTerminal *` | `termy_terminal_free` | Terminal + wake channel |
| `TermyFfiConfig *` | `termy_config_free` | Parsed config |
| `TermyFfiFrame` | `termy_frame_free` | Cell array |
| `TermyFfiFrameUpdate` | `termy_frame_update_free` | Cells + dirty spans |
| `TermyFfiDamage` | `termy_damage_free` | Dirty spans |
| `TermyFfiGlyphRenderPlan` | `termy_glyph_render_plan_free` | Entries, rects, strokes |
| `TermyFfiEventBatch` | `termy_event_batch_free` | Events + each payload |
| `TermyFfiSearchBatch` | `termy_search_batch_free` | Matches + each line |
| `TermyFfiHyperlink` | `termy_hyperlink_free` | URI bytes |
| `TermyFfiLink` | `termy_link_free` | URI bytes |
| `TermyFfiConfigDiagnosticBatch` | `termy_config_diagnostics_free` | Diagnostics + messages |
| `TermyFfiRenderConfig` | `termy_render_config_free` | Font family + theme bytes |
| `TermyFfiKittyGraphicsBatch` | `termy_kitty_graphics_batch_free` | Placements + PNG buffers |
| Standalone `TermyFfiBytes` (encoders, snapshots, replies, config strings) | `termy_buffer_free` | Byte buffer |

- Never free a nested byte field separately from its batch.
- Never edit returned pointers/lengths/capacities.
- Copying an owning struct does not duplicate ownership: freeing both copies
  is a double free.
- `TermyFfiByteSlice` is borrowed, has no free function, and lives only for
  the call/callback that supplied it.
- The containing API decides ownership, not the field type: a `TermyFfiBytes`
  inside a batch belongs to the batch.

## Threading and shutdown

A `TermyFfiTerminal` is **not** internally synchronized. Serialize every call
on a handle, including reads and encoders. Separate handles are independent.
Only `termy_terminal_wait_for_wakeup` and `termy_terminal_notify_wakeup` may
run concurrently (they touch the wake channel only).

Safe shutdown with a waiter:

1. Stop scheduling terminal work; set the host shutdown flag.
2. Let any in-flight serialized call finish.
3. `termy_terminal_notify_wakeup` so the waiter sees the flag.
4. Join the waiter; make sure queued tasks/callbacks can't touch the handle.
5. `termy_terminal_free` exactly once; clear the pointer.

Notify alone is not enough: the waiter must exit, not wait again. Never free
while any call (including a blocking wait) uses the handle. Clipboard and
reply callbacks must not re-enter the handle, even on the same thread.

## Status codes

| Status | Value | Meaning |
| --- | --- | --- |
| `TERMY_FFI_OK` | 0 | Success; result may still be empty |
| `TERMY_FFI_NULL` | 1 | Required pointer was null |
| `TERMY_FFI_INVALID_UTF8` | 2 | Text input not valid UTF-8 |
| `TERMY_FFI_SPAWN_FAILED` | 3 | Child startup failed |
| `TERMY_FFI_CONFIG_LOAD_FAILED` | 4 | Config could not load |
| `TERMY_FFI_UNKNOWN_KEY` | 5 | Unsupported key/value kind |
| `TERMY_FFI_WRITE_FAILED` | 6 | Write failed |
| `TERMY_FFI_SERIALIZE_FAILED` | 7 | Serialization failed |
| `TERMY_FFI_PANICKED` | 8 | Rust panic caught at the boundary |
| `TERMY_FFI_INVALID_ARGUMENT` | 9 | Arguments rejected |
| `TERMY_FFI_UNSUPPORTED_SNAPSHOT_VERSION` | 10 | Snapshot from incompatible format |
| `TERMY_FFI_INVALID_SNAPSHOT` | 11 | Not a snapshot, truncated, or corrupt |

`OK` from an encoder can mean zero bytes; from search, zero matches. Success
does not prove the child processed input or exited cleanly. On failure, don't
read the output as a result; log API name + status. After `PANICKED`, tear
down and recreate. Panic catching does not make bad pointers, mismatched
headers or concurrent access safe.

## Adjacent APIs (not needed to embed one terminal)

The header also has settings persistence (`termy_settings_*`, writes to disk),
CLI installation, native config getters, and tmux control helpers. A tmux
control handle has its own lifetime: `termy_tmux_control_close`,
`termy_tmux_control_notifications_free`, `termy_buffer_free` for standalone
command output. Keep session-manager features out of the frame loop.
