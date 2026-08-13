# Project and versioning reference

Use this layer before creating a GPUI app, changing a dependency, copying an
upstream example, or touching startup and platform features. GPUI is pre-1.0:
the target checkout is always more authoritative than this research snapshot.

## Contents

- [Research baseline](#research-baseline)
- [Identify the dependency shape](#identify-the-dependency-shape)
- [Choose application startup](#choose-application-startup)
- [Select platform features](#select-platform-features)
- [Create a stable project baseline](#create-a-stable-project-baseline)
- [Shield version-sensitive APIs](#shield-version-sensitive-apis)
- [Upgrade deliberately](#upgrade-deliberately)
- [Review checklist](#review-checklist)

## Research baseline

This suite was refreshed on 2026-08-13 against:

- published GPUI `0.2.2` documentation;
- Zed main at commit `7733b9922665f103abda7c6a3fde6b9dfdc8eba9`;
- the current `gpui`, `gpui_platform`, `gpui_macros`, examples, test support,
  and platform sources at that commit.

Treat these as orientation, not a floating dependency recommendation. A target
using a Git revision from yesterday, an older crates.io release, a workspace
path, or a fork can have materially different startup, rendering, element,
platform, and test APIs.

The compile-checked fixture at `../assets/reference-app` pins this exact Git
revision and commits its lockfile. Use it to verify the suite's example shapes,
not as authority over a target checkout with a different lockfile.

## Identify the dependency shape

Inspect all workspace manifests and the lockfile. Classify the project:

| Shape | Evidence | Working rule |
|---|---|---|
| Published crate | `gpui = "x.y.z"` and registry source in `Cargo.lock` | Read docs for that exact version |
| Git dependency | `git` plus optional `rev`, `tag`, or `branch` | Resolve and record the locked commit |
| Zed workspace | `workspace = true` or a local `path` | Search the checked-out source and examples |
| Fork | Non-Zed repository URL or patched crate | Treat fork source and local wrappers as authoritative |
| Wrapper library | UI crate re-exports GPUI and project components | Use its prelude, theme, and conventions first |

Run:

```sh
rg -n 'gpui(_platform)?\s*=' --glob 'Cargo.toml'
rg -n '^name = "gpui"$|^source = |^version = ' Cargo.lock
cargo tree -i gpui
```

For Git dependencies, use the `Cargo.lock` source hash or `git rev-parse` in the
dependency checkout. Do not report only a branch name: branches move.

Check the repository toolchain file and minimum supported Rust version before
adding language or standard-library features.

## Choose application startup

The current standalone upstream shape uses `gpui_platform::application()` to
construct the platform application, then opens a window whose root is an
`Entity<V>`. Older examples can use `Application::new()`, project-specific app
wrappers, or startup helpers.

Choose startup this way:

1. Keep the target project's working entrypoint when startup is outside scope.
2. For a new app, copy the smallest example from the exact pinned GPUI source.
3. Register actions, globals, assets, fonts, theme, and platform integration
   before opening views that depend on them.
4. Keep window construction in one clear owner.
5. Make startup failures observable; do not discard errors from initialization.
6. Do not rewrite startup solely to make a newer example compile.

The shape below is intentionally schematic:

```rust
fn main() {
    gpui_platform::application().run(|cx| {
        // Register app-wide state and actions first.
        cx.open_window(window_options(), |window, cx| {
            cx.new(|cx| RootView::new(window, cx))
        })
        .expect("open main window");
    });
}
```

Confirm the exact return types, result handling, and closure signatures in the
pinned source before using this.

## Select platform features

The current upstream `gpui_platform` manifest and platform entrypoint expose
these common feature choices:

- macOS: a font backend such as `font-kit` can be selected by the pinned
  project;
- Linux: select the intended window-system support, commonly `wayland`,
  `x11`, or both;
- Windows: follow the current crate's native dependencies and feature defaults.

Feature names and defaults can change. Inspect the pinned
`crates/gpui_platform/Cargo.toml` and `src/gpui_platform.rs`. Avoid copying a
feature list from a blog post.

For cross-platform apps:

- keep shared view/state code in shared modules;
- isolate AppKit, Win32, or Linux backend work in explicit platform modules;
- compile unavailable platform code out with narrow `cfg` boundaries;
- expose a capability-oriented interface to shared code;
- supply behavior and appearance fallbacks;
- test that feature combinations do not accidentally compile two backends.

Avoid scattering raw `cfg(target_os = "macos")` through view trees. Put platform
policy behind a component, theme, window, or material service.

## Create a stable project baseline

For a new application, establish:

```text
src/
  main.rs              # process startup only
  app.rs               # registration and root window ownership
  state/               # domain models and state machines
  views/               # stateful screen entities
  components/          # reusable value-like UI
  theme/               # semantic tokens and material policy
  platform/            # narrow OS bridges
  assets.rs            # asset source and identifiers
  actions.rs           # typed actions and key contexts
tests/                 # integration tests where useful
```

Prefer one obvious root entity, one source of truth per domain value, and typed
actions/events. Add abstractions after a second use case proves them.

Pin dependencies through the lockfile. In application repositories:

- commit `Cargo.lock`;
- use `cargo test --locked` in CI;
- audit changes to Git revisions and features;
- avoid an unpinned moving branch for production;
- document platform toolchains and native prerequisites.

Baseline checks:

```sh
cargo fmt --check
cargo check --workspace --all-targets
cargo test --workspace --locked
cargo clippy --workspace --all-targets -- -D warnings
```

Scale these to the owning crate when the workspace is large or has unrelated
known failures.

For the fixture bundled with this skill:

```sh
scripts/validate_reference_app.sh
```

The script requires Rust 1.97.1, matching the pinned Zed toolchain snapshot.

## Shield version-sensitive APIs

Use these shields:

1. Search the target checkout for a compiling sibling before external docs.
2. Keep GPUI-specific code near its owning component instead of hiding basic
   APIs behind a speculative framework.
3. Wrap unstable or platform-specific behavior behind a small semantic adapter:
   material application, window construction, asset loading, or test harness.
4. Keep pure logic independent from GPUI where practical.
5. Put version assumptions in a nearby comment only when the reason is not
   visible in code.
6. Do not support multiple GPUI eras unless the product actually builds them.

Good seams include:

- `MaterialPolicy::surface(role, preferences)`;
- `WindowFactory::open_main`;
- a pure reducer returning state transitions;
- a pure spring integrator;
- a domain command that returns data, with GPUI orchestration outside it.

Avoid a broad “GPUI compatibility layer” that mirrors the whole framework. It
adds a second API without making upgrades cheaper.

## Upgrade deliberately

When changing GPUI:

1. Record old and new versions or commits.
2. Read the upstream diff for crates and modules actually used.
3. Update the dependency and lockfile in isolation.
4. Compile the smallest owning crate.
5. Fix startup and type/API changes without mixing visual redesign.
6. Run targeted interaction and `#[gpui::test]` coverage.
7. Launch on every supported backend available.
8. Recheck fonts, window appearance, focus, input, overlays, lists, and
   screenshots.
9. Record untested platforms.

Never call an upgrade safe from `cargo check` alone. Backend behavior, renderer
output, text metrics, accessibility trees, and window APIs are runtime concerns.

## Review checklist

- [ ] Exact dependency source and locked revision recorded
- [ ] Toolchain and platform features confirmed from the target
- [ ] Existing startup preserved or current pinned example followed
- [ ] Shared and platform-specific responsibilities separated
- [ ] Lockfile and feature changes reviewed
- [ ] Pure logic kept testable outside GPUI where useful
- [ ] No invented compatibility abstraction
- [ ] Targeted build, tests, launch, and platform checks reported
- [ ] Time-sensitive claims refreshed from [sources.md](sources.md)
