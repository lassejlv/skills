---
name: libtermy-implementation
description: Implement, integrate, review, or optimize Termy's libtermy embeddable terminal engine. Use when working with termy_core Rust API, termy_ffi C ABI, crates/ffi/include/termy.h, Rust/C/Swift bindings, macOS SwiftUI or AppKit terminal hosts, frame snapshots, damage-scoped rendering, FFI ownership, config/render metrics, PTY/display modes, terminal input, search, events, tmux display terminals, or performance gates for libtermy-based apps.
---

# libtermy Implementation

## Core Workflow

1. Inspect the current Termy checkout or upstream docs first. Treat libtermy as experimental and breaking-change prone.
2. Choose the narrowest surface:
   - Use `termy_core` for Rust embedders or changes that should be portable to FFI, WASM, JS, and tests.
   - Use `termy_ffi` for C, Swift, Objective-C, or any host that needs a stable C ABI.
   - Use the macOS Swift reference when building or tuning the native macOS host.
3. Keep terminal behavior in Rust core. Do not reimplement VT parsing, keyboard/mouse encoding, search, shell integration, color query replies, resize anchoring, config parsing, or dirty damage tracking in the host.
4. Build hosts around full-or-partial frame updates. Prefer `frame_update` / `termy_terminal_take_frame_update` over polling full snapshots in a render loop.
5. Validate at the boundary you touched before broadening test scope.

## Reference Routing

- Read `references/libtermy-api.md` when touching `termy_core`, `termy_ffi`, ABI structs/functions, event/search/input APIs, config/render config, ownership, threading, or Rust embedding.
- Read `references/macos-swift-host.md` when implementing a macOS Swift app, SwiftPM linking, `CTermy`, `LibTermyTerminal`, wakeup monitoring, AppKit rendering, panes/tabs, settings, or tmux display terminals.
- Read `references/optimization.md` when optimizing rendering, reducing FFI marshaling, tuning cadence, avoiding CPU/RSS regressions, reviewing performance PRs, or adding gates.

## Non-Negotiable Rules

- Serialize access to each `TermyFfiTerminal` handle unless the C header explicitly names the wake channel exception.
- Free every FFI result with its matching free function. Never free payloads owned by an event/search/config batch separately.
- Derive cell size from libtermy render config or `measure_cell`; do not guess monospace ratios in the host.
- Preserve the flat cell contract: full frames are row-major; partial updates provide cells in dirty-span order.
- Keep `termy_core` independent of GPUI, desktop app chrome, Swift, and `termy_ffi`.
- On macOS, keep SwiftUI out of the hot grid path. Use retained AppKit drawing, dirty rect invalidation, cached row render plans, and display-synced polling.
- Do not force full frame updates for ordinary input, scroll, or wakeup ticks.

## Validation

Use `scripts/check_libtermy_repo.sh` to orient an agent in a Termy checkout:

```sh
~/.codex/skills/libtermy-implementation/scripts/check_libtermy_repo.sh /path/to/termy
```

Run targeted checks based on the change:

```sh
cargo test -p termy_core
cargo test -p termy_ffi
cargo build -p termy_ffi
TERMY_FFI_LIBRARY_PATH="$PWD/target/debug" swift test --package-path macos
macos/scripts/check-performance-gates.sh --native-render-metrics
macos/scripts/check-render-perf.sh
```

Use broader macOS release gates only when packaging, launch behavior, signing, or app-level regressions are in scope.
