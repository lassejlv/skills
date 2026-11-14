# Rune reference app

A small task list built with Rune and rune-kit, pinned to Rune `dev` commit
`65f8eb43f710e078f92cb82039212de50cb03113` (2026-11-14) and Rust 1.99.1, the
toolchain Rune names at that rev. It is the compile-, test- and render-checked
companion to the `build-rune-apps` skill and a starting point for new apps.

It demonstrates:

- one rev for `rune`, `rune-kit` and the four `[patch.crates-io]` entries;
- `AppSpec` with `min_size`, `on_key` and four scenes (`empty`, `many`,
  `hide-done`, `draft`), and `rune::prewarm_gpu()` before `App::run`;
- state that owns a `TextEdit` draft, rows keyed by domain id, and
  `TextEdit::clear()` after submit;
- rune-kit `TextInput`, `Button`, `Checkbox` and `Switch` on `Kit::neutral`, keyed
  after `build` and addressed by path (`task-3/check`);
- the window on `k.c.page` (a control vanishes when the window uses the card
  colour `bg_base` in light mode);
- a bounded scroll viewport (`.scroll(..).shrink().min_h(0.0)`) that keeps the
  footer in the window;
- a `Chord` shortcut (`mod+shift+h`) matched in `on_key`;
- `Runtime` tests that drive the real view with pointer input and read the
  accessibility tree;
- a headless script (`scripts/add-task.json`) that types, submits and ticks.

```sh
cargo run                                                         # the window
cargo test
cargo run -- --list-scenes
cargo run -- --snap out/many.png --scene many --theme dark --scale 2
cargo run -- --tree out/tree.json
cargo run -- --script scripts/add-task.json --snap out/after.png --at mark:end --scale 2
```

`../../scripts/validate_reference_app.sh` runs the patch-table check, fmt,
clippy, tests, every render and the tree assertions.

## Start an app from it

1. Copy the folder, rename the package, and change the title and state.
2. Pin the newest `dev` rev in every `rev = ".."`, then compare the patch table
   with `../../scripts/check_rune_patches.py --print-table <rev>`.
3. Match `rust-toolchain.toml` to Rune's at that rev.
4. Build: Cargo re-resolves Rune at the new rev, and the copied `Cargo.lock`
   keeps other dependencies at versions known to build. Render every scene
   before changing anything else.

It deliberately leaves out persistence, background work, multiple windows,
overlays (`rune_kit::root`), bundling and release builds with the `tooling`
feature; the skill's references cover those.
