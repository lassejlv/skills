---
url: /base/primitives/date-picker.md
description: A focus-aware date input that composes calendar behavior with a popup.
---

# Date Picker

A focus-aware date input that composes calendar behavior with a popup.

Like every `gpui-base` primitive, Date Picker supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- date-picker
```

## Import

```rust
use gpui_kit::base::{DatePicker};
```

## Anatomy and API

The example composes `DatePicker`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/date_picker.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/date_picker.rs). Native and browser previews compile this same file.

## State and events

The picker combines focus/input state with calendar selection. Retain its entities on the parent view.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn date_picker(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let open = self.date_open;
        let entity = cx.entity().downgrade();
        let trigger_entity = entity.clone();
        let trigger = Button::new("date-trigger")
            .w_full()
            .h_7()
            .px_3()
            .flex()
            .items_center()
            .justify_between()
            .border_1()
            .border_color(super::example_rgb(0xa3a3a3))
            .bg(super::example_rgb(0xffffff))
            .on_click(move |_, _, cx| {
                _ = trigger_entity.update(cx, |this, cx| {
                    this.date_open = !open;
                    cx.notify();
                });
            })
            .child("Aug 12, 2026")
            .child(super::chevron(false));
        let popup = Popup::new("date-picker-popup", trigger).when(open, |this| {
            this.content(
                div()
                    .w(px(250.))
                    .bg(super::example_rgb(0xffffff))
                    .child(self.calendar()),
            )
        });

        DatePicker::new("example-date-picker", &self.date_focus)
            .open(open)
            .on_open_change(move |open, _, cx| {
                _ = entity.update(cx, |this, cx| {
                    this.date_open = open;
                    cx.notify();
                });
            })
            .w(px(250.))
            .text_xs()
            .child(popup)
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Label the input, announce locale-appropriate dates, and make the calendar keyboard operable.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/date-picker) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/date-picker.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
