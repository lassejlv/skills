---
url: /base/primitives/radio.md
description: A controlled single-choice item with selectable and disabled semantics.
---

# Radio

A controlled single-choice item with selectable and disabled semantics.

Like every `gpui-base` primitive, Radio supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- radio
```

## Import

```rust
use gpui_kit::base::{Radio};
```

## Anatomy and API

The example composes `Radio`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/radio.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/radio.rs). Native and browser previews compile this same file.

## State and events

Pass a controlled checked value; `on_change` reports selection and the parent clears peers.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{
    Context, IntoElement, ParentElement as _, Styled as _, div, prelude::FluentBuilder as _, px,
};
use gpui_base::Radio;

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn radio(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let checked = self.radio_selected == 0;
        let entity = cx.entity().downgrade();
        Radio::new("example-radio")
            .text_xs()
            .checked(checked)
            .on_change(move |next, _, _, cx| {
                _ = entity.update(cx, |this, cx| {
                    if next {
                        this.radio_selected = 0;
                    }
                    cx.notify();
                });
            })
            .flex()
            .items_start()
            .gap_2()
            .child(
                div()
                    .mt(px(2.))
                    .flex()
                    .items_center()
                    .justify_center()
                    .size(px(14.))
                    .border_1()
                    .border_color(super::example_rgb(0x171717))
                    .when(checked, |this| {
                        this.child(div().size(px(6.)).bg(super::example_rgb(0x171717)))
                    }),
            )
            .child(
                div().child("Standard").child(
                    div()
                        .text_xs()
                        .text_color(super::example_rgb(0x737373))
                        .child("3–5 business days"),
                ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Give each option a label and place mutually exclusive options in a named group.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/radio) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/radio.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
