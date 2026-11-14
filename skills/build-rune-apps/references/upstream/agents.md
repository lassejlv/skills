> Upstream: [AGENTS.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/AGENTS.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

<!-- tallow -->
# Rune

A Rust GPU UI framework (wgpu, winit) for apps that feel like SwiftUI on iOS at 120 Hz on Mac, Windows, Linux, web and iOS. Views are plain Rust. Apps pin `dev` revs.

## Layout

- `crates/rune`: layout, runtime, renderer, windows, overlays, dev tooling. `crates/rune-kit`: components. `crates/rune-mermaid`: Mermaid diagrams (flowcharts, sequence and state diagrams). `crates/rune-i18n`: message catalogs generated from JSON, CLDR plurals and numbers, the system's languages. `crates/rune-motion`: springs and transitions. `crates/rune-fx`, `crates/rune-light`: effects. `crates/rune-ref`: reference renderer. `crates/procwatch`: an app's own memory and CPU (footprint, counting allocator, gauges, warnings, loopback JSON); libc only, no Rune dependency.
- `examples/`: apps and labs. `themes/`: themes. `site/`: the docs site (see `site/README.md`).
- `vendor/winit`: winit as published plus `vendor/winit.patch` (Windows: no TaskbarList COM call when a window is made), through `[patch.crates-io]`. When winit is bumped, run `scripts/vendor-winit.sh <new version>` (Git Bash on Windows) and update the `[patch.crates-io]` rev in apps that build Rune.
- `vendor/tiny-skia-path`: tiny-skia-path as published plus `vendor/tiny-skia-path.patch` (Skia's own conic splitting and stroker steps, so icons stroke as Chromium's Skia strokes them), a plain path dependency of `crates/rune`, not a patch (resvg keeps the published one). When it is bumped, run `scripts/vendor-tiny-skia-path.sh <new version>` (Git Bash on Windows).
- `vendor/wgpu-hal`: wgpu-hal as published plus `vendor/wgpu-hal.patch` (`dx12::Instance::expose_adapter`, and FXC loaded on first compile), through `[patch.crates-io]`. When wgpu is bumped, run `scripts/vendor-wgpu-hal.sh <new wgpu-hal version>` (Git Bash on Windows) and update the `[patch.crates-io]` rev in apps that build Rune.
- `PLAN.md`: direction and milestones. `research/`: notes behind decisions. `demo/`: images the docs show.

## Commands

- `cargo test -p rune -p rune-mermaid -p rune-kit --features rune-kit/markdown,rune-kit/mermaid`
- `cargo check --workspace --all-targets`
- Tests run in debug. `--release` is incremental, for looking at an app. Benchmarks use `--profile perf`; the runtime bench scripts refuse other builds.
- CI's macOS tests (`.github/workflows/macos-tests.yml`) run on a schedule and on `workflow_dispatch`, not per pull request or push: the owner's decision on 2026-11-12. Don't add those triggers back; run the workflow by hand when a change needs it.

## Changes

- Work on `dev`. `production` deploys the site.
- `dev` is fast-forward-only: never force-push or rewrite it. Apps pin its revs, so a rewrite breaks every app's build on a clean fetch.
- For any change that can move an app's output or break its build, add `changelog/unreleased/<YYYY-MM-DD>-<slug>.md` with one top-level bullet, in the style of the `CHANGELOG.md` entries. `scripts/changelog-fold` folds them into `## dev`.
- Keep Rust files under 800 non-test lines (`#[cfg(test)]` code excluded); 1,500 is a hard cap. The point is to stop god files and edit collisions, not to chop a file that reads fine as one piece. Older files over the cap are listed in `scripts/file-size-exceptions.txt` with ceilings that only go down. Run `scripts/file-size.sh` to check.
- Keep folders shaped by capability: `x.rs` or `x/` beside two or more `x_*.rs` (or three or more `x_*.rs` alone) means move them into `x/`; a folder over 40 source files warns and over 60 is an error (tests aren't counted; `examples/`, `benches/` and `bin/` are skipped). `scripts/folder-shape.sh` runs inside `scripts/file-size.sh`; old violations are in `scripts/folder-shape-exceptions.txt` with ceilings that only go down.
- Put tests in a sibling `tests.rs` or `*_tests.rs`, and keep any test file or module under 1,000 lines.
- Before adding to a file over the cap, move the area you touch into its own module, in its own PR.
- A feature owns its state, keys and registrations so it plugs in with one line. New runtime state goes in the owning subsystem's struct, not a flat `Runtime` field.
- In `lib.rs`, keep `mod` and `pub use` lists one item per line, sorted.
- Apps build these types as literals, so adding a pub field breaks them: `AppSpec`, `Env`, `Elevation`, `PaletteSeed`, `OverlaySpec`, `TextStyle`, `RunOptions`, `ScrollSpec`, `Span`, `ByteFrame`, `SurfaceDraw`, `LayerSpec`. Add a builder method instead.

## State

- Behaviour with modes or phases (hover delays, drags, IME composition, scroll modes, requests and retries) is an explicit state machine: one `enum State` whose variants carry only the data valid in them, and one `fn step(state: &mut State, event: Event) -> Effects<Effect>` (`rune::machine`) that returns effects instead of performing them. No clusters of booleans, `Option`s and timestamps whose combinations encode the mode.
- Timers are events: a timed variant stores its `Attempt` and due time on `Tx::clock`/the runtime clock, the caller turns its effect into `Tx::wake_at`, and `poll` (or the runtime's frame) feeds the timer back into `step`. An answer whose attempt the state no longer holds changes nothing.

## Performance

App-side rules live in "Launching fast" in `crates/rune/README.md` and the "Launch fast" docs page. In examples and in Rune itself:

- Start slow work (network, indexing, status items) from `on_ready`, after the first frame. Land state that arrives just after launch with `tx.instant()`, so the first second stays still.
- `poll` returns true only when visible state changed, and a loop stops asking for frames when its work ends. An idle window draws nothing.
- Read sizes with `Cx::layout_size` or `Cx::layout_with`, not whole rects, so a scroll doesn't rebuild the view every frame. A handler that only moves a live value (scroll, zoom, a transform) calls `Tx::live_only()`.
- Build only mounted rows: `virtual_rows`, with row content built inside its closure; `memo` for rows that rarely change.
- Bound every cache in entries and in bytes, counting decoded pixels, not encoded size.
- Take numbers from `--profile perf`. Compare paired, alternating runs by median, keep outliers, and say what a headless number leaves out (GPU upload, presentation).
- A motion change passes `scripts/motion-audit` with its scenario added. Fix a finding in Rune rather than allowing it.
- No file I/O in the frame loop: never read, stat, write, sync or rename a file on the UI thread during frames, input or animation. On Windows each open and `MoveFileExW` rename runs antivirus filter callbacks and can fail with a sharing violation.
- No background rewrite churn: diagnostics and logs (`rune-perf`, traces) keep one open handle and write a summary on an incident or at shutdown, never on a repeating timer while idle.
- Keep persistence APIs free of `std::fs` and `PathBuf` so `wasm32` targets can back them with browser storage.

## This repo is public

Everything pushed stays public in history. Before committing, run `git diff --cached | rg -n '/Users/|/private/var/|\.ts\.net|ses_[A-Za-z0-9]{20}'` and keep these out:

- secrets, tokens and credential file contents;
- home folder and temp paths, machine names and tailnet hostnames. Write repo-relative paths, and use `host.example.ts.net` in tests;
- session IDs, chat or Slack links, and quotes from private sessions, chats or calls;
- teammates' names attached to their plans, opinions or internal discussions, and private repos or branches;
- quotes of, or citations to, internal guides and rules. Say what the code does and why on its own terms;
- agent handoff notes (`REVIEW-TO-PARENT.md` and similar), raw evidence, logs and benchmark dumps;
- generated videos and strips nothing links to. Commit the stills a doc shows.
