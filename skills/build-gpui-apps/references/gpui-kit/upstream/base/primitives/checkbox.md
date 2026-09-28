---
url: /base/primitives/checkbox.md
description: A controlled tri-state check control with a separately styled indicator.
---

# Checkbox

A controlled tri-state check control with a separately styled indicator.

Like every `gpui-base` primitive, Checkbox supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- checkbox
```

## Import

```rust
use gpui_kit::base::{Checkbox, CheckboxIndicator};
```

## Anatomy and API

The example composes `Checkbox`, `CheckboxIndicator`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/checkbox.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/checkbox.rs). Native and browser previews compile this same file.

## State and events

Pass the controlled value to `checked`; `on_change` emits `CheckboxState`, including indeterminate.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;
use gpui::{Image, ImageFormat, img};
use std::sync::Arc;

const CHECK_SVG: &[u8] = br#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none"><path d="m3.25 8.25 3 3 6.5-7" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>"#;

impl BaseShowcase {
    pub(in super::super) fn checkbox(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let checked = self.checkbox_checked;
        let entity = cx.entity().downgrade();
        Checkbox::new("example-checkbox")
            .checked(checked)
            .flex()
            .items_center()
            .gap_2()
            .on_change(move |state, _, _, cx| {
                _ = entity.update(cx, |this, cx| {
                    this.checkbox_checked = state == CheckboxState::Checked;
                    cx.notify();
                });
            })
            .child(
                CheckboxIndicator::new()
                    .checked(checked)
                    .flex()
                    .items_center()
                    .justify_center()
                    .size_4()
                    .border_1()
                    .border_color(super::example_rgb(0x171717))
                    .when(checked, |this| {
                        this.bg(super::example_rgb(0x171717)).child(
                            img(Arc::new(Image::from_bytes(
                                ImageFormat::Svg,
                                CHECK_SVG.to_vec(),
                            )))
                            .size(px(12.)),
                        )
                    }),
            )
            .child(div().text_xs().child("Enable product updates"))
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Keep label and control associated and expose checked, unchecked, indeterminate, and disabled states.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/checkbox) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/checkbox.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
