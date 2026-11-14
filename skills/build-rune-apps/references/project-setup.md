# Project setup, revs and the development loop

Rune is pre-release and isn't on crates.io. An app depends on the git repository
at one commit of `dev`, which is fast-forward-only, so a pinned rev keeps
building. The audited rev of this skill is in [sources.md](sources.md).

## Pick the rev

- New app: the newest `dev` commit.
  `git ls-remote https://github.com/anomalyco/rune refs/heads/dev` prints it.
  Record the SHA and its date in the app's README or manifest comment.
- Existing app: keep its rev. `Cargo.lock` is the truth
  (`source = "git+https://github.com/anomalyco/rune?rev=…#<sha>"`).
- Never `branch = "dev"` or a bare git dependency: the lock moves when someone
  runs `cargo update`, and the patch table below drifts out of step.

## The manifest

```toml
[dependencies]
rune = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
rune-kit = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }   # when chosen

[features]
hot = ["rune/hot"]            # live Rust editing
tooling = ["rune/tooling"]    # headless flags in release builds

[patch.crates-io]
winit = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
parley_engine = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
wgpu-hal = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
accesskit_windows = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
```

- **The patch table is mandatory.** Rune vendors patched crates and applies them
  through its root `[patch.crates-io]`. A dependency's `[patch]` doesn't reach
  the app's workspace, so the app has to repeat it. The patches carry Rune's
  macOS input-method, Windows window-creation, bidi and shaping changes, and
  `rune` calls into them: at the audited rev a missing table fails dependency
  resolution (`parley_engine` lacks the `line-dictionaries` feature) and a
  missing `winit` entry fails to compile (`set_ime_text` not found in
  `winit::platform::macos`). At other revs an omission may build and only
  misbehave, so check rather than rely on the error. The list is Rune's root
  table at the pinned rev and can change between revs. `scripts/check_rune_patches.py Cargo.toml` compares
  them; `--print-table <rev>` prints the right block.
- In a workspace, the patch table belongs in the workspace root manifest.
- Every Rune crate is addressed by package name from the same git URL and rev:
  `rune-kit`, `rune-motion`, `rune-fx`, `rune-light`, `rune-mac`,
  `rune-notify`, `rune-perf`, `rune-knobs`, `rune-i18n`, `rune-luau`. Mixing
  revs gives two copies of `rune` and type errors between them.
- `themes/opencode` (`rune-theme-opencode`) is OpenCode's brand as data. Use it
  for an OpenCode surface, not as a neutral default; use `Kit::neutral` or
  `Kit::from_palette` instead.
- Copy Rune's profiles (`debug = "line-tables-only"`, dependency debug off,
  release `codegen-units = 16`, `incremental = true`); full debug info makes
  test builds enormous.
- Match the toolchain to Rune's `rust-toolchain.toml` at the rev (1.99.1 at the
  audited rev) or newer. Rune uses edition 2024.

## Features worth knowing

`rune` defaults: `accessibility`, `dbus`, `embedded-fonts`, `metal-backend`,
`ogg-audio`, `svg`.

| Feature | Use |
| --- | --- |
| `tooling` | `--snap`, `--tree`, `--script`, `--video` in release builds (debug always has them) |
| `keys-overlay` | `--keys` and `--pointer` keycaps over headless frames in release builds |
| `hot` | live Rust editing through `rune-hot`/`rune-dev` |
| `native-file-dialog` | native Open/Save/folder dialogs (rfd, XDG portal on Linux) |
| `embedded-fonts` | bundled Inter; turn off only when `AppSpec::fonts` supplies every face |
| `avif` | AVIF decoding (NASM needed on x86) |
| `segmenter-dictionaries` | Windows: link ICU word dictionaries instead of `icu.dll` |
| `macos-background-cursor` | private API; App Store review may reject it |
| `frame-profile`, `alloc-sites` | measurement builds only |

rune-kit adds `markdown` and `mermaid`. Read the exact list in
`crates/rune/Cargo.toml` at the rev; feature names move.

## Build prerequisites

- **Linux**: `libxkbcommon-dev libwayland-dev` (Debian/Ubuntu) at build time,
  `libxkbcommon-x11-0` to open windows, and a Vulkan driver (`mesa-vulkan-drivers`
  for software) to draw. Headless `--snap` needs neither display nor XKB.
- **Windows**: MSVC needs only the C++ build tools. The GNU toolchain also needs
  MinGW-w64 binutils (`dlltool`) on `PATH`.
- **Web**: `wasm32-unknown-unknown`, the `wasm-bindgen-cli` version in Rune's
  lockfile, and Rune's `scripts/web-build.sh`; see [web](upstream/web.md).
- **Video output** (`--video`): `ffmpeg` on `PATH`.

## Rune's own scripts

`scripts/mac-app`, `scripts/app-audit`, `scripts/rune-hot`, `scripts/rune-dev`,
`scripts/motion-audit` and `scripts/web-build.sh` live in the Rune repository.
Run them from Cargo's checkout of the pinned rev
(`~/.cargo/git/checkouts/rune-*/<first 7 of the rev>/scripts/`) or a clone at that
rev, so they match the library the app links.

## Upgrade a rev

1. Read `CHANGELOG.md` (`## dev`) and `changelog/unreleased/` between the old
   and new rev; each entry names what can move an app's output or break its build.
2. Change every `rev` together: dependencies and patch table. Run
   `check_rune_patches.py`; add new patch entries Rune added.
3. Match the toolchain if Rune's moved.
4. Build. Rune avoids new public fields on types apps build as literals
   (`AppSpec`, `Env`, `RunOptions`, `ScrollSpec`, `TextStyle`, `OverlaySpec`,
   `Span`, …) and adds builder methods instead; end `AppSpec` literals with
   `..AppSpec::new(..)` so one that slips through doesn't break the app.
5. Re-render every scene light and dark and compare with the previous renders
   before accepting the bump. Text, motion and colour can change without a
   compile error.

## Development loop

- `cargo run` opens the window. Pass Rune's flags after `--`:
  `cargo run -- --snap out.png --scene many`.
- Headless renders are the fast loop: edit, build, snap, read the PNG. See
  [headless validation](headless-validation.md).
- **Live Rust editing**: add `hot = ["rune/hot"]`, install Dioxus CLI **0.7.10** as
  `dx` in Cargo's bin directory (the Homebrew `dx` is unrelated), then from the
  Rune checkout:
  `scripts/rune-hot --manifest ../my-app/Cargo.toml --patch 'src/ui/**/*.rs' -- APP ARGS`.
  Function bodies in the patched files reload in the open window; other edits
  rebuild and relaunch. State lives in `AppSpec::init`'s value; tip-crate
  statics and thread locals may reset; `setup` runs once. See
  [restart boundaries](upstream/rune/compatible-edits-and-restart-boundaries.md).
  `scripts/rune-dev` without `--local` assumes the maintainers' build workers.
- **Mac bundle while developing**: `scripts/mac-app` installs and relaunches a
  built binary as `~/Applications/NAME.app` without the window blinking; see
  [platform delivery](platform-delivery.md).
