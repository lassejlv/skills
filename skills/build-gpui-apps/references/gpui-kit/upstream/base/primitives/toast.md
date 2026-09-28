---
url: /base/primitives/toast.md
description: A managed, animated stack of temporary status messages.
---

# Toast

A managed, animated stack of temporary status messages.

Like every `gpui-base` primitive, Toast supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- toast
```

## Import

```rust
use gpui_kit::base::{Toast, ToastManager, ToastOptions, ToastStack};
```

## Anatomy and API

The example composes `Toast`, `ToastManager`, `ToastOptions`, `ToastStack`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/toast.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/toast.rs). Native and browser previews compile this same file.

## State and events

Push messages through toast state; transition status retains an item during entry and exit.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn toast(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let visible = self.toast_visible;
        let entity = cx.entity().downgrade();
        div()
            .w_72()
            .h(px(158.))
            .text_xs()
            .relative()
            .flex()
            .items_center()
            .justify_center()
            .child(
                Button::new("show-toast")
                    .h_7()
                    .px_2()
                    .flex()
                    .items_center()
                    .justify_center()
                    .border_1()
                    .border_color(super::example_rgb(0x171717))
                    .bg(super::example_rgb(0xffffff))
                    .child("Save changes")
                    .on_click({
                        let show_entity = entity.clone();
                        move |_, _, cx| {
                            _ = show_entity.update(cx, |this, cx| {
                                this.toast_visible = true;
                                cx.notify();
                            });
                        }
                    }),
            )
            .when(visible, |this| {
                this.child(
                    Toast::new("example-toast")
                        .transition_status(ToastTransitionStatus::Present)
                        .absolute()
                        .right_0()
                        .bottom_0()
                        .w_64()
                        .p_2()
                        .border_1()
                        .border_color(super::example_rgb(0x171717))
                        .bg(super::example_rgb(0xffffff))
                        .child(
                            div()
                                .flex()
                                .justify_between()
                                .child(
                                    div()
                                        .font_weight(gpui::FontWeight::SEMIBOLD)
                                        .child("Changes saved"),
                                )
                                .child(
                                    Button::new("dismiss-toast")
                                        .size_6()
                                        .flex()
                                        .items_center()
                                        .justify_center()
                                        .child("×")
                                        .on_click({
                                            let entity = entity.clone();
                                            move |_, _, cx| {
                                                _ = entity.update(cx, |this, cx| {
                                                    this.toast_visible = false;
                                                    cx.notify();
                                                });
                                            }
                                        }),
                                ),
                        )
                        .child(
                            div()
                                .mt_1()
                                .text_color(super::example_rgb(0x737373))
                                .child("Your preferences are now up to date."),
                        ),
                )
            })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Choose live-region priority carefully and avoid essential actions only in expiring content.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/toast) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/toast.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
