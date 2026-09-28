---
url: /base/primitives/popover.md
description: An anchored floating surface with controlled or internally managed open state.
---

# Popover

An anchored floating surface with controlled or internally managed open state.

Like every `gpui-base` primitive, Popover supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- popover
```

## Import

```rust
use gpui_kit::base::{Popover};
```

## Anatomy and API

The example composes `Popover`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/popover.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/popover.rs). Native and browser previews compile this same file.

## State and events

Use `.anchor(Anchor::TopCenter).offset(px(8.))` to open below the trigger,
centered, with an eight-pixel gap. The Base offset defaults to zero.
`Top*` anchors open below, `Bottom*` above, `LeftCenter` to the right,
and `RightCenter` to the left. The anchor names the popup's own point.
Window-edge clamping does not flip the popup or change its anchor.

`on_position` observes resolved popup and trigger bounds before content
prepaint for custom presentation. Base does not draw an arrow; styled Component
Popover provides `.arrow(true)` directly (default `false`), aligned to its anchor.

Open state can be parent-controlled; activation, outside click, and Escape request lifecycle changes.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{InteractiveElement as _, IntoElement, ParentElement as _, Styled as _, div, relative};
use gpui_base::{Button, Popover};

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn popover(&self) -> impl IntoElement {
        Popover::new("example-popover")
            .trigger(
                Button::new("popover-trigger")
                    .h_7()
                    .line_height(relative(1.))
                    .px_3()
                    .flex()
                    .items_center()
                    .justify_center()
                    .bg(gpui::black())
                    .text_color(gpui::white())
                    .child("Open Popover"),
            )
            .content(|_, _, cx| {
                let state = cx.entity().downgrade();
                div()
                    .id("popover-content")
                    .w_64()
                    .p_2()
                    .flex()
                    .flex_col()
                    .gap_2()
                    .text_xs()
                    .bg(super::example_rgb(0xffffff))
                    .border_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .child("Workspace access")
                    .child(
                        div()
                            .text_xs()
                            .text_color(super::example_rgb(0x737373))
                            .child("Anyone with the link can view."),
                    )
                    .child(
                        div().mt_1().flex().justify_end().child(
                            Button::new("popover-done")
                                .h_7()
                                .line_height(relative(1.))
                                .px_3()
                                .flex()
                                .items_center()
                                .justify_center()
                                .bg(gpui::black())
                                .text_color(gpui::white())
                                .on_click(move |_, window, cx| {
                                    _ = state.update(cx, |state, cx| state.dismiss(window, cx));
                                })
                                .child("Done"),
                        ),
                    )
            })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Support Escape/outside dismissal and return focus; move focus only when its content requires it.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/popover) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/popover.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
