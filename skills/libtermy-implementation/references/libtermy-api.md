# libtermy API Reference

Source basis: Termy docs and repository main at commit `4be935f5647c05f2ab53dd2ad723ab7bdec6d2d0` from 2026-07-08. Re-check current sources before editing because libtermy is experimental.

Source URLs:
- https://termy.sh/docs/developer/libtermy
- https://github.com/lassejlv/termy/tree/main/crates/core
- https://github.com/lassejlv/termy/tree/main/crates/ffi

## Contents

- Architecture
- Rust Embedding
- C ABI Embedding
- Ownership
- Threading And Wakeups
- Frames And Damage
- Events, Search, Links, And Input
- Adding ABI Surface
- Baseline Validation

## Architecture

`libtermy` has two public layers:

- `termy_core`: Rust API for a headless terminal surface.
- `termy_ffi`: C ABI wrapper over `termy_core`, with opaque handles and C-compatible structs.

`termy_core` owns PTY startup, terminal parsing, input writes, resize, event draining, damage snapshots, frame snapshots, config conversion, search, link detection, shell integration, OSC interception, keyboard/mouse protocol helpers, launch environment, font/cell metrics, and render metrics. It must not depend on GPUI, the desktop app, Swift, or `termy_ffi`.

`termy_ffi` should stay a thin wrapper. When adding or changing ABI, keep `crates/ffi/include/termy.h`, `crates/ffi/src/lib.rs`, and FFI tests synchronized.

## Rust Embedding

Prefer direct `termy_core::Terminal` use when the host is Rust:

```rust
let loaded = termy_core::load_config_from_default_path()?;
let metrics = termy_core::measure_cell_from_config(&loaded.app_config);
let terminal = termy_core::Terminal::new(
    termy_core::TerminalSize {
        cols: 80,
        rows: 24,
        cell_width: metrics.cell_width,
        cell_height: metrics.cell_height,
    },
    None,
    None,
    None,
    Some(&loaded.runtime_config),
    None,
)?;
terminal.write(b"echo hello\r");
let update = terminal.frame_update(false);
```

Use `Terminal::new_display(size, runtime_config)` plus `feed_output(bytes)` for display-only surfaces such as tmux control-mode panes. A display terminal has no PTY; `write` is a no-op.

Use `load_config_from_default_path`, `load_config_from_path`, or `load_config_from_contents` to get `AppConfig`, diagnostics, and `TerminalRuntimeConfig`. Use `measure_cell` or `measure_cell_from_config` for layout. Do not duplicate config parsing or font metric logic in the host.

Useful public core APIs:

- Terminal lifecycle: `Terminal::new`, `Terminal::new_display`, `write`, `feed_output`, `resize`, `nudge_resize`, `child_pid`.
- Frames: `snapshot`, `frame_update(force_full)`, `TermyFrame`, `TermyFrameUpdate`, `TermyCell`, `TermyColor`.
- Damage: `take_damage_snapshot`, `TerminalDamageSnapshot`, `TerminalDirtySpan`.
- Events: `drain_events`, `TerminalEvent`, `TerminalReplyHost`.
- Input: `keystroke_to_input`, `encode_mouse_report`, `keyboard_mode`, `mouse_mode`, `bracketed_paste_mode`.
- Scroll/search/link: `scroll_display`, `scroll_to_bottom`, `clear_scrollback`, `search_with_options`, `hyperlink_at`.
- Runtime config: `TerminalRuntimeConfig`, `TerminalOptions`, `set_scrollback_history`, `set_query_colors`.

## C ABI Embedding

Use the header at `crates/ffi/include/termy.h` as the source of truth.

Common constructor flow:

1. Start from `termy_size_default()`.
2. Override `cols`, `rows`, `cell_width`, and `cell_height` from render config or host geometry.
3. Load config with `termy_config_load_default`, `termy_config_load_path`, or `termy_config_from_contents`.
4. Read render config with `termy_config_render_config_for_appearance` or `termy_config_render_config`.
5. Create the terminal with `termy_terminal_new_with_options` when the host controls config, working directory, startup command, or env overrides.
6. Drive input through `termy_terminal_write` after encoding key/mouse input through libtermy when possible.
7. Drain events, then take a frame update, then present.

