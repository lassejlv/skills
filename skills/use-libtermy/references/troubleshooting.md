# Native troubleshooting and validation

Sources: https://termy.sh/docs/developer/libtermy/troubleshooting.md,
https://termy.sh/docs/developer/libtermy/agents.md

Start from the deterministic display-only example ([rust.md](rust.md) or
[c-abi.md](c-abi.md)). Once it yields the expected cells, add the PTY, event
loop and renderer **one at a time**.

## Symptom → fix

| Symptom | Check | Fix |
| --- | --- | --- |
| Unresolved symbols / loader failure | Library path, arch, target triple, header ↔ binary match | Rebuild at the pinned revision; fix link + runtime search paths |
| PTY constructor fails | Shell exe, cwd, env, platform prereqs | Record status/error; try a known-good shell and directory |
| First frame blank | Did output arrive? Was first frame forced full? | Feed known bytes to a display terminal to split timing from parsing |
| Display-only input does nothing | Host calling `write` instead of transport | Send encoded bytes to the external process |
| Display-only loop spins | C display handles have no wake channel | Schedule from transport delivery |
| Corruption after incremental update | Span order, inclusive right bound | Apply spans sequentially into a retained full grid |
| Text stops repainting | Damage consumed twice, wakeups disabled, `has_more` ignored | One damage path; reschedule pending work |
| Cursor stuck at old position | Empty updates discarded | Copy metadata; invalidate old + new cursor rects |
| CJK drawn twice | Wide spacer cells drawn as text | Skip spacer text, keep its cell occupied |
| Combining text / underline variants lost | Compact cells used for rich typography | Use rich Rust reads |
| Glyph geometry everywhere on idle | Zero spans passed to planner | Zero spans = full plan; skip idle planning |
| Colors disagree with app queries | Host colors changed, query colors not | Apply same resolved appearance to runtime + renderer |
| Search highlights jump/wrap | Buffer rows treated as viewport rows | Convert via `history_size - display_offset`; refresh stale results |
| Remote app stalls on queries | Display-only replies discarded | Drain with reply host/callback; forward to transport |
| Clipboard reads never complete | Reply deferred past callback return | Reply synchronously; do async permission separately |
| Crash on teardown | Freed while waiter/task used handle | Stop → notify → join → cancel queued users → free |
| Memory grows per frame | Missing batch free, or output var overwritten | Audit every successful allocation's owner |
| Animated image freezes | No timer once output idles | Schedule from nonzero `next_frame_delay_ms`, refresh placements |

## Smoke-test matrix

Use deterministic parser fixtures where possible; test PTY behavior separately.

| Scenario | Expected evidence |
| --- | --- |
| ASCII + ANSI color | Correct text and colors in first full frame |
| Second chunk changing a small area | Patched retained grid == fresh full snapshot |
| Cursor move without text | Cursor redraws, no stale pixels |
| Resize smaller and larger | New dims, full retained buffer, aligned hit testing |
| Wide and combining text | No duplicate wide glyphs; documented compact/rich behavior |
| Box drawing, long/short Braille runs | Correct geometry; spinners shaped intentionally |
| Key press/repeat/release | Bytes follow the app's negotiated mode |
| Bracketed paste on/off | Exactly one delimited or plain payload |
| Mouse reporting on/off | App gets reports only when appropriate |
| Enough output for history | Scrolling works; search finds off-screen text with right highlights |
| Device/color query on display terminal | Reply reaches external process, not parser input |
| Clipboard denied + supported | Policy respected, requests always completed |
| Several queued event batches | `has_more` honored, UI not starved |
| Close while waiter blocked | Waiter exits before free; no late callbacks |
| Kitty static/animated image (if supported) | Correct clip, placement, release, timed redraw |

For incremental rendering, compare dimensions, **every** retained cell, and
cursor/scroll metadata against `snapshot()`, including after a scroll and a
resize. Comparing only the first full frame validates nothing.

## Repository checks

From the Termy repo root:

```sh
cargo test -p termy_core --test display_terminal
cargo test -p termy_core --test ffi_export_guard
cargo test -p termy_core
cargo build --release -p termy_core --lib
```

After an ABI change, rebuild the library before testing host examples so a
stale binary can't hide a mismatch. Then compile and run **the host** against
the new library. A core build doesn't prove callbacks or rendering.

Source map for verifying behavior at your pinned revision (verification only,
not public dependencies):

| Path | Verify |
| --- | --- |
| `crates/core/Cargo.toml` | Version, features, artifact types |
| `crates/core/include/termy.h` | C signatures, layouts, callbacks, concurrency |
| `crates/core/src/lib.rs` | Public Rust exports |
| `crates/core/src/runtime.rs` | Constructors, events, damage, visitors |
| `crates/core/src/frame.rs` | Compact and rich frame fields |
| `crates/core/src/ffi/mod.rs` | Numeric mappings, ownership, C → Rust behavior |
| `crates/core/src/config.rs` | Config loading, diagnostics, appearance |
| `crates/core/src/keyboard.rs`, `mouse_protocol.rs` | Key names, mode-aware encoding |
| `crates/core/src/protocol/` | Reply routing, clipboard contracts |
| `crates/core/src/glyph_geometry.rs` | Special-glyph plans |
| `crates/core/tests/display_terminal.rs` | Deterministic examples |
| `crates/core/tests/ffi_export_guard.rs` | Export/header guards |

If docs and source differ at your revision, trust the source and its tests.

## Completion criteria

Don't call an integration done after constructing a handle or seeing one
wakeup. Document: the pinned revision, platforms actually tested vs assumed,
allocation ownership, the terminal-owner thread, shutdown order, and limits
(compact-cell Unicode, unsupported clipboard/image features).

## Reporting a bug

Include: Termy commit, OS + arch, Rust or C API, PTY or display-only,
grid/cell dimensions, the smallest output byte sequence that reproduces it.
Rendering: frame API, damage kind/spans, expected vs actual retained cells.
FFI: function name + status code. Strip credentials and private terminal
content. Say which tests ran; separate parser results from visual results.
