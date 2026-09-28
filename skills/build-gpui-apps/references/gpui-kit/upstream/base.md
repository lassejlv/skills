---
url: /base.md
description: The unstyled behavior and infrastructure foundation of GPUI Kit, the Rust desktop framework.
---

# GPUI Base

`gpui-base` is the unstyled foundation of GPUI Kit, the Rust desktop application framework. It provides interaction behavior, controlled state, focus management, accessibility semantics, animation, virtual lists, and theme tokens while leaving layout and visual design to your application.

## Choose the right layer

| Use | When |
| --- | --- |
| `gpui-base` | You are building a design system and want to own every visual choice. |
| `gpui-component` | You want a complete set of styled, ready-to-use desktop components. |

The dependency points one way: `gpui-component` builds on `gpui-base`. Applications can use either layer directly.

## Principles

- **Behavior is built in.** Controls provide consistent pointer, keyboard, focus, and state behavior.
- **Presentation is yours.** Compose GPUI style methods and children without fighting default visuals.
- **Parts stay composable.** Primitives expose their meaningful subparts instead of hiding markup behind a monolith.
- **State stays explicit.** Controlled inputs report changes and your view owns the resulting state.

## Start building

Follow [Getting started](https://gpui-kit.com/getting-started.md), render selectable Markdown and HTML with [TextView](https://gpui-kit.com/text-view.md), learn how to add [window-level text selection](https://gpui-kit.com/text-selection.md) to custom renderers, then explore the [primitive catalog](https://gpui-kit.com/primitives/index.md). Each page includes Rust snippets and a live WASM example backed by the same example crate that can run natively.

Three systems are larger than a primitive and have pages of their own. [Motion](https://gpui-kit.com/motion.md) provides typed transitions, springs, keyframes, presence, and sequencing. [Virtual List](https://gpui-kit.com/virtual-list.md) renders lists of any length by drawing only what is on screen, with per-item sizes rather than a uniform row height. [Dock](https://gpui-kit.com/dock.md) is a full workspace shell — nested splits, tab groups and edge docks — whose layout is pure data you can build and serialize without a window, and whose every pixel comes from renderer traits you implement. [History](https://gpui-kit.com/history.md) covers two smaller, deliberately distinct structures: `History` is a root/current/back/forward navigation trail, while `UndoHistory` records grouped undo and redo transactions. [Plot](https://gpui-kit.com/plot.md) is the unstyled foundation for charts: scales, shapes, axes, the element that turns a `Plot` into a child, and hover tracking, with colors and timing left to your design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
