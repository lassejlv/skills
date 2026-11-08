---
name: use-libtermy
description: Embed Termy's terminal engine in an app. Covers libtermy (the termy_core Rust crate, its termy.h C ABI, the libtermy_engine static C library, and the Swift SDK with TermyAppKit Metal views) and the @termysh web packages (@termysh/web browser terminal, @termysh/xterm xterm.js drop-in, @termysh/core headless WebAssembly engine, @termysh/pty node-pty replacement). Use when building a native or browser terminal on libtermy or @termysh, wiring a PTY or WebSocket shell, rendering frames and dirty spans, encoding keyboard/mouse/paste input, draining events and protocol replies, binding the C ABI from Swift/Go/Python/C++, migrating from xterm.js or node-pty, setting up wasm loading in Vite/Next.js/webpack/esbuild, or debugging blank terminals, stalled programs, wrong wrap width, leaks, or teardown crashes. For changes inside the Termy repository itself or its macOS performance gates, use libtermy-implementation.
---

# Use libtermy

libtermy is Termy's embeddable terminal engine. It parses VT output, keeps the
grid and scrollback, runs PTYs, encodes input, and reports events, search
results and renderer-neutral frames. **It is an engine, not a widget**: your
host owns the window, rendering, fonts, clipboard policy and lifecycle. The
`@termysh` packages compile the same Rust engine to WebAssembly and add a
browser renderer.

Everything is **beta / pre-1.0**. Neither Rust source compatibility, C struct
layouts, nor npm APIs are stable between releases. Pin a version and validate
upgrades.

## Pick the surface first

| Building | Use | Read |
| --- | --- | --- |
| Native Rust app | `termy_core` crate (not a crate called `libtermy`) | [rust.md](references/rust.md) |
| macOS app in Swift / SwiftUI | Swift SDK `sdk/swift`: `Termy` + `TermyAppKit` | [swift.md](references/swift.md) |
| C, C++, Objective-C, Go, Python, any FFI host | `termy_core` C ABI, header `crates/core/include/termy.h` | [c-abi.md](references/c-abi.md) |
| Multiplexer client, replica terminals, recorder, static engine-only lib | `libtermy_engine` (`termy_engine.h`): no PTY, config, fonts or threads | [engine.md](references/engine.md) |
| Remote/SSH/replay viewer on native | Display-only terminal in any of the above | [events-and-input.md](references/events-and-input.md) |
| New browser terminal | `@termysh/web` | [web.md](references/web.md) |
| Replacing xterm.js | `@termysh/xterm` | [web-xterm.md](references/web-xterm.md) |
| Own renderer, web worker, Node/Bun, tests, server-side screen reading | `@termysh/core` | [web-core.md](references/web-core.md) |
| Server-side shell for a browser terminal; replacing node-pty | `@termysh/pty` | [web-pty-and-connect.md](references/web-pty-and-connect.md) |

Then load only what the task needs:

- Rendering, damage, cells, glyph geometry, kitty images → [rendering.md](references/rendering.md)
- Events, protocol replies, clipboard, wakeups, keyboard, mouse, paste, scrollback, search, links → [events-and-input.md](references/events-and-input.md)
- Config loading, cell measuring, appearance, live resize → [configuration.md](references/configuration.md)
- C ownership/free pairs, threading, shutdown, status codes → [c-abi.md](references/c-abi.md)
- Bundlers, React/Next/Vue, wasm serving, CSP → [web-frameworks.md](references/web-frameworks.md)
- Native symptoms, smoke-test matrix, bug reports → [troubleshooting.md](references/troubleshooting.md)
- Web symptoms → [web-troubleshooting.md](references/web-troubleshooting.md)

## Before writing code: record these decisions

Infer them from the existing host where possible; do not add a new parser, GUI
framework or session manager just to make an example run.

| Decision | Record |
| --- | --- |
| Revision | Exact Termy commit (native) or exact `@termysh/*` version (web) |
| API | Rust, C ABI, Swift SDK, engine-only, or which `@termysh` package |
| Session ownership | libtermy owns the PTY, or display-only with an external transport |
| Rendering | Toolkit, retained grid, coordinate scale, font source |
| Scheduling | Terminal-owner thread, output notification path, host timers |
| Host policy | Clipboard access, allowed URL schemes, paste behavior, shutdown |

