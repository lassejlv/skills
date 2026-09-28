---
url: /base/primitives/number-input.md
description: A numeric input with reusable increment, decrement, and step behavior.
---

# Number Input

A numeric input with reusable increment, decrement, and step behavior.

Like every `gpui-base` primitive, Number Input supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- number-input
```

## Import

```rust
use gpui_kit::base::{Decrement, Increment, NumberInput, NumberInputText};
```

## Anatomy and API

The example composes `Decrement`, `Increment`, `NumberInput`, `NumberInputText`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/number_input.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/number_input.rs). Native and browser previews compile this same file.

## State and events

The backing input state owns numeric text/value; step actions apply the configured limits.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{
    AnyElement, Context, InteractiveElement, IntoElement, ParentElement as _, Styled as _, div, px,
    relative,
};
use gpui_base::{Button, NumberInput};

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn number_input(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let valid = self.input.read(cx).value().parse::<f64>().is_ok();

        fn render_btn(this: Button, icon: AnyElement) -> Button {
            this.w(px(24.))
                .flex_1()
                .min_h_0()
                .line_height(relative(1.))
                .flex()
                .items_center()
                .justify_center()
                .bg(gpui::black())
                .text_color(gpui::white())
                .hover(|this| this.bg(gpui::black().opacity(0.8)))
                .child(icon)
        }

        fn minus_icon() -> AnyElement {
            div()
                .w(px(8.))
                .h(px(1.))
                .bg(gpui::white())
                .into_any_element()
        }

        fn plus_icon() -> AnyElement {
            div()
                .relative()
                .size(px(8.))
                .child(
                    div()
                        .absolute()
                        .top(px(3.5))
                        .left_0()
                        .w_full()
                        .h(px(1.))
                        .bg(gpui::white()),
                )
                .child(
                    div()
                        .absolute()
                        .left(px(3.5))
                        .top_0()
                        .h_full()
                        .w(px(1.))
                        .bg(gpui::white()),
                )
                .into_any_element()
        }

        div()
            .w(px(200.))
            .flex()
            .flex_col()
            .gap_1()
            .text_xs()
            .child(div().text_xs().child("Quantity"))
            .child(
                NumberInput::new(&self.input)
                    .controls_right()
                    .w_full()
                    .h_7()
                    .flex()
                    .items_center()
                    .border_1()
                    .border_color(if valid {
                        super::example_rgb(0x171717)
                    } else {
                        super::example_rgb(0x737373)
                    })
                    .input(div().w_full().px_2().child(self.input.clone()))
                    .decrement_button(|button| render_btn(button, minus_icon()))
                    .increment_button(|button| render_btn(button, plus_icon())),
            )
            .child(
                div()
                    .text_xs()
                    .text_color(super::example_rgb(0x737373))
                    .child(if valid { "Step: 1" } else { "Enter a number" }),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Expose label, value, bounds, and keyboard-accessible step actions.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/number-input) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/number-input.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
