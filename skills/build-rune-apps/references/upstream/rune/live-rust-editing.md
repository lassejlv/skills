> Upstream: [crates/rune/README.md § Live Rust editing (desktop development)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#live-rust-editing-desktop-development) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Live Rust editing (desktop development)

```sh
scripts/rune-dev settings -- --snap-on-patch perf/live-edit/settings.png --hot-control perf/live-edit/control.json
```

Edit a view function and the existing process rebuilds its keyed tree. Scroll offsets,
app state and spring tracks stay in the runtime. Layout and colour edits use the same
retargeting as input changes. Handlers are recreated before queued input runs.
Omit `--snap-on-patch` for a window on a development machine.

Hot builds type-erase the host state behind thin typed adapters, so the runtime and
shell compile once in the Rune library rather than in each changing executable.
The explicit `HotFn` boundary still calls the app's typed view function. The headless
PNG encoder uses its fastest lossless mode; normal snapshots keep their existing encoding.

The launcher currently assumes the maintainers' remote build-worker setup: it runs
the compiler and app together in one worker lease, relays source edits, and fetches
each PNG and matching `.json` tree into this checkout. Install **Dioxus CLI 0.7.10**
as `dx` in Cargo's bin directory first (`RUNE_DX` overrides the path); the
Homebrew/Deno command with the same name is unrelated. The first build is a full
development build; subsequent runs reuse `target/rune-dev/<example>`.
Compiler artifacts live in `target/live-edit-build`.

`--local` (or `RUNE_DEV_LOCAL=1`) skips the worker setup: the compiler, the edit guard and
the app all run on this machine, and an edit that needs a restart rebuilds and relaunches the
app instead of asking you to rerun. `RUNE_DEV_WRAP` runs all of that under a command prefix
(a build-queue lease, say); without it, it runs on plain `cargo`. `scripts/rune-hot` is the
same with shorter flags, for an app's own scripts:

```sh
scripts/rune-hot --manifest ../my-app/Cargo.toml --patch src/view.rs [--patch …] [--port 18745] [-- APP ARGS]
```

The `hot` feature is opt-in. Feature-off builds have no patch dependencies, connection,
dispatch, generation checks or extra runtime fields. Goldens use feature-off builds.