## Core workflow (native)

1. **Smoke test first.** Build a display-only terminal, `feed_output` known
   bytes (`"\x1b[32mhello from libtermy\x1b[0m\r\n"`), force a full frame and
   assert the text. This separates build/ABI/frame bugs from shell timing.
2. **Measure, then size.** Get cell size from config
   (`measure_cell_from_config` / `TermyFfiRenderConfig`), compute a nonzero
   grid (`floor(content / cell)`, clamped to `1..=u16::MAX`).
3. **Retain one full frame**, then patch partial updates in dirty-span order.
4. **Render loop:** schedule work on output/input/resize/timers → drain events
   and replies while `has_more` → take one frame update → patch retained grid
   and copy cursor/scroll metadata → paint affected content → idle.
5. **Add the PTY** (or the external transport) only after steps 1–4 work.
6. **Validate** with the smoke-test matrix in
   [troubleshooting.md](references/troubleshooting.md) before calling it done.

## Core workflow (web)

1. Install the package and give the container an explicit height.
2. Create the terminal in a mount effect, `open(element)`, and `dispose()` on
   unmount.
3. Pipe bytes both ways: server output → `term.write(Uint8Array)`;
   **all** `onData` (or `onBytes`) → server; **every** `onResize` → PTY resize;
   send the current size once the connection opens.
4. On exit, call `term.processExited()`.
5. Fix wasm loading for the bundler if needed (see
   [web-frameworks.md](references/web-frameworks.md)).

## Do

- Build the library, header, and bindings from the **same** Termy revision;
  pin `rev = "<full commit>"` for Git deps and commit the lockfile.
- Generate bindings from `termy.h`. Field order, `bool`, `size_t`, alignment
  and pointer width are ABI.
- Treat full-frame cells as row-major and partial-frame cells as the
  concatenation of each span, in span order. Span columns are **inclusive**
  (`len = right_col - left_col + 1`).
- Copy cursor, `display_offset` and `history_size` even when an update has no
  cell damage; invalidate both old and new cursor rects.
- Force a full frame on init, resize, appearance change, and cache loss.
- Drain events until `has_more` is false (with a host time budget; reschedule
  instead of starving the UI).
- Encode keys/mouse/paste with the engine, using the *current* modes, then
  send the bytes yourself. Treat an empty encoder result as valid.
- In display-only mode, route user input **and** protocol replies to the
  external process; resize the remote PTY through the transport too.
- Copy borrowed callback data before returning; answer clipboard reads
  synchronously inside the callback.
- Free every C result with its matching `termy_*_free`; free nested payloads
  only through their batch.
- Shut down in order: stop new work → let the in-flight call finish →
  `termy_terminal_notify_wakeup` → join the waiter → free once, clear pointer.
- Show config diagnostics to the user instead of silently using fallbacks.
- Validate URL schemes before opening links; call `link_at` on hover-with-
  modifier or click, not every mouse move.
- Web: spawn the PTY with `TERM=xterm-256color` and `COLORTERM=truecolor`;
  set `socket.binaryType = 'arraybuffer'` and write bytes, not decoded strings.
- Web: authenticate, check `Origin`, and use `wss://` before exposing any
  WebSocket that reaches a shell.

## Don't

- Don't reimplement VT parsing, key/mouse encoding, search, color-query
  replies, glyph geometry or dirty tracking in the host.
- Don't import private engine/backend types. `Terminal::with_term`,
  `TerminalOptions::term_config` and raw conversion helpers were removed in
  Rust 0.2.
- Don't reconstruct C structs from prose or trust a familiar function name to
  mean an unchanged layout.
- Don't index a partial update's cell array by absolute grid index.
- Don't call `take_damage_snapshot` / `termy_terminal_take_damage` and then
  expect `frame_update(false)` to contain the same damage. One consuming damage
  path per render cycle.
- Don't render `wide_character_spacer` cells as text (CJK appears twice), and
  don't claim compact `char`/`codepoint` is a full grapheme.
