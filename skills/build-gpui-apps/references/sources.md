# Primary sources and research ledger

This reference records the primary sources used to build the suite. Refresh
time-sensitive API claims against the target checkout.

## GPUI Kit 0.7.0 release audit

Audited on **2026-10-01** against the [published release](https://github.com/longbridge/gpui-kit/releases/tag/v0.7.0)
(published 2026-09-28) and tag commit
`0c830f4d257e69fdd17200650533ab4ca9a40cc0`. Checked the tag's
[workspace manifest](https://github.com/longbridge/gpui-kit/blob/v0.7.0/Cargo.toml)
and [Kit facade](https://github.com/longbridge/gpui-kit/blob/v0.7.0/crates/kit/src/lib.rs).
Kit is `0.7.0`, its GPUI snapshot is exactly `=0.3.7`, and `open_window`
constructs one Base Root and returns the window handle plus content entity.
The [release guide](gpui-kit/v0.7.0.md) routes the new capabilities and every
breaking-change category to the affected documentation.

Refreshed all **183 English indexed pages**; coverage is unchanged. Nine
original source hashes changed: docs landing, installation, getting started,
assets, i18n, multi-window, packaging, Component image, and Shell capabilities.
Those changes revert dependency/example versions to older `0.6`/`0.6.5`
values. Preserve the upstream text and hashes, but use the audited release
manifest for version selection. The September bundle already included the
new components and automatic Root hosting; this audit adds explicit upgrade
routing rather than claiming they were previously missing.

Context7 resolution selected `/longbridge/gpui-kit` (high-reputation official
repository). A focused Root/overlay migration query again returned older
manual-layer recipes. They conflict with the tag source and current Root
documentation and must not be copied into 0.7.0 applications. Versioned
documentation is advertised upstream, but the release installation Markdown
URLs tested under `/versions/v0.7.0` and `/versions/0.7.0` returned 404; use
the verified tag source when a versioned page is unavailable.

## GPUI Kit merge and documentation snapshot

Initially bundled on **2026-09-28** from the [official documentation](https://gpui-kit.com/docs/)
and [machine-readable index](https://gpui-kit.com/llms.txt). Context7 was
resolved through `bunx ctx7@latest library 'GPUI Kit'` to
`/longbridge/gpui-kit`, then queried for facade/bootstrap documentation.
That retrieved older manual-Root examples, so the current installation,
getting-started, window, and testing pages were used to resolve the difference.

The [bundled index](gpui-kit/upstream/index.md) covers **183 English pages**:
41 application pages, 78 Component pages, 49 Base pages, and 15 Shell pages
(counts include their four section landing pages). The saved `llms.txt` also
retains Chinese translation URLs. Images/illustrations remain remote; all
indexed English Markdown text is bundled. `upstream/manifest.json` records
retrieval time, source URL, original SHA-256, and adapted snapshot SHA-256 for
every page. Documentation links are localized and attribution is added;
prose and code are otherwise retained from the website.

At merge time the installation page specified `gpui-kit = "0.7.0"` and its recorded
`gpui-pre = 0.3.7` dependency. Other pages can contain older example versions.
Resolve that discrepancy from the selected release's manifest/source rather
than treating every snippet as a version recommendation. Current
`gpui_kit::open_window` provides Root, and Root renders overlays; the older
manual-overlay statements in the merged recipes were corrected accordingly.

Merged installed skill sources:

- [GPUI Kit skill](https://github.com/longbridge/gpui-kit/tree/main/skills/gpui-kit):
  component catalog, coding section map, conventions, usage, recipes, and all
  GPUI mechanism references, now under `references/gpui-kit/`.
- [GPUI Kit Design Guides skill](https://github.com/longbridge/gpui-kit/tree/main/skills/gpui-kit-design-guides):
  section map, non-negotiables, reading rules, and review routing, now in
  [design.md](gpui-kit/design.md). The full normative Design and Coding Guides
  are refreshed website snapshots, avoiding duplicate stale copies.

Credit GPUI Kit. Its documentation prose and original illustrations it can
license are offered under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/);
code and software use [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE).
Third-party material retains its terms. Each bundled page retains upstream
notices and links to its source; adapted skill references identify their source
and changes. Do not erase these notices when refreshing.

Refresh from the skill directory with
`python3 scripts/sync_gpui_kit_docs.py`; verify coverage and hashes offline with
`python3 scripts/sync_gpui_kit_docs.py --check`. The sync fetches every page
before writing any snapshot files. Run the repository Markdown/link validator
after refresh, review API/version changes, and reconcile adapted recipes.
A documentation snapshot is not evidence that example code was built here.

The remainder of this ledger describes the **historical direct upstream GPUI**
research and fixture. It does not override Kit's current API or imports.

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
