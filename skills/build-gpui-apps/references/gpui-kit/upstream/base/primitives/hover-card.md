---
url: /base/primitives/hover-card.md
description: A delayed floating card associated with a pointer or keyboard trigger.
---

# Hover Card

A delayed floating card associated with a pointer or keyboard trigger.

Like every `gpui-base` primitive, Hover Card supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

On iOS and Android, the trigger toggles the card on click and an outside click dismisses it. Hover and its open/close delays are ignored.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- hover-card
```

## Import

```rust
use gpui_kit::base::{HoverCard};
```

## Anatomy and API

The example composes `HoverCard`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/hover_card.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/hover_card.rs). Native and browser previews compile this same file.

## State and events

Pointer or focus entry schedules opening and exit schedules dismissal.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn hover_card(&self) -> impl IntoElement {
        HoverCard::new("example-hover-card")
            .trigger(
                div()
                    .id("hover-trigger")
                    .px_3()
                    .py_1()
                    .text_xs()
                    .text_color(super::example_rgb(0x171717))
                    .underline()
                    .child("Hover over gpui-base"),
            )
            .content(|_, _, _| {
                div()
                    .id("hover-content")
                    .w(px(210.))
                    .p_2()
                    .text_xs()
                    .bg(super::example_rgb(0xffffff))
                    .border_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .child(
                        div()
                            .flex()
                            .items_center()
                            .gap_2()
                            .child(
                                div()
                                    .size_7()
                                    .flex()
                                    .items_center()
                                    .justify_center()
                                    .border_1()
                                    .border_color(super::example_rgb(0x171717))
                                    .text_sm()
                                    .child("G"),
                            )
                            .child(
                                div().text_sm().child("gpui-base").child(
                                    div()
                                        .text_sm()
                                        .text_color(super::example_rgb(0x737373))
                                        .child("@gpui-base"),
                                ),
                            ),
                    )
                    .child(
                        div()
                            .mt_2()
                            .text_sm()
                            .text_color(super::example_rgb(0x737373))
                            .child("Unstyled primitives for GPUI."),
                    )
            })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Expose it from keyboard focus and duplicate essential information outside hover-only content.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/hover-card) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/hover-card.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