- Don't pass zero spans to the glyph planner on idle frames: zero spans means
  *full* plan.
- Don't hardcode arrow-key escapes or prefix ESC for Alt yourself.
- Don't call `write` on a display-only terminal (it's a no-op), and don't feed
  protocol replies back into `feed_output`.
- Don't wait on `termy_terminal_wait_for_wakeup` for a C display-only handle:
  it has no wake channel. Schedule from transport delivery.
- Don't call terminal methods concurrently on one C handle, or re-enter a
  handle from a clipboard/reply callback or a `_locked` visitor.
- Don't block the UI thread on the wake channel, render inside a wakeup
  notifier, or rely on a finalizer racing a waiter.
- Don't release Rust allocations with the host allocator, edit returned
  pointer/len/capacity, or free two copies of one owning struct.
- Don't guess cell size from a monospace ratio, or swap the font without
  remeasuring.
- Don't call `termy_settings_*` setters as a side effect of previewing; they
  write the user's Termy config to disk.
- Don't label an integration complete after constructing a handle or seeing
  one wakeup.
- Web: don't create the terminal during render or keep it in React state;
  don't forward only keystrokes (programs like `vim` hang without replies);
  don't parse escape sequences yourself; don't answer queries in two places
  (browser terminal *and* server `takeReplies()`).

## Ownership/choice cheatsheet

| Need | Rust | C |
| --- | --- | --- |
| PTY + flume wakeups | `Terminal::new` | `termy_terminal_new_with_options` |
| PTY + callback wakeups | `Terminal::new_with_wakeup_notifier` | (wait thread) `termy_terminal_wait_for_wakeup` |
| Parser only | `Terminal::new_display` | `termy_display_terminal_new` |
| Parser + notify on commit | `Terminal::new_display_with_wakeup_notifier` | n/a; schedule from transport |
| Full compact frame | `snapshot()` | `termy_terminal_snapshot` |
| Incremental frame | `frame_update(force_full)` | `termy_terminal_take_frame_update` |
| Rich text/underline/palette | `render_read`, generation visitors | none |
| Replies without draining | `feed_output_with_replies` | `termy_terminal_feed_output_with_replies` |
| Mirror without replying | `set_protocol_replies_enabled(false)` | `termy_terminal_set_protocol_replies_enabled` |
| tmux control-mode pane | `set_protocol_replies(Passthrough)` | none |

Full table: [c-abi.md](references/c-abi.md#api-map).

## Validation

Native, from a Termy checkout:

```sh
cargo test -p termy_core --test display_terminal
cargo test -p termy_core --test ffi_export_guard
cargo test -p termy_core
cargo build --release -p termy_core --lib
```

Then compile and run **the host** against the freshly built library. A core
build does not prove callbacks or rendering work. For incremental rendering,
compare the patched retained grid (cells, dimensions, cursor, scroll metadata)
with a fresh `snapshot()` after scroll and resize, not just after the first
frame. Swift: `just test-swift-sdk`.

Web: verify `term.ready` resolves, the wasm request returns
`application/wasm`, `vim`/`htop` draw without a key press, and wrap width
follows window resizes.

Report which checks actually ran, which platforms were tested versus assumed,
and known limits (compact-cell Unicode, unsupported clipboard/image features).

## Docs

Every page has a Markdown version: append `.md` to the URL. Fetch the live
page when the pinned revision may differ from these notes.

- Index: https://termy.sh/llms.txt, full text: https://termy.sh/llms-full.txt
- Native: https://termy.sh/docs/developer/libtermy.md (subpages `rust`, `c`,
  `engine`, `swift`, `swift-rendering`, `configuration`, `rendering`, `input`,
  `events`, `reference`, `agents`, `troubleshooting`)
- Web: https://termy.sh/docs/developer/web.md (subpages `connect`,
  `frameworks`, `options`, `themes`, `xterm`, `core`, `pty`, `troubleshooting`)
- Source of truth in a checkout: `crates/core/include/termy.h`,
  `crates/core/src/lib.rs` (public exports), `cargo doc -p termy_core --no-deps`.
