# GPUI reference app

This is the compile-checked companion to the `build-gpui-apps` skill. It pins
Zed/GPUI commit `7733b9922665f103abda7c6a3fde6b9dfdc8eba9` and Rust 1.97 so
the higher-level examples have one executable API baseline.

It demonstrates:

- `gpui_platform::application()` startup;
- root `Entity` and `Context` state ownership;
- typed actions, scoped key bindings, and application menus;
- an owned self-subscription and semantic entity event;
- cancellable async work with a stale-generation guard;
- stable IDs, roles, labels, tab stops, and focus-visible controls;
- a virtualized `uniform_list`;
- a semantic opaque material and explicit accessibility fallbacks;
- reduced-motion-aware spring orchestration;
- multiple windows and last-window close policy;
- pure Rust and `#[gpui::test]` tests.

It deliberately does not claim to be:

- a component framework;
- a production text editor or full IME implementation;
- native Liquid Glass or backdrop blur;
- proof of Windows/Linux runtime behavior from a macOS build;
- a visually accepted product screen.

Read `../../references/input-windows.md` before implementing custom editable
text, clipboard, drag/drop, dynamic menus, close prompts, or restoration.

## Validate

From the skill directory:

```sh
scripts/validate_reference_app.sh
```

The script runs formatting, exact-lockfile compilation, all tests, and Clippy
with warnings denied. macOS requires Xcode's Metal toolchain. Linux needs the
native libraries required by the selected Wayland/X11 GPUI features.

To open the sample window in a desktop session:

```sh
cargo +1.97.1 run --manifest-path assets/reference-app/Cargo.toml --locked
```

Launching remains a separate verification step; CI compilation and tests do
not prove window appearance, focus, accessibility output, or input behavior.

### Known pinned dependency notice

Rust 1.97.1 reports a future-incompatibility lint in indirect macOS dependency
`block 0.1.6` (`static of uninhabited type`). The fixture itself remains clean
under Clippy with warnings denied. Keep the notice visible and re-evaluate it
when refreshing GPUI; do not hide it or add an unreviewed dependency patch just
to silence the report.

## Refresh the pin

Do not casually float this dependency. When refreshing it:

1. Record the new Zed commit and matching toolchain.
2. Update every `gpui` and `gpui_platform` revision together.
3. Regenerate and review `Cargo.lock`.
4. Recheck source-backed API claims in the skill references.
5. Run the validation script and launch on each supported platform available.
6. Update `references/sources.md` with the new research snapshot.
