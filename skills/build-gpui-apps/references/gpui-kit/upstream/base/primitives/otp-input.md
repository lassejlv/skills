---
url: /base/primitives/otp-input.md
description: A multi-cell one-time-code input driven by a shared text state.
---

# OTP Input

A multi-cell one-time-code input driven by a shared text state.

Like every `gpui-base` primitive, OTP Input supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- otp-input
```

## Import

```rust
use gpui_kit::base::{OtpInput, OtpState};
```

## Anatomy and API

The example composes `OtpInput`, `OtpState`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/otp_input.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/otp_input.rs). Native and browser previews compile this same file.

## State and events

`OtpState` owns the complete code and active cell; visual cells share that state.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{Context, IntoElement, ParentElement as _, Styled as _, div};
use gpui_base::OtpInput;

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn otp_input(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let value: Vec<char> = self.otp.read(cx).value().chars().collect();
        let active = value.len().min(5);

        div()
            .w_56()
            .flex()
            .flex_col()
            .gap_1()
            .text_xs()
            .child(div().text_xs().child("Verification code"))
            .child(
                div().child(
                    OtpInput::new(&self.otp)
                        .flex()
                        .gap_1()
                        .children((0..6).map(|ix| {
                            div()
                                .size_7()
                                .flex()
                                .items_center()
                                .justify_center()
                                .border_1()
                                .border_color(if ix == active {
                                    super::example_rgb(0x171717)
                                } else {
                                    super::example_rgb(0xd4d4d4)
                                })
                                .child(value.get(ix).copied().unwrap_or(' ').to_string())
                        })),
                ),
            )
            .child(
                div()
                    .text_xs()
                    .text_color(super::example_rgb(0x737373))
                    .child("Enter the 6-digit code."),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Label the whole code, announce length/errors, and support paste.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/otp-input) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/otp-input.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
