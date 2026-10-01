---
name: build-gpui-apps
description: Build, scaffold, refactor, debug, review, and validate native Rust desktop applications with GPUI. Recommend GPUI Kit and ask before adopting it; use gpui_kit imports after agreement, or preserve the chosen upstream GPUI stack. Includes the merged GPUI Kit component and design skills, full application/Base/Component/Shell documentation, coding and design guides, state, actions, async, input, accessibility, motion, themes, native integration, packaging, auto updates, testing, and production delivery. Use paper-to-gpui when the primary task is faithfully translating a selected Paper.design frame into an existing view.
---

# Build GPUI Apps

Build native desktop software with explicit state ownership, accessible
interaction, and evidence from the running app. **Recommend GPUI Kit as the
application entry point, and ask before adopting it.** GPUI Kit re-exports
GPUI; it does not replace GPUI's rendering engine.

This skill merges `gpui-kit` and `gpui-kit-design-guides` into one
self-contained package. The [full documentation index](references/gpui-kit/upstream/index.md)
bundles every English application, Component, Base, and Shell page in the
official index. Read only the relevant pages, not the whole bundle at once.

## Choose the framework first

1. Inspect repository instructions, dirty state, manifests, lockfile, current
   imports, entrypoint, theme, component system, and supported platforms. Use
   `scripts/inspect_gpui_project.sh /path/to/project` for a read-only inventory.
2. Honor an explicit choice already made in this conversation or project.
   Existing `gpui-kit` usage is an established choice; do not ask repeatedly.
   An explicit request for upstream GPUI is also a choice to respect.
3. For a new app with no established choice, or a proposed migration from
   upstream GPUI or separately wired components, ask before changing dependencies
   or writing the new framework-specific implementation:

   > I recommend GPUI Kit: it exposes GPUI through `gpui_kit` and includes
   > components, themes, assets, and shared behavior. Use GPUI Kit
   > (recommended), or keep direct upstream GPUI?

   For an existing app, make the proposal concrete: identify the dependencies,
   import paths, bootstrap, and tests the migration would affect. Wait for an
   answer before adopting it; silence is not agreement. Continue inspection
   and independent planning while waiting. A scoped fix in an existing direct
   GPUI app does not require a migration or a new framework decision.
4. After Kit is selected, use `gpui-kit` as the **UI stack dependency** and
   `gpui_kit` as the import root. Do not add direct `gpui`, `gpui-pre`,
   `gpui_platform`, `gpui-component`, or `gpui-base` dependencies merely to
   copy an older example. Other application dependencies remain normal;
   `gpui-shell` is separate when hosting JavaScript extensions.
