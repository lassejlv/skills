---
url: /base/primitives/collapsible.md
description: A composable region that shows or hides content without prescribing its trigger styling.
---

# Collapsible

A composable region that shows or hides content without prescribing its trigger styling.

Like every `gpui-base` primitive, Collapsible supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- collapsible
```

## Import

```rust
use gpui_kit::base::{Collapsible};
```

## Anatomy and API

The example composes `Collapsible`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/collapsible.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/collapsible.rs). Native and browser previews compile this same file.

## State and events

Pass the controlled expanded value to `open`; update it from the trigger callback.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn collapsible(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let open = self.collapsible_open;
        let entity = cx.entity().downgrade();
        Collapsible::new()
            .open(open)
            .w_64()
            .child(
                div()
                    .flex()
                    .items_center()
                    .justify_between()
                    .child(div().text_xs().child("@gpui/base · 3 repositories"))
                    .child(
                        Button::new("collapsible-trigger")
                            .size_7()
                            .border_1()
                            .border_color(super::example_rgb(0xd4d4d4))
                            .flex()
                            .items_center()
                            .justify_center()
                            .on_click(move |_, _, cx| {
                                _ = entity.update(cx, |this, cx| {
                                    this.collapsible_open = !this.collapsible_open;
                                    cx.notify();
                                });
                            })
                            .child(if open { "−" } else { "+" }),
                    ),
            )
            .child(
                div()
                    .mt_2()
                    .px_2()
                    .h_7()
                    .flex()
                    .items_center()
                    .border_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .text_xs()
                    .child("gpui-component"),
            )
            .content(div().mt_2().flex().flex_col().gap_2().children(
                ["gpui-base", "gpui-storybook"].into_iter().map(|name| {
                    div()
                        .px_2()
                        .h_7()
                        .flex()
                        .items_center()
                        .border_1()
                        .border_color(super::example_rgb(0xd4d4d4))
                        .text_xs()
                        .child(name)
                }),
            ))
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Name the trigger, expose expanded state, and remove hidden content from focus order.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/collapsible) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/collapsible.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
