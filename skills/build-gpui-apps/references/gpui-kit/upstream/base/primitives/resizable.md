---
url: /base/primitives/resizable.md
description: Panel groups and resize handles for user-adjustable split layouts.
---

# Resizable

Panel groups and resize handles for user-adjustable split layouts.

Like every `gpui-base` primitive, Resizable supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- resizable
```

## Import

```rust
use gpui_kit::base::{ResizablePanel, ResizablePanelGroup, ResizableState, h_resizable, resizable_panel};
```

## Anatomy and API

The example composes `ResizablePanel`, `ResizablePanelGroup`, `ResizableState`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/resizable.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/resizable.rs). Native and browser previews compile this same file.

## State and events

Panel sizes live in resizable state; dragging handles updates adjacent panels subject to minimums.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Handle appearance

Base owns a handle's hit band, its cursor and the drag; what is painted inside it is the consumer's. `ResizeHandleRenderer` is handed a `ResizeHandleContext` carrying the axis and a `ResizeHandleState` — `Idle`, `Hovered`, `Pressed` or `Dragging`. The last two are tracked by base because a drag takes the pointer out of the nine-pixel band almost at once, so GPUI's hover reads false for most of a drag.

Returning `None` keeps base's own one-pixel line, so a renderer can override some handles and leave the rest alone.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{IntoElement, ParentElement as _, Styled as _, div, px};
use gpui_base::{h_resizable, resizable_panel};

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn resizable(&self) -> impl IntoElement {
        div()
            .w_72()
            .h_40()
            .text_xs()
            .border_1()
            .border_color(super::example_rgb(0x171717))
            .child(
                h_resizable("example-resizable")
                    .child(
                        resizable_panel()
                            .size(px(124.))
                            .size_range(px(116.)..px(210.))
                            .child(
                                div()
                                    .size_full()
                                    .flex()
                                    .items_center()
                                    .justify_center()
                                    .border_r_1()
                                    .border_color(super::example_rgb(0x171717))
                                    .p_2()
                                    .items_start()
                                    .justify_start()
                                    .flex_col()
                                    .gap_1()
                                    .child(
                                        div()
                                            .text_xs()
                                            .text_color(super::example_rgb(0x737373))
                                            .child("PROJECT"),
                                    )
                                    .children(["Overview", "Components", "Settings"].map(
                                        |label| {
                                            div()
                                                .w_full()
                                                .h(px(26.))
                                                .px_2()
                                                .flex()
                                                .items_center()
                                                .whitespace_nowrap()
                                                .child(label)
                                        },
                                    )),
                            ),
                    )
                    .child(
                        resizable_panel().child(
                            div()
                                .size_full()
                                .flex()
                                .items_center()
                                .justify_center()
                                .bg(super::example_rgb(0xffffff))
                                .p_2()
                                .items_start()
                                .justify_start()
                                .flex_col()
                                .gap_2()
                                .child(div().child("Workspace"))
                                .child(
                                    div()
                                        .text_color(super::example_rgb(0x737373))
                                        .child("Drag the divider to resize navigation."),
                                ),
                        ),
                    ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Provide keyboard alternatives for handles and preserve usable minimum panel sizes.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/resizable) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/resizable.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