Prefer `termy_terminal_take_frame_update(handle, force_full, &out_update)` for render loops. Use `termy_terminal_snapshot` for one-off full snapshots, initial diagnostics, or simple non-performance-critical hosts.

## Ownership

Every returned allocation has a matching free call:

| Returned value | Free with |
| --- | --- |
| `TermyFfiTerminal *` | `termy_terminal_free` |
| `TermyFfiConfig *` | `termy_config_free` |
| `TermyFfiFrame` | `termy_frame_free` |
| `TermyFfiFrameUpdate` | `termy_frame_update_free` |
| `TermyFfiDamage` | `termy_damage_free` |
| `TermyFfiEventBatch` | `termy_event_batch_free` |
| `TermyFfiSearchBatch` | `termy_search_batch_free` |
| `TermyFfiConfigDiagnosticBatch` | `termy_config_diagnostics_free` |
| `TermyFfiRenderConfig` | `termy_render_config_free` |
| `TermyFfiHyperlink` | `termy_hyperlink_free` |
| standalone `TermyFfiBytes` | `termy_buffer_free` |

Do not free event payloads owned by an event batch, search match lines owned by a search batch, or config diagnostic messages owned by a diagnostic batch. The batch free owns those payloads.

FFI byte inputs are copied by constructors where documented, including terminal options env vars. The caller may release its input arrays after the call returns.

## Threading And Wakeups

A `TermyFfiTerminal` handle is not internally synchronized. Serialize all calls for a given handle with one exception: `termy_terminal_wait_for_wakeup` and `termy_terminal_notify_wakeup` touch the wake channel and are intended for one dedicated waiter plus serialized terminal calls.

Never free a handle while another thread is inside any FFI call. For wakeup threads, stop issuing terminal calls, call `termy_terminal_notify_wakeup`, join the waiter, then call `termy_terminal_free`.

Use wakeups to avoid idle polling. While active, a display link can poll at frame cadence; while idle, the wake channel should schedule immediate polling only when output arrives.

## Frames And Damage

`TermyFfiCell` has no position. Interpret cells from context:

- Full frame/update: row-major, `index = row * cols + col`.
- Partial update: cells appear in dirty-span order, left to right for each span.

`TermyFfiFrameUpdate.damage_kind` identifies none/full/partial damage. Treat dimension changes, display offset changes, history size changes, render-config changes, or forced startup refresh as full redraw triggers in the host.

Do not discard partial damage. Store the previous frame, patch changed cells into it, and rebuild or redraw only affected rows/rects.

## Events, Search, Links, And Input

Drain events before presenting a frame. Events include wakeup, title, reset title, bell, exit, clipboard store, shell prompt/command lifecycle, progress, and working directory.

Search APIs return terminal-buffer match ranges. `termy_terminal_search_with_options` supports case-sensitive and regex flags. The docs note visible-frame behavior; current core searches the full buffer. Re-check the exact current implementation before changing UX around search scope.

Use `termy_terminal_hyperlink_at` for OSC 8 links. Hosts may fall back to local heuristic link detection, but open actions must validate schemes because terminal output is attacker-influenced.

Use `termy_terminal_encode_key` and `termy_terminal_encode_mouse` so host input respects negotiated terminal modes, including Kitty keyboard and mouse protocols. Before paste, query `termy_terminal_bracketed_paste_mode`; if enabled, wrap paste bytes and strip embedded bracket markers from the payload.

## Adding ABI Surface

When adding a capability:

1. Put behavior in `termy_core` unless it is purely host plumbing.
2. Add a small FFI wrapper in `crates/ffi/src/lib.rs`.
3. Update `crates/ffi/include/termy.h`.
4. Keep structs C-compatible: fixed-size primitive fields, explicit pointers/lengths/capacities, no Rust-only layout assumptions.
5. Catch panics at the FFI boundary and return `TERMY_FFI_PANICKED`.
6. Add `cargo test -p termy_core` coverage for behavior and `cargo test -p termy_ffi` coverage for ABI contract.
7. Update Swift bridge/tests only after the C ABI contract is stable.

## Baseline Validation

Run:

```sh
cargo test -p termy_core
cargo test -p termy_ffi
```

Use FFI tests such as `display_terminal.rs`, `c_header_contract.rs`, `ffi_export_guard.rs`, and tmux control tests as examples when expanding the ABI.
