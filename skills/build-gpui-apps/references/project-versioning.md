# Project and versioning

Read the [framework choice policy](../SKILL.md#choose-the-framework-first)
before adopting a dependency. Recommend Kit and ask once when no choice has
been established. The target lockfile and source remain the API authority.

## Identify the dependency shape

Inspect workspace and member manifests, patches, aliases, features, lockfile,
source imports, toolchain, entrypoint, and a nearby compiling component.

| Shape | Evidence | Working rule |
| --- | --- | --- |
| GPUI Kit | `gpui-kit` package and `gpui_kit` imports | Use the Kit facade and matching locked GPUI snapshot |
| Direct published GPUI | `gpui`/`gpui-pre` dependency | Preserve it for scoped work; obtain a choice before migrating |
| Direct Git GPUI | Zed/fork Git dependency with a locked commit | Follow that exact source; do not substitute Kit silently |
| Workspace/path wrapper | Workspace inheritance, path dependency, re-export crate | Inspect the wrapper and actual resolved packages |
| Separately wired Component/Base | Direct `gpui-component`/`gpui-base` plus GPUI | Treat consolidation into Kit as a dependency migration |

```sh
rg -n 'gpui([-_][[:alnum:]_]+)*' --glob 'Cargo.toml'
rg -n '^name = "gpui[^" ]*"$' Cargo.lock
rg -n 'gpui_kit::|gpui::|gpui_component::|gpui_base::|gpui_platform::' --glob '*.rs'
cargo tree -d
```

Use `cargo metadata` or the relevant `cargo tree -i <resolved-package>` when
aliases/workspace inheritance hide the real source. Record an exact lockfile
version/commit, not only a moving branch or the facade's semver requirement.

## GPUI Kit

Start with [Installation](gpui-kit/upstream/docs/installation.md) and
[Getting Started](gpui-kit/upstream/docs/getting-started.md). The documentation
refreshed on 2026-10-01 includes older `0.6` dependency examples even though
the [published 0.7.0 manifest](https://github.com/longbridge/gpui-kit/blob/v0.7.0/Cargo.toml)
declares Kit `0.7.0` and pins `gpui-pre` to `=0.3.7`. The release manifest and
locked source take precedence over conflicting installation snippets.
Read the [0.7.0 migration guide](gpui-kit/v0.7.0.md) before upgrading; retain
the target's version for work that does not include an upgrade.

```toml
[dependencies]
gpui-kit = "0.7.0" # audited release example; commit the resolved Cargo.lock
```

```rust
use gpui_kit::*;
use gpui_kit::component::button::{Button, ButtonVariants};
```

The facade covers GPUI, `component`, `base`, `assets`, and `platform`. A
`gpui-pre` package in the lockfile is expected: it publishes a recorded GPUI
snapshot, not another renderer. Do not independently override its version or
add a second direct GPUI dependency. `gpui-shell` is separate for JavaScript
extension hosts; persistence, networking, updater, and other application
crates can still be added for actual product needs.

### Upgrade a selected Kit app

An established Kit choice does not require another framework-adoption question.
Honor the requested upgrade scope, record old/new lockfile versions, and review
[0.7.0 breaking changes](gpui-kit/v0.7.0.md#breaking-changes) against actual
callers. Migrate startup, events, state lifetime, and appearance only where
affected; validate those paths in the owning app. A newer GPUI snapshot alone
is not a reason to override Kit's exact dependency pins.

### Bootstrap and overlays

1. Construct `gpui_kit::application()` and register the chosen assets.
2. Call `gpui_kit::init(cx)` once before components/windows are constructed.
3. Current `gpui_kit::open_window(options, cx, builder)` wraps the returned
   content entity in `gpui_kit::base::Root` and returns the window handle plus
   content entity. Keep whichever handles the application needs.
4. Current Root renders its overlays. Do not return another Root to the Kit
   helper or add manual `Root::render_*_layer` children to application content.
5. If using low-level `cx.open_window` deliberately, construct one Root using
   the pinned API. Keep window ownership and errors observable.

The older merged skills used manual overlay rendering; that recipe has been
updated in this package. For an older app, inspect its actual Root behavior
before removing overlay code. Read [Window](gpui-kit/upstream/docs/window.md)
and [Testing](gpui-kit/upstream/docs/test.md) for exact current signatures.

### Migrate an existing app after agreement

- Inventory direct dependencies, patches, wrappers, macros, tests, assets,
  platform features, theme initialization, windows, and overlay ownership.
- Replace the UI stack dependency declarations with the selected Kit release
  and consistent workspace inheritance. Preserve necessary non-UI crates.
- Change application paths to `gpui_kit`, `gpui_kit::component`,
  `gpui_kit::base`, `gpui_kit::assets`, and `gpui_kit::platform`. Update test
  attributes to `#[gpui_kit::test]` and configure Kit's supported test feature.
- Do not blindly replace namespace text inside dependency source or strings.
  Verify procedural macros, generated paths, extension traits, and root APIs
  against the facade; downstream forks may need real adaptation.
- Review the dependency tree for duplicate incompatible GPUI packages and
  types. Check assets, platform features, fonts, Root and overlays explicitly.
- Compile the owning crate, run meaningful tests, launch it, and exercise
  keyboard/focus, input/IME, theme, resize, overlays, and multiple windows.
- Keep visual redesign separate unless it is part of the request. Report
  migrations not completed or platforms not exercised.

### Features and platforms

Use the chosen Kit manifest and the documentation for the feature being
added. Do not copy upstream `gpui_platform` feature declarations into a Kit
application. The default Kit setup includes styled components and icon assets;
custom asset and behavior-only configurations need their documented features.

Preserve platform maturity labels and boundaries for native extensions,
WebView, mobile, WebAssembly, and Shell. Desktop support does not prove those
features behave identically on every OS. Keep platform code behind narrow
capability boundaries with fallbacks.

## Direct upstream GPUI

This path applies when explicitly selected or already used for a scoped task.
The retained reference fixture at [reference-app](../assets/reference-app/README.md)
was compiled against Zed commit
`7733b9922665f103abda7c6a3fde6b9dfdc8eba9`; the original research also examined
published GPUI `0.2.2` on 2026-08-13. These are historical baselines, not new-app
dependency recommendations and not Kit compatibility evidence.

For direct upstream apps:

- Keep the working entrypoint when startup is outside scope. Depending on the
  source, it may use `gpui_platform::application()`, `Application::new()`, or a
  project-specific wrapper. Copy only from the exact pinned revision.
- Keep related GPUI Git packages on the same commit. Inspect feature defaults
  and platform prerequisites in that source instead of assuming Kit defaults.
- Register actions, globals, assets, fonts, and native integration before views
  that use them. Give window construction and startup errors a clear owner.
- Use the upstream [worked patterns](worked-patterns.md) and
  [architecture reference](architecture-state.md) only as revision-scoped
  examples. Do not mix their imports or fixture lockfile into Kit projects.
- `scripts/validate_reference_app.sh` checks that upstream fixture and requires
  its recorded toolchain. It does not validate a Kit consumer.

## Reproducibility and upgrades

For either selected stack:

1. Record old/new package versions or commits, features, and toolchain.
2. Read the change history for the APIs actually used.
3. Commit `Cargo.lock`; use `--locked` in CI and releases.
4. Update the dependency graph together and inspect duplicate packages.
5. Build the owning crate and correct real API differences.
6. Run relevant unit/context/UI integration tests.
7. Launch and check text metrics, assets, window chrome, overlays, input,
   accessibility, focus, and async behavior on available supported backends.
8. Check installed artifacts and upgrade behavior when releasing.
9. Report unavailable platforms separately; compilation alone is not proof of
   runtime or packaging compatibility.

Prefer local source and versioned official docs. Use the full bundled
[Kit index](gpui-kit/upstream/index.md) for discovery and the
[source ledger](sources.md) for provenance and refresh instructions.