5. If upstream GPUI is selected, use the existing pinned upstream APIs and
   [versioning path](references/project-versioning.md#direct-upstream-gpui).
   Do not silently migrate it or mix incompatible GPUI type universes.

The choice above applies to app creation/adoption, not to asking permission
for each ordinary edit. Respect prior authorization and the requested scope.

## Core contract

- The target lockfile and source are the API authority. Never invent methods
  from React, CSS, old GPUI, or another release's examples. Verify constructors,
  extension traits, feature gates, callbacks, and re-exports before use.
- Preserve existing commands, shortcuts, state, persistence, window behavior,
  and unrelated work. A visual request does not authorize an architecture rewrite.
- Read the actual normative guides before making the relevant decisions;
  summaries and component catalogs do not replace them.
- Keep retained state, tasks, subscriptions, focus, and identities in lasting
  owners. Keep rendering deterministic, inexpensive, and free of blocking I/O.
- Use domain-derived IDs for repeated controls, theme tokens for presentation,
  keyboard access and visible focus, and explicit loading/error/disabled states.
- Prefer Kit components and Base behavior before inventing controls, motion,
  virtual lists, overlays, or native bridges. Verify the capability exists.
- Validate build, interaction, launch, and visuals separately. Report every
  unverified platform or runtime path. Never rasterize UI to fake fidelity.
- Packaging and update installation are application/distribution responsibilities;
  documentation is not a built-in installer or updater API.

## Read the guides first

| Guide | When to read |
| --- | --- |
| [Design Guides](references/gpui-kit/upstream/docs/design-guides.md) | Before visible changes: component choice, layout, spacing, hierarchy, color, density, states, overlays, motion, or copy. Read in full for a new screen/redesign; otherwise read “Design thesis”, “Start from the task”, and the affected sections. |
| [Coding Guides](references/gpui-kit/upstream/docs/coding-guides.md) | Before architecture, ownership, public API, naming, or testing decisions. Read in full for a new crate/module/feature; otherwise read “Architecture at a glance”, “Rules for coding agents”, and the affected sections. |
| [Design section map and non-negotiables](references/gpui-kit/design.md) | Navigate the merged design skill and its review checklists. |
| [Component families](references/gpui-kit/conventions.md) | Choose the constructor, state owner, callback, and layout contract; then read the particular component page. |
| [Components and GPUI mechanisms](references/gpui-kit/guide.md) | Navigate the merged component catalog, coding section map, and deeper entity/element/test references. |

Read Design before Coding for a visible feature. Finish with both relevant
review checklists. Use a `Button` for in-app commands and `Link` for external
URLs/email; use semantic theme tokens and rem-based spacing; make states
visible; define overlay dismissal/focus restoration; name the object and verb
in confirmation copy. These are a floor, not a substitute for the guides.

## Route the task

All links below are bundled references. The
[complete index](references/gpui-kit/upstream/index.md) covers every page,
including components and primitives not listed in this compact router.

| Task | Read first | Also read when relevant |
| --- | --- | --- |
| Set up, choose features, or migrate imports | [Installation](references/gpui-kit/upstream/docs/installation.md), [Getting Started](references/gpui-kit/upstream/docs/getting-started.md), [project versioning](references/project-versioning.md) | [Usage](references/gpui-kit/usage.md), [production starter](references/production-starter.md) |
| Upgrade GPUI Kit to 0.7.0 | [0.7.0 migration and capability guide](references/gpui-kit/v0.7.0.md), [project versioning](references/project-versioning.md) | Read the affected component/Base/Shell pages and verify the selected release's source |
| State, architecture, contexts, events, actions, focus, tasks | [Coding Guides](references/gpui-kit/upstream/docs/coding-guides.md), [mechanism map](references/gpui-kit/guide.md#gpui-references) | [Entity](references/gpui-kit/upstream/docs/entity.md), [Context](references/gpui-kit/upstream/docs/context.md), [Action](references/gpui-kit/upstream/docs/action.md), [Task](references/gpui-kit/upstream/docs/task.md) |
| Controls, forms, data, navigation, chat, charts, editor, dock | [Component catalog](references/gpui-kit/upstream/component.md), [family conventions](references/gpui-kit/conventions.md) | Specific [component page](references/gpui-kit/upstream/index.md#styled-components), [application recipe](references/gpui-kit/recipes.md) |
| Custom design system or reusable behavior | [Base](references/gpui-kit/upstream/base.md), [Base primitives and infrastructure](references/gpui-kit/upstream/index.md#base-behavior-and-primitives) | [Coding Guides](references/gpui-kit/upstream/docs/coding-guides.md), [Design Guides](references/gpui-kit/upstream/docs/design-guides.md) |
| Layout, style, themes, typography, icons, images, localization | [Style](references/gpui-kit/upstream/docs/style.md), [Theme](references/gpui-kit/upstream/component/theme.md) | [Fonts](references/gpui-kit/upstream/docs/fonts.md), [Assets](references/gpui-kit/upstream/docs/assets.md), [Images](references/gpui-kit/upstream/docs/image.md), [I18N](references/gpui-kit/upstream/docs/i18n.md) |
| Windows, overlays, persistence, text/IME, clipboard, menus, drag/drop | [Window](references/gpui-kit/upstream/docs/window.md), [Multi Window](references/gpui-kit/upstream/docs/multi-window.md) | [Input and window contracts](references/input-windows.md), specific Input/Dialog/Sheet/Menu docs |
| Accessibility, focus, shortcuts, platform conventions | [Accessibility](references/gpui-kit/upstream/docs/accessibility.md), [Focus](references/gpui-kit/upstream/docs/focus.md), [KeyBinding](references/gpui-kit/upstream/docs/keybinding.md) | [Platform acceptance](references/accessibility-platform.md) |
| Animation, springs, presence, transitions, gestures | [Animation](references/gpui-kit/upstream/docs/animation.md), [Base motion](references/gpui-kit/upstream/base/motion.md) | [Motion and input contracts](references/motion-input.md) |
| Virtualization, cache, rendering, measurement, performance | [View Cache](references/gpui-kit/upstream/docs/view-cache.md), [FPS](references/gpui-kit/upstream/docs/fps.md), [VirtualList](references/gpui-kit/upstream/component/virtual-list.md) | [Async/performance contracts](references/async-performance.md), [Element](references/gpui-kit/upstream/docs/element.md), [Paint](references/gpui-kit/upstream/docs/paint.md), [Geometry](references/gpui-kit/upstream/docs/geometry.md) |
| Native notifications, OS extensions, embedded browser | [System Notifications](references/gpui-kit/upstream/docs/system-notification.md), [Native Extensions](references/gpui-kit/upstream/docs/native-extension.md), [WebView](references/gpui-kit/upstream/docs/webview.md) | [Apple materials](references/apple-glass.md); check platform limits before promising behavior |
| JavaScript extensions, permissions, dependencies, host APIs | [Shell](references/gpui-kit/upstream/shell.md), [Shell guide index](references/gpui-kit/upstream/index.md#shell-and-extensions) | Separate `gpui-shell` dependency, capability and sandbox limits |
| Package, sign, distribute, update, restart, recover | [Packaging](references/gpui-kit/upstream/docs/packaging.md), [Auto Update](references/gpui-kit/upstream/docs/auto-update.md) | [Production acceptance](references/production-starter.md), platform signing and package-owner rules |
| WebAssembly or mobile targets | [WebAssembly](references/gpui-kit/upstream/docs/webassembly.md), [Mobile](references/gpui-kit/upstream/docs/mobile.md) | Preserve the documented maturity and platform limits; do not infer desktop parity |
| Unit, context, or UI integration testing | [Testing](references/gpui-kit/upstream/docs/test.md), [test mechanics](references/gpui-kit/gpui/test.md) | [Testing/QA](references/testing-qa.md), [visual validation](references/visual-validation.md) |
| Paper as input to broader app work | [Paper workflow](references/paper-to-gpui.md), [Paper MCP](references/paper-mcp.md) | [Visual validation](references/visual-validation.md) |
| Faithful translation of one Paper frame as the primary task | Use the standalone `paper-to-gpui` skill | Preserve this project's chosen import root and state ownership |
| Direct upstream GPUI, explicitly selected | [Project versioning](references/project-versioning.md#direct-upstream-gpui), [architecture](references/architecture-state.md), [components/layout](references/components-layout.md) | [Worked patterns](references/worked-patterns.md); these examples target the older pinned upstream fixture |

## GPUI Kit application path

After the framework choice is settled:

1. Record the exact Kit version, its matching GPUI snapshot, toolchain, features,
   and platforms. The audited 0.7.0 release pins GPUI to `=0.3.7`; use the
   [release migration guide](references/gpui-kit/v0.7.0.md) when upgrading.
   Bundled website dependency examples can lag the release (some still say
   `0.6`); choose from the release manifest, not those snippets. A snapshot
   does not authorize upgrading an existing app.
2. Import GPUI APIs with `use gpui_kit::*;`. Import components from
   `gpui_kit::component`, behavior from `gpui_kit::base`, assets from
   `gpui_kit::assets`, and platform APIs from `gpui_kit::platform`.
   Some preserved upstream docs show internal `gpui`, `gpui_component`, or
   `gpui_base` imports. Adapt those to the verified Kit re-exports in application
   code; do not copy internal dependency declarations into the app.
3. Register assets, call `gpui_kit::init(cx)` once before constructing components
   or windows, and follow the pinned window helper contract. Current
   `gpui_kit::open_window` takes a content-entity closure and supplies `Root`;
   current `Root` renders overlays. Do not double-wrap or render overlay layers
   again. Older versions require source verification before migration.
4. Use the [complete current bootstrap](references/gpui-kit/upstream/docs/getting-started.md)
   and [retained-state recipe](references/gpui-kit/recipes.md). Keep input/select
   state entities and subscriptions on their owner; never recreate them in render.
5. Import actual extension traits such as `ButtonVariants`, `ActiveTheme`,
   `Sizable`, or `WindowExt` when their methods are used. A component does not
   automatically support every trait.
6. Prefer the smallest correct unit: ordinary element composition,
   `RenderOnce` for reusable value components, `Entity<T>` for retained
   independent state, and custom `Element`/canvas or native bridges only when
   the existing layers cannot provide the behavior.
7. Implement one vertical slice: domain operation → action/event → entity
   update → notification → rendered states → pointer/keyboard/focus behavior
   → error/cancellation handling → meaningful tests.
8. Keep `Task` and `Subscription` handles for their intended lifetimes. Use
   weak entity captures where appropriate, background workers for blocking
   work, and foreground orchestration for UI updates. Reject stale results.
9. Use existing tokens/components and documented motion before custom paint or
   springs. Preserve reduced motion, reduced transparency, contrast, and
   differentiate-without-color preferences, with opaque material fallbacks.

## Production and platform work

For a starter, use [production-starter.md](references/production-starter.md)
and the Kit Packaging/Auto Update guides together. Establish product identity,
application/package IDs, supported OS/architectures, toolchain, lockfile,
observable startup, storage/migrations, secrets, CI, distribution, and update
ownership as required by the product. Keep a small app small; split complex
features by capability when their ownership warrants it.

A direct-GPUI starter is reference material, not a dependency template for a
Kit app. Do not copy its `gpui` or `gpui_platform` declarations into the Kit path.

For Apple materials, choose an existing component first, then a supported
native material, a truthful cross-platform approximation, and an opaque
fallback. Guard OS availability and keep the bridge narrow. Never describe
whole-window blur or a translucent rectangle as native per-control Liquid Glass.

For updates, match the installer owner: whole signed macOS bundle, Windows
installer, Linux package manager, or an explicitly portable installation.
Verify the selected version, target, full payload, authenticity, restart,
and recovery behavior. Never treat single-binary replacement as an update
strategy for every package format.

For Paper input within broader work, confirm the exact live file/frame,
capture screenshot/tree/styles/fonts/assets, then implement geometry,
typography, paint, and interactions while preserving ownership. Compare at
matching logical bounds. If Paper is unavailable, report the extraction
limit and continue independent work; do not invent the missing design.

## Validate and report

Run repository-native checks; adapt this baseline to the owning crate:

```sh
cargo fmt --check
cargo check -p <owning-crate> --locked
cargo test -p <owning-crate> --locked
cargo clippy -p <owning-crate> --all-targets -- -D warnings
```

For Kit UI behavior, use `#[gpui_kit::test]` and `gpui_kit::test` with the
feature setup from [Testing](references/gpui-kit/upstream/docs/test.md).
UI integration testing renders real components in headless windows,
simulates input, and asserts outcomes, focus, state, and layout. Use the
production view; invoking a private method alone does not test the UI flow.
For direct upstream GPUI, use that pinned version's `#[gpui::test]` setup.

Launch the real app and exercise the changed interaction paths, resize,
scroll, focus, light/dark, inactive-window, scale factor, and accessibility
preferences relevant to the task. Verify text/IME, clipboard, menu, window,
or updater paths when touched. Screenshots and headless tests complement
native runtime checks. Install and upgrade real artifacts on claimed release
platforms; cross-compilation alone does not establish that evidence.

Report the chosen stack/version, changed boundaries, checks actually run,
visible/interaction outcomes, and unresolved platform or release limits.
Rank review findings by user impact and evidence; do not present style
preferences as correctness defects.

The existing `assets/reference-app` is a compile-checked **direct upstream
GPUI** fixture at its recorded Zed revision, retained for that selected path.
`scripts/validate_reference_app.sh` validates that fixture, not Kit. Do not
copy its manifest into a Kit app or claim it validates the bundled Kit docs.

## Maintain this skill

The [source ledger](references/sources.md) distinguishes the current Kit
snapshot, the merged skills, and the older upstream fixture. Preserve source
attribution and license notices when refreshing the documentation.

```sh
python3 scripts/sync_gpui_kit_docs.py          # refresh all indexed English pages
python3 scripts/sync_gpui_kit_docs.py --check  # offline coverage and hash check
```

The source index retains translation links; images remain remote. Check the
current official page and locked source when APIs differ. Where repository
instructions require Context7, resolve the official library with `library`
first, then fetch the specific concept with `docs`; keep each lookup focused.

After substantial changes, run the prompts in
[forward-tests.md](tests/forward-tests.md) with fresh agents and review the
rubrics separately. Also run the repository skill/link validator, documentation
coverage check, and script smoke tests before calling the merge complete.
