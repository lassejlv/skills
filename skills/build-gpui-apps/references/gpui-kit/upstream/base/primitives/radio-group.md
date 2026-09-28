---
url: /base/primitives/radio-group.md
description: Groups radio items and provides keyboard navigation for a single selection.
---

# Radio Group

Groups radio items and provides keyboard navigation for a single selection.

Like every `gpui-base` primitive, Radio Group supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- radio-group
```

## Import

```rust
use gpui_kit::base::{Radio, RadioGroup};
```

## Anatomy and API

The example composes `Radio`, `RadioGroup`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/radio_group.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/radio_group.rs). Native and browser previews compile this same file.

## State and events

The group coordinates one selected value and keyboard movement; `Radio` renders each option.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{
    Context, IntoElement, ParentElement as _, Styled as _, div, prelude::FluentBuilder as _, px,
};
use gpui_base::{Radio, RadioGroup};

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn radio_group(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let entity = cx.entity().downgrade();
        RadioGroup::new("example-radio-group")
            .w_56()
            .text_xs()
            .flex()
            .flex_col()
            .gap_2()
            .child(self.radio(cx))
            .child(
                Radio::new("express-radio")
                    .checked(self.radio_selected == 1)
                    .on_change(move |next, _, _, cx| {
                        if next {
                            _ = entity.update(cx, |this, cx| {
                                this.radio_selected = 1;
                                cx.notify();
                            });
                        }
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
                            .when(self.radio_selected == 1, |this| {
                                this.child(div().size(px(6.)).bg(super::example_rgb(0x171717)))
                            }),
                    )
                    .child(
                        div().child("Express").child(
                            div()
                                .text_xs()
                                .text_color(super::example_rgb(0x737373))
                                .child("Next business day"),
                        ),
                    ),
            )
            .child(
                Radio::new("pickup-radio")
                    .disabled(true)
                    .flex()
                    .items_start()
                    .gap_2()
                    .opacity(0.45)
                    .child(
                        div()
                            .mt(px(2.))
                            .size(px(14.))
                            .border_1()
                            .border_color(super::example_rgb(0x171717)),
                    )
                    .child(
                        div()
                            .child("Local pickup")
                            .child(div().text_xs().child("Currently unavailable")),
                    ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Label the group, expose one checked item, and support arrow keys among enabled choices.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/radio-group) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/radio-group.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
