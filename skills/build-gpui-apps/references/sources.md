# Primary sources and research ledger

This reference records the primary sources used to build the suite. Refresh
time-sensitive API claims against the target checkout.

## Contents

- [Snapshot](#snapshot)
- [GPUI and Zed](#gpui-and-zed)
- [GPUI starter example](#gpui-starter-example)
- [Apple design and AppKit](#apple-design-and-appkit)
- [Paper](#paper)
- [Rust quality](#rust-quality)
- [Suite validation toolchain](#suite-validation-toolchain)
- [Refresh protocol](#refresh-protocol)

## Snapshot

Research date: **2026-08-13**

Upstream Zed commit:

```text
7733b9922665f103abda7c6a3fde6b9dfdc8eba9
```

Published GPUI version reviewed: `0.2.2`.

Local source areas inspected at that commit:

- `crates/gpui/README.md` and `Cargo.toml`
- `crates/gpui/src/app.rs`
- `crates/gpui/src/app/context.rs`
- `crates/gpui/src/entity.rs`
- `crates/gpui/src/elements/animation.rs`
- `crates/gpui/src/elements/div.rs`
- `crates/gpui/src/window.rs` and `window/a11y.rs`
- `crates/gpui/src/input.rs` and the current text-input example
- `crates/gpui/src/app/test_context.rs`
- `crates/gpui/src/touch_gestures.rs`
- `crates/gpui_platform`
- GPUI examples for accessibility, data tables, drag/drop, images, menus,
  multi-window behavior, text input, and tab stops

The local macOS 26 SDK header for `NSGlassEffectView` and
`NSGlassEffectContainerView` was also checked. Stable target SDK headers remain
more authoritative than beta web properties.

## GPUI and Zed

- [GPUI home](https://www.gpui.rs/)
- [GPUI 0.2.2 API documentation](https://docs.rs/gpui/0.2.2/gpui/)
- [GPUI source in Zed](https://github.com/zed-industries/zed/tree/main/crates/gpui)
- [GPUI README](https://github.com/zed-industries/zed/blob/main/crates/gpui/README.md)
- [GPUI platform source](https://github.com/zed-industries/zed/tree/main/crates/gpui_platform)
- [Pinned GPUI tree used by this snapshot](https://github.com/zed-industries/zed/tree/7733b9922665f103abda7c6a3fde6b9dfdc8eba9/crates/gpui)
- [AccessKit project](https://github.com/AccessKit/accesskit)

Use the pinned tree for claims in this suite about:

- `App`, `Context<T>`, `Entity<T>`, and async contexts;
- held/detached `Task` and `Subscription` behavior;
- foreground/background executor paths;
- reduced-motion integration in finite animations;
- window background appearance;
- accessibility identity/actions;
- `EntityInputHandler`, UTF-16 selection, clipboard, and input geometry;
- typed drag payloads, menus, and window lifecycle/context methods;
- non-opaque window backgrounds disabling the pinned subpixel text path;
- touch gesture defaults;
- `TestAppContext` and `#[gpui::test]`.

## GPUI starter example

- [lassejlv/gpui-starter](https://github.com/lassejlv/gpui-starter)
- [Inspected repository commit](https://github.com/lassejlv/gpui-starter/tree/9781c9295178f6b357cba167fca77df9e070d713)
- [Workspace manifest at the inspected commit](https://github.com/lassejlv/gpui-starter/blob/9781c9295178f6b357cba167fca77df9e070d713/Cargo.toml)
- [Desktop startup at the inspected commit](https://github.com/lassejlv/gpui-starter/blob/9781c9295178f6b357cba167fca77df9e070d713/crates/desktop/src/main.rs)

The production-starter sub-skill was grounded on 2026-08-13 in repository
commit `9781c9295178f6b357cba167fca77df9e070d713`. Its lockfile resolved GPUI and
`gpui_platform` from Zed commit
`101ca00a1352ed71ef398f21b47836565d1998e3`; that Zed commit's checked-in
toolchain is Rust 1.95.0.

At that snapshot the example contains `desktop` and `ui` crates, a committed
lockfile, `just` development commands, window/menu/keybinding setup, icons, a
theme, and a small button gallery. It intentionally does not yet contain CI,
packaging/signing, persistence, structured diagnostics, or meaningful tests.

Local source validation at the recorded commits:

- workspace check passed with `--locked --all-targets` on macOS;
- workspace test build passed with zero tests;
- strict workspace Clippy passed with warnings denied;
- `cargo fmt --all -- --check` reported committed formatting differences;
- launch, visuals, accessibility, other platforms, and packaged artifacts were
  not verified.

Refresh the repository before using it as a source. Treat the example as a
minimal architectural baseline, not a current production-readiness claim.

## Apple design and AppKit

- [Human Interface Guidelines: Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Human Interface Guidelines: Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Human Interface Guidelines: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/)
- [Meet Liquid Glass, WWDC25](https://developer.apple.com/videos/play/wwdc2025/219/)
- [Get to know the new design system, WWDC25](https://developer.apple.com/videos/play/wwdc2025/356/)
- [NSGlassEffectView](https://developer.apple.com/documentation/appkit/nsglasseffectview)
- [NSGlassEffectContainerView](https://developer.apple.com/documentation/appkit/nsglasseffectcontainerview)
- [NSVisualEffectView](https://developer.apple.com/documentation/appkit/nsvisualeffectview)
- [NSWorkspace accessibility display options](https://developer.apple.com/documentation/appkit/nsworkspace/accessibilitydisplayoptionsdidchangenotification)

Important boundaries derived from these sources:

- Liquid Glass belongs primarily to controls/navigation above content.
- Regular and clear glass have different legibility use cases.
- System preferences can alter transparency and contrast.
- `NSGlassEffectView`/container are macOS 26-era AppKit APIs.
- `NSVisualEffectView` remains a different standard material/vibrancy path.
- AppKit web documentation can expose beta members absent from a stable SDK.

## Paper

- [Paper Desktop MCP](https://paper.design/docs/mcp)
- [Paper tokens](https://paper.design/docs/tokens)
- [Paper documentation index](https://paper.design/docs)
- [Paper support and troubleshooting](https://paper.design/docs/support)
- [Paper build log](https://paper.design/build-log)
- [Paper downloads/current desktop release](https://paper.design/downloads)

The MCP endpoint and Codex connection instructions come from Paper's MCP
documentation. Token capabilities and design-feature chronology come from the
tokens page and build log. Always inspect the live MCP schemas for the actual
tool set and arguments.

## Rust quality

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Clippy documentation](https://doc.rust-lang.org/clippy/)
- [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)
- [Cargo check](https://doc.rust-lang.org/cargo/commands/cargo-check.html)
- [Cargo tree](https://doc.rust-lang.org/cargo/commands/cargo-tree.html)

Follow the target repository's stricter linting, unsafe-code, dependency,
documentation, and testing policy when it differs.

## Suite validation toolchain

The repository workflow was refreshed on 2026-08-13 against these primary
release sources and pins their release commits rather than floating tags:

- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
- [actions/setup-python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0)
- [actions/cache v5.1.0](https://github.com/actions/cache/releases/tag/v5.1.0)
- [PyYAML 6.0.3](https://pypi.org/project/PyYAML/6.0.3/)

The workflow installs Rust 1.97.1 directly with `rustup`, matching the pinned
Zed toolchain, and runs the GPUI fixture on a hosted macOS runner so the Metal
backend can compile. Refresh action pins when their majors, runner runtime
requirements, or security guidance change.

## Refresh protocol

Refresh this suite when:

- the target GPUI revision differs materially;
- GPUI releases a new minor version;
- app startup or platform features no longer compile;
- accessibility/window/animation APIs change;
- Apple changes Liquid Glass/AppKit availability or stable members;
- Paper changes MCP transport/tools or extraction data.
- the `gpui-starter` example changes its architecture, revision, or release
  tooling.
- validation actions or hosted runner requirements change.

Refresh steps:

1. Record date, published version, and exact upstream commit.
2. Inspect source, not only rendered docs.
3. Check a current compiling example for each changed API.
4. Inspect stable SDK headers for AppKit availability.
5. Inspect live Paper tool schemas.
6. Update examples and capability claims together.
7. Run the inspector, skill validator, shell syntax check, and spring tests.
8. Compile, test, and lint `assets/reference-app` with its locked revision.

Do not remove version warnings merely because one example compiles.
